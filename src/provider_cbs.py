from util_beautifulsoup import beautifulsoup_scrape_class, beautifulsoup_find_class
from util_dictionary import dictionary_sort_desc
from util_json import json_check_and_create_file, json_check_and_add_to_file

url_base = 'https://www.cbssports.com'
trends_dictionary = {}
sorted_trends_dictionary = {}
json_filename = 'mlb-players-cbs'


# Returns data of web page to search
def cbs_startup(url_tab):
    trends_dictionary.clear()
    sorted_trends_dictionary.clear()
    json_check_and_create_file(json_filename)  # Replace with separate _get_player_names()
    url = url_base + url_tab
    results_page = beautifulsoup_scrape_class(url, '', 'div', 'Page-shell', False)
    return results_page


# Returns a numerically ordered dictionary of players names by trends
def cbs_get_added_dropped_trends():
    url_tab = '/fantasy/baseball/trends/added/all/'
    results_page = cbs_startup(url_tab)
    # Loop through tabs Most-Added and Most-Dropped
    elements_tabs = beautifulsoup_find_class(results_page, 'all', 'a', 'PageTabsNav-link', True)[0:2]
    player_dict = cbs_finishup(elements_tabs, 4)
    sorted_dict = dictionary_sort_desc(player_dict)
    return sorted_dict


# Returns a numerically ordered dictionary of players names by trends
def cbs_get_viewed_trends():
    url_tab = '/fantasy/baseball/trends/viewed/all/'
    results_page = cbs_startup(url_tab)
    # Loop through tab Most-Viewed
    elements_tabs = beautifulsoup_find_class(results_page, 'all', 'a', 'PageTabsNav-link', True)[2:3]
    player_dict = cbs_finishup(elements_tabs, 3)
    sorted_dict = dictionary_sort_desc(player_dict)
    return sorted_dict


# Returns a numerically ordered dictionary of players names by trends
def cbs_get_traded_trends():
    url_tab = '/fantasy/baseball/trends/traded/all/'
    results_page = cbs_startup(url_tab)
    # Loop through tab Most-Traded
    elements_tabs = beautifulsoup_find_class(results_page, 'all', 'a', 'PageTabsNav-link', True)[3:4]
    player_dict = cbs_finishup(elements_tabs, 2)
    sorted_dict = dictionary_sort_desc(player_dict)
    return sorted_dict


# Returns sorted dictionary for the function
def cbs_finishup(elements_tabs, column):
    for tab in elements_tabs:
        url_tab = str(tab['href'])
        url = url_base + url_tab
        results_page = beautifulsoup_scrape_class(url, '', 'div', 'Page-shell', False)
        # Loop through all positions
        elements_positions = beautifulsoup_find_class(results_page, 'all', 'a', 'Dropdown-link', True)
        for position in elements_positions:
            url_tab = str(position['href'])
            url = url_base + url_tab
            results_table = beautifulsoup_scrape_class(url, '', 'div', 'TableBaseWrapper', False)
            elements_rows = beautifulsoup_find_class(results_table, 'all', 'tr', 'TableBase-bodyTr', False)
            elements_players_info = beautifulsoup_find_class(results_table, 'all', 'span', 'CellPlayerName--long', False)
            start = column - 1
            elements_7day_change = beautifulsoup_find_class(results_table, 'all', 'td', 'TableBase-bodyTd', False)[start::column]
            # Loop through all rows
            for index, _ in enumerate(elements_rows):
                # Find Player's name
                player_name = str(elements_players_info[index].text.split('\n')[0])
                # Find Player's 7 day change in ownership %s
                if elements_7day_change[index].text.strip() == '—':
                    # Handle players with 0 trades '—' by skipping
                    continue
                player_change = int(elements_7day_change[index].text.strip())
                # Add Player's name to permanent trends dictionary
                if player_name not in trends_dictionary:
                    trends_dictionary[player_name] = player_change
                json_check_and_add_to_file(player_name, json_filename)
    return trends_dictionary


# Tests with `pipenv run python src/provider_cbs.py`
if __name__ == '__main__':
    print('\n', 'cbs_get_added_dropped_trends', '\n', cbs_get_added_dropped_trends())
    print('\n', 'cbs_get_viewed_trends', '\n', cbs_get_viewed_trends())
    print('\n', 'cbs_get_traded_trends', '\n', cbs_get_traded_trends())
