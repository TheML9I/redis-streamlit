#!/bin/bash
# backup-script.sh - Redis backup script for Docker container

# Set variables
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
BACKUP_DIR=/backups
MAX_BACKUPS=7
DATE=$(date +%Y%m%d-%H%M%S)

# Ensure backup directory exists
mkdir -p ${BACKUP_DIR}

echo "========================================"
echo "Starting Redis backup - $(date)"
echo "========================================"

# Create RDB backup using redis-cli
echo "Triggering SAVE command..."
redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} SAVE

# Copy the dump.rdb file
echo "Copying RDB file..."
redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} --rdb ${BACKUP_DIR}/redis-${DATE}.rdb

# Back up AOF file if it exists (requires redis to enable appendonly)
echo "Copying AOF file if available..."
redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} CONFIG GET appendonly | grep -q "yes"
if [ $? -eq 0 ]; then
    cp /data/appendonly.aof ${BACKUP_DIR}/appendonly-${DATE}.aof
fi

# Delete old backups
echo "Cleaning up old backups, keeping last ${MAX_BACKUPS}..."
ls -tp ${BACKUP_DIR}/redis-*.rdb | grep -v '/$' | tail -n +$((MAX_BACKUPS+1)) | xargs -I {} rm -- {}
ls -tp ${BACKUP_DIR}/appendonly-*.aof | grep -v '/$' | tail -n +$((MAX_BACKUPS+1)) | xargs -I {} rm -- {}

echo "Backup completed successfully - $(date)"
echo "Redis RDB backup: ${BACKUP_DIR}/redis-${DATE}.rdb"
echo "Redis AOF backup: ${BACKUP_DIR}/appendonly-${DATE}.aof"
echo "========================================"