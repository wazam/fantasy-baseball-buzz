import os
import json
import threading
from db import DATA_FOLDER

# Favorite trends, saved in the data folder so they survive restarts and rebuilds. Only changes
# from the is_favorite defaults in sources.py are kept, keyed '<source>/<trend key>' so reordering
# trends there doesn't move a favorite to a different trend
FAVORITES_FILE = os.path.join(DATA_FOLDER, 'trend-favorites.json')
_lock = threading.Lock()


def _read():
    try:
        with open(FAVORITES_FILE, encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        print(f"Could not read trend favorites: {e}")
        return {}


def is_favorite(source_key, trend, saved=None):
    """Return whether a trend is a favorite: its saved choice, else its default in sources.py."""
    saved = _read() if saved is None else saved
    return saved.get(f"{source_key}/{trend['key']}", trend.get('is_favorite', False))


def read_all():
    """Return every saved choice, to pass to is_favorite when checking many trends at once."""
    return _read()


def set_favorite(source_key, trend, favorite):
    """Save whether a trend is a favorite, dropping the entry when it matches the default in sources.py."""
    key = f"{source_key}/{trend['key']}"
    with _lock:
        saved = _read()
        if favorite == trend.get('is_favorite', False):
            saved.pop(key, None)
        else:
            saved[key] = favorite
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        # Write to a temp file and swap it in, so a crash mid-write can't leave half a file
        temp = FAVORITES_FILE + '.tmp'
        with open(temp, 'w', encoding='utf-8') as file:
            json.dump(saved, file, indent=2, sort_keys=True)
        os.replace(temp, FAVORITES_FILE)
    return favorite
