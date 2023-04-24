FROM python:3.11.3-slim

WORKDIR /app

ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

EXPOSE 5000

COPY . .

CMD pipenv run flask run
