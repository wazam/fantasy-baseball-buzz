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
    if eval(environ.get('ENABLE_CBS', True)) == True:
        data = cbs_trends()
        return data
    else:
        return Response(status = 503)


@app.route("/espn")
def espn_page():
    if eval(environ.get('ENABLE_ESPN', True)) == True:
        data = espn_trends()
        return data
    else:
        return Response(status = 503)


@app.route("/pitcherlist/pitcher-trends")
def pitcherlist_page_1():
    if eval(environ.get('ENABLE_PITCHERLIST', True)) == True:
        data = pitcherlist.get_pitcher_trends()
        return data
    else:
        return Response(status = 503)

@app.route("/pitcherlist/pitcher-ranks")
def pitcherlist_page_2():
    if eval(environ.get('ENABLE_PITCHERLIST', True)) == True:
        data = pitcherlist.get_pitcher_ranks()
        return data
    else:
        return Response(status = 503)

@app.route("/pitcherlist/pitcher-streamers")
def pitcherlist_page_3():
    if eval(environ.get('ENABLE_PITCHERLIST', True)) == True:
        data = pitcherlist.get_pitcher_streamers()
        return data
    else:
        return Response(status = 503)

@app.route("/pitcherlist/batter-trends")
def pitcherlist_page_4():
    if eval(environ.get('ENABLE_PITCHERLIST', True)) == True:
        data = pitcherlist.get_batter_trends()
        return data
    else:
        return Response(status = 503)

@app.route("/pitcherlist/batter-ranks")
def pitcherlist_page_5():
    if eval(environ.get('ENABLE_PITCHERLIST', True)) == True:
        data = pitcherlist.get_batter_ranks()
        return data
    else:
        return Response(status = 503)


@app.route("/yahoo")
def yahoo_page_1():
    if eval(environ.get('ENABLE_YAHOO', True)) == True:
        data = yahoo_trends(7)
        return data
    else:
        return Response(status = 503)

@app.route("/yahoo/1")
def yahoo_page_2():
    if eval(environ.get('ENABLE_YAHOO', True)) == True:
        data = yahoo_trends(1)
        return data
    else:
        return Response(status = 503)


if __name__ == "__main__":
    app.run()
