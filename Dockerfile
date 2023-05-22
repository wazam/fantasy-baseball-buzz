FROM python:3.11.3-slim

ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0

USER root
RUN apt-get update
RUN apt-get install -y --no-install-recommends firefox-esr

# https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user
ARG USERNAME=fbb
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

WORKDIR /home/fbb/fantasy-baseball-buzz
COPY Pipfile* ./
RUN pip install --upgrade pip && pip install pipenv && pipenv install --system --deploy --ignore-pipfile --verbose
COPY . .

EXPOSE 5000/tcp

USER fbb
CMD pipenv run flask run
