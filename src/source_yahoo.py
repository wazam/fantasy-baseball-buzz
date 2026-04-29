from util_beautifulsoup import beautifulsoup_scrape, beautifulsoup_find
from util_nocodb import search_record, create_records, update_records
from unidecode import unidecode
from datetime import date
from datetime import timedelta


def date_X_days_ago(days):
    date_today = date.today()
    date_days_back = timedelta(days=days)
    date_back = date_today - date_days_back
    return date_back


##
def yahoo_get(trend_type):
    return None
##


url_base = 'https://baseball.fantasysports.yahoo.com'
weekly_dict = {}
daily_dict = {}
data_rows = []


# Returns a numerically ordered dictionary of Players' names with their add/drop roster trends
def yahoo_get_added_dropped_trends_X_days(number_of_days_to_scrape):
    column_name = 'yahoo_get_added_dropped_trends'
    weekly_dict.clear()
    name_lookup_cache = {}  # in-memory cache replacing old JSON lookup file

    # Get position page URLs from daily page
    for day in range(0, int(number_of_days_to_scrape)):
        daily_dict.clear()
        date_scrape = date_X_days_ago(day)
        url_tab = '/b1/buzzindex?sort=BI_S&src=combined&bimtab=ALL&trendtab=O&pos=ALL&date='
        url_scrape = url_base + url_tab + str(date_scrape)
        elements_positions = beautifulsoup_scrape(url_scrape, 'all', 'a', 'Navtarget', True)[46::]

        # Get Players table data from position page
        for position in elements_positions:
            url_tab = str(position['href'])
            url_scrape = url_base + url_tab
            results_table = beautifulsoup_scrape(url_scrape, 'all', 'table', 'Tst-table Table', False)[0]
            elements_rows = beautifulsoup_find(results_table, 'all', 'tr', '', False)[2::]
            elements_players = beautifulsoup_find(results_table, 'all', 'a', 'Nowrap', True)

            # Get index from row of all Player's column data
            data_rows.clear()
            for index, row in enumerate(elements_rows):
                elements_columns = beautifulsoup_find(row, 'all', 'td', '', False)
                elements_columns = [each_column.text.strip() for each_column in elements_columns]
                data_rows.append([each_column for each_column in elements_columns if each_column])

                # Get Player's short name by trying to removing team names until the string is successfully shortened
                mlb_teams = ['ARI', 'ATL', 'BAL', 'BOS', 'CWS', 'CHC', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYY', 'NYM', 'OAK', 'PHI', 'PIT', 'SD', 'SF', 'SEA', 'STL', 'TB', 'TEX', 'TOR', 'WAS']
                for team in mlb_teams:
                    if len(str(str(data_rows[index][0].split('\n')[1].strip()).rsplit(str(team + ' - '), 2)[0].strip())) < len(str(data_rows[index][0].split('\n')[1].strip())):
                        player_name_short = unidecode(str(str(data_rows[index][0].split('\n')[1].strip()).rsplit(team, 2)[0].strip())).title().strip()
                        break

                # Get Player's full name from in-memory cache, fall back to web request
                if player_name_short in name_lookup_cache:
                    player_name_full = name_lookup_cache[player_name_short]
                else:
                    url_scrape = str(elements_players[index]['href'])
                    element_player_name_full = beautifulsoup_scrape(url_scrape, '', 'span', 'ys-name', False)
                    player_name_full = unidecode(element_player_name_full.text).title().strip()
                    name_lookup_cache[player_name_short] = player_name_full

                # Add Player's Name and Change to daily dictionary, only on first occurrence
                player_add = int(data_rows[index][4])
                player_drop = int(data_rows[index][3])
                player_change = player_add - player_drop
                if player_name_full not in daily_dict:
                    daily_dict[player_name_full] = player_change

        # Add Player's Name and Change to weekly dictionary, accumulating across all days
        for key in daily_dict.keys():
            if key not in weekly_dict:
                weekly_dict[key] = daily_dict[key]
            else:
                weekly_dict[key] = weekly_dict[key] + daily_dict[key]

    # Update or create NocoDB records for each player's trend data
    update_list, create_list = [], []
    for player_name, change_value in weekly_dict.items():
        entry = {"Player": player_name, column_name: change_value}
        existing = search_record(entry, "Yahoo")
        if existing:
            update_list.append({"Id": existing["Id"], column_name: change_value})
        else:
            create_list.append(entry)

    if update_list:
        update_records(update_list, "Yahoo")
    if create_list:
        create_records(create_list)

    sorted_weekly_dict = dict(sorted(weekly_dict.items(), key=lambda x: x[1], reverse=True))
    return sorted_weekly_dict


# Returns all Players' add/drop trends for the past week
def yahoo_get_added_dropped_trends():
    data = yahoo_get_added_dropped_trends_X_days(7)
    return data


# Returns all Players to NocoDB
def yahoo_get_player_list():
    url_tab = '/b1/149226/players?status=A&pos=B&cut_type=33&stat1=S_S_2023&myteam=0&sort=R_PO&sdir=1&count=1200'
    url = url_base + url_tab
    return ('204', 204)


# Returns all deeper-searched Players to NocoDB
def yahoo_get_player_list_deep():
    url_tab = '/b1/149226/showforced'
    url = url_base + url_tab
    return ('204', 204)


# Tests with `pipenv run python src/source_yahoo.py`
if __name__ == '__main__':
    print('\n', 'yahoo_get_added_dropped_trends_X_days()', '\n', yahoo_get_added_dropped_trends(1))
    # print('\n', 'yahoo_get_added_dropped_trends', '\n', yahoo_get_added_dropped_trends())
    # print('\n', 'yahoo_get_player_list', '\n', yahoo_get_player_list())
    # print('\n', 'yahoo_get_player_list_deep', '\n', yahoo_get_player_list_deep())
