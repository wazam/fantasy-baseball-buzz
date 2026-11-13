import os
import json
import queue
import threading
import traceback
from datetime import datetime, timezone
from config import SettingError, logger
from db import RESULTS_FOLDER

# One worker runs queued scrapes one at a time, so a double click or a second tab never starts a
# duplicate run and only one rate limiter is busy at once. Live state is in memory, which relies on
# Buzz running as a single process (flask run, or one gunicorn worker with threads)
_queue = queue.Queue()
_lock = threading.Lock()
_jobs = {}
_worker = None

# Every finished run is appended here as one JSON line, so history, counts and failures survive restarts
RUN_LOG = os.path.join(RESULTS_FOLDER, 'runs.jsonl')


def _now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def enqueue(job_id, func, *args, log_fields=None):
    """Queue func(*args) as job_id and return its status, unchanged if it is already queued or running.

    log_fields (e.g. source and trend) are saved with the run's outcome in RUN_LOG.
    """
    global _worker
    with _lock:
        job = _jobs.get(job_id)
        if job and job['state'] in ('queued', 'running'):
            return dict(job)
        _jobs[job_id] = {'state': 'queued', 'queued_at': _now()}
        _queue.put((job_id, func, args, log_fields or {}))
        # Started on first use, so the debug reloader's watcher process never runs scrapes
        if _worker is None:
            _worker = threading.Thread(target=_work, name='scrape-worker', daemon=True)
            _worker.start()
        return dict(_jobs[job_id])


def status():
    """Return a copy of every job's status, keyed by job id."""
    with _lock:
        return {job_id: dict(job) for job_id, job in _jobs.items()}


def read_run_log():
    """Return every logged run, oldest first."""
    try:
        with open(RUN_LOG, encoding='utf-8') as log:
            return [json.loads(line) for line in log if line.strip()]
    except FileNotFoundError:
        return []


def _update(job_id, **fields):
    with _lock:
        _jobs[job_id].update(fields)


def _log_run(job_id, log_fields):
    with _lock:
        job = dict(_jobs[job_id])
    entry = {**log_fields, **{key: job.get(key) for key in ('state', 'started_at', 'finished_at', 'count', 'error')}}
    try:
        os.makedirs(RESULTS_FOLDER, exist_ok=True)
        with open(RUN_LOG, 'a', encoding='utf-8') as log:
            log.write(json.dumps(entry) + '\n')
    except OSError as e:
        # A full or read-only disk shouldn't take the worker down with it
        print(f"Could not write the run log: {e}")


def _work():
    while True:
        job_id, func, args, log_fields = _queue.get()
        _update(job_id, state='running', started_at=_now())
        try:
            result = func(*args)
        except SettingError as e:
            # A trend that needs a setting that isn't set: the message names it, so no traceback
            logger.error(f"{job_id} can't run: {e}")
            _update(job_id, state='failed', finished_at=_now(), error=str(e))
        except Exception as e:
            traceback.print_exc()
            _update(job_id, state='failed', finished_at=_now(), error=str(e) or type(e).__name__)
        else:
            # Trends without a scraper return None; the app normally stops them before they're queued
            if result is None:
                _update(job_id, state='failed', finished_at=_now(), error='Not implemented yet')
            else:
                _update(job_id, state='done', finished_at=_now(), count=len(result))
        _log_run(job_id, log_fields)
