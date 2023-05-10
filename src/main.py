import os
from flask import Flask, render_template, send_from_directory, redirect
from provider_cbs import cbs_get_added_dropped_trends, cbs_get_viewed_trends, cbs_get_traded_trends
from provider_espn import espn_get_added_dropped_trends, espn_get_player_list, espn_get_rostered_players
from provider_fantasypros import fantasypros_get_player_list
from provider_mlb import mlb_get_player_list
from provider_pitcherlist import pitcherlist_get_starting_pitcher_rank_trends, pitcherlist_get_starting_pitcher_ranks, \
    pitcherlist_get_streaming_starting_pitcher_ranks, pitcherlist_get_starting_pitcher_matchup_tiers, \
    pitcherlist_get_two_start_starting_pitcher_matchup_tiers, pitcherlist_get_batter_rank_trends, pitcherlist_get_batter_ranks, \
    pitcherlist_get_closing_pitcher_rank_trends, pitcherlist_get_closing_pitcher_ranks, pitcherlist_get_relief_pitcher_rank_trends, \
    pitcherlist_get_relief_pitcher_ranks
from provider_yahoo import yahoo_get_added_dropped_trends, yahoo_get_player_list, yahoo_get_player_list_deep

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.json.sort_keys = False


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


@app.route('/espn_1')
def espn_1():
    data = espn_get_added_dropped_trends()
    return data
@app.route('/espn_2')
def espn_2():
    espn_get_player_list()
    return
@app.route('/espn_3')
def espn_3():
    espn_get_rostered_players()
    return


@app.route('/yahoo_1')
def yahoo_1():
    data = yahoo_get_added_dropped_trends(7)
    return data
@app.route('/yahoo_2')
def yahoo_2():
    yahoo_get_player_list()
    return
@app.route('/yahoo_3')
def yahoo_3():
    yahoo_get_player_list_deep()
    return


@app.route('/cbs_1')
def cbs_1():
    data = cbs_get_added_dropped_trends()
    return data
@app.route('/cbs_2')
def cbs_2():
    data = cbs_get_viewed_trends()
    return data
@app.route('/cbs_3')
def cbs_3():
    data = cbs_get_traded_trends()
    return data

@app.route('/pitcherlist_1')
def pitcherlist_1():
    data = pitcherlist_get_starting_pitcher_rank_trends()
    return data
@app.route('/pitcherlist_2')
def pitcherlist_2():
    data = pitcherlist_get_streaming_starting_pitcher_ranks()
    return data
@app.route('/pitcherlist_3')
def pitcherlist_3():
    data = pitcherlist_get_starting_pitcher_matchup_tiers()
    return data
@app.route('/pitcherlist_4')
def pitcherlist_4():
    data = pitcherlist_get_two_start_starting_pitcher_matchup_tiers()
    return data
@app.route('/pitcherlist_5')
def pitcherlist_5():
    data = pitcherlist_get_batter_rank_trends()
    return data
@app.route('/pitcherlist_6')
def pitcherlist_6():
    data = pitcherlist_get_batter_ranks()
    return data
@app.route('/pitcherlist_7')
def pitcherlist_7():
    data = pitcherlist_get_closing_pitcher_rank_trends()
    return data
@app.route('/pitcherlist_8')
def pitcherlist_8():
    data = pitcherlist_get_closing_pitcher_ranks()
    return data
@app.route('/pitcherlist_9')
def pitcherlist_9():
    data = pitcherlist_get_relief_pitcher_rank_trends()
    return data
@app.route('/pitcherlist_10')
def pitcherlist_10():
    data = pitcherlist_get_relief_pitcher_ranks()
    return data
@app.route('/pitcherlist_11')
def pitcherlist_11():
    data = pitcherlist_get_starting_pitcher_ranks()
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
