import os
from flask import Flask, render_template, send_from_directory, redirect

import provider_pitcherlist as pitcherlist
import provider_yahoo as yahoo
import provider_espn as espn
import provider_cbs as cbs

import combined as MyC


app = Flask(__name__, template_folder='../templates', static_url_path='/static', static_folder='../static')
app.json.sort_keys = False  # app.config['JSON_SORT_KEYS'] = False  # deprecated


@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/about')
def about_page():
    return redirect("http://github.com/wazam/fantasy-baseball-buzz")


# Takes 2m 50s to fully run
@app.route('/combined')
def combined_page():
    return render_template('combined.html', \
        apiPlayers=MyC.get_names(), \
        apiTrends01=MyC.get_trend(espn.get_added_dropped_trends()), \
        apiTrends02=MyC.get_trend(cbs.get_added_dropped_trends()), \
        apiTrends03=MyC.get_trend(yahoo.get_added_dropped_trends(7)), \
        apiTrends04=MyC.get_trend(yahoo.get_added_dropped_trends(1)), \
        apiTrends05=MyC.get_trend(cbs.get_viewed_trends()), \
        apiTrends06=MyC.get_trend(cbs.get_traded_trends()), \
        apiTrends07=MyC.get_trend(pitcherlist.get_starting_pitcher_rank_trends()), \
        apiTrends08=MyC.get_trend(pitcherlist.get_starting_pitcher_ranks()), \
        apiTrends09=MyC.get_trend(pitcherlist.get_streaming_starting_pitcher_ranks()), \
        apiTrends10=MyC.get_trend(pitcherlist.get_starting_pitcher_matchup_tiers()), \
        apiTrends11=MyC.get_trend(pitcherlist.get_two_start_starting_pitcher_matchup_tiers()), \
        apiTrends12=MyC.get_trend(pitcherlist.get_batter_rank_trends()), \
        apiTrends13=MyC.get_trend(pitcherlist.get_batter_ranks()), \
        apiTrends14=MyC.get_trend(pitcherlist.get_closing_pitcher_rank_trends()), \
        apiTrends15=MyC.get_trend(pitcherlist.get_closing_pitcher_ranks()), \
        apiTrends16=MyC.get_trend(pitcherlist.get_relief_pitcher_rank_trends()), \
        apiTrends17=MyC.get_trend(pitcherlist.get_relief_pitcher_ranks()))


@app.route("/cbs/1")
def cbs_page_1():
    data = cbs.get_added_dropped_trends()
    return data

@app.route("/cbs/2")
def cbs_page_2():
    data = cbs.get_viewed_trends()
    return data

@app.route("/cbs/3")
def cbs_page_3():
    data = cbs.get_traded_trends()
    return data


@app.route("/espn/1")
def espn_page_1():
    data = espn.get_added_dropped_trends()
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
    data = yahoo.get_added_dropped_trends(1)
    return data

@app.route("/yahoo/2")
def yahoo_page_2():
    data = yahoo.get_added_dropped_trends(7)
    return data

@app.route("/yahoo/3")
def yahoo_page_3():
    data = yahoo.get_added_dropped_trends(14)
    return data


# Used for testing with `pipenv run flask run`
if __name__ == "__main__":
    app.run()
