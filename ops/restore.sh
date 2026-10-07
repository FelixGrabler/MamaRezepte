#!/bin/sh
# Run through scripts/restore.sh after stopping writers.
set -eu
BACKUP_ROOT=${BACKUP_ROOT:-/backups}
UPLOAD_ROOT=${UPLOAD_ROOT:-/uploads}
PASSWORD_FILE=${PASSWORD_FILE:-/run/secrets/postgres_password}
umask 077
stamp=${1:?Snapshot name required}
case "$stamp" in ????????T??????Z) ;; *) echo "Invalid snapshot name" >&2; exit 1;; esac
case "$stamp" in *[!0-9TZ]*) echo "Invalid snapshot name" >&2; exit 1;; esac
snapshot="${BACKUP_ROOT}/$stamp"
exec 9>"$BACKUP_ROOT/.lock"
flock -n 9 || { echo "Another backup or restore is running" >&2; exit 1; }
(cd "$snapshot" && sha256sum -c SHA256SUMS)
pg_restore --list "$snapshot/database.dump" >/dev/null
tar -tzf "$snapshot/uploads.tar.gz" >/dev/null
export PGPASSWORD="$(cat "$PASSWORD_FILE")"
# Restore files before the database can reference them. Existing orphan files
# may remain, but are inaccessible through the API without a recipe reference.
tar -xzf "$snapshot/uploads.tar.gz" -C "$UPLOAD_ROOT"
pg_restore --clean --if-exists --no-owner --no-acl --single-transaction --exit-on-error --dbname="$PGDATABASE" "$snapshot/database.dump"
echo "Restored $stamp"
