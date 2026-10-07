#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
stamp=${1:?Usage: scripts/restore.sh YYYYMMDDTHHMMSSZ}
# All writers must stop before restoring; leave them stopped on any failure.
docker compose stop backend backup
docker compose up -d recipes-db
docker compose -f docker-compose.yml -f ops/restore-compose.yml run --rm --no-deps --entrypoint /bin/sh backup /ops/restore.sh "$stamp"
docker compose up -d backend backup
