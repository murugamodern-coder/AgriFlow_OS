#!/usr/bin/env bash
# Backup + restore validation for staging/prod MariaDB (run on host with docker compose).
set -eu

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker/docker-compose.staging.yml}"
ENV_FILE="${ENV_FILE:-infra/docker/.env.staging}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/agriflow-backup}"
STAMP=$(date +%Y%m%d_%H%M%S)
DUMP="$BACKUP_DIR/agriflow_${STAMP}.sql"

mkdir -p "$BACKUP_DIR"
source "$ENV_FILE" 2>/dev/null || true

echo "Backing up database..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T mariadb \
  mysqldump -u"${MARIADB_USER:-agriflow}" -p"${MARIADB_PASSWORD}" "${MARIADB_DATABASE}" > "$DUMP"

echo "Backup written: $DUMP ($(wc -c < "$DUMP") bytes)"

if [ "${VALIDATE_RESTORE:-0}" = "1" ]; then
  TEST_DB="${MARIADB_DATABASE}_restore_test"
  echo "Restore validation into $TEST_DB (manual drop after verify)"
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T mariadb \
    mariadb -u"${MARIADB_USER:-agriflow}" -p"${MARIADB_PASSWORD}" -e "CREATE DATABASE IF NOT EXISTS \`${TEST_DB}\`;"
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T mariadb \
    mariadb -u"${MARIADB_USER:-agriflow}" -p"${MARIADB_PASSWORD}" "$TEST_DB" < "$DUMP"
  echo "Restore test complete"
fi
