FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add postgresql-libs postgresql-client bash --no-cache && \
    apk add --no-cache --virtual .build-deps gcc musl-dev openssl-dev libffi-dev postgresql-dev && \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

COPY . .

COPY docker/config.py config.py

ENV PYTHONUNBUFFERED=0

CMD ["/bin/bash", "/app/docker/deploy/run.sh"]
