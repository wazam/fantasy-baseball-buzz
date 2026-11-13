from datetime import date

import config

# Fantrax league ID from the league's URL; Fantrax only serves player stats within a league. Empty when it's
# not set. config.check_settings() checks its shape at startup, before anything uses it
FANTRAX_LEAGUE_ID = config.setting('FANTRAX_LEAGUE_ID') or ''

# Latest MLB season with stats, rolling over each March when spring training starts
SEASON = date.today().year if date.today().month >= 3 else date.today().year - 1

# Each source's 'source' is its ID (Index page anchors, trend URLs, label prefixes and its Id_ column), and
# an optional 'name' replaces it on the Index page. Each trend has a key (favorites, the run log and results file
# names use it, so keep it stable), a name shown on the Index page, and labels: the players table columns it
# fills, which the page shows without the source name. Add a new trend with no labels, and add them with its
# scraper, since every label adds a column to buzz.db. Labels follow 'Source Metric Format
# Variant Window', as in 'CBS Rank Roto Pos' or 'ESPN Roster % Chg 7D', using these words:
#   Metric:  Pts, Rank, ADP, AAV, Roster %, Active %, Draft %, Inj, Value
#   Format:  Pts (points leagues), Roto, H2H (head-to-head categories)
#   Variant: Pos, Chg, Min, Max, Picks
#   Window:  Today, 7D, 15D, 30D, Season, Proj, Next 7D, 7D Ago
# Renaming a label adds a new column and leaves the old one in buzz.db, so after a rename, rebuild the
# database from saved results (the README's Your Data section).
#
# Adding a source (src/source_mlb.py is the shortest example):
#   1. Add it and its trends here. Add each numeric label to NUMERIC_LABELS.
#   2. Write src/source_<name>.py with <name>_get(trend_type) and a SUPPORTED_TRENDS set. Fetch with
#      ratelimit_get_url() or ratelimit_post_url() from util_beautifulsoup.py, and pass each trend's players
#      to save_and_import() from db.py. For a list players drop off, such as injuries, also call
#      clear_stale_values(), so a player who's no longer listed doesn't keep old values.
#   3. Register it in SOURCE_HANDLERS and SUPPORTED_TRENDS in main.py.
#   4. Add it to SOURCE_NAMES in db.py, which gives it an Id_ column and names its results files.
#   5. The five fantasy platforms (ESPN, Yahoo, CBS, Fantrax, NFBC) have a color in style-dark.css and
#      style-light.css; other sources show in grey.
#   6. Its runs write to data/buzz.db, so back up the data folder before testing it.
SOURCES = [
    {
        "source": "ESPN",
        "trends": [
            {
                "key": "players",
                "name": "Players",
                "url": "https://fantasy.espn.com/baseball/leaders?view=trending&statSplit=currSeason&scoringPeriodId=0&lineupSlot=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C19",
                "is_favorite": True,
                "run_frequency": "daily",
                "labels": [
                    "ESPN Pts 7D",
                    "ESPN Pts 15D",
                    "ESPN Pts 30D",
                    "ESPN Pts Season",
                    "ESPN Rank Pos",
                    "ESPN ADP",
                    "ESPN Roster %",
                    "ESPN Roster % Chg 7D",
                    "ESPN Roster % 7D Ago"
                ]
            },
            {
                "key": "stats",
                "name": "Stats",
                "url": "https://fantasy.espn.com/baseball/leaders?view=stats",
                "run_frequency": "daily",
                "labels": [
                    "ESPN Pts Today"
                ]
            },
            {
                "key": "schedule",
                "name": "Schedule",
                "url": "https://fantasy.espn.com/baseball/leaders?view=schedule",
                "run_frequency": "weekly",
                "labels": [
                    "ESPN Games Next 7D"
                ]
            },
            {
                "key": "news",
                "name": "News",
                "url": "https://fantasy.espn.com/baseball/leaders?view=news",
                "run_frequency": "weekly",
                "labels": [
                    "ESPN News",
                    "ESPN News Spin"
                ]
            },
            {
                "key": "projections",
                "name": "Projections",
                "url": "https://fantasy.espn.com/baseball/players/projections?leagueFormatId=2",
                "run_frequency": "once",
                "labels": [
                    "ESPN Rank Proj",
                    "ESPN Roster %",
                    "ESPN Roster % Chg 7D",
                    "ESPN Pts Proj",
                    "ESPN Pts/G Proj"
                ]
            },
            {
                "key": "outlooks",
                "name": "Outlooks",
                "url": "https://fantasy.espn.com/baseball/players/projections?leagueFormatId=2",
                "run_frequency": "once",
                "labels": [
                    "ESPN Rank Proj",
                    "ESPN Pts Last Season",
                    "ESPN Pts Proj",
                    "ESPN Outlook"
                ]
            },
            {
                "key": "undroppables",
                "name": "Undroppables",
                "url": "https://fantasy.espn.com/baseball/players/undroppables",
                "run_frequency": "once",
                "labels": [
                    "ESPN Undroppable"
                ]
            },
            {
                "key": "draft",
                "name": "Draft Results",
                "url": "https://fantasy.espn.com/baseball/livedraftresults",
                "run_frequency": "once",
                "labels": [
                    "ESPN ADP",
                    "ESPN ADP Chg 7D",
                    "ESPN AAV",
                    "ESPN AAV Chg 7D",
                    "ESPN Roster %"
                ]
            },
            {
                "key": "player-rater",
                "name": "Player Rater",
                "url": "https://fantasy.espn.com/baseball/playerrater",
                "run_frequency": "weekly",
                "labels": [
                    "ESPN Roster %",
                    "ESPN Rating"
                ]
            },
            {
                "key": "rankings-pts",
                "name": "Points Rankings",
                # ESPN publishes these rankings as a new article (new ID) each season, update yearly
                "url": "https://www.espn.com/fantasy/baseball/story/_/id/35437997/fantasy-baseball-rankings-points-leagues-2025-espn-cockcroft",
                "run_frequency": "weekly",
                "labels": [
                    "ESPN Rank Pts",
                    "ESPN Rank Pts Chg",
                    "ESPN Value Pts 10T",
                    "ESPN Value Pts 12T",
                    "ESPN Rank Pts Pos",
                    "ESPN Age"
                ]
            },
            {
                "key": "rankings-roto",
                "name": "Roto Rankings",
                # ESPN publishes these rankings as a new article (new ID) each season, update yearly.
                # They cover head-to-head categories and rotisserie leagues
                "url": "https://www.espn.com/fantasy/baseball/story/_/id/35438162/fantasy-baseball-rankings-head-head-rotisserie-leagues-2025-espn-karabell",
                "run_frequency": "weekly",
                "labels": [
                    "ESPN Rank Roto",
                    "ESPN Rank Roto Chg",
                    "ESPN Value Roto 10T",
                    "ESPN Value Roto 12T",
                    "ESPN Rank Roto Pos",
                    "ESPN Age"
                ]
            },
            {
                "key": "closer-chart",
                "name": "Closer Chart",
                "url": "https://www.espn.com/fantasy/baseball/flb/story?page=REcloserorgchart",
                "run_frequency": "weekly",
                "labels": [
                    "ESPN Bullpen Role"
                ]
            },
            {
                "key": "depth-charts",
                "name": "Depth Charts",
                "url": "https://www.espn.com/mlb/story/_/id/29473590/current-mlb-depth-charts-all-30-teams",
                "run_frequency": "weekly",
                "labels": []
            }
        ]
    },
    {
        "source": "Yahoo",
        "trends": [
            {
                "key": "buzz-index",
                "name": "Buzz Index",
                "url": "https://baseball.fantasysports.yahoo.com/b1/buzzindex",
                "is_favorite": True,
                "run_frequency": "daily",
                "labels": [
                    "Yahoo Roster %",
                    "Yahoo Active %",
                    "Yahoo Adds Today",
                    "Yahoo Drops Today",
                    "Yahoo Trades Today"
                ]
            },
            {
                "key": "buzz-index-7d",
                "name": "Buzz Index (7 Days)",
                "url": "https://baseball.fantasysports.yahoo.com/b1/buzzindex",
                "run_frequency": "daily",
                "labels": [
                    "Yahoo Adds 7D",
                    "Yahoo Drops 7D",
                    "Yahoo Trades 7D"
                ]
            },
            {
                "key": "whos-hot",
                "name": "Who's Hot",
                "url": "https://baseball.fantasysports.yahoo.com/b1/whoshot",
                "run_frequency": "weekly",
                "labels": [
                    "Yahoo Rank Hot"
                ]
            },
            {
                "key": "mvps",
                "name": "MVPs",
                "url": "https://baseball.fantasysports.yahoo.com/b1/keystosuccess",
                "run_frequency": "weekly",
                "labels": [
                    "Yahoo MVP % H2H",
                    "Yahoo MVP % Roto"
                ]
            },
            {
                "key": "injuries",
                "name": "Injuries",
                "url": "https://baseball.fantasysports.yahoo.com/b1/injuries",
                "run_frequency": "weekly",
                "labels": [
                    "Yahoo Inj Status",
                    "Yahoo Inj Type"
                ]
            },
            {
                "key": "matchup-ratings",
                "name": "Matchup Ratings",
                "url": "https://baseball.fantasysports.yahoo.com/b1/playermatchups",
                "run_frequency": "daily",
                "labels": [
                    "Yahoo Matchup Rating",
                    "Yahoo Matchup Opp"
                ]
            },
            {
                "key": "adp",
                "name": "Draft Analysis",
                # The page builds its table in the browser (window.bootstrapFantasyStatTable, with columns
                # percentDrafted, preseasonAdp, adp and adpLast7) from an API it doesn't name, so find that
                # request in the browser's network tab once Yahoo's pages are back for the season
                "url": "https://baseball.fantasysports.yahoo.com/b1/draftanalysis",
                "run_frequency": "once",
                "labels": []
            }
        ]
    },
    {
        "source": "CBS",
        # source_cbs.py reads the 'most-*' tables one column per label, in order, so keep those lists
        # matching their tables. CBS's H2H rankings and ADP are for points leagues, so they're labeled Pts
        "trends": [
            {
                "key": "team-stats",
                "name": "Team Stats",
                "url": "https://www.cbssports.com/mlb/teams/",
                "run_frequency": "weekly",
                "labels": []
            },
            {
                "key": "most-added",
                "name": "Most Added",
                "url": "https://www.cbssports.com/fantasy/baseball/trends/added/",
                "is_favorite": True,
                "run_frequency": "daily",
                "labels": [
                    "CBS Roster % 7D Ago",
                    "CBS Roster %",
                    "CBS Roster % Chg 7D"
                ]
            },
            {
                "key": "most-dropped",
                "name": "Most Dropped",
                "url": "https://www.cbssports.com/fantasy/baseball/trends/dropped/",
                "run_frequency": "daily",
                "labels": [
                    "CBS Roster % 7D Ago",
                    "CBS Roster %",
                    "CBS Roster % Chg 7D"
                ]
            },
            {
                "key": "most-viewed",
                "name": "Most Viewed",
                "url": "https://www.cbssports.com/fantasy/baseball/trends/viewed/",
                "run_frequency": "daily",
                "labels": [
                    "CBS Views Recent",
                    "CBS Views Today"
                ]
            },
            {
                "key": "most-traded",
                "name": "Most Traded",
                "url": "https://www.cbssports.com/fantasy/baseball/trends/traded/",
                "run_frequency": "daily",
                "labels": [
                    "CBS Trades Today"
                ]
            },
            {
                "key": "draft",
                "name": "ADP",
                "url": "https://www.cbssports.com/fantasy/baseball/draft/averages/",
                "run_frequency": "once",
                "labels": [
                    "CBS ADP Pts",
                    "CBS ADP Pts Chg",
                    "CBS ADP Pts Min",
                    "CBS ADP Pts Max",
                    "CBS Draft % Pts",
                    "CBS ADP Roto",
                    "CBS ADP Roto Chg",
                    "CBS ADP Roto Min",
                    "CBS ADP Roto Max",
                    "CBS Draft % Roto"
                ]
            },
            {
                "key": "rankings",
                "name": "Rankings",
                "url": "https://www.cbssports.com/fantasy/baseball/rankings/",
                "run_frequency": "weekly",
                "labels": [
                    "CBS Rank Roto",
                    "CBS Rank Roto Pos",
                    "CBS Rank Pts",
                    "CBS Rank Pts Pos"
                ]
            },
            {
                "key": "depth-chart",
                "name": "Depth Chart",
                "url": "https://www.cbssports.com/fantasy/baseball/depth-chart/",
                "run_frequency": "weekly",
                "labels": [
                    "CBS Depth"
                ]
            },
            {
                "key": "bios",
                "name": "Player Bios",
                "url": "https://www.cbssports.com/mlb/players/",
                "run_frequency": "weekly",
                "labels": [
                    "CBS Jersey #",
                    "CBS Bats",
                    "CBS Throws",
                    "CBS Height",
                    "CBS Weight",
                    "CBS DOB",
                    "CBS Age",
                    "CBS MLB Yrs"
                ]
            },
            {
                "key": "batting-stats",
                "name": "Batting Stats",
                "url": "https://www.cbssports.com/mlb/stats/player/batting/mlb/regular/all-pos/all/",
                "run_frequency": "weekly",
                "labels": []
            },
            {
                "key": "fantasy-stats",
                "name": "Fantasy Stats",
                "url": "https://www.cbssports.com/fantasy/baseball/stats/",
                "run_frequency": "weekly",
                "labels": []
            },
            {
                "key": "injuries",
                "name": "Injuries",
                "url": "https://www.cbssports.com/mlb/injuries/",
                "run_frequency": "weekly",
                "labels": [
                    "CBS Inj Status",
                    "CBS Inj Type",
                    "CBS Inj Return",
                    "CBS Inj Updated"
                ]
            },
            {
                "key": "two-start-pitchers",
                "name": "Two-Start Pitchers",
                "url": "https://www.cbssports.com/fantasy/baseball/two-start-pitchers/",
                "run_frequency": "weekly",
                "labels": []
            },
            {
                "key": "probable-pitchers",
                "name": "Probable Pitchers",
                "url": "https://www.cbssports.com/fantasy/baseball/probable-pitchers/",
                "run_frequency": "daily",
                "labels": []
            }
        ]
    },
    {
        "source": "Fantrax",
        "trends": [
            {
                "key": "players",
                "name": "Players",
                "url": f"https://www.fantrax.com/fantasy/league/{FANTRAX_LEAGUE_ID}/players;view=OVERVIEW;positionOrGroup=ALL;miscDisplayType=1;maxResultsPerPage=100;pageNumber=1",
                "is_favorite": True,
                "run_frequency": "daily",
                "labels": [
                    "Fantrax Rank Pts",
                    "Fantrax Pts Season",
                    "Fantrax Pts/G",
                    "Fantrax Draft %",
                    "Fantrax ADP",
                    "Fantrax Roster %",
                    "Fantrax Roster % Chg 7D",
                    "Fantrax Active %",
                    "Fantrax Active % Chg 7D",
                    "Fantrax Roster % 7D Ago",
                    "Fantrax Active % 7D Ago"
                ]
            }
        ]
    },
    {
        "source": "NFBC",
        "trends": [
            {
                "key": "players",
                "name": "Players",
                # Scrapes the "NFBC - Points" table
                "url": "https://nfc.shgn.com/players/baseball",
                "is_favorite": True,
                "run_frequency": "daily",
                "labels": [
                    "NFBC Roster %",
                    "NFBC Active %",
                    "NFBC Pts Season",
                    "NFBC Pts/G"
                ]
            },
            {
                "key": "draft",
                "name": "ADP",
                "url": "https://nfc.shgn.com/adp/baseball",
                "run_frequency": "once",
                "labels": [
                    "NFBC ADP",
                    "NFBC ADP Min",
                    "NFBC ADP Max",
                    "NFBC ADP Picks"
                ]
            },
            {
                "key": "auction",
                "name": "AAV",
                "url": "https://nfc.shgn.com/aav/baseball",
                "run_frequency": "once",
                "labels": [
                    "NFBC AAV",
                    "NFBC AAV Min",
                    "NFBC AAV Max",
                    "NFBC AAV Picks"
                ]
            },
            {
                "key": "injuries",
                "name": "Injuries",
                "url": "https://nfc.shgn.com/sportinjuries/baseball",
                "run_frequency": "weekly",
                "labels": [
                    "NFBC Inj Status",
                    "NFBC Inj Type",
                    "NFBC Inj Return",
                    "NFBC Inj Note"
                ]
            }
        ]
    },
    {
        "source": "FantasyPros",
        "trends": [
            {
                "key": "most-added-dropped",
                "name": "Most Added and Dropped",
                "url": "https://www.fantasypros.com/mlb/most-added-dropped.php",
                "run_frequency": "daily",
                "labels": []
            },
            {
                "key": "rankings",
                "name": "Expert Consensus Rankings",
                "url": "https://www.fantasypros.com/mlb/rankings/overall.php",
                "run_frequency": "weekly",
                "labels": []
            },
            {
                "key": "rankings-ros",
                "name": "Rest of Season Rankings",
                "url": "https://www.fantasypros.com/mlb/rankings/ros-overall.php",
                "run_frequency": "weekly",
                "labels": []
            },
            {
                "key": "adp",
                "name": "ADP",
                "url": "https://www.fantasypros.com/mlb/adp/overall.php",
                "run_frequency": "once",
                "labels": []
            }
        ]
    },
    {
        "source": "Fleaflicker",
        "trends": [
            {
                "key": "most-added-dropped",
                "name": "Most Added and Dropped",
                "url": "https://www.fleaflicker.com/mlb/most-added-dropped?statType=0&countDuration=WEEK",
                "run_frequency": "daily",
                "labels": []
            }
        ]
    },
    {
        "source": "FBThinkTank",
        "name": "FB Think Tank",
        "trends": [
            {
                "key": "roster-trends",
                "name": "Roster Trends",
                "url": "https://www.fbthinktank.com/roster-trends",
                "run_frequency": "daily",
                "labels": []
            }
        ]
    },
    {
        "source": "LineupExperts",
        # Its pages answer automated requests with 403 (checked 2026-11-04), so its trends may need smarter
        # scraping, or may come off the Index page and stay links only (ROADMAP, In Development 5 and 13)
        "trends": [
            {
                "key": "added-dropped",
                "name": "Added and Dropped",
                "url": "https://www.lineupexperts.com/baseball/added_dropped",
                "run_frequency": "daily",
                "labels": []
            }
        ]
    },
    {
        "source": "FantasySP",
        # Its pages answer automated requests with 403 (checked 2026-11-04), so its trends may need smarter
        # scraping, or may come off the Index page and stay links only (ROADMAP, In Development 5 and 13)
        "trends": [
            {
                "key": "waiver-wire",
                "name": "Waiver Wire",
                "url": "https://www.fantasysp.com/waiver-wire/baseball",
                "run_frequency": "daily",
                "labels": []
            },
            {
                "key": "trade-values",
                "name": "Trade Value Chart",
                "url": "https://www.fantasysp.com/trade-value-chart/mlb",
                "run_frequency": "weekly",
                "labels": []
            }
        ]
    },
    {
        "source": "Razzball",
        "trends": [
            {
                "key": "player-rater",
                "name": "Player Rater",
                "url": "https://razzball.com/playerrater/",
                "run_frequency": "weekly",
                "labels": []
            }
        ]
    },
    {
        "source": "RTSports",
        "name": "RT Sports",
        "trends": [
            {
                "key": "adp",
                "name": "ADP",
                # A PDF report of RT Sports' roto 5x5 drafts
                "url": "https://www.rtsports.com/baseball/baseball-pdf-adp.php",
                "run_frequency": "once",
                "labels": []
            }
        ]
    },
    {
        "source": "FanGraphs",
        "trends": [
            {
                "key": "projections",
                "name": "Projections",
                "url": "https://www.fangraphs.com/projections",
                "run_frequency": "weekly",
                "labels": []
            }
        ]
    },
    {
        "source": "RotoWire",
        "trends": [
            {
                "key": "rankings",
                "name": "Rankings",
                "url": "https://www.rotowire.com/baseball/rankings.php",
                "run_frequency": "weekly",
                "labels": []
            }
        ]
    },
    {
        "source": "RotoChamp",
        "trends": [
            {
                "key": "rankings",
                "name": "Rankings",
                "url": "https://www.rotochamp.com/Baseball/PlayerRankings.aspx",
                "run_frequency": "once",
                "labels": []
            }
        ]
    },
    {
        "source": "RotoBaller",
        "trends": [
            {
                "key": "rankings",
                "name": "Rankings",
                "url": "https://www.rotoballer.com/fantasy-baseball-rankings/440514",
                "run_frequency": "weekly",
                "labels": []
            }
        ]
    },
    {
        "source": "BaseballReference",
        "name": "Baseball-Reference",
        "trends": [
            {
                "key": "batting-stats",
                "name": "Batting Stats",
                "url": f"https://www.baseball-reference.com/leagues/majors/{SEASON}-standard-batting.shtml",
                "run_frequency": "weekly",
                "labels": []
            },
            {
                "key": "pitching-stats",
                "name": "Pitching Stats",
                "url": f"https://www.baseball-reference.com/leagues/majors/{SEASON}-standard-pitching.shtml",
                "run_frequency": "weekly",
                "labels": []
            }
        ]
    },
    {
        "source": "MLB",
        "trends": [
            {
                "key": "players",
                "name": "Players",
                # Read from MLB's Stats API, which mlb.com's player pages are built from
                "url": "https://www.mlb.com/players",
                "run_frequency": "weekly",
                "labels": [
                    "MLB Age",
                    "MLB Bats",
                    "MLB Throws",
                    "MLB Debut"
                ]
            }
        ]
    }
]

# Labels a scraper fills with numbers. They're stored as numbers so they sort numerically, and get
# number filters in the players table; add a label here once its scraper writes numbers
NUMERIC_LABELS = {
    "ESPN Pts 7D",
    "ESPN Pts 15D",
    "ESPN Pts 30D",
    "ESPN Pts Season",
    "ESPN ADP",
    "ESPN Roster %",
    "ESPN Roster % Chg 7D",
    "ESPN Roster % 7D Ago",
    "Yahoo Roster %",
    "Yahoo Active %",
    "Yahoo Adds Today",
    "Yahoo Drops Today",
    "Yahoo Trades Today",
    "Yahoo Adds 7D",
    "Yahoo Drops 7D",
    "Yahoo Trades 7D",
    "Yahoo Rank Hot",
    "Yahoo MVP % H2H",
    "Yahoo MVP % Roto",
    "Yahoo Matchup Rating",
    "CBS Roster % 7D Ago",
    "CBS Roster %",
    "CBS Roster % Chg 7D",
    "CBS Views Recent",
    "CBS Views Today",
    "CBS Trades Today",
    "Fantrax Rank Pts",
    "Fantrax Pts Season",
    "Fantrax Pts/G",
    "Fantrax Draft %",
    "Fantrax ADP",
    "Fantrax Roster %",
    "Fantrax Roster % Chg 7D",
    "Fantrax Active %",
    "Fantrax Active % Chg 7D",
    "Fantrax Roster % 7D Ago",
    "Fantrax Active % 7D Ago",
    "NFBC Roster %",
    "NFBC Active %",
    "NFBC Pts Season",
    "NFBC Pts/G",
    "NFBC ADP",
    "NFBC ADP Min",
    "NFBC ADP Max",
    "NFBC ADP Picks",
    "NFBC AAV",
    "NFBC AAV Min",
    "NFBC AAV Max",
    "NFBC AAV Picks",
    "MLB Age",
}

# Values a source sends when it has no number for a player. Imports store them as empty, so they don't
# sort and filter as real numbers: ESPN gives every undrafted player an ADP of 260 (0 if the field is
# missing), and Fantrax shows a dash, which parse_number reads as 0. A real ADP is never below 1
PLACEHOLDER_VALUES = {
    "ESPN ADP": {0, 260},
    "Fantrax ADP": {0},
}
