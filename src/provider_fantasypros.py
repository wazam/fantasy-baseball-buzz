from util_airtable import airtable_update_player_data
from util_beautifulsoup import beautifulsoup_scrape

url_base = 'https://www.fantasypros.com'


# One lead function to that redirects to one of two 
def fantasypros_get_player_list(tab):
    # Returns Players rest of season ranks
    if str(tab).lower() == 'ROS'.lower():
        url_tab = '/mlb/rankings/ros-overall.php'
    # Returns Players draft day ranks
    elif str(tab).lower() == 'Draft'.lower():
        url_tab = '/mlb/rankings/overall.php'
    fantasypros_internal_get_player_list(url_tab)
    return


def fantasypros_internal_get_player_list(url_tab):
    url_page = url_base + url_tab
    result_rows = beautifulsoup_scrape(url_page, 'all', 'tr', '', False)
    # Loop through all rows of Players
    for player, _ in enumerate(result_rows, 1):
        player_data = result_rows[player].text.split('\n')
        player_name = player_data[1].split('(')[0].strip()
        try:
            player_team = player_data[1].split('(')[1].strip().split(')')[0].split('-')[0].strip()
        except IndexError:
            break
        player_position_raw = player_data[1].split('(')[1].strip().split(')')[0].split('-')[1].strip()
        player_position_fix_outfield = player_position_raw.replace('LF', 'OF').replace('CF', 'OF').replace('RF', 'OF')
        if player_position_fix_outfield.count('OF') > 1:
            player_position_fix_list = player_position_fix_outfield.split(',')
            player_position_fix_deduplicated = []
            [player_position_fix_deduplicated.append(x) for x in player_position_fix_list if x not in player_position_fix_deduplicated]
            player_position = ''
            for index, position in enumerate(player_position_fix_deduplicated):
                if index == 0:
                    pass
                else:
                    player_position = player_position + ', '
                player_position = player_position + position
        else:
            player_position = player_position_fix_outfield.replace(',', ', ')
        player_rank = int(player_data[0])
        print(player_name, '|', player_team, '|', player_position, '|', 'FP Rnk', '|', player_rank)
        airtable_update_player_data(player_name, player_team, player_position, 'FP Rnk', player_rank)
    return


# Tests with `pipenv run python src/provider_fantasypros.py`
if __name__ == '__main__':
    print('\n', 'fantasypros_get_player_list()', '\n', fantasypros_get_player_list('ros'))
    # print('\n', 'fantasypros_get_player_list_draft()', '\n', fantasypros_get_player_list_draft('draft'))
