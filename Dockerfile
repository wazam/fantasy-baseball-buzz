ARG DOCKER_PYTHON_V=3.14-alpine

# Stage 1: Build dependencies
FROM python:${DOCKER_PYTHON_V} AS builder

WORKDIR /usr/src

# Quiet pip's running-as-root and version-check notices during the build, and keep the venv in the project
ENV PIP_ROOT_USER_ACTION=ignore \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIPENV_VENV_IN_PROJECT=1

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv sync

# Stage 2: Runtime image
FROM python:${DOCKER_PYTHON_V} AS runtime

ARG DOCKER_PYTHON_V

# Labels that don't change between builds. Docker Publish adds created, revision and version, so local
# builds leave them out rather than guess, and reads the description from here for GHCR's package page
LABEL org.opencontainers.image.title="Buzz" \
    org.opencontainers.image.description="Self-hosted fantasy baseball dashboard that aggregates MLB player trends from top fantasy platforms" \
    org.opencontainers.image.url="https://github.com/wazam/fantasy-baseball-buzz" \
    org.opencontainers.image.source="https://github.com/wazam/fantasy-baseball-buzz" \
    org.opencontainers.image.documentation="https://github.com/wazam/fantasy-baseball-buzz#readme" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.authors="James Wazam" \
    org.opencontainers.image.vendor="wazam" \
    org.opencontainers.image.base.name="docker.io/library/python:${DOCKER_PYTHON_V}"

# apk upgrade takes Alpine's security updates that the base image doesn't have yet
RUN apk upgrade --no-cache && \
    apk add --no-cache firefox-esr geckodriver

# FLASK_* are for the flask run dev server in compose.dev.yaml; the image itself serves with Gunicorn.
# The root filesystem may be read-only (hardened stacks), so Python doesn't write .pyc files; dependencies
# were compiled at build time. The runtime UID has no passwd entry, so HOME gives Firefox a writable home.
ENV FLASK_APP=src/main.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=9108 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/tmp

WORKDIR /usr/src

COPY --from=builder /usr/src/.venv/ ./.venv/
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/

# Owned by the default runtime UID; to run as another user with user:, mount a data folder owned by that user
RUN mkdir -p /usr/src/data/results && \
    chown -R 1000:1000 /usr/src/data

EXPOSE 9108/tcp

USER 1000:1000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --start-interval=5s --retries=3 \
    CMD wget -q --spider http://127.0.0.1:9108/index || exit 1

# src/config.py checks the settings, then starts the command after it, so a bad value stops the container
# before Gunicorn runs. One process, since src/jobs.py keeps the run queue in memory; threads serve requests
# concurrently. --workers is set here so a WEB_CONCURRENCY variable can't raise it
CMD ["./.venv/bin/python", "src/config.py", \
     "./.venv/bin/gunicorn", "--pythonpath", "src", "--bind", "0.0.0.0:9108", \
     "--workers", "1", "--threads", "4", "--access-logfile", "-", "main:app"]
