from util_beautifulsoup import ratelimit_get_url
from db import save_and_import
from sources import SOURCES, SEASON

mlb_config = next(source for source in SOURCES if source['source'].lower() == 'mlb')
trend_keys = [trend['key'] for trend in mlb_config['trends']]

# Trends mlb_get can scrape, which the app shows as runnable
SUPPORTED_TRENDS = {'players'}

# mlb.com's player pages are built from MLB's public Stats API, which needs no login. sportId 1 is the
# major leagues. A season's player list holds its major leaguers, 40-man roster players who haven't debuted
# included, and fills before the season starts (1,099 players for 2027 in November 2026)
API_URL = 'https://statsapi.mlb.com/api/v1'


def mlb_get(trend_type):
    """Return a list of player trends by trend type, and save them to a trend-specific JSON file."""

    if trend_type not in trend_keys:
        raise ValueError(f"Invalid trend_type '{trend_type}'. Choose from: {trend_keys}")
    if trend_type not in SUPPORTED_TRENDS:
        return None

    return mlb_players(trend_type)


def fetch(path, params):
    response = ratelimit_get_url(f'{API_URL}/{path}', params=params)
    response.raise_for_status()
    return response.json()


def player_entry(player, teams):
    """Return one player's 'players' trend values, keyed by their labels."""
    return {
        "Player": player['fullName'],
        # 'P' for every pitcher, and 'TWP' for a two-way player
        "Position": player.get('primaryPosition', {}).get('abbreviation', ''),
        "Team": teams.get((player.get('currentTeam') or {}).get('id'), ''),
        "Id_MLB": str(player['id']),
        "MLB Age": player.get('currentAge'),
        "MLB Bats": (player.get('batSide') or {}).get('code'),
        "MLB Throws": (player.get('pitchHand') or {}).get('code'),
        "MLB Debut": player.get('mlbDebutDate'),
    }


def mlb_players(trend_type):
    """Import SEASON's major leaguers with MLB's player ID, so each source's row for a major leaguer carries
    it. A name shared with a minor leaguer then shows which row is the major leaguer."""
    teams = {team['id']: team['abbreviation'] for team in fetch('teams', {'sportId': 1, 'season': SEASON})['teams']}
    players = fetch('sports/1/players', {'season': SEASON})['people']
    trends_list = [player_entry(player, teams) for player in players]
    if not trends_list:
        raise RuntimeError(f"MLB returned no players for the {SEASON} season")

    save_and_import(trends_list, 'mlb', trend_type)
    return trends_list


# Tests with `docker exec buzz ./.venv/bin/python src/source_mlb.py` (imports the results into the database)
if __name__ == '__main__':
    print('\n', 'mlb_get(players)', '\n', mlb_get('players'))
