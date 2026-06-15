#!/bin/bash
# AgriFlow OS - Daily Backup Script
# Schedule via cron: 0 2 * * * /home/agriflow/scripts/backup.sh

set -e

SITE_NAME="agriflow.yourcompany.com"
BENCH_DIR="/home/agriflow/frappe-bench"
BACKUP_DIR="/home/agriflow/backups"
RETENTION_DAYS=7

# Create backup dir
mkdir -p $BACKUP_DIR

# Take backup
cd $BENCH_DIR
./env/bin/bench --site $SITE_NAME backup --with-files

# Move to backup dir
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mv sites/$SITE_NAME/private/backups/*.sql.gz $BACKUP_DIR/db_$TIMESTAMP.sql.gz 2>/dev/null || true
mv sites/$SITE_NAME/private/backups/*public-files*.tar $BACKUP_DIR/public_$TIMESTAMP.tar 2>/dev/null || true
mv sites/$SITE_NAME/private/backups/*private-files*.tar $BACKUP_DIR/private_$TIMESTAMP.tar 2>/dev/null || true

# Cleanup old backups
find $BACKUP_DIR -mtime +$RETENTION_DAYS -delete

# Optional: Upload to cloud storage
# aws s3 sync $BACKUP_DIR s3://agriflow-backups/ --delete

echo "✅ Backup complete: $TIMESTAMP"
echo "Files in $BACKUP_DIR:"
ls -lah $BACKUP_DIR | tail -10