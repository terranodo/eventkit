#!/bin/bash
set -e

POSTGRES="psql --username ${POSTGRES_USER}"

echo "Creating database: ${DB_NAME} & ${DB_DATA_NAME}"

$POSTGRES <<EOSQL
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER} TEMPLATE template_postgis;
CREATE DATABASE ${DB_DATA_NAME} OWNER ${DB_USER} TEMPLATE template_postgis;
EOSQL
