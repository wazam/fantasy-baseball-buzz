<h1 align="center">
  <a href="https://github.com/wazam/fantasy-baseball-buzz">
    <img
      width="120"
      alt="Buzz Logo"
      src="static/favicon.png">
  </a>
  <br/>
  Buzz
</h1>

<p align="center">
  <a href="https://github.com/wazam/fantasy-baseball-buzz/actions/workflows/publish-docker-image.yml">
    <img src="https://github.com/wazam/fantasy-baseball-buzz/actions/workflows/publish-docker-image.yml/badge.svg" alt="Build & Publish Docker Image CI Status" />
  </a>
  <a href="https://github.com/wazam/fantasy-baseball-buzz/actions/workflows/test-docker-compose-stack.yml">
    <img src="https://github.com/wazam/fantasy-baseball-buzz/actions/workflows/test-docker-compose-stack.yml/badge.svg" alt="Test Docker Compose Stack CI Status" />
  </a>
  <br />
  <a href="https://github.com/wazam/fantasy-baseball-buzz/releases">
    <img src="https://img.shields.io/github/v/release/wazam/fantasy-baseball-buzz?sort=semver" alt="Latest Release" />
  </a>
  <a href="https://github.com/wazam/fantasy-baseball-buzz/pkgs/container/fantasy-baseball-buzz">
    <img src="https://img.shields.io/docker/image-size/wazam/fantasy-baseball-buzz/latest?registry_url=https://ghcr.io&label=docker%20image&logo=docker" alt="Docker Image Size" />
  </a>
  <a href="https://github.com/wazam/fantasy-baseball-buzz/stargazers">
    <img src="https://img.shields.io/github/stars/wazam/fantasy-baseball-buzz?style=social" alt="GitHub Stars" />
  </a>
</p>

**Buzz** is a self-hosted fantasy baseball dashboard that aggregates **MLB player trends**, rankings, projections, and social fantasy signals like **% rostered**, **adds/drops**, and **% started** from top platforms. It presents a unified, sortable, and filterable view of how players are valued across fantasy leagues, combining social signals with real-life performance metrics and rest-of-season projections.

Rather than forecasting player talent, Buzz reveals how the fantasy community is reacting, surfacing surging pickups, fading names, and platform-specific roster shifts. By tracking this behavior in near real time, you can act on emerging trends before your league does. Whether you're a data-driven GM or just playing the wire, Buzz delivers **fantasy market intelligence** with no third-party logins, no subscriptions, and no fluff.

<details><summary><strong>Table of Contents</strong></summary>

- [Features](#features)
- [Tech Stack](#tech-stack)
- [NocoDB Setup](#nocodb-setup)
- [Quick Start](#quick-start)
  - [Run via Docker Compose](#run-via-docker-compose)
  - [Build from Source](#build-from-source)
- [Environment Variables](#environment-variables)
  - [Additional NocoDB Environment Variables](#additional-nocodb-environment-variables)
  - [Additional PostgreSQL Environment Variables](#additional-postgresql-environment-variables)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [Disclaimers](#disclaimers)
- [License](#license)

</details>

---

## Features

- **Multi-Source Coverage**: Pulls fantasy player data from multiple popular league platforms for comprehensive tracking.
- **Unified Player Dashboard**: See every eligible MLB player in a sortable, filterable table with side-by-side comparisons across platforms.
- **Fantasy Sentiment Tracking**: Focuses on social signals like ownership trends and transaction volume to reveal shifts in player value before your league reacts.
- **Fantasy Valuation Metrics**: Covers projection-based, statistic-based, and opinion-based rankings for various timeframes including preseason, weekly, and rest-of-season to give a complete picture of a player's value.
- **Manual Data Refresh**: Trigger scrapes manually to pull the most up-to-date data directly from each platform with no stale caches or outdated snapshots.
- **Fully Self-Hosted**: Runs entirely on your own machine with no third-party accounts, logins, or subscriptions required.
- **Responsive Design**: Clean UI optimized for desktop and mobile use.
- **One-Command Docker Launch**: Spin up the full stack with Docker Compose with no complicated setup needed.

## Tech Stack

- **Language and Runtime**: Python, powered by Flask for the web app, Requests for HTTP, and BeautifulSoup for scraping, managed with Pipenv.
- **Frontend and Templating**: Jinja2 for dynamic HTML, styled with responsive CSS for mobile and desktop support.
- **Database Layer**: PostgreSQL, accessed and managed visually through NocoDB (open-source Airtable alternative).
- **Infrastructure and Deployment**: Containerized with Docker, orchestrated using Docker Compose for seamless local and server-side setup.
- **Automation and CI/CD**: GitHub Actions for testing, building, and publishing Docker images automatically.

## NocoDB Setup

> [!NOTE]
> These steps configure NocoDB and generate the required environment values for Buzz. Complete this after launching the stack for the first time.

1. **Access NocoDB**

    Go to [http://localhost:8080](http://localhost:8080) and register as a Super Admin (e.g. `example@anything.whatever` / `mysecretpassword`)

    <details><summary>See Setup Screenshot</summary>

    ![NocoDB Setup 01](assets/images/setup-nocodb-01.jpg)

    </details>

2. **Import JSON Template**

    Import [`assets/setup/nocodb-template.json`](assets/setup/nocodb-template.json) as a new table.

    > [!WARNING]
    > Do not delete or rename columns, but feel free to reorder, resize, or hide them in your dashboard.

    <details><summary>See Setup Screenshots</summary>

    ![NocoDB Setup 02](assets/images/setup-nocodb-02.jpg)
    ![NocoDB Setup 03](assets/images/setup-nocodb-03.jpg)
    ![NocoDB Setup 04](assets/images/setup-nocodb-04.jpg)

    </details>

3. **Get API Token**

    Go to *Account Settings > Tokens* to generate your personal token and copy it.

    ```yaml
        environment:
          - NOCODB_API_TOKEN=EA_Lcy903zCah6GWiwnWyr6clTF0Alj43KIXuXRG
    ```

    <details><summary>See Setup Screenshots</summary>

    ![NocoDB Setup 05](assets/images/setup-nocodb-05.jpg)
    ![NocoDB Setup 06](assets/images/setup-nocodb-06.jpg)
    ![NocoDB Setup 07](assets/images/setup-nocodb-07.jpg)
    ![NocoDB Setup 08](assets/images/setup-nocodb-08.jpg)

    </details>

4. **Get Base ID and Table ID**

    Navigate to the database view to copy your Base ID and Table ID.

    ```yaml
        environment:
          - NOCODB_BASE_ID=p5qesumr1rzlee2
          - NOCODB_TABLE_ID=m2ghe4zq9dgdzdf
    ```

    <details><summary>See Setup Screenshots</summary>

    ![NocoDB Setup 09](assets/images/setup-nocodb-09.jpg)
    ![NocoDB Setup 10](assets/images/setup-nocodb-10.jpg)
    ![NocoDB Setup 11](assets/images/setup-nocodb-11.jpg)

    </details>

5. **Get Public URL and ID**

    Click the **Share** button (top-right corner of table view), enable public viewing, change optional settings, and copy the URL. The raw copy paste has 2 parts you need to parse manually.

    ```yaml
        environment:
          - NOCODB_URL=http://localhost:8080
          - NOCODB_PUBLIC_ID=5b55dc5d-42b9-4aef-b89e-16f104d89b61
    ```

    <details><summary>See Setup Screenshot</summary>

    ![NocoDB Setup 12](assets/images/setup-nocodb-12.jpg)

    </details>

6. **Apply Environment Variables**

    Add all the required environment values to your `compose.yaml` file and restart:

    ```sh
    docker compose stop
    docker compose up -d
    ```

7. **Access Buzz**

    Success! Buzz is now connected to your NocoDB instance. Visit and bookmark [http://localhost:5000/](http://localhost:5000/) to begin using **Buzz**.

## Quick Start

> [!TIP]
> Run via Docker Compose is recommended for most users.

### Run via Docker Compose

1. **Create `compose.yaml`**

    ```yaml
    services:
      buzz:
        image: ghcr.io/wazam/fantasy-baseball-buzz:latest
        container_name: buzz
        restart: unless-stopped
        environment:
          - NOCODB_API_TOKEN=    # Required - see NocoDB Setup above
          - NOCODB_TABLE_ID=     # Required - see NocoDB Setup above
          - NOCODB_PUBLIC_ID=    # Required - see NocoDB Setup above
        ports:
          - 5000:5000
        depends_on:
          - nocodb

      nocodb:
        image: nocodb/nocodb:latest
        container_name: nocodb
        restart: unless-stopped
        environment:
          - NC_DB=pg://postgres:5432?u=postgres&p=password&d=postgres
          - NC_DISABLE_TELE=true
        ports:
          - 8080:8080
        depends_on:
          - postgres

      postgres:
        image: postgres:16-alpine
        container_name: postgres
        restart: unless-stopped
        environment:
          - POSTGRES_PASSWORD=password
          - POSTGRES_DB=postgres
          - POSTGRES_USER=postgres
        volumes:
          - ./data/postgres:/var/lib/postgresql/data
    ```

2. **Launch the Docker stack**

    ```sh
    docker compose up -d
    ```

3. **Proceed to [NocoDB Setup](#nocodb-setup) to configure your instance**

### Build from Source

1. **Clone the repository**

    ```sh
    git clone https://github.com/wazam/fantasy-baseball-buzz.git
    cd fantasy-baseball-buzz
    ```

2. **Build the Docker image and launch the app**

    ```sh
    docker build -t ghcr.io/wazam/fantasy-baseball-buzz:latest .
    docker compose up -d
    ```

3. **Proceed to [NocoDB Setup](#nocodb-setup) to configure your instance**

## Environment Variables

You can customize Buzz behavior using these optional environment variables:

| Variable                | Description                                                                                                                                                                          | Default / Options                                                                                                                |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `NOCODB_BASE_ID`        | Private ID for the *Base* where the *Table* is. Used to personalize the menu's editor link directly to the user's *Table* for immediate dashboard editing. (already mentioned above) | *(not set)* (default), accepts any `string`                                                                                      |
| `NOCODB_URL`            | Public-facing URL for the NocoDB backend. Used to embed the NocoDB dashboard table directly in the Buzz app. (already mentioned above)                                               | `http://localhost:8080` (default), accepts any `string` like `http://192.168.0.10:8080` or `https://nocodb.mysite.com`           |
| `PRIMARY_LEAGUE_SOURCE` | Sets the authoritative fantasy platform for player names, positions, etc. to align the UI with your league's conventions.                                                            | `ESPN` (default), `Yahoo`, `CBS`, `Fantrax`, or `NFBC`                                                                           |
| `LEAGUE_LOGIN_EMAIL`    | Email or username used to fetch rostered players from your private league.                                                                                                           | *(not set)* (default), accepts any `string`                                                                                      |
| `LEAGUE_LOGIN_PASSWORD` | Password for the above login.                                                                                                                                                        | *(not set)* (default), accepts any `string`                                                                                      |
| `REQUEST_DELAY_SECONDS` | Delay (in seconds) between outbound requests to a platform.                                                                                                                          | `5.5` (default), accepts any `float > 0`                                                                                         |
| `REQUESTS_PER_WINDOW`   | Max number of requests allowed per rate limit window.                                                                                                                                | `1` (default), accepts any `int >= 1`                                                                                            |
| `REQUEST_DELAY_MIN`     | Minimum randomized delay (in seconds) before each request.                                                                                                                           | `0.5` (default), accepts any `float > 0`                                                                                         |
| `REQUEST_DELAY_MAX`     | Maximum randomized delay (in seconds) before each request.                                                                                                                           | `1.5` (default), accepts any `float > 0`                                                                                         |
| `TZ`                    | Time zone used for logs and scraping schedules.                                                                                                                                      | `UTC` (docker default), accepts any TZ identifier from [list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) |

> [!TIP]
> For remote access from another device, set `NOCODB_URL` or the app will only be reachable on `localhost`.
>
> Do not put this on the Internet if you do not know what you are doing.

The `buzz` service does **not** include a health check by default, but you may add one.

```yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/index"]
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 3s
```

---

### Additional NocoDB Environment Variables

| Variable                                                                                                  | Description                                                         | Default / Options                                                                                      |
|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| [`NC_DISABLE_TELE`](https://docs.nocodb.com/getting-started/self-hosted/environment-variables/#telemetry) | Disables the telemetry to prevent sending anonymous usage data.     | *(not set)* (default), `true`                                                                          |
| [`NC_DB`](https://docs.nocodb.com/getting-started/self-hosted/environment-variables/#database)            | The primary database where all NocoDB metadata and data are stored. | *(not set)* (default), format: `pg://host.docker.internal:5432?u=username&p=password&d=database_name`. |
| [`PORT`](https://docs.nocodb.com/getting-started/self-hosted/environment-variables/#backend)              | Specifies the network port on which NocoDB will run.                | `8080` (default)                                                                                       |

> [!CAUTION]
> If you're trying to use SQLite instead of PostgreSQL, you must:
>
> - Remove the `postgres` service from `compose.yaml`.
> - Remove the `NC_DB` environment variable entirely.
> - Add a local volume mount for `./your/path/to/nocodb/data:/usr/app/data`.

---

### Additional PostgreSQL Environment Variables

| Variable                                                                                                       | Description                                              | Default    |
|----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|------------|
| [`POSTGRES_DB`](https://github.com/docker-library/docs/blob/master/postgres/README.md#postgres_db)             | Name of the default PostgreSQL database                  | `postgres` |
| [`POSTGRES_USER`](https://github.com/docker-library/docs/blob/master/postgres/README.md#postgres_user)         | Username for PostgreSQL authentication                   | `postgres` |
| [`POSTGRES_PASSWORD`](https://github.com/docker-library/docs/blob/master/postgres/README.md#postgres_password) | Password for the specified user (already required above) | `password` |

> [!WARNING]
> If you change any of these defaults, be sure to update the `NC_DB` environment variable for the `nocodb` service in your `compose.yaml` accordingly.

The `postgres` service does **not** include a health check by default, but you may add one to ensure the container is ready before other services attempt to connect.

```yaml
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 2s
      retries: 10
```

## Screenshots

<table>
<tr>
<th>Desktop (Light)</th>
<th>Mobile (Light)</th>
</tr>
<tr>
<td><img src="assets/images/screenshot-desktop-dashboard.jpg" alt="Buzz Dashboard"/><br/><img src="assets/images/screenshot-desktop-page.jpg" alt="Platform Page 1"/><br/><img src="assets/images/screenshot-desktop-page-2.jpg" alt="Platform Page 2"/></td>
<td><img src="assets/images/screenshot-mobile-dashboard.jpg" alt="Mobile Dashboard"/><br/><img src="assets/images/screenshot-mobile-page.jpg" alt="Mobile Page 1"/><br/><img src="assets/images/screenshot-mobile-page-2.jpg" alt="Mobile Page 2"/></td>
</tr>
</table>

<table>
<tr>
<th>Desktop (Dark)</th>
<th>Mobile (Dark)</th>
</tr>
<tr>
<td><img src="assets/images/screenshot-desktop-dashboard-dark.jpg" alt="Dashboard Dark"/><br/><img src="assets/images/screenshot-desktop-page-dark.jpg" alt="Platform Dark"/></td>
<td><img src="assets/images/screenshot-mobile-dashboard-dark.jpg" alt="Mobile Dashboard Dark"/><br/><img src="assets/images/screenshot-mobile-page-dark.jpg" alt="Mobile Page Dark"/></td>
</tr>
</table>

## Contributing

Report bugs or feature requests by opening an issue on the [GitHub repository](https://github.com/wazam/fantasy-baseball-buzz/issues). See [ROADMAP.md](ROADMAP.md) for planned and proposed features. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting pull requests.

## Disclaimers

- [ESPN Terms of Use](https://disneytermsofuse.com/english/)
- [Yahoo Terms of Service](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html)
- [CBS Terms of Use](https://www.viacomcbs.legal/us/en/cbsi/terms-of-use)
- [Fantrax Terms of Service](https://www.fantrax.com/terms-of-service)
- [NFBC Terms of Service](https://idsrv.fanball.com/terms)

## License

This project is licensed under the [MIT License](LICENSE).
