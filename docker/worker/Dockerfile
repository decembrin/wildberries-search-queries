FROM python:3.13-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./.env ./
COPY ./requirements.txt ./
RUN pip install -r requirements.txt