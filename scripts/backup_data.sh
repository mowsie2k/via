#!/bin/bash
set -e

BACKUP_DIR="/home/ec2-user/backups/data"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEMP_DIR=$(mktemp -d)

echo "Starting backup process at $(date)"

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
docker exec docker_compose-relational_db-1 pg_dump -U postgres postgres > "$TEMP_DIR/postgres_dump.sql"
if [ $? -ne 0 ]; then
    echo "Error: PostgreSQL backup failed"
    exit 1
fi

# Backup Vespa index data
echo "Backing up Vespa index data..."
docker run --rm --volumes-from docker_compose-index-1 -v "$TEMP_DIR:/backup" alpine tar czf "/backup/vespa_backup.tar.gz" -C /opt/vespa/var .
if [ $? -ne 0 ]; then
    echo "Error: Vespa backup failed"
    exit 1
fi

# Create full backup
echo "Creating full backup..."
tar czf "$BACKUP_DIR/full_backup_$TIMESTAMP.tar.gz" -C "$TEMP_DIR" .
if [ $? -ne 0 ]; then
    echo "Error: Full backup creation failed"
    exit 1
fi

# Clean up temporary files
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# Remove backups older than 7 days
echo "Removing old backups..."
find "$BACKUP_DIR" -name "full_backup_*.tar.gz" -mtime +7 -delete

echo "Backup process completed successfully at $(date)"


