from util_beautifulsoup import beautifulsoup_scrape_class, beautifulsoup_find_class
from util_csv import csv_create_file, csv_check_and_add_to_file

url_base = 'https://www.fantasypros.com'
csv_filename = 'mlb-players-fp'


# Creates CSV file with list of Players' names
def fantasypros_get_player_list():
    # Scrape table from URL
    url_tab = '/mlb/rankings/overall.php'
    csv_create_file(csv_filename)
    url = url_base + url_tab
    results_page = beautifulsoup_scrape_class(url, '', 'div', 'mobile-table', False)
    # Loop through all rows for Player's names
    elements_players = beautifulsoup_find_class(results_page, 'all', 'a', 'player-name', True)
    for index, _ in enumerate(elements_players):
        player_name = str(elements_players[index].text.split('\n')[0])
        # Add Player's name to csv file
        csv_check_and_add_to_file(player_name, csv_filename)
    return


# Tests with `pipenv run python src/provider_fantasypros.py`
if __name__ == '__main__':
    print('\n', 'fantasypros_get_player_list', '\n', fantasypros_get_player_list())
