ARG DOCKER_PYTHON_V="3.11.3-slim"

# https://pipenv.pypa.io/en/latest/docker/
FROM docker.io/python:$DOCKER_PYTHON_V AS builder
RUN RUN pip install --upgrade pip \
    && pip install --user pipenv
ENV PIPENV_VENV_IN_PROJECT=1
ADD Pipfile.lock Pipfile /usr/src/
WORKDIR /usr/src
RUN /root/.local/bin/pipenv sync

FROM docker.io/python:$DOCKER_PYTHON_V AS runtime
RUN mkdir -v /usr/src/.venv
COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0

ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NOWARNINGS="yes"
RUN apt-get update \
    && apt-get --no-install-recommends --assume-yes --quiet install \
        firefox-esr

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

ADD . /usr/src/

WORKDIR /usr/src/

EXPOSE 5000/tcp

USER fbb

CMD ["./.venv/bin/python", "-m", "flask", "run"]
