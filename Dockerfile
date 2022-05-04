FROM python:3.10-slim

WORKDIR /app

ENV TZ=America/New_York

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY . .

CMD pipenv run flask run
