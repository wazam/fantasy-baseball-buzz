FROM python:3.7.5-slim

WORKDIR /discord

ENV DISCORD_SECRET_TOKEN= \
    DISCORD_CHANNEL_ID= \
    NBA_ENABLED=True \
    NBA_PT_DIFFERENTIAL=5 \
    NBA_MINS_LEFT=4 \
    NBA_PERIOD=4 \
    MLB_ENABLED=False \
    MLB_MINIMUM_INNING=9 \
    MLB_MAXIMUM_SCORE_DIFFERENTIAL=1 \
    MLB_THRESHOLD_MEN_ON_BASE="RISP" \
    TZ=America/New_York

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY . .

CMD pipenv run python src/main.py