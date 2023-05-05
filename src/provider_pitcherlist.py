from util_beautifulsoup import beautifulsoup_scrape_class, beautifulsoup_find_class, beautifulsoup_find
from util_dictionary import dictionary_sort, dictionary_sort_desc
from util_json import json_check_and_add_to_file, json_get_from_file
from util_unidecode import fix_str_format

url_base = 'https://www.pitcherlist.com'
player_dict = {}


# Return data from search in current week's article
def pl_startup(url_tab, all, name, attrib, href):
    player_dict.clear()
    url_start_page = url_base + url_tab
    start_page = beautifulsoup_scrape_class(url_start_page, '', 'div', 'hold-me', False)
    url_weekly_page = beautifulsoup_find_class(start_page, '', 'a', 'link', True)['href']
    weekly_page = beautifulsoup_scrape_class(url_weekly_page, all, name, attrib, href)
    return weekly_page


# Return Players' name and rank
def pl_get_ranks(rows):
    for i, _ in enumerate(rows):
        player_name_diacritics = rows[i].a.text
        player_name = fix_str_format(player_name_diacritics)
        player_rank = int(rows[i].td.text)
        if player_name not in player_dict:
            player_dict[player_name] = player_rank
        json_check_and_add_to_file(player_name, 'mlb-players-pl')
    return player_dict


# Return Players' name and change in rank
def pl_get_trends(rows):
    for i, _ in enumerate(rows):
        player_name_diacritics = rows[i].a.text
        player_name = fix_str_format(player_name_diacritics)
        player_trend_column = len(rows[i].find_all('td')) - 1
        player_trend_text = rows[i].find_all('td')[player_trend_column].text
        if player_trend_text == '-':
            player_trend = 0
        elif player_trend_text == '+UR':
            player_rank = int(rows[i].td.text)
            total_ranks = len(rows) + 1
            player_trend = total_ranks - player_rank
        else:
            player_trend = int(player_trend_text)
        if player_name not in player_dict:
            player_dict[player_name] = player_trend
        json_check_and_add_to_file(player_name, 'mlb-players-pl')
    return player_dict


# Return name and change in rank, sorted high to low
def pl_get_starting_pitcher_rank_trends():
    weekly_rows = pl_startup('/category/fantasy/the-list', 'all', 'tr', 'new-tier', False)
    player_dict = pl_get_trends(weekly_rows)
    sorted_dict = dictionary_sort(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def pl_get_starting_pitcher_ranks():
    weekly_rows = pl_startup('/category/fantasy/the-list', 'all', 'tr', 'new-tier', False)
    player_dict = pl_get_ranks(weekly_rows)
    sorted_dict = dictionary_sort_desc(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def pl_get_streaming_starting_pitcher_ranks():
    streamers_page = pl_startup('/category/fantasy/sp-streamers/', '', 'div', 'row article-wrap', False)
    row_streamers = beautifulsoup_find(streamers_page, 'all', 'tr', False)
    for i, _ in enumerate(row_streamers):
        if row_streamers[i].a == None:
            continue
        player_name = fix_str_format(row_streamers[i].a.text)
        player_rank = int(row_streamers[i].td.text)
        if player_name not in player_dict:
            player_dict[player_name] = player_rank
        json_check_and_add_to_file(player_name, 'mlb-players-pl')
    sorted_dict = dictionary_sort_desc(player_dict)
    return sorted_dict


# Return name (short) and projected matchup(s) tier, combined for all weekly matchups, sorted high to low
def pl_get_starting_pitcher_matchup_tiers():
    matchups_page = pl_startup('/category/fantasy/sit-or-start/', '', 'div', 'row article-wrap', False)
    matchups_row = beautifulsoup_find(matchups_page, 'all', 'tr', False)
    for i, _ in enumerate(matchups_row):
        try:
            player1_name_short = fix_str_format(matchups_row[i].find_all('td')[2].text)
            player1_rating = int(matchups_row[i].find_all('td')[3].text.split('-')[1])
            if player1_name_short not in player_dict:
                player_dict[player1_name_short] = player1_rating
            else:
                player1_rating_updated = player_dict[player1_name_short] + player1_rating
                player_dict.update({player1_name_short: player1_rating_updated})
            player2_name_short = fix_str_format(matchups_row[i].find_all('td')[4].text)
            player2_rating = int(matchups_row[i].find_all('td')[5].text.split('-')[1])
            if player2_name_short not in player_dict:
                player_dict[player2_name_short] = player2_rating
            else:
                player2_rating_updated = player_dict[player2_name_short] + player2_rating
                player_dict.update({player2_name_short: player2_rating_updated})
        except IndexError:
            continue

        # Get Player's full name from JSON file
        players_json = json_get_from_file('lookup-first-name-abbreviation')
        for key, _ in enumerate(players_json['players']):
            if player1_name_short == players_json['players'][key]['short_name']:
                player1_name_full = players_json['players'][key]['full_name']
            if player2_name_short == players_json['players'][key]['short_name']:
                player2_name_full = players_json['players'][key]['full_name']
            elif key == len(players_json['players']) - 1:
                # No full name found, try scraping more
                break

        json_check_and_add_to_file(player1_name_full, 'mlb-players-pl')
        json_check_and_add_to_file(player2_name_full, 'mlb-players-pl')

    sorted_dict = dictionary_sort(player_dict)
    return sorted_dict


# Return name and projected matchups tier
def pl_get_two_start_starting_pitcher_matchup_tiers():
    tables = pl_startup('/category/fantasy/two-start-pitchers/', 'all', 'table', 'dataTableLaunch bold centered rounded stats dataTable no-footer', False)
    for i, _ in enumerate(tables):
        for j in range(0, len(tables[i].find_all('a'))):
            player_name = tables[i].find_all('a')[j].text
            player_projection = 2 - i
            player_dict[player_name] = player_projection
    return player_dict


# Return name and change in rank, sorted high to low
def pl_get_batter_rank_trends():
    weekly_rows = pl_startup('/category/fantasy/hitter-list', 'all', 'tr', 'new-tier', False)
    player_dict = pl_get_trends(weekly_rows)
    sorted_dict = dictionary_sort(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def pl_get_batter_ranks():
    weekly_rows = pl_startup('/category/fantasy/hitter-list', 'all', 'tr', 'new-tier', False)
    player_dict = pl_get_ranks(weekly_rows)
    sorted_dict = dictionary_sort(player_dict)
    return sorted_dict


# Return name and change in rank, sorted high to low
def pl_get_closing_pitcher_rank_trends():
    weekly_rows = pl_startup('/category/fantasy/closing-time/', 'all', 'tr', 'new-tier', False)
    player_dict = pl_get_trends(weekly_rows)
    sorted_dict = dictionary_sort(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def pl_get_closing_pitcher_ranks():
    weekly_rows = pl_startup('/category/fantasy/closing-time/', 'all', 'tr', 'new-tier', False)
    player_dict = pl_get_ranks(weekly_rows)
    sorted_dict = dictionary_sort(player_dict)
    return sorted_dict


# Return name and change in rank, sorted high to low
def pl_get_relief_pitcher_rank_trends():
    weekly_rows = pl_startup('/category/fantasy/the-hold-up/', 'all', 'tr', 'new-tier', False)
    player_dict = pl_get_trends(weekly_rows)
    sorted_dict = dictionary_sort(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def pl_get_relief_pitcher_ranks():
    weekly_rows = pl_startup('/category/fantasy/the-hold-up/', 'all', 'tr', 'new-tier', False)
    player_dict = pl_get_ranks(weekly_rows)
    sorted_dict = dictionary_sort(player_dict)
    return sorted_dict


# Tests with `pipenv run python src/provider_pitcherlist.py`
if __name__ == '__main__':
    print('\n', 'pl_get_starting_pitcher_rank_trends', '\n', pl_get_starting_pitcher_rank_trends())
    print('\n', 'pl_get_starting_pitcher_ranks', '\n', pl_get_starting_pitcher_ranks())
    print('\n', 'pl_get_streaming_starting_pitcher_ranks', '\n', pl_get_streaming_starting_pitcher_ranks())
    print('\n', 'pl_get_starting_pitcher_matchup_tiers', '\n', pl_get_starting_pitcher_matchup_tiers())
    print('\n', 'pl_get_two_start_starting_pitcher_matchup_tiers', '\n', pl_get_two_start_starting_pitcher_matchup_tiers())
    print('\n', 'pl_get_batter_rank_trends', '\n', pl_get_batter_rank_trends())
    print('\n', 'pl_get_batter_ranks', '\n', pl_get_batter_ranks())
    print('\n', 'pl_get_closing_pitcher_rank_trends', '\n', pl_get_closing_pitcher_rank_trends())
    print('\n', 'pl_get_closing_pitcher_ranks', '\n', pl_get_closing_pitcher_ranks())
    print('\n', 'pl_get_relief_pitcher_rank_trends', '\n', pl_get_relief_pitcher_rank_trends())
    print('\n', 'pl_get_relief_pitcher_ranks', '\n', pl_get_relief_pitcher_ranks())
