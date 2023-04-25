import src.utils.my_beautifulsoup as MyBS
import src.utils.my_datetime as MyDT
import src.utils.my_dictionary as MyD
import src.utils.my_json as MyJ
import src.utils.my_unidecode as MyU


url_base = "http://baseball.fantasysports.yahoo.com"
headers_import = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
weekly_dict = {}
daily_dict = {}


# Returns a numerically ordered dictionary of Players' names with their add/drop roster trends
def yahoo_trends(number_of_days_to_scrape):
    weekly_dict.clear()

    # Get position page URLs from daily page
    for day in range(0, int(number_of_days_to_scrape)):
        daily_dict.clear()
        date_scrape = MyDT.days_before_today(day)
        url_tab = "/b1/buzzindex?sort=BI_S&src=combined&bimtab=ALL&trendtab=O&pos=ALL&date="
        url_scrape = url_base + url_tab + str(date_scrape)
        elements_positions = MyBS.scrape_class(url_scrape, headers_import, 'all', 'a', 'Navtarget', True)[46::]

        # Get Players table data from position page
        for position in elements_positions:
            url_tab = str(position['href'])
            url_scrape = url_base + url_tab
            results_table = MyBS.scrape_class(url_scrape, headers_import, 'all', 'table', 'Tst-table Table', False)[0]
            elements_rows = MyBS.find(results_table, 'all', 'tr', False)[2::]
            elements_players = MyBS.find_class(results_table, 'all', 'a', 'Nowrap', True)

            # Get index from row of all Player's column data
            data_rows = []
            for index, row in enumerate(elements_rows):
                elements_columns = MyBS.find(row, 'all', 'td', False)
                elements_columns = [each_column.text.strip() for each_column in elements_columns]
                data_rows.append([each_column for each_column in elements_columns if each_column])

                # Get Player's short name by trying to removing team names until the string is successfully shortened
                mlb_teams = ["ARI","ATL","BAL","BOS","CWS","CHC","CIN","CLE","COL","DET","HOU","KC","LAA","LAD","MIA","MIL","MIN","NYY","NYM","OAK","PHI","PIT","SD","SF","SEA","STL","TB","TEX","TOR","WAS"]
                for team in mlb_teams:
                    if len(str(str(data_rows[index][0].split('\n')[1].strip()).rsplit(str(team + ' - '), 2)[0].strip())) < len(str(data_rows[index][0].split('\n')[1].strip())):
                        player_name_short = MyU.fix_str(str(str(data_rows[index][0].split('\n')[1].strip()).rsplit(team, 2)[0].strip()))
                        break
                
                # breakpoint()
                # Get Player's full name from JSON file (web request and save to JSON if full name is not present)
                players_json = MyJ.get_json('yahoo-players')
                for key, _ in enumerate(players_json['players']):
                    if player_name_short == players_json['players'][key]['short_name']:
                        player_name_full = players_json['players'][key]['full_name']
                        break
                    elif key == len(players_json['players']) - 1:
                        url_scrape = str(elements_players[index]['href'])
                        element_player_name_full = MyBS.scrape_class(url_scrape, headers_import, '', 'span', 'ys-name', False)
                        player_name_full = MyU.fix_str(element_player_name_full.text)
                        new_player = {"short_name": player_name_short, "full_name": player_name_full}
                        MyJ.write_json(new_player, 'yahoo-players')
                        break

                # Add Player's Name and Change to daily dictionary, only on first occurrence, across all position pages for the day
                player_add = int(data_rows[index][4])
                player_drop = int(data_rows[index][3])
                player_change = player_add - player_drop
                if player_name_full not in daily_dict:
                    daily_dict[player_name_full] = player_change

        # Add Player's Name and Change to weekly dictionary, add Changes across all days
        for key in daily_dict.keys():
            if key not in weekly_dict:
                weekly_dict[key] = daily_dict[key]
            else:
                weekly_dict[key] = weekly_dict[key] + daily_dict[key]

    # Sort the weekly dictionary from High to Low
    sorted_weekly_dict = MyD.sort(weekly_dict)
    return sorted_weekly_dict


# Used for testing with `pipenv run python -m src.providers.yahoo`
if __name__ == "__main__":
    days = 14
    data = yahoo_trends(days)
    print(data)
