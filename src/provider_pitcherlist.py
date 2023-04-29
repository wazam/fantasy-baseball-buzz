import utils.my_beautifulsoup as MyBS
import utils.my_dictionary as MyD
import utils.my_json as MyJ
import utils.my_unidecode as MyU


url_base = "http://www.pitcherlist.com"
player_dict = {}


# Return data from search in current week's article
def startup(url_tab, all, name, attrib, href):
    player_dict.clear()
    url_start_page = url_base + url_tab
    start_page = MyBS.scrape_class(url_start_page, '', 'div', 'hold-me', False)
    url_weekly_page = MyBS.find_class(start_page, '', 'a', 'link', True)['href']
    weekly_page = MyBS.scrape_class(url_weekly_page, all, name, attrib, href)
    return weekly_page


# Return Players' name and rank
def get_ranks(rows):
    for i, _ in enumerate(rows):
        player_name_diacritics = rows[i].a.text
        player_name = MyU.fix_str(player_name_diacritics)
        player_rank = int(rows[i].td.text)
        if player_name not in player_dict:
            player_dict[player_name] = player_rank
        MyJ.add_name_to(player_name, 'player-names')
    return player_dict


# Return Players' name and change in rank
def get_trends(rows):
    for i, _ in enumerate(rows):
        player_name_diacritics = rows[i].a.text
        player_name = MyU.fix_str(player_name_diacritics)
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
        MyJ.add_name_to(player_name, 'player-names')
    return player_dict


# Return name and change in rank, sorted high to low
def get_starting_pitcher_rank_trends():
    weekly_rows = startup('/category/fantasy/the-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_trends(weekly_rows)
    sorted_dict = MyD.sort(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def get_starting_pitcher_ranks():
    weekly_rows = startup('/category/fantasy/the-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_ranks(weekly_rows)
    sorted_dict = MyD.sort_desc(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def get_streaming_starting_pitcher_ranks():
    streamers_page = startup('/category/fantasy/sp-streamers/', '', 'div', 'row article-wrap', False)
    row_streamers = MyBS.find(streamers_page, 'all', 'tr', False)
    for i, _ in enumerate(row_streamers):
        if row_streamers[i].a == None:
            continue
        player_name = MyU.fix_str(row_streamers[i].a.text)
        player_rank = int(row_streamers[i].td.text)
        if player_name not in player_dict:
            player_dict[player_name] = player_rank
        MyJ.add_name_to(player_name, 'player-names')
    sorted_dict = MyD.sort_desc(player_dict)
    return sorted_dict


# Return name (short) and projected matchup(s) tier, combined for all weekly matchups, sorted high to low
def get_starting_pitcher_matchup_tiers():
    matchups_page = startup('/category/fantasy/sit-or-start/', '', 'div', 'row article-wrap', False)
    matchups_row = MyBS.find(matchups_page, 'all', 'tr', False)
    for i, _ in enumerate(matchups_row):
        try:
            player1_name_short = MyU.fix_str(matchups_row[i].find_all('td')[2].text)
            player1_rating = int(matchups_row[i].find_all('td')[3].text.split('-')[1])
            if player1_name_short not in player_dict:
                player_dict[player1_name_short] = player1_rating
            else:
                player1_rating_updated = player_dict[player1_name_short] + player1_rating
                player_dict.update({player1_name_short: player1_rating_updated})
            player2_name_short = MyU.fix_str(matchups_row[i].find_all('td')[4].text)
            player2_rating = int(matchups_row[i].find_all('td')[5].text.split('-')[1])
            if player2_name_short not in player_dict:
                player_dict[player2_name_short] = player2_rating
            else:
                player2_rating_updated = player_dict[player2_name_short] + player2_rating
                player_dict.update({player2_name_short: player2_rating_updated})
        except IndexError:
            continue

        # Get Player's full name from JSON file
        players_json = MyJ.get_json('yahoo-players')
        for key, _ in enumerate(players_json['players']):
            if player1_name_short == players_json['players'][key]['short_name']:
                player1_name_full = players_json['players'][key]['full_name']
            if player2_name_short == players_json['players'][key]['short_name']:
                player2_name_full = players_json['players'][key]['full_name']
            elif key == len(players_json['players']) - 1:
                # No full name found, try scraping more
                break

        MyJ.add_name_to(player1_name_full, 'player-names')
        MyJ.add_name_to(player2_name_full, 'player-names')

    sorted_dict = MyD.sort(player_dict)
    return sorted_dict


# Return name and projected matchups tier
def get_two_start_starting_pitcher_matchup_tiers():
    tables = startup('/category/fantasy/two-start-pitchers/', 'all', 'table', 'dataTableLaunch bold centered rounded stats dataTable no-footer', False)
    for i, _ in enumerate(tables):
        for j in range(0, len(tables[i].find_all('a'))):
            player_name = tables[i].find_all('a')[j].text
            player_projection = 2 - i
            player_dict[player_name] = player_projection
    return player_dict


# Return name and change in rank, sorted high to low
def get_batter_rank_trends():
    weekly_rows = startup('/category/fantasy/hitter-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_trends(weekly_rows)
    sorted_dict = MyD.sort(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def get_batter_ranks():
    weekly_rows = startup('/category/fantasy/hitter-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_ranks(weekly_rows)
    sorted_dict = MyD.sort_desc(player_dict)
    return sorted_dict


# Return name and change in rank, sorted high to low
def get_closing_pitcher_rank_trends():
    weekly_rows = startup('/category/fantasy/closing-time/', 'all', 'tr', 'new-tier', False)
    player_dict = get_trends(weekly_rows)
    sorted_dict = MyD.sort(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def get_closing_pitcher_ranks():
    weekly_rows = startup('/category/fantasy/closing-time/', 'all', 'tr', 'new-tier', False)
    player_dict = get_ranks(weekly_rows)
    sorted_dict = MyD.sort_desc(player_dict)
    return sorted_dict


# Return name and change in rank, sorted high to low
def get_relief_pitcher_rank_trends():
    weekly_rows = startup('/category/fantasy/the-hold-up/', 'all', 'tr', 'new-tier', False)
    player_dict = get_trends(weekly_rows)
    sorted_dict = MyD.sort(player_dict)
    return sorted_dict


# Return name and rank, sorted low to high
def get_relief_pitcher_ranks():
    weekly_rows = startup('/category/fantasy/the-hold-up/', 'all', 'tr', 'new-tier', False)
    player_dict = get_ranks(weekly_rows)
    sorted_dict = MyD.sort_desc(player_dict)
    return sorted_dict


# Used for testing with `pipenv run python src/provider_pitcherlist.py`
if __name__ == '__main__':
    print('\n', 'get_starting_pitcher_rank_trends', '\n', get_starting_pitcher_rank_trends())
    print('\n', 'get_starting_pitcher_ranks', '\n', get_starting_pitcher_ranks())
    print('\n', 'get_streaming_starting_pitcher_ranks', '\n', get_streaming_starting_pitcher_ranks())
    print('\n', 'get_starting_pitcher_matchup_tiers', '\n', get_starting_pitcher_matchup_tiers())
    print('\n', 'get_two_start_starting_pitcher_matchup_tiers', '\n', get_two_start_starting_pitcher_matchup_tiers())
    print('\n', 'get_batter_rank_trends', '\n', get_batter_rank_trends())
    print('\n', 'get_batter_ranks', '\n', get_batter_ranks())
    print('\n', 'get_closing_pitcher_rank_trends', '\n', get_closing_pitcher_rank_trends())
    print('\n', 'get_closing_pitcher_ranks', '\n', get_closing_pitcher_ranks())
    print('\n', 'get_relief_pitcher_rank_trends', '\n', get_relief_pitcher_rank_trends())
    print('\n', 'get_relief_pitcher_ranks', '\n', get_relief_pitcher_ranks())