#!/bin/bash

# Navigate to the backup directory within your project
cd "$(dirname "$0")"

# Database credentials and details
DB_NAME="RezeptDB"
DB_USER="jessonardo"
DB_PASSWORD="jessonardo"
DB_HOST="host.docker.internal"  # Adjust accordingly
BACKUP_FILE="backup.sql"  # Ensure this matches your actual backup file's name and extension

# Run pg_restore using Docker, with options for a cleaner restore
docker run --rm -v "$(pwd):/backup" -e PGPASSWORD=$DB_PASSWORD postgres:latest \
pg_restore -U "$DB_USER" -h "$DB_HOST" -d "$DB_NAME" --clean --if-exists -v "/backup/$BACKUP_FILE"

echo "Database restored from $(pwd)/$BACKUP_FILE"
