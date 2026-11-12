import os
import json
import threading
from db import DATA_FOLDER, SOURCE_NAMES, as_id

# The Favorites and Compare lists from the Players page, saved in the data folder so they survive
# restarts. Each player is saved by a source ID such as 'MLB:671277' rather than a row number, since
# row numbers change when buzz.db is rebuilt; a row is on a list when any of its source IDs is
LISTS_FILE = os.path.join(DATA_FOLDER, 'player-lists.json')
LISTS = ('favorite', 'compare')
# The players table columns that show each list, in the same order
COLUMNS = ('Favorite', 'Compare')
# The ID a player is saved under: MLB's when the row has one, since it never changes, then ESPN's, then any other
KEY_SOURCES = ['MLB', 'ESPN'] + [name for name in SOURCE_NAMES.values() if name not in ('MLB', 'ESPN')]
_lock = threading.Lock()


def _read():
    try:
        with open(LISTS_FILE, encoding='utf-8') as file:
            saved = json.load(file)
    except FileNotFoundError:
        saved = {}
    except (OSError, ValueError) as e:
        print(f"Could not read player lists: {e}")
        saved = {}
    return {name: list(saved.get(name, [])) for name in LISTS}


def _write(lists):
    os.makedirs(os.path.dirname(LISTS_FILE), exist_ok=True)
    # Write to a temp file and swap it in, so a crash mid-write can't leave half a file
    temp = LISTS_FILE + '.tmp'
    with open(temp, 'w', encoding='utf-8') as file:
        json.dump(lists, file, indent=2)
    os.replace(temp, LISTS_FILE)


def row_keys(row):
    """Return a row's source IDs as list keys, most stable first, e.g. ['MLB:671277', 'ESPN:40459']."""
    return [f"{name}:{as_id(row[f'Id_{name}'])}" for name in KEY_SOURCES if as_id(row.get(f'Id_{name}'))]


def read_all():
    """Return each list as a set of keys, to check many rows at once with on_list."""
    return {name: set(keys) for name, keys in _read().items()}


def on_list(keys, saved_keys):
    return any(key in saved_keys for key in keys)


def set_player(list_name, row, on):
    """Add a row to a list or take it off. Returns False if the row has no source ID to save it by."""
    keys = row_keys(row)
    if not keys:
        return False
    with _lock:
        lists = _read()
        saved = [key for key in lists[list_name] if key not in keys]
        if on:
            saved.append(keys[0])
        lists[list_name] = saved
        _write(lists)
    return True


def clear(list_name):
    """Empty a list, such as Compare at the start of a new week."""
    with _lock:
        lists = _read()
        lists[list_name] = []
        _write(lists)
