import os
from flask import Flask, render_template, send_from_directory, abort, redirect, url_for, jsonify, request
from datetime import datetime, timezone

import trend_favorites
import player_lists
import jobs
import source_espn
import source_yahoo
import source_cbs
import source_fantrax
import source_nfbc
import source_mlb
import db
import reverse_proxy
import config
from sources import SOURCES, NUMERIC_LABELS
from db import RESULTS_FOLDER

SOURCE_HANDLERS = {
    'espn': source_espn.espn_get,
    'yahoo': source_yahoo.yahoo_get,
    'cbs': source_cbs.cbs_get,
    'fantrax': source_fantrax.fantrax_get,
    'nfbc': source_nfbc.nfbc_get,
    'mlb': source_mlb.mlb_get,
}

# Trends each source can scrape; the rest, and every trend of a source with no scraper yet, are listed as
# not yet supported and can't be run
SUPPORTED_TRENDS = {
    'espn': source_espn.SUPPORTED_TRENDS,
    'yahoo': source_yahoo.SUPPORTED_TRENDS,
    'cbs': source_cbs.SUPPORTED_TRENDS,
    'fantrax': source_fantrax.SUPPORTED_TRENDS,
    'nfbc': source_nfbc.SUPPORTED_TRENDS,
    'mlb': source_mlb.SUPPORTED_TRENDS,
}

# A setting the app can't use stops it here, before anything runs
config.check_settings()
db.check_data_folder()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
# Behind a reverse proxy, take the client IP and scheme from forwarded headers, but only from trusted addresses
app.wsgi_app = reverse_proxy.TrustedProxyFix(app.wsgi_app, config.trusted_networks())


@app.route('/')
def home():
    return render_template('pages/players.html')


def column_groups(filled):
    """Group the filled columns for the players table: player fields, then each source's labels, then IDs."""
    def column(field, title):
        return {'field': field, 'title': title, 'numeric': field in NUMERIC_LABELS}

    # The Favorite and Compare toggles lead, since frozen columns must sit at the table's edge
    base = list(player_lists.COLUMNS) + list(db.BASE_COLUMNS)
    groups = [{'source': None, 'columns': [column(c, c) for c in base if c in filled]}]
    for source in SOURCES:
        name = source['source']
        labels = dict.fromkeys(label for trend in source['trends'] for label in trend['labels'] if label in filled)
        # 'ESPN Roster %' reads 'Roster %' under the ESPN heading
        columns = [column(label, label.removeprefix(name + ' ')) for label in labels]
        if columns:
            groups.append({'source': name, 'columns': columns})
    ids = [column(c, c.removeprefix('Id_')) for c in filled if c.startswith('Id_')]
    if ids:
        groups.append({'source': 'IDs', 'columns': ids})
    return groups


@app.route('/players')
def players():
    table = db.read_players()
    columns = table['columns']
    id_columns = [(i, column.removeprefix('Id_')) for i, column in enumerate(columns) if column.startswith('Id_')]
    saved = player_lists.read_all()
    rows = []
    # Each row starts with a 1 or 0 per list, from its source IDs; the cached table itself isn't changed
    for row in table['rows']:
        keys = [f"{name}:{db.as_id(row[i])}" for i, name in id_columns if db.as_id(row[i])]
        rows.append([int(player_lists.on_list(keys, saved[name])) for name in player_lists.LISTS] + list(row))
    fields = list(player_lists.COLUMNS) + columns
    return jsonify(groups=column_groups(fields), fields=fields, rows=rows)


@app.route('/players/<int:player_id>/<list_name>', methods=['POST'])
def set_player_list(player_id, list_name):
    """Add a player to the Favorites or Compare list, or take them off; the body is {"on": true|false}."""
    if list_name not in player_lists.LISTS:
        abort(404)
    body = request.get_json(silent=True) or {}
    if not isinstance(body.get('on'), bool):
        return jsonify(error="Expected a JSON body like {\"on\": true}."), 400
    row = db.player_row(player_id)
    if row is None:
        abort(404)
    if not player_lists.set_player(list_name, row, body['on']):
        return jsonify(error="This player has no source ID to save them by."), 409
    return jsonify(on=body['on'])


@app.route('/players/compare/clear', methods=['POST'])
def clear_compare():
    """Empty the Compare list, to start a new week's comparison."""
    player_lists.clear('compare')
    return jsonify(cleared=True)


@app.route('/index')
def index():
    return render_template(
        'pages/index.html',
        sources=SOURCES,
        statuses=trend_status()
    )


@app.route('/<source>')
def source_page(source):
    """Redirect an old per-source page, such as /cbs, to its section of the Index page."""
    source_data = next(
        (s for s in SOURCES if s['source'].lower() == source.lower()), None
    )
    if not source_data:
        abort(404)

    return redirect(url_for('index', _anchor=source_data['source'].lower()))


def find_trend(source, func_id):
    """Return (job id, trend key, handler) for a trend number, or abort with 404 if there is none."""
    source_data = next((s for s in SOURCES if s['source'].lower() == source.lower()), None)
    # Trend numbers start at 1, so 0 must not wrap around to the last trend
    if not source_data or not 1 <= func_id <= len(source_data['trends']):
        abort(404)

    source_key = source_data['source'].lower()
    trend_type = source_data['trends'][func_id - 1]['key']
    return f"{source_key}/{func_id}", trend_type, SOURCE_HANDLERS.get(source_key)


def last_results_file(results, source_key, trend_key):
    """Return a run like the run log's, from the newest results file of a trend run before the log existed."""
    # Results files are named '<local timestamp>_<source>-<trend>.json', see db.save_and_import
    suffix = f"_{source_key}-{trend_key.replace('/', '-')}.json"
    newest = next((f for f in reversed(results) if f.endswith(suffix)), None)
    if not newest:
        return None
    finished_at = datetime.strptime(newest[:19], '%Y-%m-%d_%H-%M-%S').astimezone().isoformat()
    return {'state': 'done', 'finished_at': finished_at, 'count': None}


def trend_status():
    """Return every trend's live job state, whether it can run, whether it's a favorite, and its latest run and latest successful run."""
    current = jobs.status()
    saved_favorites = trend_favorites.read_all()
    latest, latest_success = {}, {}
    for run in jobs.read_run_log():
        key = (run.get('source'), run.get('trend'))
        latest[key] = run
        if run.get('state') == 'done':
            latest_success[key] = run
    results = sorted(os.listdir(RESULTS_FOLDER)) if os.path.isdir(RESULTS_FOLDER) else []

    statuses = {}
    for source in SOURCES:
        source_key = source['source'].lower()
        for number, trend in enumerate(source['trends'], start=1):
            job_id = f"{source_key}/{number}"
            key = (source_key, trend['key'])
            statuses[job_id] = {
                **current.get(job_id, {'state': 'idle'}),
                'supported': trend['key'] in SUPPORTED_TRENDS.get(source_key, set()),
                'favorite': trend_favorites.is_favorite(source_key, trend, saved_favorites),
                'last_run': latest.get(key),
                'last_success': latest_success.get(key) or last_results_file(results, source_key, trend['key']),
            }
    return statuses


@app.route('/<source>/<int:func_id>')
def show_source_func(source, func_id):
    """Report a trend's status only; scrapes start from a POST so links and prefetching can't run them."""
    job_id, _, _ = find_trend(source, func_id)
    return jsonify(trend_status()[job_id])


@app.route('/<source>/<int:func_id>/run', methods=['POST'])
def run_source_func(source, func_id):
    """Queue a scrape for the background worker and return at once."""
    job_id, trend_type, handler = find_trend(source, func_id)
    source_key = job_id.split('/')[0]
    if trend_type not in SUPPORTED_TRENDS.get(source_key, set()):
        return jsonify(state='failed', error=f"Trend '{trend_type}' for source '{source}' is not supported yet."), 501
    return jsonify(jobs.enqueue(job_id, handler, trend_type, log_fields={'source': source_key, 'trend': trend_type})), 202


@app.route('/<source>/<int:func_id>/favorite', methods=['POST'])
def favorite_source_func(source, func_id):
    """Make a trend a favorite or take it off; the body is {"favorite": true|false}."""
    job_id, _, _ = find_trend(source, func_id)
    source_key, number = job_id.split('/')
    trend = next(s for s in SOURCES if s['source'].lower() == source_key)['trends'][int(number) - 1]
    body = request.get_json(silent=True) or {}
    if not isinstance(body.get('favorite'), bool):
        return jsonify(error="Expected a JSON body like {\"favorite\": true}."), 400
    try:
        return jsonify(favorite=trend_favorites.set_favorite(source_key, trend, body['favorite']))
    except OSError as e:
        return jsonify(error=f"Could not save trend favorites: {e}"), 500


@app.route('/status')
def status():
    return jsonify(trend_status())


@app.route('/dashboard')
def dashboard_redirect():
    return redirect(url_for('home'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def get_file_version(filename):
    filepath = os.path.join(app.static_folder, filename)
    if os.path.exists(filepath):
        ts = os.path.getmtime(filepath)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime('%Y%m%d%H%M%S')
    else:
        return datetime.now(tz=timezone.utc).strftime('%Y%m%d%H%M%S')


@app.context_processor
def inject_version_cache():
    return {
        "version_cache": get_file_version("style-common.css"),
        "version_dark": get_file_version("style-dark.css"),
        "version_light": get_file_version("style-light.css"),
    }
