import os
from flask import Flask, render_template, send_from_directory, redirect
from provider_cbs import cbs_get_added_dropped_trends, cbs_get_viewed_trends, cbs_get_traded_trends
from provider_espn import espn_get_added_dropped_trends, espn_get_player_list, espn_get_rostered_players
from provider_fantasypros import fantasypros_get_player_list
from provider_mlb import mlb_get_player_list
from provider_pitcherlist import pitcherlist_get_starting_pitcher_rank_trends, pitcherlist_get_starting_pitcher_ranks, \
    pitcherlist_get_streaming_starting_pitcher_ranks, pitcherlist_get_starting_pitcher_matchup_tiers, \
    pitcherlist_get_two_start_starting_pitcher_matchup_tiers, pitcherlist_get_batter_rank_trends, \
    pitcherlist_get_batter_ranks, pitcherlist_get_closing_pitcher_rank_trends, pitcherlist_get_closing_pitcher_ranks, \
    pitcherlist_get_relief_pitcher_rank_trends, pitcherlist_get_relief_pitcher_ranks
from provider_yahoo import yahoo_get_added_dropped_trends, yahoo_get_player_list, yahoo_get_player_list_deep

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.json.sort_keys = False
html_404_page = '<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>'


@app.route('/')
def start_page():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/about')
def about_page():
    return redirect('https://github.com/wazam/fantasy-baseball-buzz')


@app.route('/airtable')
def airtable_page():
    url = 'https://airtable.com/' + os.environ.get('AIRTABLE_BASE_ID')
    return redirect(url)


@app.route('/espn/<int:func_id>')
def show_espn(func_id):
    func_list = [espn_get_added_dropped_trends, espn_get_player_list, espn_get_rostered_players]
    if int(func_id) > 0 and int(func_id) <= len(func_list):
        func_name = func_list[func_id-1]
        data = func_name()
    else:
        data = (html_404_page, 404)
    return data


@app.route('/yahoo/<int:func_id>')
def show_yahoo(func_id):
    func_list = [yahoo_get_added_dropped_trends, yahoo_get_player_list, yahoo_get_player_list_deep]
    if int(func_id) > 0 and int(func_id) <= len(func_list):
        func_name = func_list[func_id-1]
        data = func_name()
    else:
        data = (html_404_page, 404)
    return data


@app.route('/cbs/<int:func_id>')
def show_cbs(func_id):
    func_list = [cbs_get_added_dropped_trends, cbs_get_viewed_trends, cbs_get_traded_trends]
    if int(func_id) > 0 and int(func_id) <= len(func_list):
        func_name = func_list[func_id-1]
        data = func_name()
    else:
        data = (html_404_page, 404)
    return data


@app.route('/pitcherlist/<int:func_id>')
def show_pitcherlist(func_id):
    func_list = [pitcherlist_get_starting_pitcher_rank_trends, pitcherlist_get_starting_pitcher_ranks, \
        pitcherlist_get_streaming_starting_pitcher_ranks, pitcherlist_get_starting_pitcher_matchup_tiers, \
        pitcherlist_get_two_start_starting_pitcher_matchup_tiers, pitcherlist_get_batter_rank_trends, \
        pitcherlist_get_batter_ranks, pitcherlist_get_closing_pitcher_rank_trends, \
        pitcherlist_get_closing_pitcher_ranks, pitcherlist_get_relief_pitcher_rank_trends, \
        pitcherlist_get_relief_pitcher_ranks]
    if int(func_id) > 0 and int(func_id) <= len(func_list):
        func_name = func_list[func_id-1]
        # return_func = getattr(provider_pitcherlist, func_name)
        # data = return_func()
        data = func_name()
    else:
        data = (html_404_page, 404)
    return data


@app.route('/mlb_1')
def mlb_1():
    mlb_get_player_list()
    return


@app.route('/fantasypros_1')
def fantasypros_1():
    fantasypros_get_player_list()
    return


# Tests with `pipenv run flask run` or `pipenv run python src/main.py`
if __name__ == '__main__':
    app.run()
