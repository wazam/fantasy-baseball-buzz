import requests
from bs4 import BeautifulSoup


#Function to return a numerically ordered dictionary of players' names and players' trends
def cbs_trends():

    #Create dictionary for storing Player's names and X Day +/-
    trends_dictionary = {}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'}
    url_base = "http://www.cbssports.com"
    url_tab = "/fantasy/baseball/trends/added/all/"
    url_scrape = url_base + url_tab
    html_page = requests.get(url_scrape, headers=headers)
    html_doc = html_page.content
    html_soup = BeautifulSoup(html_doc, "html.parser")
    results_page = html_soup.find("div", class_="Page-shell")

    #Loop through all tabs
    elements_tabs = results_page.find_all("a", class_="PageTabsNav-link", href=True)[0:2]
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
            elements_7day_change = results_table.find_all("td", class_="TableBase-bodyTd")[3::4]
            for index, row in enumerate(elements_rows):
                #Find Player's name
                player_name = str(elements_players_info[index].text.split('\n')[0])
                #Find Player's 7 day change in ownership %s
                player_change = int(elements_7day_change[index].text.strip())
                #Add Player's name to permanent trends dictionary
                if player_name not in trends_dictionary:
                    trends_dictionary[player_name] = player_change

    # Create new dictionary to sort the Players' by their net change across the requested day(s)
    sorted_trends_dictionary = {}
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
    data = cbs_trends()
    print(data)
