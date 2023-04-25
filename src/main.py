import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, send_from_directory, redirect

import src.providers.pitcherlist as pitcherlist

from src.providers.yahoo import yahoo_trends
from src.providers.espn import espn_trends
from src.providers.cbs import cbs_trends


load_dotenv(find_dotenv())
app = Flask(__name__, template_folder='../templates', static_url_path='/static', static_folder='../static')
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/about')
def web_about():
    return redirect("https://github.com/wazam/fantasy-baseball-buzz")


@app.route("/cbs")
def cbs_page():
    data = cbs_trends()
    return data


@app.route("/espn")
def espn_page():
    data = espn_trends()
    return data


@app.route("/pitcherlist/1")
def pitcherlist_page_1():
    data = pitcherlist.get_starting_pitcher_rank_trends()
    return data

@app.route("/pitcherlist/2")
def pitcherlist_page_2():
    data = pitcherlist.get_starting_pitcher_ranks()
    return data

@app.route("/pitcherlist/3")
def pitcherlist_page_3():
    data = pitcherlist.get_streaming_starting_pitcher_ranks()
    return data

@app.route("/pitcherlist/4")
def pitcherlist_page_4():
    data = pitcherlist.get_starting_pitcher_matchup_tiers()
    return data

@app.route("/pitcherlist/5")
def pitcherlist_page_5():
    data = pitcherlist.get_two_start_starting_pitcher_matchup_tiers()
    return data

@app.route("/pitcherlist/6")
def pitcherlist_page_6():
    data = pitcherlist.get_batter_rank_trends()
    return data

@app.route("/pitcherlist/7")
def pitcherlist_page_7():
    data = pitcherlist.get_batter_ranks()
    return data

@app.route("/pitcherlist/8")
def pitcherlist_page_8():
    data = pitcherlist.get_closing_pitcher_rank_trends()
    return data

@app.route("/pitcherlist/9")
def pitcherlist_page_9():
    data = pitcherlist.get_closing_pitcher_ranks()
    return data

@app.route("/pitcherlist/10")
def pitcherlist_page_10():
    data = pitcherlist.get_relief_pitcher_rank_trends()
    return data

@app.route("/pitcherlist/11")
def pitcherlist_page_11():
    data = pitcherlist.get_relief_pitcher_ranks()
    return data


@app.route("/yahoo/1")
def yahoo_page_1():
    data = yahoo_trends(7)
    return data

@app.route("/yahoo/2")
def yahoo_page_2():
    data = yahoo_trends(1)
    return data


if __name__ == "__main__":
    app.run()
