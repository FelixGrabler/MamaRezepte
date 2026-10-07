#!/bin/sh
set -eu
BACKUP_ROOT=${BACKUP_ROOT:-/backups}
UPLOAD_ROOT=${UPLOAD_ROOT:-/uploads}
PASSWORD_FILE=${PASSWORD_FILE:-/run/secrets/postgres_password}
umask 077
mkdir -p "$BACKUP_ROOT"
# The kernel releases this lock even if the process/container is killed.
exec 9>"$BACKUP_ROOT/.lock"
if ! flock -n 9; then
    echo "Another backup or restore is running" >&2
    exit 1
fi
stage=""
cleanup() {
    if [ -n "$stage" ]; then rm -rf "$stage"; fi
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM
export PGPASSWORD="$(cat "$PASSWORD_FILE")"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
if [ -e "$BACKUP_ROOT/$stamp" ]; then
    echo "A snapshot already exists for this second; retry shortly" >&2
    exit 1
fi
stage="${BACKUP_ROOT}/.pending-$stamp"
mkdir "$stage"
pg_dump --format=custom --no-owner --no-acl --file="$stage/database.dump"
# Images are immutable and retained after replacement/deletion, so every file
# referenced by the database snapshot remains available while this archive runs.
tar -czf "$stage/uploads.tar.gz" -C "$UPLOAD_ROOT" .
(cd "$stage" && sha256sum database.dump uploads.tar.gz > SHA256SUMS)
mv "$stage" "${BACKUP_ROOT}/$stamp"
stage=""
date +%s > "$BACKUP_ROOT/.last-success.tmp"
mv "$BACKUP_ROOT/.last-success.tmp" "$BACKUP_ROOT/last-success"
keep=${BACKUP_KEEP:-8}
case "$keep" in ''|*[!0-9]*|0) echo "Invalid BACKUP_KEEP" >&2; exit 1;; esac
# Only prune completed snapshot directories, never temporary or unrelated files.
find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -name '????????T??????Z' | sort -r | tail -n +$((keep + 1)) | while IFS= read -r old; do
    rm -rf "$old"
done
echo "Backup completed: $stamp"
