from datetime import date, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from util_beautifulsoup import beautifulsoup_scrape, parse_number
from db import save_and_import, clear_stale_values
from sources import SOURCES

url_base = 'https://baseball.fantasysports.yahoo.com'
yahoo_config = next(source for source in SOURCES if source['source'].lower() == 'yahoo')
trend_keys = [trend['key'] for trend in yahoo_config['trends']]
trend_labels = {trend['key']: trend['labels'] for trend in yahoo_config['trends']}

# Between seasons every Yahoo fantasy baseball page answers "The document you requested was not found"
OFFSEASON = "Yahoo takes it offline between seasons"

# Buzz Index table headers mapped to the labels they fill, plus how many days each trend covers
BUZZ_INDEX_TRENDS = {
    'buzz-index': (1, {
        '% Ros': 'Yahoo Roster %',
        '% Start': 'Yahoo Active %',
        'Adds': 'Yahoo Adds Today',
        'Drops': 'Yahoo Drops Today',
        'Trades': 'Yahoo Trades Today',
    }),
    'buzz-index-7d': (7, {
        'Adds': 'Yahoo Adds 7D',
        'Drops': 'Yahoo Drops 7D',
        'Trades': 'Yahoo Trades 7D',
    }),
}

# Who's Hot tabs: Batters and Pitchers, 25 players each
WHOS_HOT_TABS = ['B', 'AP']

# MVPs tabs and the labels they fill
MVP_TABS = {'roto': 'Yahoo MVP % Roto', 'head': 'Yahoo MVP % H2H'}

# Matchup Ratings' all-players view has a tab per position, each listing up to 50 players
MATCHUP_POSITIONS = ['ALL', 'C', '1B', '2B', '3B', 'SS', 'OF', 'Util', 'SP', 'RP', 'P']


def yahoo_get(trend_type):
    """Return a list of player trends by trend type, and save them to a trend-specific JSON file."""

    if trend_type not in trend_keys:
        raise ValueError(f"Invalid trend_type '{trend_type}'. Choose from: {trend_keys}")
    if trend_type in BUZZ_INDEX_TRENDS:
        days, columns = BUZZ_INDEX_TRENDS[trend_type]
        return yahoo_buzz_index(trend_type, days, columns)
    scraper = PAGE_TRENDS.get(trend_type)
    return scraper(trend_type) if scraper else None


def player_entry(cell):
    """Return the player in a row's first cell (name, team, position and Yahoo ID), or None if it has none."""
    name_tag = cell.find('a', class_='name') if cell else None
    if not name_tag:
        return None

    # Shown as 'MIN - SP' under the player's name; injury tags like 'IL10' share the Fz-xxs style
    team_position = cell.select_one('span.D-b > span.Fz-xxs')
    team, _, position = team_position.get_text(strip=True).partition(' - ') if team_position else ('', '', '')
    return {
        "Player": name_tag.get_text(strip=True),
        "Position": position,
        "Team": team,
        "Id_Yahoo": name_tag.get('data-ys-playerid'),
    }


def player_rows(table, wanted):
    """Yield (player entry, {header: cell}) for each player row, reading the cells under the wanted headers."""
    header_row = next((row for row in table.find_all('tr')
                       if set(wanted) <= {cell.get_text(' ', strip=True) for cell in row.find_all(['th', 'td'])}), None)
    if header_row is None:
        raise RuntimeError(f"Yahoo's table has no {wanted} columns; the page may have changed")
    headers = [cell.get_text(' ', strip=True) for cell in header_row.find_all(['th', 'td'])]

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        entry = player_entry(cells[0]) if cells else None
        if entry:
            yield entry, {header: cells[headers.index(header)] for header in wanted}


def parse_buzz_table(table, columns):
    """Return one entry per player row, with the values under each header in columns stored as its label."""
    if table is None:
        print("No Buzz Index table found.")
        return []
    try:
        return [{**entry, **{label: parse_number(cells[header].get_text(strip=True)) for header, label in columns.items()}}
                for entry, cells in player_rows(table, list(columns))]
    except RuntimeError as e:
        print(f"Buzz Index: {e}")
        return []


def buzz_index_day(date_scrape, columns):
    """Return the All Positions table plus each position tab's table for one day."""
    url = f"{url_base}/b1/buzzindex?sort=BI_S&src=combined&bimtab=A&trendtab=O&pos=ALL&date={date_scrape}"
    page = beautifulsoup_scrape(url, '', 'body', '', False)
    if page is None:
        return []

    entries = parse_buzz_table(page.find('table', class_='Tst-table'), columns)

    # Each position tab (C, 1B, ... P) lists that position's top 50, reaching deeper than All Positions
    for link in page.find_all('a', class_='Navtarget', href=True):
        query = parse_qs(urlparse(link['href']).query)
        if query.get('bimtab') == ['A'] and query.get('trendtab') == ['O'] and query.get('pos', ['ALL']) != ['ALL']:
            table = beautifulsoup_scrape(urljoin(url_base, link['href']), '', 'table', 'Tst-table', False)
            entries += parse_buzz_table(table, columns)
    return entries


def yahoo_buzz_index(trend_type, days, columns):
    """Process the Buzz Index for the last `days` days, summing each player's numbers across days."""
    totals = {}
    for day in range(days):
        date_scrape = date.today() - timedelta(days=day)
        print(f"Processing Buzz Index for {date_scrape} ({day + 1}/{days}) for trend type '{trend_type}'...")

        # A player listed under several tabs counts once per day, from its first (All Positions) row
        day_entries = {}
        for entry in buzz_index_day(date_scrape, columns):
            day_entries.setdefault(entry['Id_Yahoo'] or entry['Player'], entry)

        # Today's row comes first, so each player keeps their latest name, team and position
        for player_key, entry in day_entries.items():
            if player_key not in totals:
                totals[player_key] = entry
                continue
            for label in columns.values():
                if isinstance(entry[label], (int, float)) and isinstance(totals[player_key][label], (int, float)):
                    totals[player_key][label] += entry[label]

    trends_list = list(totals.values())
    if not trends_list:
        raise RuntimeError(f"Yahoo's Buzz Index returned no player table; {OFFSEASON}")

    save_and_import(trends_list, 'yahoo', trend_type)
    return trends_list


def fetch_table(path, page_name, table_class='Tst-table'):
    """Return a Yahoo page's player table. Raises when the page or its table is missing, so a run never imports
    part of a list and then clears the players on the page that failed."""
    page = beautifulsoup_scrape(f"{url_base}{path}", '', 'body', '', False)
    table = page.find('table', class_=table_class) if page else None
    if table is None:
        raise RuntimeError(f"Yahoo's {page_name} returned no player table; {OFFSEASON}")
    return table


def import_page_trend(trends_list, trend_type, page_name):
    """Import a page trend's players, then blank its labels on players no longer listed."""
    if not trends_list:
        raise RuntimeError(f"Yahoo's {page_name} listed no players; {OFFSEASON}")
    save_and_import(trends_list, 'yahoo', trend_type)
    clear_stale_values(trend_labels[trend_type], 'Id_Yahoo', {entry['Id_Yahoo'] for entry in trends_list}, 'Yahoo')
    return trends_list


def whos_hot(trend_type):
    """Rank the players on Who's Hot, 1 to 25 among batters and again among pitchers."""
    trends_list = []
    for tab in WHOS_HOT_TABS:
        table = fetch_table(f"/b1/whoshot?pos={tab}", "Who's Hot")
        trends_list += [{**entry, "Yahoo Rank Hot": rank}
                        for rank, (entry, _) in enumerate(player_rows(table, ['Player']), 1)]
    return import_page_trend(trends_list, trend_type, "Who's Hot")


def mvps(trend_type):
    """Return each MVP's percentage from the Rotisserie and Head-to-Head tabs. Between seasons the page shows
    'MVPs data will be available on' a date instead of players."""
    players = {}
    for tab, label in MVP_TABS.items():
        table = fetch_table(f"/b1/keystosuccess?st={tab}", "MVPs")
        notice = table.get_text(' ', strip=True)
        if 'will be available' in notice:
            raise RuntimeError(f"Yahoo's MVPs page says '{notice}'")
        for entry, cells in player_rows(table, ['Player', 'Percent']):
            # Both labels are set, so a player on only one tab doesn't keep an old value on the other
            player = players.setdefault(entry['Id_Yahoo'], {**entry, **{name: None for name in MVP_TABS.values()}})
            player[label] = parse_number(cells['Percent'].get_text(strip=True))
    return import_page_trend(list(players.values()), trend_type, "MVPs")


def injuries(trend_type):
    """Return every player on the injury report with their designation (IL10, IL60, DTD, SUSP) and injury."""
    table = fetch_table("/b1/injuries", "injury report", 'Table-mid')
    trends_list = []
    for entry, cells in player_rows(table, ['Player', 'Note', 'Status']):
        # The detailed designation sits beside the name; the Status column only says IL, DTD or SUSP
        designation = cells['Player'].select_one('span.ysf-player-status span')
        trends_list.append({
            **entry,
            "Yahoo Inj Status": (designation or cells['Status']).get_text(strip=True),
            "Yahoo Inj Type": cells['Note'].get_text(' ', strip=True),
        })
    return import_page_trend(trends_list, trend_type, "injury report")


def matchup_ratings(trend_type):
    """Return each player's matchup rating (1 to 5 stars) and opponent from every position tab."""
    players = {}
    for position in MATCHUP_POSITIONS:
        table = fetch_table(f"/b1/playermatchups?tab=ALL&pos={position}", "Matchup Ratings")
        for entry, cells in player_rows(table, ['Player', 'Opp', 'Rating']):
            # Every shaded star counts toward the rating, whether shaded positive, neutral or negative
            stars = len(cells['Rating'].select('span.F-positive, span.F-neutral, span.F-negative'))
            players.setdefault(entry['Id_Yahoo'], {
                **entry,
                "Yahoo Matchup Rating": stars,
                "Yahoo Matchup Opp": cells['Opp'].get_text(' ', strip=True),
            })
    return import_page_trend(list(players.values()), trend_type, "Matchup Ratings")


# Trends read from one page each (or one page per tab), keyed by trend
PAGE_TRENDS = {
    'whos-hot': whos_hot,
    'mvps': mvps,
    'injuries': injuries,
    'matchup-ratings': matchup_ratings,
}

# Trends yahoo_get can scrape, which the app shows as runnable
SUPPORTED_TRENDS = set(BUZZ_INDEX_TRENDS) | set(PAGE_TRENDS)


# Tests with `docker exec buzz ./.venv/bin/python src/source_yahoo.py` (imports the results into the database)
if __name__ == '__main__':
    print('\n', 'yahoo_get(buzz-index)', '\n', yahoo_get('buzz-index'))
