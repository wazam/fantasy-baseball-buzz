import unidecode

import util.my_beautifulsoup as MyBS
import util.my_dictionary as MyD


url_base = 'http://www.pitcherlist.com'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
player_dict = {}
sorted_dict = {}


def startup(url_tab, all, name, attrib, href):
    player_dict.clear()
    sorted_dict.clear()
    url_start_page = url_base + url_tab
    start_page = MyBS.scrape_class(url_start_page, headers, '', 'div', 'hold-me', False)
    url_weekly_page = MyBS.find_class(start_page, '', 'a', 'link', True)['href']    
    weekly_page_rows = MyBS.scrape_class(url_weekly_page, headers, all, name, attrib, href)
    return weekly_page_rows


def get_ranks(rows):
    for i, r in enumerate(rows):
        player_name_diacritics = rows[i].a.text
        player_name = unidecode.unidecode(player_name_diacritics)
        player_rank = int(rows[i].td.text)
        if player_name not in player_dict:
            player_dict[player_name] = player_rank
    return player_dict


def get_trends(rows):
    for i, r in enumerate(rows):
        player_name_diacritics = rows[i].a.text
        player_name = unidecode.unidecode(player_name_diacritics)
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


def get_pitcher_trends():
    weekly_rows = startup('/category/fantasy/the-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_trends(weekly_rows)
    sorted_dict = MyD.sort(player_dict, True)
    return sorted_dict


def get_pitcher_ranks():
    weekly_rows = startup('/category/fantasy/the-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_ranks(weekly_rows)
    sorted_dict = MyD.sort(player_dict, False)
    return sorted_dict


def get_pitcher_streamers():
    streamers_page = startup('/category/fantasy/sp-streamers/', '', 'div', 'row article-wrap', False)
    row_streamers = MyBS.find(streamers_page, 'all', 'tr', False)
    for index, row in enumerate(row_streamers):
        if row_streamers[index].a == None:
            continue
        player_name_diacritics = row_streamers[index].a.text
        player_name = unidecode.unidecode(player_name_diacritics)
        player_rank = int(row_streamers[index].td.text)
        if player_name not in player_dict:
            player_dict[player_name] = player_rank
    dict_sort = MyD.sort(player_dict, False)
    return dict_sort


def get_batter_trends():
    weekly_rows = startup('/category/fantasy/hitter-list', 'all', 'tr', 'new-tier', False)
    player_dict =  get_trends(weekly_rows)
    sorted_dict = MyD.sort(player_dict, True)
    return sorted_dict


def get_batter_ranks():
    weekly_rows = startup('/category/fantasy/hitter-list', 'all', 'tr', 'new-tier', False)
    player_dict = get_ranks(weekly_rows)
    sorted_dict = MyD.sort(player_dict, False)
    return sorted_dict


# ```python src/pitcherlist.py```
if __name__ == '__main__':
    print(get_pitcher_trends())
    print(get_pitcher_ranks())
    print(get_pitcher_streamers())
    print(get_batter_trends())
    print(get_batter_ranks())
