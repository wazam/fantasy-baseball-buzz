# [Jamball](https://github.com/wazam/fantasy-baseball-buzz)

Jamball aggregates MLB player trends, statistics, and projections from multiple baseball and fantasy sources to provide you a more in-depth picture of player true values across all parts of the internet. Written in Python.

## Installation

<details><summary><i>Build From Source</i></summary>

1. Install [git](https://git-scm.com/downloads) and [docker-compose](https://docs.docker.com/compose/install/).
2. Clone the repo.

    ```sh
    git clone https://github.com/wazam/fantasy-baseball-buzz.git
    ```

3. Change to the current working directory.

    ```sh
    cd ./fantasy-baseball-buzz
    ```

4. Run the `docker-compose.yml` file to build and run the app.

    ```sh
    docker-compose up -d
    ```

</details><details><summary><i>Docker-compose</i></summary>

```sh
---
version: "3"
services:
  app:
    image: ghcr.io/wazam/fantasy-baseball-buzz:main
    container_name: fantasy-baseball-buzz
    environment:
      - TZ=America/New_York
    ports:
      - "5000:5000"
```

</details>

## Supported Sites

<details><summary><i>ESPN</i></summary>

- [❌ % Rostered](https://fantasy.espn.com/baseball/playerrater)
  - [❌ 1 Day Change in % Rostered](https://fantasy.espn.com/baseball/addeddropped)
  - [✅ 7 Day Change in % Rostered](https://fantasy.espn.com/baseball/addeddropped)
- [❌ ADP](https://fantasy.espn.com/baseball/livedraftresults)
  - [❌ 1 Day Change in ADP](https://fantasy.espn.com/baseball/livedraftresults)
  - [❌ 7 Day Change in ADP](https://fantasy.espn.com/baseball/livedraftresults)
- [❌ Player Ratings](https://fantasy.espn.com/baseball/playerrater)
- [❌ Point Leaders](https://fantasy.espn.com/baseball/leaders?statSplit=currSeason&scoringPeriodId=0)
  - [❌ 7 Day Point Leaders](https://fantasy.espn.com/baseball/leaders?statSplit=currSeason&scoringPeriodId=0)
- [❌ Undroppables](https://fantasy.espn.com/baseball/players/undroppables)
- [❌ Closer Chart](https://www.espn.com/fantasy/baseball/flb/story?page=REcloserorgchart)
- [❌ ROS Points Rankings](https://www.espn.com/fantasy/baseball/story/_/id/33199412)
  - [❌ 7 Day Change in Rank](https://www.espn.com/fantasy/baseball/story/_/id/33199412)
  - [❌ ROS Points Position Rankings](https://www.espn.com/fantasy/baseball/story/_/id/33199412)
- [❌ ROS Category/Rotisserie Rankings](https://www.espn.com/fantasy/baseball/story/_/id/33208450)
- [❌ Daily Matchup Rankings](https://www.google.com/search?q=intitle:%22Fantasy+baseball+pitcher+rankings,+lineup+advice+for%22+intitle:%22Fantasy+baseball+pitcher+rankings,+lineup+advice+for%22+site:www.espn.com&tbs=sbd:1,qdr:m&tbm=nws&filter=0)

</details><details><summary><i>Yahoo! Sports</i></summary>

- [❌ % Rostered](https://baseball.fantasysports.yahoo.com/b1/148799/players)
  - [❌ 1 Day Change in % Rostered](https://baseball.fantasysports.yahoo.com/b1/buzzindex)
  - [❌ 7 Day Change in % Rostered](https://baseball.fantasysports.yahoo.com/b1/buzzindex)
- [✅ 1 Day Change in Roster Adds/Drops](https://baseball.fantasysports.yahoo.com/b1/buzzindex)
  - [✅ 7 Day Change in Roster Adds/Drops](https://baseball.fantasysports.yahoo.com/b1/buzzindex)
- [❌ Can't Cut](https://baseball.fantasysports.yahoo.com/b1/148799/cantcutlist)
- [❌ Who's Hot](https://baseball.fantasysports.yahoo.com/b1/whoshot)
- [❌ H2H MVPs](https://baseball.fantasysports.yahoo.com/b1/keystosuccess?st=head)
- [❌ Roto MVPs](https://baseball.fantasysports.yahoo.com/b1/keystosuccess?st=roto)
- [❌ Point Leader Rankings](https://baseball.fantasysports.yahoo.com/b1/148799/players)
  - [❌ 7 Day Rankings](https://baseball.fantasysports.yahoo.com/b1/148799/players?&sort=AR&sdir=1&status=ALL&pos=B&stat1=S_L7&jsenabled=1)
  - [❌ 14 Day Rankings](https://baseball.fantasysports.yahoo.com/b1/148799/players?&sort=AR&sdir=1&status=ALL&pos=B&stat1=S_L14&jsenabled=1)
  - [❌ 30 Day Rankings](https://baseball.fantasysports.yahoo.com/b1/148799/players?&sort=AR&sdir=1&status=ALL&pos=B&stat1=S_L30&jsenabled=1)
  - [❌ Pre-Season Rankings](https://baseball.fantasysports.yahoo.com/b1/148799/players?status=A&pos=B&cut_type=33&stat1=S_S_2022&myteam=0&sort=OR&sdir=1&pspid=782201687&activity=players_sort_click)

</details><details><summary><i>CBS Sports</i></summary>

- [❌ % Rostered](https://www.cbssports.com/search/baseball/players/)
  - [❌ 1 Day Change in % Rostered](https://www.cbssports.com/fantasy/baseball/trends/added/all/)
  - [✅ 7 Day Change in % Rostered](https://www.cbssports.com/fantasy/baseball/trends/added/all/)
- [❌ % Started](https://www.cbssports.com/search/baseball/players/)
- [❌ Position Ranking](https://www.cbssports.com/search/baseball/players/)
- [❌ Most Viewed](https://www.cbssports.com/fantasy/baseball/trends/viewed/all/)
- [❌ Point Leader Rankings](https://www.cbssports.com/fantasy/baseball/stats/)
  - [❌ 7 Day Rankings](https://www.cbssports.com/fantasy/baseball/stats/U/2022/7d/stats/)
  - [❌ 14 Day Rankings](https://www.cbssports.com/fantasy/baseball/stats/U/2022/14d/stats/)
  - [❌ 28 Day Rankings](https://www.cbssports.com/fantasy/baseball/stats/U/2022/28d/stats/)
- [❌ ROS H2H Rankings](https://www.cbssports.com/fantasy/baseball/rankings/h2h/C/)
- [❌ ROS Roto Rankings](https://www.cbssports.com/fantasy/baseball/rankings/roto/C/)
- [❌ H2H ADP](https://www.cbssports.com/fantasy/baseball/draft/averages/)
- [❌ Roto ADP](https://www.cbssports.com/fantasy/baseball/draft/averages/both/roto/all/)

</details><details><summary><i>Pitcher List</i></summary>

- [✅ ROS Starting Pitcher Rankings](https://www.pitcherlist.com/category/fantasy/the-list/)
  - [✅ 7 Day Change in Rank](https://www.pitcherlist.com/category/fantasy/the-list/)
- [✅ ROS Batter Rankings](https://www.pitcherlist.com/category/fantasy/hitter-list/)
  - [✅ 7 Day Change in Rank](https://www.pitcherlist.com/category/fantasy/hitter-list/)
- [✅ ROS Closing Pitcher Rankings](https://www.pitcherlist.com/category/fantasy/closing-time/)
  - [✅ 7 Day Change in Rank](https://www.pitcherlist.com/category/fantasy/closing-time/)
- [✅ ROS Relief Pitcher Rankings](https://www.pitcherlist.com/category/fantasy/the-hold-up/)
  - [✅ 7 Day Change in Rank](https://www.pitcherlist.com/category/fantasy/the-hold-up/)
- [✅ 7 Day Starting Pitcher Matchup Rankings](https://www.pitcherlist.com/category/fantasy/sit-or-start/)
- [✅ 7 Day 2-Start Pitcher Matchup Rankings](https://www.pitcherlist.com/category/fantasy/two-start-pitchers/)
- [✅ 2 Day Streaming Pitcher Matchup Rankings](https://www.pitcherlist.com/category/fantasy/sp-streamers/)
- [❌ Daily Player Projections](https://www.pitcherlist.com/category/dfs-betting/betting-picks/)
- [❌ Daily Player Projections](https://www.pitcherlist.com/category/fantasy/dfs/)
- [❌ Category Power Rankings](https://www.pitcherlist.com/category/fantasy/category-power-rankings/)
- [❌ Add/Drop Recommendations](https://www.pitcherlist.com/category/fantasy/buy-sell/)

</details><details><summary><i>Fantrax</i></summary>

- [❌ % Rostered](https://www.fantrax.com/login)
  - ❌ 1 Day Change in % Rostered
  - ❌ 7 Day Change in % Rostered
- ❌ % Started
  - ❌ 1 Day Change in % Rostered
  - ❌ 7 Day Change in % Rostered
- ❌ ADP
- ❌ Position Ranking
  - ❌ 7 Day Rankings
  - ❌ 14 Day Rankings
  - ❌ 30 Day Rankings
  - ❌ 60 Day Rankings
- ❌ Point Leader Rankings
  - ❌ 7 Day Rankings
  - ❌ 14 Day Rankings
  - ❌ 30 Day Rankings
  - ❌ 60 Day Rankings

</details><details><summary><i>RotoBaller</i></summary>

- [❌ 7 Day Starting Pitcher Matchup Rankings](https://www.rotoballer.com/tag/mlb-start-sit-series-for-fantasy-baseball)
- [❌ 7 Day 2-Start Pitcher Matchup Rankings](https://www.rotoballer.com/?s=%22Two-Start%20Pitcher%20Streamers%20for%20Fantasy%20Baseball%20-%20Week%22)
- [❌ 7 Day Streaming Hitter Recommendations](https://www.rotoballer.com/?s=%22Top%20Hitter%20Streamers%20and%20Starts%20for%20Fantasy%20Baseball%20-%20Week%22)
- [❌ Waiver Wire Rankings](https://www.rotoballer.com/fantasy-baseball-rankings/440514?pa=left#!/waiver-wire?league=Overall&page=1&perPage=100)
- [❌ Starting Pitcher Pickups](https://www.rotoballer.com/?s=%22Starting%20Pitcher%20Waiver%20Wire%20Pickups%20for%20Fantasy%20Baseball%20Week%22)
- [❌ Points Pitcher Pickups](https://www.rotoballer.com/?s=%22Points%20League%20Pitchers:%20Waiver%20Wire%20Pickups%20-%20Week%22)
- [❌ Points Hitter Pickups](https://www.rotoballer.com/?s=%22Points%20League%20Hitters:%20Waiver%20Wire%20Pickups%20-%20Week%22)

</details><details><summary><i>FantasyPros</i></summary>

- [❌ ROS Rankings](https://www.fantasypros.com/mlb/rankings/ros-overall.php)
- [❌ Current Rankings](https://www.fantasypros.com/mlb/rankings/overall.php)
- [❌ ADP Rankings](https://www.fantasypros.com/mlb/adp/overall.php)
- [❌ Streaming Pitcher Matchup Rankings](https://www.fantasypros.com/mlb/streaming-pitchers.php)
- [❌ Two Start Pitcher Matchup Rankings](https://www.fantasypros.com/mlb/two-start-pitchers.php)
- [❌ Stats](https://www.fantasypros.com/mlb/stats/hitters.php)
- [❌ Projections](https://www.fantasypros.com/mlb/projections/ros-hitters.php)
- [❌ Zeile Consensus Projections](https://www.fantasypros.com/mlb/projections/hitters.php)

</details><details><summary><i>NFBC</i></summary>

- [❌ % Rostered](https://nfc.shgn.com/players/baseball)
  - [❌ 1 Day Change in % Rostered](https://nfc.shgn.com/players/baseball)
  - [❌ 7 Day Change in % Rostered](https://nfc.shgn.com/players/baseball)
- [❌ % Started](https://nfc.shgn.com/players/baseball)
  - [❌ 1 Day Change in % Rostered](https://nfc.shgn.com/players/baseball)
  - [❌ 7 Day Change in % Rostered](https://nfc.shgn.com/players/baseball)
- [❌ Point Leader Rankings](https://nfc.shgn.com/players/baseball)
  - [❌ 7 Day Rankings](https://nfc.shgn.com/players/baseball)
  - [❌ 14 Day Rankings](https://nfc.shgn.com/players/baseball)
  - [❌ 30 Day Rankings](https://nfc.shgn.com/players/baseball)
- [❌ ADP](https://nfc.shgn.com/adp/baseball)

</details><details><summary><i>RT Sports</i></summary>

- [❌ Points ADP](https://rtsports.com/baseball/baseball-rankings.php?RULES=11&)
- [❌ Roto ADP](https://rtsports.com/baseball/baseball-rankings.php?RULES=11&)

</details><details><summary><i>Other</i></summary>

- [❌ Swish Analytics Next 24 Hours DraftKings Most Points](https://swishanalytics.com/optimus/mlb/fanduel-draftkings-live-scoring)
- [❌ FantasyData ROS Rankings](https://fantasydata.com/mlb/fantasy-baseball-rankings)
- [❌ RotoGrinders Past 7 Days FanDuel Most Points](https://rotogrinders.com/game-stats/mlb-hitter?site=fanduel&range=1week)
- [❌ SP Streamer Next 3 Days Pitcher Streamers](https://spstreamer.com/streamer-central/)
- [❌ Vegas Insider Bettings Odds](https://www.vegasinsider.com/mlb/odds/las-vegas/)
- [❌ BettingPros Betting Odds](https://www.bettingpros.com/mlb/odds/moneyline/)
- [❌ MLB Baseball Savant](https://baseballsavant.mlb.com/)
- [❌ FanGraphs](https://www.fangraphs.com/projections.aspx?pos=all&stats=bat&type=rzips)
- [❌ RotoWire](https://www.rotowire.com/daily/mlb/)
- [❌ RotoChamp](https://rotochamp.com/baseball/PlayerRankings.aspx?Position=AllPlayers)
- [❌ Mr. Cheatsheet](https://mrcheatsheet.com/)
- [❌ Clay Davenport](http://claydavenport.com/projections/PROJHOME.shtml)
- [❌ Baseball-Reference](https://www.baseball-reference.com/)
- [❌ Draft Buddy Projections](https://www.draftbuddy.com/baseball/projections.php)
- [❌ Razzball Rankings](https://razzball.com/2022-fantasy-baseball-rankings/)
- [❌ MLB Pipeline Prospect Rankings](https://www.mlb.com/prospects/top100/)
- [❌ Baseball America Rankings](https://www.baseballamerica.com/rankings/)

</details>

##

<details><summary><i>Disclaimers</i></summary>

- [MLB Terms of Use](https://www.mlb.com/official-information/terms-of-use)
- [Disney (ESPN) Terms of Use](https://disneytermsofuse.com/english/)
- [Yahoo Terms of Service](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html)
- [Paramount (CBS) Terms of Use](https://www.viacomcbs.legal/us/en/cbsi/terms-of-use)
- [Pitcher List Terms of Service](https://www.pitcherlist.com/terms-of-service/)

</details>
