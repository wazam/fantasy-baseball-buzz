import enum
import util.my_beautifulsoup as MyBS
import util.my_dictionary as MyD
import util.my_unidecode as MyU

url_base = 'http://www.pitcherlist.com'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
player_dict = {}


# Return Player data rows from current week's article
def startup(url_tab, all, name, attrib, href):
    player_dict.clear()
    url_start_page = url_base + url_tab
    start_page = MyBS.scrape_class(url_start_page, headers, '', 'div', 'hold-me', False)
    url_weekly_page = MyBS.find_class(start_page, '', 'a', 'link', True)['href']    
    weekly_page_data = MyBS.scrape_class(url_weekly_page, headers, all, name, attrib, href)
    return weekly_page_data


# Return Players' name and rank
def get_ranks(rows):
    for i, _ in enumerate(rows):
        player_name_diacritics = rows[i].a.text
        player_name = MyU.fix_str(player_name_diacritics)
        player_rank = int(rows[i].td.text)
        if player_name not in player_dict:
            player_dict[player_name] = player_rank
    return player_dict


# Return Players' name and change in rank
def get_trends(rows):
    for i, _ in enumerate(rows):
        player_name_diacritics = rows[i].a.text
        player_name = MyU.fix_str(player_name_diacritics)
        player_trend_text = rows[i].find_all('td')[3].text
        if player_trend_text == '-':
            player_trend = 0
        elif player_trend_text == '+UR':
            player_rank = int(rows[i].td.text)
            player_trend = 101 - player_rank
        else:
            player_trend = int(player_trend_text)
        if player_name not in player_dict:
            player_dict[player_name] = player_trend
    return player_dict


# Return sorted Pitchers' name and change in rank
def get_pitcher_trends():
    weekly_rows = startup('/category/fantasy/the-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_trends(weekly_rows)
    sorted_dict = MyD.sort(player_dict)
    return sorted_dict


# Return sorted Pitchers' name and rank
def get_pitcher_ranks():
    weekly_rows = startup('/category/fantasy/the-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_ranks(weekly_rows)
    sorted_dict = MyD.sort_desc(player_dict)
    return sorted_dict


# Return sorted Pitchers' name and rank
def get_pitcher_streamers():
    streamers_page = startup('/category/fantasy/sp-streamers/', '', 'div', 'row article-wrap', False)
    row_streamers = MyBS.find(streamers_page, 'all', 'tr', False)
    for i, _ in enumerate(row_streamers):
        if row_streamers[i].a == None:
            continue
        player_name = MyU.fix_str(row_streamers[i].a.text)
        player_rank = int(row_streamers[i].td.text)
        if player_name not in player_dict:
            player_dict[player_name] = player_rank
    sorted_dict = MyD.sort_desc(player_dict)
    return sorted_dict


# Return sorted Pitchers' name and projected week matchup(s) favor
def get_pitcher_matchups():
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
    sorted_dict = MyD.sort(player_dict)
    return sorted_dict


def get_pitcher_two_starts():
    tables = startup('/category/fantasy/two-start-pitchers/', 'all', 'table', 'dataTableLaunch bold centered rounded stats dataTable no-footer', False)
    for i, _ in enumerate(tables):
        for j in range(0, len(tables[i].find_all('a'))):
            player_name = tables[i].find_all('a')[j].text
            player_projection = 2 - i
            player_dict[player_name] = player_projection
    return player_dict


# Return sorted Batters' name and change in rank
def get_batter_trends():
    weekly_rows = startup('/category/fantasy/hitter-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_trends(weekly_rows)
    sorted_dict = MyD.sort(player_dict)
    return sorted_dict


# Return sorted Batters' name and rank
def get_batter_ranks():
    weekly_rows = startup('/category/fantasy/hitter-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_ranks(weekly_rows)
    sorted_dict = MyD.sort_desc(player_dict)
    return sorted_dict


# ```python src/pitcherlist.py```
if __name__ == '__main__':
    # print(get_pitcher_trends())
    # print(get_pitcher_ranks())
    # print(get_pitcher_streamers())
    #print(get_pitcher_matchups())
    print(get_pitcher_two_starts())
    # print(get_batter_trends())
    # print(get_batter_ranks())
