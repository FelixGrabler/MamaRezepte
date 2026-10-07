#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
umask 077
mkdir -p secrets
if [ ! -f secrets/postgres_password.txt ]; then
    python3 -c 'import secrets; print(secrets.token_urlsafe(48))' > secrets/postgres_password.txt
fi
echo 'Recipe database secret is ready.'
