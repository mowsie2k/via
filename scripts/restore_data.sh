#!/bin/bash
set -e

BACKUP_FILE="$1"
EXTRACT_DIR="/home/ec2-user/backups/data/"

echo "Extracting backup from: $BACKUP_FILE"
echo "Extracting to: $EXTRACT_DIR"

# Extract the full backup
tar xzf "$BACKUP_FILE" -C "$EXTRACT_DIR"

# Debug: List contents of extract directory
echo "Contents of $EXTRACT_DIR:"
ls -R "$EXTRACT_DIR"

# Find and restore PostgreSQL database
POSTGRES_DUMP=$(find "$EXTRACT_DIR" -name "postgres_dump_*.sql" | head -n 1)
if [ -z "$POSTGRES_DUMP" ]; then
    echo "Error: PostgreSQL dump file not found"
    exit 1
fi
echo "Restoring PostgreSQL dump from: $POSTGRES_DUMP"
docker exec -i docker_compose-relational_db-1 psql -U postgres -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
cat "$POSTGRES_DUMP" | docker exec -i docker_compose-relational_db-1 psql -U postgres -d postgres

# Find and restore Vespa index data
VESPA_BACKUP=$(find "$EXTRACT_DIR" -name "vespa_backup_*.tar.gz" | head -n 1)
if [ -z "$VESPA_BACKUP" ]; then
    echo "Error: Vespa backup file not found"
    exit 1
fi
echo "Restoring Vespa index data from: $VESPA_BACKUP"
docker run --rm --volumes-from docker_compose-index-1 -v "$(dirname "$VESPA_BACKUP"):/backup" alpine sh -c "rm -rf /opt/vespa/var/* && tar xzf /backup/$(basename "$VESPA>

# Cleanup
echo "Cleaning up extracted files"
rm -rf "$EXTRACT_DIR"

