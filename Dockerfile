FROM python:3.8-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add postgresql-libs --no-cache && \
    apk add --no-cache --virtual .build-deps gcc musl-dev openssl-dev libffi-dev postgresql-dev && \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

COPY . .

COPY config.docker.py config.py

CMD until pg_isready --host=$EP_DB_HOST; do sleep 1; done \
    python3 /app/main.py
