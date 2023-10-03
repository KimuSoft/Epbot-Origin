FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add postgresql-libs postgresql-client bash py3-setuptools git --no-cache && \
    apk add --no-cache gcc musl-dev openssl-dev libffi-dev postgresql-dev \
    tiff-dev jpeg-dev openjpeg-dev zlib-dev freetype-dev lcms2-dev \
    libwebp-dev tcl-dev tk-dev harfbuzz-dev fribidi-dev libimagequant-dev \
    libxcb-dev libpng-dev && \
    pip install -r requirements.txt

COPY . .

COPY docker/config.py config.py

ENV PYTHONUNBUFFERED=0

CMD ["/bin/bash", "/app/docker/deploy/run.sh"]
