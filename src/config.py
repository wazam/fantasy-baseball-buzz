"""Settings from environment variables, checked once at startup.

Run as a script, it checks every setting and then starts the command it is given, as in the Dockerfile's CMD:
    python src/config.py gunicorn ...
The check has to run before Gunicorn, which reads FORWARDED_ALLOW_IPS itself and stops on a bad value with a
line that doesn't name the variable. main.py runs the same check again when the server imports it.
"""
import ipaddress
import logging
import os
import re
import sys
import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Gunicorn's and uvicorn's own default: the IPv4 and IPv6 loopback
DEFAULT_ALLOW_IPS = '127.0.0.1,::1'

# Same line format as Gunicorn's own log, since these lines sit next to its startup lines
logger = logging.getLogger('buzz')
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s',
                                            datefmt='%Y-%m-%d %H:%M:%S %z'))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


class SettingError(ValueError):
    """One or more settings have a value the app can't use. problems holds one message per problem."""

    def __init__(self, *problems):
        super().__init__(' '.join(problems))
        self.problems = list(problems)


def setting(name):
    """The variable's value without surrounding spaces, or None when it's unset or empty, so an empty value
    means unset. Compose sends an empty value for a setting that .env doesn't set."""
    return os.environ.get(name, '').strip() or None


def fantrax_league_id():
    """The Fantrax league ID, or None when it's not set. Fantrax IDs are letters and digits."""
    value = setting('FANTRAX_LEAGUE_ID')
    if value is not None and not re.fullmatch(r'[A-Za-z0-9]+', value):
        raise SettingError("FANTRAX_LEAGUE_ID must be the letters and digits after /league/ in your Fantrax "
                           f"league URL, got '{value}'.")
    return value


def allow_entries():
    """FORWARDED_ALLOW_IPS as a list of entries, the default's when it's unset or holds nothing but commas."""
    value = setting('FORWARDED_ALLOW_IPS') or DEFAULT_ALLOW_IPS
    return [entry.strip() for entry in value.split(',') if entry.strip()] or DEFAULT_ALLOW_IPS.split(',')


def trusted_networks():
    """FORWARDED_ALLOW_IPS as a list of networks. None means '*', which trusts every address.
    Strict, like Gunicorn's own check of the same variable, so 192.0.2.1/24 (host bits set) fails in both."""
    entries = allow_entries()
    if '*' in entries:
        return None
    networks, problems = [], []
    for entry in entries:
        try:
            networks.append(ipaddress.ip_network(entry))
        except ValueError as error:
            problems.append("FORWARDED_ALLOW_IPS must be comma-separated IP addresses or CIDR ranges, or *, "
                            f"got '{entry}': {error}.")
    if problems:
        raise SettingError(*problems)
    return networks


def apply_time_zone():
    """Make TZ a zone the C library knows. An unknown TZ only changes displayed times and file names, so it
    warns and uses UTC instead of stopping the app; the C library would use UTC without saying so."""
    name = setting('TZ')
    if name is not None:
        try:
            ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError, OSError):
            logger.warning(f"TZ '{name}' isn't a known time zone. Using UTC.")
            name = None
    os.environ['TZ'] = name or 'UTC'
    time.tzset()


def check_settings():
    """Read every setting once at startup, so a bad value stops the app here, with one line per problem,
    instead of failing later or not at all."""
    apply_time_zone()
    problems = []
    for read in (fantrax_league_id, trusted_networks):
        try:
            read()
        except SettingError as error:
            problems.extend(error.problems)
    for problem in problems:
        logger.error(problem)
    if problems:
        sys.exit(1)
    # Gunicorn reads the same variable, so hand it the value without empty entries or spaces
    entries = allow_entries()
    os.environ['FORWARDED_ALLOW_IPS'] = '*' if '*' in entries else ','.join(entries)


if __name__ == '__main__':
    check_settings()
    if len(sys.argv) > 1:
        os.execvp(sys.argv[1], sys.argv[1:])
