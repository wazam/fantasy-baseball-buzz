import re
from datetime import datetime
from bs4 import BeautifulSoup
from util_beautifulsoup import ratelimit_get_url, ratelimit_post_url, parse_number
from db import save_and_import, clear_stale_values
from sources import SOURCES

nfbc_config = next(source for source in SOURCES if source['source'].lower() == 'nfbc')
trend_urls = {trend['key']: trend['url'] for trend in nfbc_config['trends']}
nfbc_trend_labels = {trend['key']: trend['labels'] for trend in nfbc_config['trends']}

# Trends nfbc_get can scrape, which the app shows as runnable
SUPPORTED_TRENDS = set(trend_urls)

# nfc.shgn.com serves all four trends without a login: the players page loads two JSON endpoints, the
# ADP and auction pages POST their filters to adp.data.php for table rows, and injuries is a plain table
SITE_URL = 'https://nfc.shgn.com'
PLAYERS_DATA_URL = f'{SITE_URL}/api/react/players_data'
PLAYERS_STATS_URL = f'{SITE_URL}/api/react/players_stats'
DRAFT_DATA_URL = f'{SITE_URL}/adp.data.php'

# Scoring style ID of the "NFBC - Points" table the players trend reads
POINTS_SCORING_ID = '15'
# draft_type values from the ADP page's filter: all non-auction drafts, and average auction values
DRAFT_TYPES = {'draft': '0', 'auction': '896'}
# adp.data.php columns are Rk, Player, Team, Position(s), ADP / AAV, Min, Max, Difference, # Picks;
# these are the ones the labels take, in label order
DRAFT_VALUE_COLUMNS = [0, 4, 5, 6, 8]
INJURY_LABELS = ['NFBC Inj Status', 'NFBC Inj Type', 'NFBC Inj Return', 'NFBC Inj Note']
PLAYER_LINK = re.compile(r'/player/baseball/(\d+)/')


def nfbc_get(trend_type):
    """Return a list of player trends by trend type, and save them to a trend-specific JSON file."""

    if trend_type not in trend_urls:
        raise ValueError(f"Invalid trend_type '{trend_type}'. Choose from: {list(trend_urls.keys())}")
    if trend_type == 'players':
        return nfbc_players(trend_type)
    if trend_type == 'injuries':
        return nfbc_injuries(trend_type)
    return nfbc_draft(trend_type)


def fetch_json(url, params):
    response = ratelimit_get_url(url, extra_headers={'Referer': trend_urls['players']}, params=params)
    response.raise_for_status()
    return response.json()


def split_total(value):
    """Return a points value as a number; two-way players come as 'hitting/pitching', which are summed."""
    if isinstance(value, str) and '/' in value:
        parts = [parse_number(part) for part in value.split('/')]
        return sum(parts) if all(isinstance(part, (int, float)) for part in parts) else value
    return parse_number(str(value)) if value is not None else None


def nfbc_players(trend_type):
    """Import NFBC's player pool with roster and active percentages and season points."""
    pool = fetch_json(PLAYERS_DATA_URL, {'claims': '0', 'sport': 'baseball'})
    # 'y' lists the stat years newest first
    stats = fetch_json(PLAYERS_STATS_URL, {'sport': 'baseball', 'stattype': 'season', 'typeval': pool['y'][0], 'ssid': POINTS_SCORING_ID})

    trends_list = []
    for player_id, player in pool['p'].items():
        player_stats = stats.get(player_id) or {}
        points = split_total(player_stats.get('pts'))
        per_game = player_stats.get('ppg')
        # Skip the pool's long tail: no one rosters them and they have no points
        if not player.get('o%') and not points:
            continue
        trends_list.append({
            "Player": f"{player['f']} {player['l']}",
            "Position": ', '.join(player.get('p', [])),
            "Team": player.get('t', ''),
            "Id_NFBC": player_id,
            "NFBC Roster %": player.get('o%'),
            "NFBC Active %": player.get('s%'),
            "NFBC Pts Season": points,
            # A two-way player's per-game rates are per role, and adding them would mean nothing
            "NFBC Pts/G": None if isinstance(per_game, str) and '/' in per_game else split_total(per_game),
        })

    if not trends_list:
        raise RuntimeError("NFBC returned no players with roster percentages or points")

    save_and_import(trends_list, 'nfbc', trend_type)
    return trends_list


def nfbc_draft(trend_type):
    """Import NFBC's ADP (draft) or average auction value (auction) table."""
    form = {
        'team_id': '0', 'from_date': '', 'to_date': '', 'num_teams': '0', 'position': '', 'league_teams': '0',
        'draft_type': DRAFT_TYPES[trend_type], 'sport': 'baseball',
    }
    response = ratelimit_post_url(DRAFT_DATA_URL, data=form)
    response.raise_for_status()

    labels = nfbc_trend_labels[trend_type]
    trends_list = []
    for row in BeautifulSoup(response.text, 'html.parser').find_all('tr'):
        cells = row.find_all('td')
        link = row.find('a', href=PLAYER_LINK)
        if len(cells) <= max(DRAFT_VALUE_COLUMNS) or not link:
            continue
        entry = {
            "Player": cells[1].get_text(strip=True),
            "Position": cells[3].get_text(strip=True),
            "Team": cells[2].get_text(strip=True),
            "Id_NFBC": PLAYER_LINK.search(link['href']).group(1),
        }
        for label, column in zip(labels, DRAFT_VALUE_COLUMNS):
            entry[label] = parse_number(cells[column].get_text(strip=True))
        trends_list.append(entry)

    if not trends_list:
        # NFBC answers with this one row until the season's first drafts or auctions are in
        if 'No ADP Information Available' in response.text:
            raise RuntimeError(f"NFBC has no {trend_type} data yet; it fills once this season's {trend_type}s start")
        raise RuntimeError(f"NFBC returned no {trend_type} rows")

    save_and_import(trends_list, 'nfbc', trend_type)
    return trends_list


def iso_date(text):
    """Return '2/1/2027' as '2027-02-01' so dates sort correctly, or the text as is if it isn't a date."""
    try:
        return datetime.strptime(text, '%m/%d/%Y').strftime('%Y-%m-%d')
    except ValueError:
        return text or None


def nfbc_injuries(trend_type):
    """Import NFBC's injury list, and clear the injury fields of players no longer on it."""
    response = ratelimit_get_url(trend_urls[trend_type])
    response.raise_for_status()
    table = BeautifulSoup(response.text, 'html.parser').find('table', id='injuries')
    if table is None:
        raise RuntimeError(f"No injuries table found on {trend_urls[trend_type]}; its layout may have changed")

    trends_list = []
    team = ''
    for row in table.find_all('tr'):
        # Players are grouped under a header row naming their team, e.g. 'Arizona Diamondbacks'
        header = row.find('th')
        if header:
            team = header.get_text(strip=True)
            continue
        # Columns are Return Date, Player, Status, Prognosis, Comment; rows without a player link are column titles
        cells = row.find_all('td')
        link = row.find('a', href=PLAYER_LINK)
        if len(cells) < 5 or not link:
            continue
        trends_list.append({
            "Player": cells[1].get_text(strip=True),
            "Position": '',
            "Team": team,
            "Id_NFBC": PLAYER_LINK.search(link['href']).group(1),
            "NFBC Inj Status": cells[2].get_text(strip=True) or None,
            "NFBC Inj Type": cells[3].get_text(strip=True) or None,
            "NFBC Inj Return": iso_date(cells[0].get_text(strip=True)),
            "NFBC Inj Note": cells[4].get_text(strip=True) or None,
        })

    save_and_import(trends_list, 'nfbc', trend_type)
    clear_stale_values(INJURY_LABELS, 'Id_NFBC', {entry['Id_NFBC'] for entry in trends_list}, 'NFBC')
    return trends_list


# Tests with `docker exec buzz ./.venv/bin/python src/source_nfbc.py` (imports the results into the database)
if __name__ == '__main__':
    print('\n', 'nfbc_get(draft)', '\n', nfbc_get('draft'))
