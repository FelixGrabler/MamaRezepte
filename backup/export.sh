#!/bin/bash

# Navigate to the backup directory within your project
cd "$(dirname "$0")"

# Database credentials and details
DB_NAME="RezeptDB"
DB_USER="jessonardo"
DB_PASSWORD="jessonardo"
DB_HOST="host.docker.internal" # Use this if the database is accessible via the host network
BACKUP_FILE="backup.sql"

# Run pg_dump using Docker, pass the POSTGRES_PASSWORD as an environment variable
docker run --rm -v "$(pwd):/backup" -e PGPASSWORD=$DB_PASSWORD postgres:latest pg_dump -U "$DB_USER" -h "$DB_HOST" -d "$DB_NAME" -F c -b -v -f "/backup/$BACKUP_FILE"

echo "Backup saved to $(pwd)/$BACKUP_FILE"
