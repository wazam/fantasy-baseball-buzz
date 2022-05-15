from dotenv import load_dotenv, find_dotenv
from os import environ
from flask import Flask, Response, redirect

from yahoo import yahoo_trends
from espn import espn_trends
from cbs import cbs_trends
import pitcherlist

load_dotenv(find_dotenv())
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def home_page():
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
