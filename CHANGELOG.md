# Changelog

Release notes for every version, newest first. Each version is tagged in git and has a matching [release on GitHub](https://github.com/wazam/fantasy-baseball-buzz/releases), and its images are on [GHCR](https://github.com/wazam/fantasy-baseball-buzz/pkgs/container/fantasy-baseball-buzz) and [Docker Hub](https://hub.docker.com/r/wazam123/fantasy-baseball-buzz). Changes that haven't been released yet collect under **Unreleased**, and [RELEASING.md](RELEASING.md) covers how to ship them.

## Unreleased

### Bug Fixes

- With one player on Compare, **Clear compare** asks "Take 1 player off Compare?" instead of "Take all 1 players off Compare?".

## [v0.4.0](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/v0.4.0) (2026-11-12)

### Upgrading

- Replace your `compose.yaml` with the one in the README. NocoDB and PostgreSQL are gone, since Buzz now keeps its players table in a SQLite file, so the new file drops the `nocodb` and `postgres` services. It also mounts `./data` at `/usr/src/data`, moves Buzz from port `5000` to `9108`, and runs the container read-only as uid `1000` with all capabilities dropped, `no-new-privileges`, `init`, and a 256 MB `/tmp` tmpfs, capped at 512 MB of memory and 128 processes.
- Make sure uid `1000` can write to the `data` folder next to `compose.yaml`. It holds the players database, scrape results, and favorite trends. On a new install, `mkdir -p data` creates it as your user. If you're upgrading, Docker created `./data` as root for Postgres, so hand it over with `sudo chown 1000:1000 data`, or, if the folder belongs to another user (Synology shares are often `1026:100`), set `user:` in `compose.yaml` to its owner from `ls -nd data`.
- Open Buzz at `http://<host>:9108` instead of port `5000`, and update any bookmarks.
- Run your trends again from the Index page to fill the players table. Player data in NocoDB isn't carried over. Once you no longer need it, delete `data/postgres`.
- Remove these settings from your `.env` and `compose.yaml`, since Buzz no longer reads them: `NOCODB_API_TOKEN`, `NOCODB_TABLE_ID`, `NOCODB_PUBLIC_ID`, `NOCODB_BASE_ID`, `NOCODB_URL`, `ESPN_LOGIN_EMAIL`, `ESPN_LOGIN_PASSWORD`, `ESPN_LEAGUE_ID`, `ESPN_TEAM_NAME`, `ESPN_TEAM_ABBREVIATION`, `LEAGUE_LOGIN_EMAIL`, `LEAGUE_LOGIN_PASSWORD`, `PRIMARY_LEAGUE_SOURCE`, `REQUESTS_PER_WINDOW`, `REQUEST_DELAY_SECONDS`, `REQUEST_DELAY_MIN`, `REQUEST_DELAY_MAX`, and `SELENIUM_HEADLESS`. Nothing needs an account or login any more, and every remaining setting is optional. Buzz now waits a fixed 5.5 seconds between requests, plus a random 0.5 to 1.5 seconds.
- Change any script that runs a trend by opening its URL so it sends a POST to the trend's `/run` URL instead, for example `curl -X POST http://localhost:9108/cbs/2/run`. Opening `/cbs/2` now returns the trend's status as JSON, so links and browser prefetching can't start a scrape and hold the page until it finishes.
- Yahoo's trends are renumbered, since the player lists and can't-cut list are gone: the Buzz Index is `/yahoo/1` (was `/yahoo/3`) and its 7-day version `/yahoo/2` (was `/yahoo/4`). Update any script that runs them by number.

### What's New

- Players page: every player in one sortable, filterable table, with each source's columns grouped under its name. Select the star on a player to add them to Favorites, a list to keep across weeks, or the eye to add them to Compare, a short set to look at side by side. The **Favorites** and **Compare** buttons show only those players, and **Clear compare** empties Compare for a new week. Both lists are saved in `data/player-lists.json` by each player's source IDs, so they survive a rebuild of the players table. Show or hide each source's columns with its button, or single columns from the Columns menu, and the browser remembers which are hidden. It's the home page, and `/dashboard` redirects to it.
- Index page: a section per source listing its trends, the columns each one fills, how often to run it, its last run, and its status. Trends that can't be scraped yet are listed separately. The old per-source pages, such as `/cbs`, redirect to their section.
- The Index page lists planned trends as not yet supported, with links to their pages: Yahoo ADP, CBS two-start and probable pitchers, ESPN depth charts, and 12 sources to come (FantasyPros, Fleaflicker, FB Think Tank, LineupExperts, FantasySP, Razzball, RT Sports, FanGraphs, RotoWire, RotoChamp, RotoBaller, and Baseball-Reference). Only sources with a working trend get a summary tile.
- Clearer trend and column names. The Index page names each trend as its source does, such as Most Added or Who's Hot. Columns use the same words across sources: `Pts` (was `Points`), `ADP` (was `Draft ADP`), `AAV`, `Inj` for injuries, and `Pts` or `Roto` for the league format a ranking or ADP is for.
- Runs happen in the background. Select **Run** on a trend and the page updates as it queues, runs, and finishes. Runs go one at a time, and a double click or a second tab won't start a duplicate.
- Every run is recorded in `data/results/runs.jsonl`, so the last run, its player count, and any failure survive restarts.
- Make the trends you use most favorites on the Index page with their star. Favorites are saved in `data/trend-favorites.json`.
- New NFBC source: players with points stats, draft ADP, auction values, and injuries, with no login.
- New MLB source: its players trend reads the season's major leaguers from MLB's public Stats API, adding their MLB ID, age, bats, throws, and debut date. Among rows that share a name, the one with an MLB ID is the major leaguer.
- Fantrax players trend: roster %, active %, and points across Fantrax. It needs `FANTRAX_LEAGUE_ID`, which must be a league from the current season.
- Trends that run: ESPN players (adds every player with team and position), Yahoo Buzz Index for today and the last 7 days, Who's Hot, MVPs, injuries and matchup ratings, CBS most added, dropped, viewed and traded plus injuries, Fantrax players, NFBC players, draft, auction and injuries, and MLB players.
- New Yahoo trends from Yahoo's public pages: Who's Hot (each hot batter's and pitcher's rank), MVPs (the Rotisserie and Head-to-Head percentages), injuries (the IL designation, such as `IL15` or `DTD`, and the injury), and matchup ratings (1 to 5 stars and the opponent). Yahoo takes its fantasy pages offline between seasons, so they first return players when the 2027 season opens. Yahoo's player lists and can't-cut list are removed, since they only exist inside a Yahoo league.
- Saved results can be imported again into an empty players table with `db.py import`. The README's Your Data section has the steps.
- Players are matched across sources by each source's ID, then by name, ignoring accents, case, periods, hyphens, and suffixes, so `C.J. Abrams` and `CJ Abrams` are one player. Team, batter or pitcher, and position decide between players who share a name, and a batter and a pitcher with the same name are never combined.
- `db.py duplicates` lists every player name on more than one row, and `db.py merge` combines two rows that are the same player. The README's Your Data section has the steps.
- Buzz is served by Gunicorn instead of Flask's development server, so the logs no longer warn about it on every start.
- Built-in health check against `/index`.
- Buzz checks at startup that it can write to the `data` folder. If it can't, it stops and logs the `chown` command or `user:` setting that fixes it, instead of failing on the first run or page load.
- The Players page reuses the players table until a run or `db.py` changes it, so reloads are quicker.
- Python 3.14 (was 3.13.13), and each image build picks up the latest 3.14 patch. Firefox and geckodriver come from Alpine packages instead of being downloaded at runtime.
- The image holds only the app (`src/`, `templates/`, `static/`) and its dependencies.
- The image's labels are accurate: title `Buzz` and Buzz's own description instead of the repository name and its GitHub About text, plus the base image's name. Local builds leave out the build date, commit, and version instead of setting them to `unknown`.
- Images on both GHCR and Docker Hub carry a GitHub build provenance attestation, recording the repository, workflow, tag and commit that built them, in place of the cosign signature only GHCR's images had. To check one: `gh attestation verify oci://ghcr.io/wazam/fantasy-baseball-buzz:<version> --repo wazam/fantasy-baseball-buzz`. Each image index now lists only the amd64 and arm64 images.
- Refreshed light and dark themes, and a smaller favicon.
- `.env.example` lists every setting with its default.
- `compose.override.yaml` builds a local image, and `compose.dev.yaml` adds live reload for development.
- `.gitattributes` keeps every file's line endings LF in git, whatever editor or OS saved it.
- Dependabot is retired. Dependencies are updated by hand with `pipenv lock --clear`, as RELEASING.md describes.
- New README screenshots of the Players and Index pages, on desktop and phone, in light and dark mode.
- This changelog, and `RELEASING.md` for the release steps. `CONTRIBUTING.md` is gone; the README's Build from Source has the development setup.

### Bug Fixes

- Trend number `0`, such as `/cbs/0`, returns 404 instead of running the source's last trend.
- Trends that can't be scraped yet are marked unsupported instead of failing when run.
- ESPN and Fantrax ADP are empty for players with no ADP, instead of `260` (ESPN) or `0` (Fantrax), so those players no longer sort and filter as if drafted at that pick. Run both trends again to clear the old values.
- GHCR's package page shows the image, with its description and a `docker pull` command for it. On 0.3.3 it showed the cosign signature, which was stored as a tag in the same package and, pushed last, became the version the page showed.

## [v0.3.3](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/v0.3.3) (2026-04-29)

### What's New

- Images are also published to Docker Hub as `wazam123/fantasy-baseball-buzz`.
- Images are built for `linux/arm64` as well as `linux/amd64`, so Buzz runs on a Raspberry Pi or Apple Silicon.
- Every release is also tagged `X.Y`, so you can follow patch releases without picking up a new minor version.

### Bug Fixes

- The README's image size badge shows the GHCR image again.

## [v0.3.2](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/v0.3.2) (2026-04-29)

### What's New

- Every release is also tagged `main`, alongside `X.Y.Z` and `latest`.

### Bug Fixes

- GHCR images are signed with cosign again. The release workflow was failing at the signing step.

## [v0.3.1](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/v0.3.1) (2026-04-29)

### Upgrading

- Replace your `compose.yaml` with the one in the README. It runs the whole stack, `buzz`, `nocodb`, and `postgres`, with the database in `./data/postgres`, and renames the Buzz service from `fantasy-baseball-buzz` to `buzz`.

### What's New

- Rewritten README with a step-by-step NocoDB setup guide and screenshots, and a new ROADMAP.
- Python 3.13.13 (was 3.13.2).
- NocoDB telemetry is turned off.

### Bug Fixes

- The container no longer exits right after starting. The app user couldn't write its results folder.
- The CBS source no longer crashes on load.
- ESPN and Yahoo trends save to NocoDB. They were still calling the old Airtable code.
- Running a trend no longer fails with an internal error.
- Buzz starts when `NOCODB_PUBLIC_ID` isn't set.

## [v0.3.0](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/v0.3.0) (2026-04-29)

A rewrite, and the first release under the name Buzz (was Jamball).

### Upgrading

- Set up a self-hosted NocoDB on PostgreSQL in place of Airtable, following the README's NocoDB Setup, then set `NOCODB_API_TOKEN`, `NOCODB_TABLE_ID`, and `NOCODB_PUBLIC_ID`. Remove `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, and `AIRTABLE_TABLE_NAME`.
- Run the published image, `ghcr.io/wazam/fantasy-baseball-buzz:latest`, instead of building it locally.

### What's New

- The PitcherList, MLB, and FantasyPros sources are removed.
- New web UI: a Dashboard that embeds the shared NocoDB view, an Index page listing every source and trend, and a page per source. Light and dark themes, and a layout that works on phones.
- Players are matched across sources by name variations, team, and position, so each player is a single row.
- Fantrax and NFBC are listed as sources, alongside ESPN, Yahoo, and CBS, though they can't be scraped yet.
- Alpine-based image on Python 3.13.2 (was 3.11.3 on Debian), with Firefox ESR, running as a non-root user.

## [v0.2.0](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/v0.2.0) (2023-06-05)

### Upgrading

- Create an Airtable table for the trends to write to, and set `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, and `AIRTABLE_TABLE_NAME`. It replaces the Combined page, which is removed.
- Set `ESPN_LOGIN_EMAIL`, `ESPN_LOGIN_PASSWORD`, `ESPN_LEAGUE_ID`, `ESPN_TEAM_NAME`, and `ESPN_TEAM_ABBREVIATION` so the ESPN trends can sign in to ESPN.
- Point links to Yahoo's 7-day adds and drops at `/yahoo/1` (was `/yahoo/2`). The 1-day and 14-day versions are removed, and `/yahoo/2` and `/yahoo/3` now return Yahoo player lists.

### What's New

- ESPN full player list, and the rostered players in your ESPN league.
- Yahoo player lists.
- `/airtable` opens your Airtable base.
- Every trend is at `/<source>/<number>`, and a number that doesn't exist returns 404.
- Groundwork for MLB and FantasyPros sources, not usable yet.

## [v0.1.1](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/v0.1.1) (2023-04-29)

### Upgrading

- Change links from `/cbs` to `/cbs/1` and from `/espn` to `/espn/1`. Trend URLs are now numbered.
- Remove `BROWSER` from your `.env`. The image includes Firefox, and the ESPN trend always uses it.
- If you set `ENABLE_HEADLESS`, rename it to `SELENIUM_HEADLESS`.

### What's New

- A start page linking to every trend, and a Combined page showing every trend side by side for each player. The Combined page runs every scrape, so it takes about three minutes to load.
- CBS most viewed and most traded trends.
- Yahoo adds and drops over the last 14 days.
- `/about` opens the GitHub repo.
- Python 3.11.3 (was 3.10.4), and the container runs as a non-root user.

### Bug Fixes

- Scrapers updated for the 2023 season's site changes.
- The ESPN trend works inside the Docker image. It used to crash because the image had no browser.

## [v0.1.0](https://github.com/wazam/fantasy-baseball-buzz/releases/tag/v0.1.0) (2022-05-28)

The first release, named Jamball. Each trend is a URL that scrapes its source and returns the players as JSON.

### What's New

- ESPN change in % rostered over the last 7 days.
- Yahoo adds and drops over the last day and the last 7 days.
- CBS change in % rostered over the last 7 days.
- 11 PitcherList lists: rankings for starting pitchers, batters, closers, and relievers with the rank changes for each, plus streamers, matchup tiers, and two-start pitchers.
- Docker image on Python 3.10.4, serving on port 5000.
