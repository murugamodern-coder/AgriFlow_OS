#!/usr/bin/env bash
# Generate staging secrets into .env.staging (do not commit).
set -eu

DIR="$(cd "$(dirname "$0")/../docker" && pwd)"
OUT="${1:-$DIR/.env.staging}"
EXAMPLE="$DIR/.env.staging.example"
DOMAIN="${STAGING_DOMAIN:-staging.example.com}"

if [ -f "$OUT" ] && [ "${FORCE:-0}" != "1" ]; then
  echo "Exists: $OUT (set FORCE=1 to overwrite secrets)"
  exit 0
fi

gen() { openssl rand -hex 24; }

cp "$EXAMPLE" "$OUT"
sed -i "s|^STAGING_DOMAIN=.*|STAGING_DOMAIN=$DOMAIN|" "$OUT"
sed -i "s|^FRAPPE_SITE=.*|FRAPPE_SITE=$DOMAIN|" "$OUT"
sed -i "s|^MARIADB_ROOT_PASSWORD=.*|MARIADB_ROOT_PASSWORD=$(gen)|" "$OUT"
sed -i "s|^MARIADB_PASSWORD=.*|MARIADB_PASSWORD=$(gen)|" "$OUT"
sed -i "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=$(gen)|" "$OUT"
sed -i "s|^MINIO_ROOT_PASSWORD=.*|MINIO_ROOT_PASSWORD=$(gen)|" "$OUT"

JWT_FILE="$DIR/.jwt_secret"
openssl rand -hex 32 > "$JWT_FILE"
chmod 600 "$JWT_FILE"

echo "Wrote $OUT and JWT secret $JWT_FILE"
echo "Apply JWT: bench --site $DOMAIN set-config agriflow_jwt_secret \"\$(cat $JWT_FILE)\""
