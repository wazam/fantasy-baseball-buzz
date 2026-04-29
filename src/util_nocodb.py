import requests
import json
import re
import os
from unidecode import unidecode
import urllib.parse
from os import path


# NocoDB API Setup
BASE_URL = os.getenv('NOCODB_URL', 'http://localhost:8080')
TABLE_ID = os.getenv('NOCODB_TABLE_ID')
PRIMARY_SOURCE = os.getenv('PRIMARY_LEAGUE_SOURCE', 'ESPN').upper()

HEADERS = {
    "xc-token": os.getenv('NOCODB_API_TOKEN'),
    "Content-Type": "application/json"
}

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

TEAM_NAME_MAP = {
    alias.upper(): std for std, aliases in TEAM_ALIASES.items() for alias in aliases
}

SOURCE_DISPLAY_OVERRIDES = {
    "ESPN": {
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
    },
    "YAHOO": {
        "ARI": "AZ"
    },
    "CBS": {
        "CWS": "CHW",
        "WSH": "WAS"
    },
    "NFBC": {
        "ARI": "ARZ",
        "MIL": "MLW",
        "WSH": "WAS"
    },
    "FANTRAX": {}  # No changes
}


def standardize_team_name(name):
    """
    Standardizes a team name based on the default aliases and returns the
    source-specific display name for the PRIMARY_SOURCE.
    """
    canonical = TEAM_NAME_MAP.get(name.upper())
    if not canonical:
        return name  # fallback if no match found

    # Use display override if defined for this source
    return SOURCE_DISPLAY_OVERRIDES.get(PRIMARY_SOURCE, {}).get(canonical, canonical)


def standardize_player_name(name):
    """Generate multiple name variants to catch inconsistencies."""
    name_variants = set()
    
    standardized_name = unidecode(name).title().strip()
    name_variants.add(standardized_name)
    name_variants.add(standardized_name.replace('-', ' '))
    name_variants.add(standardized_name.replace('.', ''))

    suffixes = [' Jr.', ' Sr.', ' II', ' III', ' IV']
    for suffix in suffixes:
        name_variants.add(standardized_name + suffix)
        name_variants.add(standardized_name.replace(suffix, ''))

    # Initial-based format (e.g., J.C. Mejia (ESPN) vs Jean-Carlos Mejia (Yahoo!))
    name_parts = standardized_name.split('-')
    if len(name_parts) > 1:
        initials = ''.join([x[0] + "." for x in name_parts]) + " " + standardized_name.split()[-1]
        name_variants.add(initials)

    return list(name_variants)


def standardize_position_type(position):
    """standardize all batting/fielding positions to 'Bat' and all pitching positions to 'P'."""
    if not position:
        return ""

    batting_keywords = {"C", "1B", "2B", "SS", "3B", "OF", "LF", "RF", "CF", "DH", "U", "UT", "UTIL", "INF", "CI", "MI", "IF"}
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

    # Mapping known sources
    source_map = {
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

    for key in source_map:
        if re.match(fr"^{key}(\b|[_\-])?", filename):
            return source_map[key]

    return filename  # Default to filename without extension if no match


def search_nocodb(query):
    """Generic function to query NocoDB."""
    url = f"{BASE_URL}/api/v2/tables/{TABLE_ID}/records?where={query}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("list", [])
    return []


def search_record(entry, source):
    """Search for an existing record using various criteria, refining search until unique."""
    source_id = entry.get(f"Id_{source}")
    raw_name = entry.get("Player")
    team = entry.get("Team", "")
    position = entry.get("Position", "")

    name_variants = standardize_player_name(raw_name)
    standardized_team = standardize_team_name(team)
    position_type = standardize_position_type(position)

    # Step 1: Highest Priority - Search by ID
    if source_id:
        query = f"(Id_{source},eq,{source_id})"
        results = search_nocodb(query)
        if results:
            print("Unique match found via ID.")
            return results[0]

    # Step 2: Search by Name Variants & Standardized Position Type
    search_queries = []
    for variant in name_variants:
        encoded_name = urllib.parse.quote(variant)
        search_queries.append((
            f"(Player,eq,{encoded_name})~and(Team,eq,{standardized_team})~and(Type,eq,{position_type})", 
            "Player+Team+PositionType"
        ) if team and position else None)
        search_queries.append((
            f"(Player,eq,{encoded_name})~and(Type,eq,{position_type})", 
            "Player+PositionType"
        ) if position else None)
        search_queries.append((
            f"(Player,eq,{encoded_name})~and(Team,eq,{standardized_team})", 
            "Player+Team"
        ) if team else None)

    # Execute queries in priority order
    search_queries = [q for q in search_queries if q]  # Remove None values
    for query, desc in search_queries:
        results = search_nocodb(query)
        if results:
            if len(results) == 1:
                print(f"Unique match found via {desc}.")
                return results[0]
            print(f"Multiple matches found via {desc}. Refining...")

    # Step 3: Final Fallback - Search by Player Name Only
    for variant in name_variants:
        encoded_name = urllib.parse.quote(variant)
        query = f"(Player,eq,{encoded_name})"
        results = search_nocodb(query)
        if results:
            print(f"Player found via Player Only search. {len(results)} potential matches.")
            return results[0] if len(results) == 1 else None  # If multiple matches, return None

    return None  # No unique match found


def create_records(records):
    """Create new records in NocoDB, adding 'Type' based on 'Position' if available."""
    
    for record in records:
        if "Position" in record and record["Position"]:  # Ensure 'Position' key exists and is not empty
            record["Type"] = standardize_position_type(record["Position"])  # Add 'Type' based on position

    url = f"{BASE_URL}/api/v2/tables/{TABLE_ID}/records"
    response = requests.post(url, headers=HEADERS, json=records)
    
    if response.status_code == 200:
        print(f"Created {len(records)} new records.")
        return True
    else:
        print(f"Error creating records: {response.status_code} - {response.text}")
        return False


def update_records(records, source):
    """
    Batch update records, protecting sensitive fields unless
    the update is coming from the user's primary league source.
    """
    sensitive_fields = {
        "Player", "Team", "Position", "Type", "Roster", "Injury", "Watch"
    }

    primary_source = os.getenv("PRIMARY_LEAGUE_SOURCE", "ESPN").upper()

    filtered_records = [
        record if source.upper() == primary_source
        else {k: v for k, v in record.items() if k not in sensitive_fields}
        for record in records
    ]

    url = f"{BASE_URL}/api/v2/tables/{TABLE_ID}/records"
    response = requests.patch(url, headers=HEADERS, json=filtered_records)

    if response.status_code == 200:
        print(f"Updated {len(filtered_records)} records.")
        return True
    else:
        print(f"Error updating records: {response.status_code} - {response.text}")
        return False


def process_json_file(file_path):
    """Process a JSON file and update/create records in NocoDB."""
    filename_as_source = extract_source_from_filename(file_path)
    print(f"Processing file from source: {filename_as_source}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    update_list, create_list = [], []

    for entry in data:
        entry["Team"] = standardize_team_name(entry.get("Team", ""))
        entry["Position"] = entry.get("Position", "")

        existing_record = search_record(entry, filename_as_source)

        if existing_record:
            print(f"Updating: {entry['Player']} ({entry['Team']}) ({entry['Position']})")
            update_list.append({"Id": existing_record["Id"], **entry})
        else:
            print(f"Creating new: {entry['Player']} ({entry['Team']}) ({entry['Position']})")
            create_list.append(entry)

    # Process batch updates & creations
    if update_list:
        update_records(update_list, filename_as_source)
    if create_list:
        create_records(create_list)


# Tests with `pipenv run python src/util_nocdb.py`
if __name__ == '__main__':
    print('\n', 'process_json_file()', '\n', process_json_file("./data/testing.json"))
