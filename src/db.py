import sqlite3
import json
import re
import os
import sys
import tempfile
import threading
from datetime import datetime
from unidecode import unidecode
from os import path

from sources import SOURCES, NUMERIC_LABELS, PLACEHOLDER_VALUES


# ESPN is the authoritative source: only its imports may change player names, teams and positions
PRIMARY_SOURCE = 'ESPN'

DATA_FOLDER = '/usr/src/data/'
# Every scrape's results are saved here as '<local timestamp>_<source>-<trend>.json' before import
RESULTS_FOLDER = os.path.join(DATA_FOLDER, 'results/')
DB_FILE = os.path.join(DATA_FOLDER, 'buzz.db')

# Sources with an Id_<source> column, keyed by how they appear in results filenames
SOURCE_NAMES = {
    "espn": "ESPN",
    "yahoo": "Yahoo",
    "cbs": "CBS",
    "fantrax": "Fantrax",
    "nfbc": "NFBC",
    "rotoballer": "RotoBaller",
    "fantasypros": "FantasyPros",
    "rtsports": "RTSports",
    "fangraphs": "FanGraphs",
    "rotowire": "RotoWire",
    "baseballreference": "BaseballReference",
    "razzball": "Razzball",
    "mlb": "MLB"
}

# Player fields before the source columns. Only the primary source may change them. The Favorites and
# Compare lists live in data/player-lists.json (player_lists.py), so they survive a rebuild of this table
BASE_COLUMNS = {
    "Player": "TEXT",
    "Team": "TEXT",
    "Position": "TEXT",
    "Type": "TEXT",
    "Roster": "TEXT",
    "Injury": "TEXT",
}
SENSITIVE_FIELDS = set(BASE_COLUMNS)

NAME_SUFFIXES = [' Jr.', ' Sr.', ' II', ' III', ' IV']

TEAM_ALIASES = {
    "ARI": ["DIAMONDBACKS", "ARIZONA DIAMONDBACKS", "ARZ", "AZ"],
    "ATH": ["ATHLETICS", "SACRAMENTO ATHLETICS", "OAK"],
    "ATL": ["BRAVES", "ATLANTA BRAVES"],
    "BAL": ["ORIOLES", "BALTIMORE ORIOLES"],
    "BOS": ["RED SOX", "BOSTON RED SOX"],
    "CHC": ["CUBS", "CHICAGO CUBS", "CHN"],
    "CIN": ["REDS", "CINCINNATI REDS"],
    "CLE": ["GUARDIANS", "CLEVELAND GUARDIANS"],
    "COL": ["ROCKIES", "COLORADO ROCKIES"],
    "CWS": ["WHITE SOX", "CHICAGO WHITE SOX", "CHA", "CHW"],
    "DET": ["TIGERS", "DETROIT TIGERS"],
    "HOU": ["ASTROS", "HOUSTON ASTROS"],
    "KC": ["ROYALS", "KANSAS CITY ROYALS", "KCA", "KCR"],
    "LAA": ["ANGELS", "LOS ANGELES ANGELS", "ANA"],
    "LAD": ["DODGERS", "LOS ANGELES DODGERS", "LAN"],
    "MIA": ["MARLINS", "MIAMI MARLINS"],
    "MIL": ["BREWERS", "MILWAUKEE BREWERS", "MLW"],
    "MIN": ["TWINS", "MINNESOTA TWINS"],
    "NYM": ["METS", "NEW YORK METS", "NYN"],
    "NYY": ["YANKEES", "NEW YORK YANKEES", "NYA"],
    "PHI": ["PHILLIES", "PHILADELPHIA PHILLIES"],
    "PIT": ["PIRATES", "PITTSBURGH PIRATES"],
    "SD": ["PADRES", "SAN DIEGO PADRES", "SDN", "SDP"],
    "SEA": ["MARINERS", "SEATTLE MARINERS"],
    "SF": ["GIANTS", "SAN FRANCISCO GIANTS", "SFN", "SFG"],
    "STL": ["CARDINALS", "ST. LOUIS CARDINALS", "SLN"],
    "TB": ["RAYS", "TAMPA BAY RAYS", "TBA", "TBR"],
    "TEX": ["RANGERS", "TEXAS RANGERS"],
    "TOR": ["BLUE JAYS", "TORONTO BLUE JAYS"],
    "WSH": ["NATIONALS", "WASHINGTON NATIONALS", "WAS"],
    "(N/A)": ["FREE AGENT", "(NOT ON TEAM)", "INACTIVE", "MINOR LEAGUES", "MILB", "FA"]
}

# Each standard abbreviation maps to itself too, so 'MIN' from CBS or Fantrax becomes ESPN's 'Min'
TEAM_NAME_MAP = {
    **{std: std for std in TEAM_ALIASES},
    **{alias.upper(): std for std, aliases in TEAM_ALIASES.items() for alias in aliases},
}

# Teams are shown in ESPN's style, e.g. 'ChW' and 'FA'; teams not listed keep their standard abbreviation
ESPN_TEAM_DISPLAY = {
    "ARI": "Ari",
    "ATH": "Ath",
    "ATL": "Atl",
    "BAL": "Bal",
    "BOS": "Bos",
    "CHC": "ChC",
    "CWS": "ChW",
    "CIN": "Cin",
    "CLE": "Cle",
    "COL": "Col",
    "DET": "Det",
    "HOU": "Hou",
    "MIA": "Mia",
    "MIL": "Mil",
    "MIN": "Min",
    "PHI": "Phi",
    "PIT": "Pit",
    "SEA": "Sea",
    "STL": "StL",
    "TEX": "Tex",
    "TOR": "Tor",
    "WSH": "Wsh",
    "(N/A)": "FA"
}


def standardize_team_name(name):
    """Return ESPN's display name for a team name, after mapping it through the default aliases."""
    if not name:
        return ""  # sources sometimes send no team (null) at all

    canonical = TEAM_NAME_MAP.get(name.upper())
    if not canonical:
        return name  # fallback if no match found

    return ESPN_TEAM_DISPLAY.get(canonical, canonical)


def name_keys(name):
    """Return the keys a player's name matches on. Accents, case, periods, apostrophes, hyphens and suffixes
    such as 'Jr.' don't count, so 'C.J. Abrams' and 'CJ Abrams' share a key, as do 'Elian Peña' and
    'Elian Pena'. A hyphenated first name also matches its initials: 'Jean-Carlos Mejia' and 'J.C. Mejia'."""
    plain = unidecode(name or "").strip().lower()
    for suffix in NAME_SUFFIXES:
        written = next((form for form in (suffix.lower(), suffix.lower().rstrip('.')) if plain.endswith(form)), None)
        if written:
            plain = plain[:-len(written)].strip()
            break

    def key(text):
        return ' '.join(re.sub(r"[.']", "", text).replace('-', ' ').split())

    keys = {key(plain)}
    first_name, _, rest = plain.partition(' ')
    if '-' in first_name and rest:
        keys.add(key(''.join(part[0] for part in first_name.split('-') if part) + ' ' + rest))
    keys.discard('')  # a missing name matches nothing
    return keys


def name_index(conn):
    """Return {name key: set of row Ids} for the whole table, so name lookups don't scan it."""
    index = {}
    for row_id, player in conn.execute("SELECT Id, Player FROM players"):
        for key in name_keys(player):
            index.setdefault(key, set()).add(row_id)
    return index


def standardize_position_type(position):
    """Return 'P' when the first position is a pitching one, else 'Bat'."""
    if not position:
        return ""

    pitching_keywords = {"SP", "RP", "P"}

    # Split positions by common delimiters (comma, space, slash, hyphen)
    position_parts = re.split(r'[,\s/\-]', position.upper())

    # Use only the first position to determine classification
    first_position = position_parts[0] if position_parts else ""

    if first_position in pitching_keywords:
        return "P"

    return "Bat"  # Default to "Bat" if the first position is not a pitcher


def extract_source_from_filename(file_path):
    """Extract the source name from the filename using predefined mappings."""
    filename = path.basename(file_path).replace(".json", "").lower()

    # Results files are named '<timestamp>_<source>-<trend>.json'
    for key, name in SOURCE_NAMES.items():
        if re.search(fr"(^|_){key}($|[_\-])", filename):
            return name

    return filename  # Default to filename without extension if no match


def quote(name):
    """Quote a column name for SQL, since labels have spaces and symbols ('CBS Roster % Chg 7D')."""
    return '"' + name.replace('"', '""') + '"'


def schema_columns():
    """Return every column the players table should have, in display order, with its SQL type."""
    columns = dict(BASE_COLUMNS)
    for source in SOURCES:
        for trend in source['trends']:
            for label in trend['labels']:
                # NUMERIC stores '90' from an older scrape as the number 90, so the column still sorts
                columns.setdefault(label, "NUMERIC" if label in NUMERIC_LABELS else "TEXT")
    for name in SOURCE_NAMES.values():
        columns[f"Id_{name}"] = "TEXT"
    return columns


def check_data_folder():
    """Stop the app with the fix if the data folder can't be written, e.g. a root-owned ./data that Docker
    created. Otherwise the app looks healthy and fails on its first scrape or Players page load."""
    folder = DATA_FOLDER
    try:
        for folder in (DATA_FOLDER, RESULTS_FOLDER):
            os.makedirs(folder, exist_ok=True)
            with tempfile.TemporaryFile(dir=folder):
                pass
    except OSError as error:
        uid, gid = os.getuid(), os.getgid()
        print(f"Buzz can't write to {folder} ({error.strerror}). It runs as {uid}:{gid}, so on the host, give the\n"
              f"data folder next to compose.yaml to that user: sudo chown -R {uid}:{gid} data\n"
              "Or, if the folder belongs to another user, set user: in compose.yaml to the owner shown by: ls -nd data",
              file=sys.stderr, flush=True)
        # An exception, not sys.exit: Gunicorn respawns a worker that exits, but stops on a worker that fails to boot
        raise RuntimeError(f"{folder} is not writable") from None


def table_columns(conn):
    return [row[1] for row in conn.execute("PRAGMA table_info(players)")]


def ensure_schema(conn):
    """Create the players table, and add a column for each label added to the config since."""
    # WAL lets the players table load while a scrape is writing
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE IF NOT EXISTS players (Id INTEGER PRIMARY KEY, "
                 + ", ".join(f"{quote(column)} {sql_type}" for column, sql_type in BASE_COLUMNS.items()) + ")")
    existing = table_columns(conn)
    for column, sql_type in schema_columns().items():
        if column not in existing:
            conn.execute(f"ALTER TABLE players ADD COLUMN {quote(column)} {sql_type}")
    for column in ["Player"] + [f"Id_{name}" for name in SOURCE_NAMES.values()]:
        conn.execute(f"CREATE INDEX IF NOT EXISTS {quote('idx_' + column)} ON players ({quote(column)})")
    conn.commit()


_schema_lock = threading.Lock()
_schema_ready = False


def connect():
    """Open the database, bringing its schema up to date on first use."""
    global _schema_ready
    os.makedirs(DATA_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=30)
    conn.row_factory = sqlite3.Row
    with _schema_lock:
        if not _schema_ready:
            ensure_schema(conn)
            _schema_ready = True
    return conn


def as_id(value):
    """Return a source ID as text, or None when empty, since source IDs are stored and compared as text."""
    return None if value in (None, "") else str(value)


def search_players(conn, where, params=()):
    """Return the players matching a SQL condition, as dicts."""
    return [dict(row) for row in conn.execute(f"SELECT * FROM players WHERE {where}", params)]


def position_set(position):
    """Return a position string's positions, e.g. 'SS, DH, 2B' as {'SS', 'DH', '2B'}."""
    return {part for part in re.split(r'[,\s/\-]+', (position or "").upper()) if part}


def match_score(record, team, position_type, positions):
    """Score a row that matches a player's name, or return None if it can't be the same player: both its
    team and whether it bats or pitches differ, like a batter and a pitcher who share a name.
    One of the two may differ: teams go stale between scrapes, and a two-way player has both types."""
    team_differs = bool(team and record["Team"] and record["Team"] != team)
    type_differs = bool(position_type and record["Type"] and record["Type"] != position_type)
    if team_differs and type_differs:
        return None
    # ESPN keeps its rows' teams and positions current, so its row wins a tie on everything else
    return sum([
        2 * bool(team and record["Team"] == team),
        2 * bool(position_type and record["Type"] == position_type),
        bool(positions & position_set(record["Position"])),
        bool(as_id(record.get(f"Id_{PRIMARY_SOURCE}"))),
    ])


def best_match(candidates, entry):
    """Return the row that best matches the player's team and position, or None unless one row scores
    higher than every other."""
    team = standardize_team_name(entry.get("Team", ""))
    position = entry.get("Position", "")
    scored = sorted(((score, record) for record in candidates if (score := match_score(
        record, team, standardize_position_type(position), position_set(position))) is not None),
        key=lambda pair: pair[0], reverse=True)
    if len(scored) == 1 or (scored and scored[0][0] > scored[1][0]):
        return scored[0][1]
    if scored:
        print(f"{len(scored)} rows match {entry.get('Player')} equally well, so it gets its own row.")
    return None


def search_record(conn, entry, source, index=None):
    """Return the player's row: the one holding the source's ID, else the best name match (see best_match),
    or None to create a new row. index is name_index(conn), built here if not given."""
    id_field = f"Id_{source}"
    source_id = as_id(entry.get(id_field))
    has_id_column = id_field in table_columns(conn)

    if source_id and has_id_column:
        results = search_players(conn, f"{quote(id_field)} = ?", (source_id,))
        if results:
            return results[0]

    if index is None:
        index = name_index(conn)
    row_ids = sorted(set().union(*(index.get(key, set()) for key in name_keys(entry.get("Player")))))
    if not row_ids:
        return None

    # A record already carrying a different ID from this source is a namesake, e.g. a minor leaguer
    # sharing a star's name, so name matches never return it
    candidates = [record for record in search_players(conn, f"Id IN ({', '.join('?' * len(row_ids))})", row_ids)
                  if not source_id or not has_id_column or as_id(record.get(id_field)) in (None, source_id)]
    return best_match(candidates, entry)


def known_fields(columns, record, warned):
    """Drop fields with no column, warning once per field, so one odd key can't fail a whole import."""
    for key in record:
        if key not in columns and key not in warned:
            warned.add(key)
            print(f"Skipping '{key}': no such column. Add it to a trend's labels in sources.py.")
    return {key: value for key, value in record.items() if key in columns}


def create_records(conn, records):
    """Create new records, adding 'Type' based on 'Position' if available."""
    for record in records:
        if record.get("Position"):
            record["Type"] = standardize_position_type(record["Position"])  # Add 'Type' based on position

    columns, warned = set(table_columns(conn)), set()
    for record in records:
        fields = known_fields(columns, record, warned)
        names = ", ".join(quote(key) for key in fields)
        conn.execute(f"INSERT INTO players ({names}) VALUES ({', '.join('?' * len(fields))})", list(fields.values()))

    print(f"Created {len(records)} new records.")
    return True


def update_records(conn, records, source):
    """Batch update records, protecting sensitive fields unless the update comes from ESPN, the authoritative
    source."""
    filtered_records = [
        record if source.upper() == PRIMARY_SOURCE
        else {k: v for k, v in record.items() if k not in SENSITIVE_FIELDS}
        for record in records
    ]

    # ESPN can change a player's Position (new eligibility, a reclassified pitcher), so Type follows it
    # as it does on create; other sources never send Position, since it's a protected field
    for record in filtered_records:
        if record.get("Position"):
            record["Type"] = standardize_position_type(record["Position"])

    columns, warned = set(table_columns(conn)) - {"Id"}, set()
    for record in filtered_records:
        fields = known_fields(columns, {k: v for k, v in record.items() if k != "Id"}, warned)
        if fields:
            assignments = ", ".join(f"{quote(key)} = ?" for key in fields)
            conn.execute(f"UPDATE players SET {assignments} WHERE Id = ?", [*fields.values(), record["Id"]])

    print(f"Updated {len(filtered_records)} records.")
    return True


def save_and_import(trends_list, source, trend_type):
    """Save a scrape's results to RESULTS_FOLDER, import them into the database, and return the file's path."""
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    # A trend key with a '/' would otherwise point into a subfolder
    file_path = f"{RESULTS_FOLDER}{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{source}-{trend_type.replace('/', '-')}.json"
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(trends_list, json_file, indent=4)

    print(f"Processing complete. Saved results to {file_path}")
    process_json_file(file_path)
    return file_path


def clear_stale_values(labels, id_field, current_ids, source):
    """Blank labels on records whose id_field isn't in current_ids, e.g. CBS injuries that have healed."""
    current_ids = {as_id(value) for value in current_ids}
    with connect() as conn:
        rows = conn.execute(f"SELECT Id, {quote(id_field)} FROM players WHERE {quote(labels[0])} IS NOT NULL").fetchall()
        stale = [{"Id": row[0], **{label: None for label in labels}} for row in rows if as_id(row[1]) not in current_ids]
        if stale:
            print(f"Clearing {len(stale)} records no longer listed.")
            update_records(conn, stale, source)
    conn.close()


def clear_placeholders(entry):
    """Blank a source's "no number" values, such as ESPN's ADP of 260 for undrafted players. Done on import
    rather than in the scrapers, so replaying older results files clears them too."""
    for label, placeholders in PLACEHOLDER_VALUES.items():
        if isinstance(entry.get(label), (int, float)) and entry[label] in placeholders:
            entry[label] = None


def process_json_file(file_path):
    """Process a JSON file and update/create records in the database, all in one transaction."""
    filename_as_source = extract_source_from_filename(file_path)
    print(f"Processing file from source: {filename_as_source}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    update_list, create_list = [], []
    claimed_ids, seen_source_ids = set(), set()

    # The connection's context manager commits on success and rolls back if anything fails
    with connect() as conn:
        # Rows are only written after the loop, so one index serves the whole file
        index = name_index(conn)
        for entry in data:
            # A player listed twice in one scrape (older CBS results repeat players across pages) is
            # still one player, so only the first listing counts
            source_id = as_id(entry.get(f"Id_{filename_as_source}"))
            if source_id in seen_source_ids:
                continue
            if source_id:
                seen_source_ids.add(source_id)

            entry["Team"] = standardize_team_name(entry.get("Team", ""))
            entry["Position"] = entry.get("Position", "")
            clear_placeholders(entry)

            existing_record = search_record(conn, entry, filename_as_source, index)

            # Two entries matching one record means a name match also caught a namesake. Scrapers list the
            # most rostered players first, so the first keeps the record and the later one gets its own
            if existing_record and existing_record["Id"] in claimed_ids:
                existing_record = None

            if existing_record:
                claimed_ids.add(existing_record["Id"])
                print(f"Updating: {entry['Player']} ({entry['Team']}) ({entry['Position']})")
                update_list.append({"Id": existing_record["Id"], **entry})
            else:
                print(f"Creating new: {entry['Player']} ({entry['Team']}) ({entry['Position']})")
                create_list.append(entry)

        # Process batch updates & creations
        if update_list:
            update_records(conn, update_list, filename_as_source)
        if create_list:
            create_records(conn, create_list)
    conn.close()


# sqlite3 releases the GIL for every row it fetches, so threads reading the whole table at once keep
# waiting on each other for the GIL: six together took about a minute each instead of 0.15s. One at a time is quicker
_read_lock = threading.Lock()
_players_cache = {"state": None, "table": None}


def database_state():
    """Return the database file's and its WAL's modification times and sizes. Every write changes one of
    them, including writes from another process such as `db.py import`."""
    state = []
    for file in (DB_FILE, DB_FILE + '-wal'):
        try:
            stat = os.stat(file)
            state.append((stat.st_mtime_ns, stat.st_size))
        except FileNotFoundError:
            state.append(None)
    return tuple(state)


def read_players():
    """Return the players table for the browser: the columns holding any data, and each row as a list of
    their values. Lists instead of dicts keep 150 column names from repeating on every row. The result is
    reused until the database changes, so callers must not modify it."""
    with _read_lock:
        # Taken before reading, so a write during the read makes the next call read again
        state = database_state()
        if state != _players_cache["state"]:
            _players_cache.update(state=state, table=read_players_uncached())
        return _players_cache["table"]


def read_players_uncached():
    with connect() as conn:
        cursor = conn.execute("SELECT * FROM players ORDER BY Id")
        columns = [description[0] for description in cursor.description]
        rows = [tuple(row) for row in cursor]
    conn.close()
    filled = [i for i, column in enumerate(columns)
              if column == "Id" or any(row[i] not in (None, "") for row in rows)]
    return {
        "columns": [columns[i] for i in filled],
        "rows": [[row[i] for i in filled] for row in rows],
    }


def player_row(player_id):
    """Return one player's row as a dict, or None if there's no such player."""
    with connect() as conn:
        rows = search_players(conn, "Id = ?", (player_id,))
    conn.close()
    return rows[0] if rows else None


def same_name_groups(conn):
    """Return the rows whose names share a key (see name_keys), as lists of row dicts. These are the rows
    imports choose between by name, so they include true namesakes as well as one player split in two."""
    rows = [dict(row) for row in conn.execute("SELECT * FROM players ORDER BY Id")]
    group_of, first_row_with = {}, {}

    def root(row_id):
        while group_of.setdefault(row_id, row_id) != row_id:
            row_id = group_of[row_id]
        return row_id

    for row in rows:
        for key in name_keys(row["Player"]):
            if key in first_row_with:
                group_of[root(row["Id"])] = root(first_row_with[key])
            else:
                first_row_with[key] = row["Id"]

    groups = {}
    for row in rows:
        groups.setdefault(root(row["Id"]), []).append(row)
    return [group for group in groups.values() if len(group) > 1]


def source_ids(row):
    """Return the row's source IDs as {source: ID}, skipping sources it has none from."""
    return {name: row[f"Id_{name}"] for name in SOURCE_NAMES.values() if as_id(row.get(f"Id_{name}"))}


def describe_ids(row):
    """Return the row's source IDs for printing, e.g. 'ESPN 42402, Fantrax 04qk8'."""
    return ", ".join(f"{name} {value}" for name, value in source_ids(row).items()) or "no source IDs"


def print_duplicates():
    """Print every name on more than one row, with each row's Id, team, type and source IDs."""
    with connect() as conn:
        groups = same_name_groups(conn)
        total = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    conn.close()
    for group in sorted(groups, key=lambda rows: rows[0]["Player"].lower()):
        print(f"\n{group[0]['Player']} ({len(group)} rows)")
        for row in group:
            print(f"  {row['Id']:>5}  {row['Player']:<24} {row['Team'] or '':<5} {row['Position'] or '':<12} "
                  f"{row['Type'] or '':<4} {describe_ids(row)}")
    print(f"\n{len(groups)} names on {sum(len(group) for group in groups)} of {total} rows.")


def plan_merge(conn, keep_id, drop_id):
    """Return the fields to copy into the kept row and the dropped row, or raise ValueError if the rows
    can't be merged. Different IDs from one source prove they're different players."""
    if keep_id == drop_id:
        raise ValueError("Keep and drop are the same row.")
    rows = {row["Id"]: row for row in search_players(conn, "Id IN (?, ?)", (keep_id, drop_id))}
    missing = [str(row_id) for row_id in (keep_id, drop_id) if row_id not in rows]
    if missing:
        raise ValueError(f"No player with Id {' or '.join(missing)}.")
    keep, drop = rows[keep_id], rows[drop_id]

    kept_ids = source_ids(keep)
    conflicts = [f"{name} {kept_ids[name]} and {value}" for name, value in source_ids(drop).items()
                 if name in kept_ids and as_id(kept_ids[name]) != as_id(value)]
    if conflicts:
        raise ValueError(f"Not merging: the rows hold different IDs from {', '.join(conflicts)}, so they're different players.")

    copy = {column: value for column, value in drop.items()
            if column != "Id" and value not in (None, "") and keep[column] in (None, "")}
    return copy, drop


def merge_players(keep_id, drop_id, apply):
    """Copy the fields the kept row lacks from the dropped row, then delete the dropped row. Prints the
    plan and changes nothing unless apply is set. Exits with an error if the rows can't be merged."""
    with connect() as conn:
        try:
            copy, drop = plan_merge(conn, keep_id, drop_id)
        except ValueError as error:
            sys.exit(str(error))
        print(f"Keep {keep_id}, copying {len(copy)} fields from {drop_id}:")
        for column, value in copy.items():
            print(f"  {column}: {value}")
        print(f"Delete {drop_id}: {drop['Player']} ({drop['Team']}) ({drop['Position']}), {describe_ids(drop)}")
        if apply:
            update_records(conn, [{"Id": keep_id, **copy}], PRIMARY_SOURCE)
            conn.execute("DELETE FROM players WHERE Id = ?", (drop_id,))
            print("Merged.")
        else:
            print("Nothing changed. Add --yes to merge.")
    conn.close()


USAGE = """Commands, run with: docker exec buzz ./.venv/bin/python src/db.py <command>
  import [file.json ...]          Replay saved results into the database, oldest first, e.g. after
                                  starting over with an empty one. Every results file if none are listed.
  duplicates                      List every name on more than one row. Changes nothing.
  merge <keep Id> <drop Id>       Show what merging two rows would copy and delete.
  merge <keep Id> <drop Id> --yes Merge them.
With no command it runs a read-only lookup as a quick test."""


if __name__ == '__main__':
    command, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else (None, [])
    if command == 'import':
        files = args or sorted(
            os.path.join(RESULTS_FOLDER, name) for name in os.listdir(RESULTS_FOLDER) if name.endswith('.json'))
        for file_path in files:
            process_json_file(file_path)
        print(f"Imported {len(files)} results files.")
    elif command == 'duplicates' and not args:
        print_duplicates()
    elif command == 'merge':
        row_ids = [arg for arg in args if arg != '--yes']
        if len(row_ids) != 2 or not all(arg.isdigit() for arg in row_ids):
            sys.exit(USAGE)
        merge_players(int(row_ids[0]), int(row_ids[1]), apply='--yes' in args)
    elif command is None:
        with connect() as conn:
            print('\n', 'search_record()', '\n', search_record(conn, {"Player": "Shohei Ohtani", "Team": "LAD"}, PRIMARY_SOURCE))
    else:
        sys.exit(USAGE)
