#!/bin/bash

# Set variables
BACKUP_DIR="/home/ec2-user/backups/letsencrypt"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="letsencrypt-backup_${TIMESTAMP}.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create the backup
sudo tar -czvf "${BACKUP_DIR}/${BACKUP_FILE}" /etc/letsencrypt/

echo "Backup created: ${BACKUP_DIR}/${BACKUP_FILE}"

