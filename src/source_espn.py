import json
from util_beautifulsoup import ratelimit_get_url
from db import save_and_import, clear_stale_values
from sources import SOURCES, SEASON

espn_config = next(source for source in SOURCES if source['source'].lower() == 'espn')
trend_keys = [trend['key'] for trend in espn_config['trends']]

# fantasy.espn.com loads its player tables from this JSON service, so no browser or login is needed.
# leaguedefaults/2 is ESPN's default points league, which is where the "ESPN Pts" values come from.
# ESPN doesn't document this service. These notes cover it, plus its news feed, for the planned ESPN trends:
#   https://github.com/pseudo-r/Public-ESPN-API
#   https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b
#   https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/news
API_URL = f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/{SEASON}'
PLAYERS_URL = f'{API_URL}/segments/0/leaguedefaults/2'
PAGE_SIZE = 500

# Stat split IDs for actual (not projected) stats
SPLIT_SEASON, SPLIT_7D, SPLIT_15D, SPLIT_30D = 0, 1, 2, 3

# ESPN position IDs, for a player's main position and the lineup slots they're eligible for
DEFAULT_POSITIONS = {1: 'SP', 2: 'C', 3: '1B', 4: '2B', 5: '3B', 6: 'SS', 7: 'LF', 8: 'CF', 9: 'RF', 10: 'DH', 11: 'RP'}
SLOT_POSITIONS = {0: 'C', 1: '1B', 2: '2B', 3: '3B', 4: 'SS', 5: 'OF', 11: 'DH', 14: 'SP', 15: 'RP'}

# Trends espn_get can scrape, which the app shows as runnable; the others return None (not implemented)
# until they are mapped from the same data
SUPPORTED_TRENDS = {'players'}


def espn_get(trend_type):
    """Return a list of player trends by trend type, and save them to a trend-specific JSON file."""

    if trend_type not in trend_keys:
        raise ValueError(f"Invalid trend_type '{trend_type}'. Choose from: {trend_keys}")
    if trend_type not in SUPPORTED_TRENDS:
        return None

    return espn_players(trend_type)


def espn_api_get(url, params, fantasy_filter=None):
    """Return the JSON from one ESPN API request, raising on any HTTP error."""
    extra_headers = {'X-Fantasy-Filter': json.dumps(fantasy_filter)} if fantasy_filter else None
    response = ratelimit_get_url(url, extra_headers=extra_headers, params=params)
    response.raise_for_status()
    return response.json()


def fetch_team_abbreviations():
    """Return ESPN's team abbreviations by team ID, e.g. {30: 'TB', 0: 'FA'}."""
    teams = espn_api_get(API_URL, {'view': 'proTeamSchedules_wl'})['settings']['proTeams']
    return {team['id']: team['abbrev'] for team in teams}


def fetch_owned_players():
    """Return every player rostered in at least some ESPN leagues, most rostered first."""
    players = []
    offset = 0
    while True:
        fantasy_filter = {'players': {
            'limit': PAGE_SIZE,
            'offset': offset,
            'sortPercOwned': {'sortPriority': 1, 'sortAsc': False},
            'filterStatsForSourceIds': {'value': [0]},
            'filterStatsForSplitTypeIds': {'value': [SPLIT_SEASON, SPLIT_7D, SPLIT_15D, SPLIT_30D]},
            'filterStatsForExternalIds': {'value': [SEASON]},
        }}
        page = espn_api_get(PLAYERS_URL, {'view': 'kona_player_info'}, fantasy_filter).get('players', [])
        owned = [item for item in page if (item['player'].get('ownership') or {}).get('percentOwned', 0) > 0]
        players += owned
        print(f"Fetched {len(players)} rostered players...")

        # Sorted by ownership, so the first unowned player (or a short page) ends the list
        if len(owned) < len(page) or len(page) < PAGE_SIZE:
            return players
        offset += PAGE_SIZE


def player_entry(item, teams):
    """Return one player's 'players' trend values, keyed by their labels."""
    player = item['player']
    ownership = player.get('ownership') or {}
    points = {
        stat['statSplitTypeId']: round(stat.get('appliedTotal', 0), 1)
        for stat in player.get('stats', [])
        if stat.get('statSourceId') == 0 and stat.get('seasonId') == SEASON
    }
    season_rating = (item.get('ratings') or {}).get('0') or {}
    position = DEFAULT_POSITIONS.get(player.get('defaultPositionId'), '')
    position_rank = season_rating.get('positionalRanking')
    roster_percent = round(ownership.get('percentOwned', 0), 2)
    roster_change = round(ownership.get('percentChange', 0), 2)

    return {
        "Player": player['fullName'],
        "Position": ', '.join(SLOT_POSITIONS[slot] for slot in player.get('eligibleSlots', []) if slot in SLOT_POSITIONS),
        "Team": teams.get(player.get('proTeamId'), ''),
        "Id_ESPN": str(player['id']),
        "ESPN Pts 7D": points.get(SPLIT_7D),
        "ESPN Pts 15D": points.get(SPLIT_15D),
        "ESPN Pts 30D": points.get(SPLIT_30D),
        "ESPN Pts Season": points.get(SPLIT_SEASON),
        # Shown like 'DH2', the player's season rank at their main position
        "ESPN Rank Pos": f"{position}{position_rank}" if position and position_rank else '',
        "ESPN ADP": round(ownership.get('averageDraftPosition', 0), 1),
        "ESPN Roster %": roster_percent,
        "ESPN Roster % Chg 7D": roster_change,
        "ESPN Roster % 7D Ago": round(roster_percent - roster_change, 2),
    }


def espn_players(trend_type):
    """Process ESPN's player data and return a list of player trends."""
    teams = fetch_team_abbreviations()
    trends_list = [player_entry(item, teams) for item in fetch_owned_players()]
    if not trends_list:
        raise RuntimeError("ESPN returned no rostered players")

    save_and_import(trends_list, 'espn', trend_type)
    # Players no longer rostered anywhere drop out of the list, and would otherwise keep their last values.
    # Team and Position stay as last seen
    labels = next(trend['labels'] for trend in espn_config['trends'] if trend['key'] == trend_type)
    clear_stale_values(labels, 'Id_ESPN', {entry['Id_ESPN'] for entry in trends_list}, 'ESPN')
    return trends_list


# Tests with `docker exec buzz ./.venv/bin/python src/source_espn.py` (imports the results into the database)
if __name__ == '__main__':
    print('\n', 'espn_get(players)', '\n', espn_get('players'))
