#!/usr/bin/env bash
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/../.." && pwd)}"
COMPOSE_FILE="$REPO/infra/docker/docker-compose.staging.yml"
ENV_FILE="$REPO/infra/docker/.env.staging"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/agriflow}"
RETENTION="${BACKUP_RETENTION_DAYS:-14}"

mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d_%H%M%S)
source "$ENV_FILE"

DUMP="$BACKUP_DIR/mariadb_${STAMP}.sql.gz"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T mariadb \
  mysqldump -u"${MARIADB_USER}" -p"${MARIADB_PASSWORD}" "${MARIADB_DATABASE}" | gzip > "$DUMP"

find "$BACKUP_DIR" -name 'mariadb_*.sql.gz' -mtime +"$RETENTION" -delete
echo "$(date -Is) backup $DUMP ($(wc -c < "$DUMP") bytes)"
