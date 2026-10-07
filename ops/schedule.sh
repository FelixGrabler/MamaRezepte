#!/bin/sh
set -eu
BACKUP_ROOT=${BACKUP_ROOT:-/backups}
UPLOAD_ROOT=${UPLOAD_ROOT:-/uploads}
PASSWORD_FILE=${PASSWORD_FILE:-/run/secrets/postgres_password}
# Catch up on startup; otherwise take a snapshot every seven days.
while :; do
    now=$(date +%s)
    last=0
    if [ -f "$BACKUP_ROOT/last-success" ]; then last=$(cat "$BACKUP_ROOT/last-success"); fi
    if [ $((now - last)) -ge 604800 ]; then
        if ! /bin/sh /ops/backup.sh; then echo "Backup failed; retrying in an hour" >&2; fi
    fi
    sleep 3600 &
    wait $!
done
