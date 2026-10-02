#!/usr/bin/env bash

set -euo pipefail
source ../.env

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <backup_file.sql>"
    exit 1
fi

filename="$1"

docker exec postgres psql -U ${DB_USER} -d ${DB_NAME} -f "/backups/${filename}"

echo "Database restored from: '/backups/${filename}'"