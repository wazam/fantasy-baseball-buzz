from flask import Flask
from yahoo import yahoo_trends
from espn import espn_trends
from cbs import cbs_trends

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route("/yahoo")
def yahoo_api():
    data = yahoo_trends(7, True)
    return data

@app.route("/espn")
def espn_api():
    data = espn_trends()
    return data

@app.route("/cbs")
def cbs_api():
    data = cbs_trends()
    return data
