#!/bin/bash
# ============================================================
# WarpHelix Database Backup Script (via docker)
# ============================================================

set -e

BACKUP_DIR="/opt/biomni/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/biomni_${DATE}.sql.gz"

# 从 docker .env 读取密码
if [ -f /opt/biomni/docker/.env ]; then
    source /opt/biomni/docker/.env
else
    echo "Error: docker .env not found"
    exit 1
fi

mkdir -p ${BACKUP_DIR}

echo "Starting backup..."
docker exec mysql57 mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" biomni | gzip > ${BACKUP_FILE}

# 保留最近 30 天的备份
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

echo "Backup saved: ${BACKUP_FILE} ($(du -h ${BACKUP_FILE} | cut -f1))"
