import os
from flask import Flask, render_template, send_from_directory, redirect
from provider_cbs import cbs_get_added_dropped_trends, cbs_get_viewed_trends, cbs_get_traded_trends
from provider_espn import espn_get_added_dropped_trends
from provider_pitcherlist import pl_get_starting_pitcher_rank_trends, pl_get_starting_pitcher_ranks, \
    pl_get_streaming_starting_pitcher_ranks, pl_get_starting_pitcher_matchup_tiers, pl_get_two_start_starting_pitcher_matchup_tiers, \
    pl_get_batter_rank_trends, pl_get_batter_ranks, pl_get_closing_pitcher_rank_trends, pl_get_closing_pitcher_ranks, \
    pl_get_relief_pitcher_rank_trends, pl_get_relief_pitcher_ranks
from provider_yahoo import yahoo_get_added_dropped_trends
from util_combine import combined_get_names, combined_get_trend

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


# Takes 2m 50s to fully run
@app.route('/combined')
def combined_page():
    return render_template('combined.html', \
        apiPlayers=combined_get_names(), \
        apiTrends01=combined_get_trend(espn_get_added_dropped_trends()), \
        apiTrends02=combined_get_trend(cbs_get_added_dropped_trends()), \
        apiTrends03=combined_get_trend(yahoo_get_added_dropped_trends(7)), \
        apiTrends04=combined_get_trend(yahoo_get_added_dropped_trends(1)), \
        apiTrends05=combined_get_trend(cbs_get_viewed_trends()), \
        apiTrends06=combined_get_trend(cbs_get_traded_trends()), \
        apiTrends07=combined_get_trend(pl_get_starting_pitcher_rank_trends()), \
        apiTrends08=combined_get_trend(pl_get_starting_pitcher_ranks()), \
        apiTrends09=combined_get_trend(pl_get_streaming_starting_pitcher_ranks()), \
        apiTrends10=combined_get_trend(pl_get_starting_pitcher_matchup_tiers()), \
        apiTrends11=combined_get_trend(pl_get_two_start_starting_pitcher_matchup_tiers()), \
        apiTrends12=combined_get_trend(pl_get_batter_rank_trends()), \
        apiTrends13=combined_get_trend(pl_get_batter_ranks()), \
        apiTrends14=combined_get_trend(pl_get_closing_pitcher_rank_trends()), \
        apiTrends15=combined_get_trend(pl_get_closing_pitcher_ranks()), \
        apiTrends16=combined_get_trend(pl_get_relief_pitcher_rank_trends()), \
        apiTrends17=combined_get_trend(pl_get_relief_pitcher_ranks()))


@app.route('/cbs')
def cbs_page_1():
    return cbs_get_added_dropped_trends()


@app.route('/espn')
def espn_page_1():
    return espn_get_added_dropped_trends()


@app.route('/pitcherlist')
def pitcherlist_page():
    return pl_get_starting_pitcher_ranks()


@app.route('/yahoo')
def yahoo_page():
    return yahoo_get_added_dropped_trends(7)


# Tests with `pipenv run flask run` or `pipenv run python src/main.py`
if __name__ == '__main__':
    app.run()
