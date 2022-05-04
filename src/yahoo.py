# Used to load web pages
import requests
# Used to scrape web pages
from bs4 import BeautifulSoup
# Used to get current date
from datetime import date
# Used to calculate prior dates
from datetime import timedelta
# Used to remove accent marks from Player's names
import unidecode

# Returns a numerically ordered dictionary of Players' names with their add/drop roster trends
def yahoo_trends(number_of_days, fetch_full_names):
    # Create new dictionary to save all the Players' adds/drops for all the day(s)
    trends_dictionary = {}
    # Site-specific url
    url_base = "http://baseball.fantasysports.yahoo.com"
    # Loop through all days to scape all daily pages for positional URLs
    for each_day in range(0, int(number_of_days)):
        # Calculate scape date by continually removing 1 day from current day
        date_scrape = date.today() - timedelta(days = each_day)
        # Site-specific url
        url_tab = "/b1/buzzindex?sort=BI_S&src=combined&bimtab=ALL&trendtab=O&pos=ALL&date="
        # Create scrapable URL to load position pages from
        url_scrape = url_base + url_tab + str(date_scrape)
        # Load daily page
        html_page = requests.get(url_scrape)
        # Create HTML document for BeautifulSoup
        html_doc = html_page.content
        # Create searchable HTML with BeautifulSoup parsing
        html_soup = BeautifulSoup(html_doc, "html.parser")
        # Find intended main content on web page
        results_page = html_soup.find(id="yspmaincontent")
        # Find positional pages navigational web page targets in main content, save HREF for URL later, start on the 5th element because the first 4 navitems aren't relavant
        elements_positions = results_page.find_all("a", class_="Navtarget", href=True)[5::]
        # Create new dictionary to save Players' adds/drops for the day across all positions without double counting Players eligible in mutliple positions
        daily_dictionary = {}
        # Loop through all positional pages to scrape table data of Players for the day
        for position in elements_positions:
            # Get href URL for each positions' page for scraping
            url_tab = str(position['href'])
            # Create scrapable URL to load table data from
            url_scrape = url_base + url_tab
            # Load position page
            html_page = requests.get(url_scrape)
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
                # Find Player's full name with new full page request (no other option as data is not on main content page otherwise in any form) for cross-site comparison because the same abbreviated name is sometimes shared by different Players
                if fetch_full_names:
                    # Get href URL for each Players' individual page for scraping
                    url_scrape = str(elements_players[index]['href'])
                    # Load individual Player page
                    html_page = requests.get(url_scrape)
                    # Create HTML document for BeautifulSoup
                    html_doc = html_page.content
                    # Create searchable HTML with BeautifulSoup parsing
                    html_soup = BeautifulSoup(html_doc, "html.parser")
                    # Find intended main content on web page
                    results_page = html_soup.find(id="Main")
                    # Find Player's full name (with applicable diacritics) in main content
                    element_full_name = results_page.find("span", class_="ys-name")
                    # Set current Player's name and remove diacritics for cross-site comparison
                    player_name = unidecode.unidecode(str(element_full_name.text))
                # Find Player's shortened name without a new page request from the current data
                else:
                    # List of Yahoo! formatted MLB team names
                    player_teams = ["Ari","Atl","Bal","Bos","CWS","ChC","Cin","Cle","Col","Det","Hou","KC","LAA","LAD","Mia","Mil","Min","NYY","NYM","Oak","Phi","Pit","SD","SF","Sea","StL","TB","Tex","Tor","Was"]
                    # Loop through all the teams
                    for team in player_teams:
                        # Try removing team names until the string is successfully shortened
                        if len(str(str(data_rows[index][0].split('\n')[1].strip()).rsplit(str(team + ' - '), 2)[0].strip())) < len(str(data_rows[index][0].split('\n')[1].strip())):
                            # Set current Player's name and remove diacritics for cross-site comparison
                            player_name = unidecode.unidecode(str(str(data_rows[index][0].split('\n')[1].strip()).rsplit(team, 2)[0].strip()))
                            # Stop checking team names
                            break
                # Set current Player's adds for the day by looking at the column cell value for the current row
                player_add = int(data_rows[index][4])
                # Set current Player's drops for the day by looking at thr column cell value for the current row
                player_drop = int(data_rows[index][3])
                # Set Player's net change to remove drops from adds (unlike Yahoo which combines drops to adds)
                player_change = player_add - player_drop
                # Check if Player is already in daily dictionary to avoid duplicating Player's adds/drops for Players eligible on multiple position pages for the current day
                if player_name not in daily_dictionary:
                    # Add Player to daily dictionary with net change
                    daily_dictionary[player_name] = player_change
        # Loop through all the Players in the daily dictionary after scraping all the position pages for the day
        for key in daily_dictionary.keys():
            # Check if Player is already in the weekly trends dictionary
            if key not in trends_dictionary:
                # Add Player to weekly trends dictionary with their adds/drop
                trends_dictionary[key] = daily_dictionary[key]
            # For Players with existing key/values
            else:
                # Update Player in weekly trends dictionary while keeping their add/drops from prior day(s)
                trends_dictionary[key] = trends_dictionary[key] + daily_dictionary[key]
    # Create new dictionary to sort the Players' by their net change across the requested day(s)
    sorted_trends_dictionary = {}
    # Create a function to decide the custom sorting order
    def by_value(item):
        # Return the Player's adds/drops net change
        return item[1]
    # Loop through all the Players' net change values in the weekly trends dictionary for custom sorting in descending order
    for key, value in sorted(trends_dictionary.items(), key=by_value, reverse=True):
        # Add Player to sorted weekly trends dictionary with their adds/drop
        sorted_trends_dictionary[key] = value
    # Return sorted dictionary of Players' names and adds/drops for the function
    return sorted_trends_dictionary

# Used for "pipenv run python yahoo.py"
if __name__ == "__main__":
    # Set development value for number of prior days to scape adds/drops for
    number_of_days = 2
    # Set development value for scraping Players' full names at the cost of an additional page request per each Player
    fetch_full_names = False
    # Get Player's trends dictionary from function above
    data = yahoo_trends(number_of_days,fetch_full_names)
    # Print command line interface heading for data
    print('\x1b[6;30;42m' + "Past " + str(number_of_days) + " day(s) of Yahoo trends" + '\x1b[0m')
    # Print Player trends data
    print(data)
