#!/bin/bash

until pg_isready --host=$EP_DB_HOST; do sleep 1; done
python3 /app/main.py