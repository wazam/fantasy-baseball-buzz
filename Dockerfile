FROM python:3.11.3-slim

USER root
RUN apt-get update
RUN apt-get install -y --no-install-recommends xvfb
RUN apt-get install -y --no-install-recommends firefox-esr
# RUN apt-get -y purge firefox-esr

# RUN adduser --system --group --no-create-home newuser
RUN groupadd --gid 1000 newuser && useradd --uid 1000 --gid 1000 -m newuser
RUN mkdir app && chown newuser app

ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile --system
COPY . /app/

EXPOSE 5000
USER newuser
CMD pipenv run flask run
