import requests
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta
import unidecode
import json

import util.my_dictionary as MyD
import util.my_json as MyJ

url_base = "http://baseball.fantasysports.yahoo.com"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}


# Returns a numerically ordered dictionary of Players' names with their add/drop roster trends
def yahoo_trends(number_of_days, fetch_full_names):
    # Create new dictionary to save all the Players' adds/drops for all the day(s)
    trends_dictionary = {}
    # Site-specific url
    # Loop through all days to scape all daily pages for position URLs
    for each_day in range(0, int(number_of_days)):
        # Calculate scape date by continually removing 1 day from current day
        date_scrape = date.today() - timedelta(days = each_day)
        # Site-specific url
        url_tab = "/b1/buzzindex?sort=BI_S&src=combined&bimtab=ALL&trendtab=O&pos=ALL&date="
        # Create scrapable URL to load position pages from
        url_scrape = url_base + url_tab + str(date_scrape)
        # Load daily page
        html_page = requests.get(url_scrape, headers= headers)
        # Create HTML document for BeautifulSoup
        html_doc = html_page.content
        # Create searchable HTML with BeautifulSoup parsing
        html_soup = BeautifulSoup(html_doc, "html.parser")
        # Find intended main content on web page
        results_page = html_soup.find(id="yspmaincontent")
        # Find position pages navigational web page targets in main content, save HREF for URL later, start on the 5th element because the first 4 navitems aren't relavant
        elements_positions = results_page.find_all("a", class_="Navtarget", href=True)[5::]
        # Create new dictionary to save Players' adds/drops for the day across all positions without double counting Players eligible in mutliple positions
        daily_dictionary = {}
        # Loop through all position pages to scrape table data of Players for the day
        for position in elements_positions:
            # Get href URL for each positions' page for scraping
            url_tab = str(position['href'])
            # Create scrapable URL to load table data from
            url_scrape = url_base + url_tab
            # Load position page
            html_page = requests.get(url_scrape, headers= headers)
            # Create HTML document for BeautifulSoup
            html_doc = html_page.content
            # Create searchable HTML with BeautifulSoup parsing
            html_soup = BeautifulSoup(html_doc, "html.parser")
            # Find first table on web page with Players' data
            results_table = html_soup.find_all("table", class_="Tst-table Table")[0]
            # Find all the HTML rows (of Players) in the table, skip the header rows
            elements_rows = results_table.find_all("tr")[2::]
            # Find rows of Players in the table for full-name URL scraping later
            elements_players = results_table.find_all("a", class_="Nowrap", href=True)
            # Create new index to save column data into for each row
            data_rows = []
            # Loop through all the rows of Players on the current table on the current position page for the current day
            for index, each_row in enumerate(elements_rows):
                # Find all the column cells in each row
                elements_columns = each_row.find_all("td")
                # Remove spaces at the beginning/end of each column cell value
                elements_columns = [each_column.text.strip() for each_column in elements_columns]
                # Remove empty column cell values
                data_rows.append([each_column for each_column in elements_columns if each_column])

                # List of Yahoo! formatted MLB team names
                player_teams = ["Ari","Atl","Bal","Bos","CWS","ChC","Cin","Cle","Col","Det","Hou","KC","LAA","LAD","Mia","Mil","Min","NYY","NYM","Oak","Phi","Pit","SD","SF","Sea","StL","TB","Tex","Tor","Was"]
                # Loop through all the teams
                for team in player_teams:
                    # Try removing team names until the string is successfully shortened
                    if len(str(str(data_rows[index][0].split('\n')[1].strip()).rsplit(str(team + ' - '), 2)[0].strip())) < len(str(data_rows[index][0].split('\n')[1].strip())):
                        player_name_short = unidecode.unidecode(str(str(data_rows[index][0].split('\n')[1].strip()).rsplit(team, 2)[0].strip()))
                        break

                players_json = json.load(open('./data/yahoo-players.json'))
                print("player is " + player_name_short)
                for key, _ in enumerate(players_json['players']):
                    if player_name_short == players_json['players'][key]['short_name']:
                        player_name_full = players_json['players'][key]['full_name']
                        print("found old player")
                        break
                    elif key == len(players_json['players']) - 1:
                        url_scrape = str(elements_players[index]['href'])
                        html_page = requests.get(url_scrape, headers= headers)
                        html_soup = BeautifulSoup(html_page.content, "html.parser")
                        results_page = html_soup.find(id="Main")
                        player_name_full = unidecode.unidecode(str(results_page.find("span", class_="ys-name").text))
                        new_player = {"short_name": player_name_short, "full_name": player_name_full}
                        MyJ.write_json(new_player, filename= './data/yahoo-players.json')
                        print("added new player")
                        break
                    else:
                        print("no player found yet")

                player_name = player_name_full
                player_add = int(data_rows[index][4])
                player_drop = int(data_rows[index][3])
                player_change = player_add - player_drop

                if player_name not in daily_dictionary:
                    daily_dictionary[player_name] = player_change

        for key in daily_dictionary.keys():
            if key not in trends_dictionary:
                trends_dictionary[key] = daily_dictionary[key]
            else:
                trends_dictionary[key] = trends_dictionary[key] + daily_dictionary[key]
    sorted_trends_dictionary = MyD.sort(trends_dictionary, True)
    return sorted_trends_dictionary


# ```python src/yahoo.py```
if __name__ == "__main__":
    number_of_days = 1
    fetch_full_names = True
    data = yahoo_trends(number_of_days,fetch_full_names)
    print(data)
