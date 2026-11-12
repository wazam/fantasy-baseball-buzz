import re
from datetime import datetime
from urllib.parse import urljoin
from util_beautifulsoup import beautifulsoup_scrape, beautifulsoup_find, parse_number, ratelimit_get_url
from db import save_and_import, clear_stale_values
from sources import SOURCES

cbs_config = next(source for source in SOURCES if source['source'].lower() == 'cbs')
trend_urls = {trend['key']: trend['url'] for trend in cbs_config['trends']}
cbs_trend_labels = {trend['key']: trend['labels'] for trend in cbs_config['trends']}

# The 'most-*' pages share the Player | value | value table this parser reads
TREND_PAGES = {'most-added', 'most-dropped', 'most-viewed', 'most-traded'}

# CBS's public JSON data service, used where it covers a trend. It has no trends endpoint, so the
# 'most-*' trends stay on the pages above; the remaining trends return None (not implemented)
API_URL = 'https://api.cbssports.com/fantasy'
API_PARAMS = {'version': '3.0', 'SPORT': 'baseball', 'response_format': 'JSON'}
INJURY_LABELS = ['CBS Inj Status', 'CBS Inj Type', 'CBS Inj Return', 'CBS Inj Updated']

# Trends cbs_get can scrape, which the app shows as runnable
SUPPORTED_TRENDS = TREND_PAGES | {'injuries'}


def cbs_get(trend_type):
    """Return a list of player trends by trend type, and save them to a trend-specific JSON file."""

    if trend_type not in trend_urls:
        raise ValueError(f"Invalid trend_type '{trend_type}'. Choose from: {list(trend_urls.keys())}")
    if trend_type == 'injuries':
        return cbs_injuries(trend_type)
    if trend_type not in TREND_PAGES:
        return None

    return cbs_finishup(trend_urls[trend_type], cbs_trend_labels[trend_type], trend_type)


def cbs_injuries(trend_type):
    """Import CBS's current injury list, and clear the injury fields of players no longer on it."""
    response = ratelimit_get_url(f'{API_URL}/players/injuries', params=API_PARAMS)
    response.raise_for_status()

    trends_list = []
    for injury in response.json()['body']['injuries']:
        player = injury['player']
        # CBS files a few injuries under an 'UnKnown Player' placeholder with no team or position
        if not player.get('pro_team') and not player.get('position'):
            continue
        updated = injury.get('updated')
        trends_list.append({
            "Player": player.get('fullname') or f"{player['firstname']} {player['lastname']}",
            "Position": player.get('position') or '',
            "Team": player.get('pro_team') or '',
            "Id_CBS": str(injury['player_id']),
            "CBS Inj Status": injury.get('status'),
            "CBS Inj Type": injury.get('injury_type'),
            # An exact date when CBS has one, otherwise its estimate like 'Expected to be out until at least May 1'
            "CBS Inj Return": injury.get('return_date') or injury.get('expected_return'),
            "CBS Inj Updated": datetime.fromtimestamp(updated).strftime('%Y-%m-%d') if updated else None,
        })

    save_and_import(trends_list, 'cbs', trend_type)
    clear_stale_values(INJURY_LABELS, 'Id_CBS', {entry['Id_CBS'] for entry in trends_list}, 'CBS')
    return trends_list


def parse_trend_row(row, labels):
    """Return one table row's player and values keyed by label, or None for a row without a player."""
    player_cell, *value_cells = row.find_all('td')
    player_info = player_cell.find('span', class_='CellPlayerName--long')
    player_name_tag = player_info.find('a', href=True) if player_info else None
    if not player_name_tag:
        return None

    player_id_match = re.search(r'/mlb/players/(\d+)', player_name_tag['href'])
    player_pos = player_info.find('span', class_='CellPlayerName-position')
    player_team = player_info.find('span', class_='CellPlayerName-team')

    player_entry = {
        "Player": player_name_tag.get_text(strip=True),
        "Position": player_pos.get_text(strip=True) if player_pos else '',
        "Team": player_team.get_text(strip=True) if player_team else '',
        "Id_CBS": player_id_match.group(1) if player_id_match else None
    }
    for label, cell in zip(labels, value_cells):
        player_entry[label] = parse_number(cell.get_text())
    return player_entry


def cbs_finishup(url_trend, labels, trend_type):
    """Process CBS Sports trend tables and return a list of player trends."""
    # Each position filter link (All, C, 1B, ...) leads to one trends table
    results_page = beautifulsoup_scrape(url_trend, '', 'body', '', False)
    elements_position_pages = beautifulsoup_find(results_page, 'all', 'a', 'Dropdown-link', True)
    if elements_position_pages is None:
        raise RuntimeError(f"No position links found on {url_trend}; the page failed to load or its layout changed")

    trends_list = []
    total_position_pages = len(elements_position_pages)  # Total number of position pages
    print(f"Total position pages to process: {total_position_pages}")

    for page_index, position_page in enumerate(elements_position_pages, start=1):
        url_full = urljoin(url_trend, position_page['href'])
        results_table = beautifulsoup_scrape(url_full, '', 'div', 'TableBaseWrapper', False)

        # Positions with no movement have no table, which is normal in the offseason
        if results_table is None:
            print(f"Skipping page {page_index}/{total_position_pages}: Unable to retrieve results table.")
            continue

        elements_rows = beautifulsoup_find(results_table, 'all', 'tr', 'TableBase-bodyTr', False)
        if elements_rows is None:
            print(f"Skipping page {page_index}/{total_position_pages}: No data found.")
            continue

        # The first column is the player, then one column per label in table order
        value_headers = results_table.find_all('th')[1:]
        if len(value_headers) != len(labels):
            print(f"Skipping page {page_index}/{total_position_pages}: expected {len(labels)} value columns, found {len(value_headers)}.")
            continue

        print(f"Processing position page {page_index}/{total_position_pages} for trend type '{trend_type}'...")
        trends_list += [entry for row in elements_rows if (entry := parse_trend_row(row, labels))]

    if not trends_list:
        raise RuntimeError(f"No players found on any of the {total_position_pages} position pages for trend type '{trend_type}'")

    # The 'All' page and each position page list the same players, so keep each player's first entry.
    # Keyed by CBS ID because different players can share a name (e.g. both Will Smiths)
    unique_trends = {}
    for entry in trends_list:
        unique_trends.setdefault(entry['Id_CBS'] or entry['Player'], entry)
    trends_list = list(unique_trends.values())

    save_and_import(trends_list, 'cbs', trend_type)
    return trends_list


# Tests with `docker exec buzz ./.venv/bin/python src/source_cbs.py` (imports the results into the database)
if __name__ == '__main__':
    print('\n', 'cbs_get(most-added)', '\n', cbs_get('most-added'))
