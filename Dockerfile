ARG DOCKER_PYTHON_V=3.13.2-alpine
ARG GIT_COMMIT
ARG BUILD_DATE
ARG IMAGE_VERSION

FROM docker.io/python:${DOCKER_PYTHON_V} AS builder

RUN pip install --upgrade pip \
    && pip install --user pipenv
ENV PIPENV_VENV_IN_PROJECT=1

COPY Pipfile Pipfile.lock /usr/src/
WORKDIR /usr/src
RUN /root/.local/bin/pipenv sync

FROM docker.io/python:${DOCKER_PYTHON_V} AS runtime

LABEL org.opencontainers.image.title="Buzz" \
    org.opencontainers.image.description="Self-hosted dashboard for tracking MLB player trends, stats, and projections from top fantasy baseball sources" \
    org.opencontainers.image.version="${IMAGE_VERSION}" \
    org.opencontainers.image.source="https://github.com/wazam/fantasy-baseball-buzz" \
    org.opencontainers.image.documentation="https://github.com/wazam/fantasy-baseball-buzz#readme" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.authors="James (wazam)" \
    org.opencontainers.image.vendor="wazam" \
    org.opencontainers.image.revision="${GIT_COMMIT:-unknown}" \
    org.opencontainers.image.created="${BUILD_DATE:-unknown}"

RUN apk update \
    && apk add --no-cache firefox-esr

RUN mkdir -v /usr/src/.venv
COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

ARG USERNAME=fbb
ARG USER_UID=1000
ARG USER_GID=${USER_UID}
RUN addgroup -g ${USER_GID} ${USERNAME} && \
    adduser -D -u ${USER_UID} -G ${USERNAME} ${USERNAME}

ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR /usr/src/
COPY . .

RUN mkdir -p /usr/src/data/results && \
    chown -R fbb:fbb /usr/src/data

EXPOSE 5000/tcp

USER fbb

CMD ["./.venv/bin/python", "-m", "flask", "run"]
