import requests
from bs4 import BeautifulSoup

import utils.my_json as MyJ


url_base = "http://www.cbssports.com"
trends_dictionary = {}
sorted_trends_dictionary = {}
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"}


def startup(url_tab):
    #Create dictionary for storing Player's names and X Day +/-
    trends_dictionary.clear()
    sorted_trends_dictionary.clear()
    url_scrape = url_base + url_tab
    html_page = requests.get(url_scrape, headers=headers)
    html_doc = html_page.content
    html_soup = BeautifulSoup(html_doc, "html.parser")
    results_page = html_soup.find("div", class_="Page-shell")
    return results_page


#Function to return a numerically ordered dictionary of players' names and players' trends
def get_added_dropped_trends():
    url_tab = "/fantasy/baseball/trends/added/all/"
    results_page = startup(url_tab)
    #Loop through tabs Most-Added and Most-Dropped
    elements_tabs = results_page.find_all("a", class_="PageTabsNav-link", href=True)[0:2]
    return finishup(elements_tabs, 4)

def get_viewed_trends():
    url_tab = "/fantasy/baseball/trends/viewed/all/"
    results_page = startup(url_tab)
    #Loop through tabs Most-Viewed
    elements_tabs = results_page.find_all("a", class_="PageTabsNav-link", href=True)[2:3]
    return finishup(elements_tabs, 3)

def get_traded_trends():
    url_tab = "/fantasy/baseball/trends/traded/all/"
    results_page = startup(url_tab)
    #Loop through tabs Most-Traded
    elements_tabs = results_page.find_all("a", class_="PageTabsNav-link", href=True)[3:4]
    return finishup(elements_tabs, 2)


def finishup(elements_tabs, column):
    for tab in elements_tabs:
        url_tab = str(tab['href'])
        url_scrape = url_base + url_tab
        html_page = requests.get(url_scrape, headers=headers)
        html_doc = html_page.content
        html_soup = BeautifulSoup(html_doc, "html.parser")
        results_page = html_soup.find("div", class_="Page-shell")
        
        #Loop through all positions
        elements_positions = results_page.find_all("a", class_="Dropdown-link", href=True)
        for position in elements_positions:
            url_tab = str(position['href'])
            url_scrape = url_base + url_tab
            html_page = requests.get(url_scrape, headers=headers)
            html_doc = html_page.content
            html_soup = BeautifulSoup(html_doc, "html.parser")
            results_table = html_soup.find(id="TableBase")

            #Loop through all rows
            elements_rows = results_table.find_all("tr", class_="TableBase-bodyTr")
            elements_players_info = results_table.find_all("span", class_="CellPlayerName--long")
            start = column - 1
            elements_7day_change = results_table.find_all("td", class_="TableBase-bodyTd")[start::column]
            for index, row in enumerate(elements_rows):
                #Find Player's name
                player_name = str(elements_players_info[index].text.split('\n')[0])
                #Find Player's 7 day change in ownership %s
                if elements_7day_change[index].text.strip() == "—":
                    # Handle players with 0 trades "—" by skipping
                    continue
                player_change = int(elements_7day_change[index].text.strip())
                #Add Player's name to permanent trends dictionary
                if player_name not in trends_dictionary:
                    trends_dictionary[player_name] = player_change
                MyJ.check_and_add(player_name, 'player-names')

    # Create a function to decide the custom sorting order
    def by_value(item):
        # Return the Player's net change
        return item[1]
    # Loop through all the Players' net change values in the weekly trends dictionary for custom sorting in descending order
    for key, value in sorted(trends_dictionary.items(), key=by_value, reverse=True):
        # Add Player to sorted weekly trends dictionary with their net change
        sorted_trends_dictionary[key] = value
    #Return sorted dictionary for the function
    return sorted_trends_dictionary


# Used for testing with `pipenv run python src/provider_cbs.py`
if __name__ == "__main__":
    print('\n', 'get_added_dropped_trends', '\n', get_added_dropped_trends())
    print('\n', 'get_viewed_trends', '\n', get_viewed_trends())
    print('\n', 'get_traded_trends', '\n', get_traded_trends())
