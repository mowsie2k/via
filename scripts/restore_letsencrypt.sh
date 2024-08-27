#!/bin/bash

# Set variables
BACKUP_DIR="/home/ec2-user/backups/letsencrypt"

#
# List available backups
echo "Available backups:"
backups=($(ls -1 "$BACKUP_DIR"/letsencrypt-backup_*.tar.gz))
for i in "${!backups[@]}"; do
    echo "$((i+1)). ${backups[$i]##*/}"
done

# Prompt user to select a backup file by number
read -p "Enter the number of the backup file to restore: " selection

# Validate input
if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt "${#backups[@]}" ]; then
    echo "Error: Invalid selection. Please enter a number between 1 and ${#backups[@]}."
    exit 1
fi

# Get the selected backup file
BACKUP_FILE="${backups[$((selection-1))]}"

# Check if the file exists (this should always be true, but it's good to check)
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found."
    exit 1
fi

# Restore the backup
sudo tar -xzvf "$BACKUP_FILE" -C /

echo "Backup restored from: $BACKUP_FILE"
