from dotenv import load_dotenv, find_dotenv
from os import environ
from flask import Flask, Response, redirect
from yahoo import yahoo_trends
from espn import espn_trends
from cbs import cbs_trends

# Set environment variables from local .env
load_dotenv(find_dotenv())

app = Flask(__name__)

# Disable Flask automatically alphabetizing Player trend dictionaries
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

@app.route("/yahoo")
def yahoo_page():
    if eval(environ.get('ENABLE_YAHOO', True)) == True:
        data = yahoo_trends(7, False) # set `True` later fix
        return data
    else:
        return Response(status = 503)

if __name__ == "__main__":
        app.run()
