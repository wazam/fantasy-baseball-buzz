# syntax=docker/dockerfile:1

FROM python:3.11.2-slim

WORKDIR /app

ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV TZ=America/New_York

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

EXPOSE 5000

COPY . .

CMD pipenv run flask run
