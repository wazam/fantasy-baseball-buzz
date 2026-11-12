from util_beautifulsoup import ratelimit_post_url, parse_number
from db import save_and_import, clear_stale_values
from sources import SOURCES, FANTRAX_LEAGUE_ID, SEASON

fantrax_config = next(source for source in SOURCES if source['source'].lower() == 'fantrax')
trend_keys = [trend['key'] for trend in fantrax_config['trends']]

# Trends fantrax_get can scrape, which the app shows as runnable
SUPPORTED_TRENDS = set(trend_keys)

# fantrax.com loads its player tables from this JSON endpoint. It needs a league ID (FPts follow that
# league's scoring) but no login; roster and active percentages are across all Fantrax leagues
API_URL = 'https://www.fantrax.com/fxpa/req'
PAGE_SIZE = 500
SORT_BY_ROSTERED = 'OVERVIEW_PERCENT_OWNED_2'

# Table header keys mapped to the labels they fill
COLUMNS = {
    'rankOv': 'Fantrax Rank Pts',
    'fpts': 'Fantrax Pts Season',
    'fptsPerGame': 'Fantrax Pts/G',
    'OVERVIEW_PERCENT_DRAFTED': 'Fantrax Draft %',
    'OVERVIEW_AVG_DRAFT_POSITION': 'Fantrax ADP',
    'OVERVIEW_PERCENT_OWNED_2': 'Fantrax Roster %',
    'OVERVIEW_PLUS_MINUS_PERCENT_OWNED_2': 'Fantrax Roster % Chg 7D',
    'OVERVIEW_PERCENT_ACTIVE_2': 'Fantrax Active %',
    'OVERVIEW_PLUS_MINUS_PERCENT_ACTIVE_2': 'Fantrax Active % Chg 7D',
}
# Each row also carries last week's roster and active percentages, in two cells after the header columns
LAST_WEEK_LABELS = ['Fantrax Roster % 7D Ago', 'Fantrax Active % 7D Ago']


def fantrax_get(trend_type):
    """Return a list of player trends by trend type, and save them to a trend-specific JSON file."""

    if trend_type not in trend_keys:
        raise ValueError(f"Invalid trend_type '{trend_type}'. Choose from: {trend_keys}")
    if not FANTRAX_LEAGUE_ID:
        raise ValueError("FANTRAX_LEAGUE_ID is not set; Fantrax only serves player stats for a league")

    return fantrax_players(trend_type)


def fetch_player_page(page_number):
    """Return one page of the league's player table, most rostered players first."""
    body = {'msgs': [{'method': 'getPlayerStats', 'data': {
        'leagueId': FANTRAX_LEAGUE_ID,
        'statusOrTeamFilter': 'ALL',
        'view': 'OVERVIEW',
        'positionOrGroup': 'ALL',
        'miscDisplayType': '1',
        'sortType': SORT_BY_ROSTERED,
        'pageNumber': str(page_number),
        'maxResultsPerPage': str(PAGE_SIZE),
    }}]}
    response = ratelimit_post_url(API_URL, json=body, params={"leagueId": FANTRAX_LEAGUE_ID})
    response.raise_for_status()
    result = response.json()
    if 'pageError' in result:
        raise RuntimeError(f"Fantrax error: {result['pageError'].get('code')} {result['pageError'].get('text', '')}".strip())
    return result['responses'][0]['data']


def player_entry(row, label_indexes, header_count):
    """Return one player's trend values, keyed by their labels."""
    scorer = row['scorer']
    cells = [cell.get('content', '') for cell in row['cells']]
    team = scorer.get('teamShortName', '')
    # Players traded this season show every team, like 'BAL/DET/ATL', ending with the current one.
    # Free agents show '(N/A)', on its own or ending a chain ('BAL/(N/A)'), and its '/' isn't a separator
    if team.endswith('(N/A)'):
        team = '(N/A)'
    elif '/' in team:
        team = team.split('/')[-1]
    entry = {
        "Player": scorer['name'],
        "Position": ', '.join(scorer.get('posShortNames', '').split(',')),
        "Team": team,
        "Id_Fantrax": scorer['scorerId'],
    }
    for index, label in label_indexes.items():
        entry[label] = parse_number(cells[index])
    if len(cells) == header_count + len(LAST_WEEK_LABELS):
        for label, content in zip(LAST_WEEK_LABELS, cells[header_count:]):
            entry[label] = parse_number(content)
    return entry


def fetch_rostered_players():
    """Return every player rostered in at least 1% of Fantrax leagues, most rostered first."""
    players = []
    page_number = 1
    while True:
        data = fetch_player_page(page_number)

        # A league ID belongs to one season and Fantrax only serves that league's seasons, so an old
        # league would import last year's stats under this year's labels
        season = data['displayedSeasonOrProjection']['name']
        if not season.startswith(str(SEASON)):
            raise RuntimeError(f"FANTRAX_LEAGUE_ID {FANTRAX_LEAGUE_ID} shows '{season}', not the {SEASON} season; set it to a {SEASON} Fantrax league")

        headers = data['tableHeader']['cells']
        label_indexes = {i: COLUMNS[key] for i, cell in enumerate(headers) if (key := cell.get('key') or cell.get('sortKey')) in COLUMNS}
        missing = set(COLUMNS.values()) - set(label_indexes.values())
        if missing:
            raise RuntimeError(f"Fantrax player table is missing columns for {sorted(missing)}")

        rows = [player_entry(row, label_indexes, len(headers)) for row in data['statsTable']]
        # Percentages are whole numbers, so 0% is everyone below 0.5% and ends the list
        rostered = [row for row in rows if isinstance(row['Fantrax Roster %'], int) and row['Fantrax Roster %'] > 0]
        players += rostered
        print(f"Fetched {len(players)} rostered players...")

        if len(rostered) < len(rows) or page_number >= data['paginatedResultSet']['totalNumPages']:
            return players
        page_number += 1


def fantrax_players(trend_type):
    """Process the league's Fantrax player table and return a list of player trends."""
    trends_list = fetch_rostered_players()
    if not trends_list:
        raise RuntimeError("Fantrax returned no rostered players")

    save_and_import(trends_list, 'fantrax', trend_type)
    # Players who drop below 1% rostered (or off a new season's list) would otherwise keep old values
    clear_stale_values(list(COLUMNS.values()) + LAST_WEEK_LABELS, 'Id_Fantrax', {entry['Id_Fantrax'] for entry in trends_list}, 'Fantrax')
    return trends_list


# Tests with `docker exec buzz ./.venv/bin/python src/source_fantrax.py` (imports the results into the database)
if __name__ == '__main__':
    print('\n', 'fantrax_get(players)', '\n', fantrax_get('players'))
