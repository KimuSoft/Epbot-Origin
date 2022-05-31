FROM postgres

ENV POSTGRES_PASSWORD=kimubabo

ENV PGDATA=/var/lib/postgresql/data/pgdata

COPY setup.sql /docker-entrypoint-initdb.d/setup.sql
