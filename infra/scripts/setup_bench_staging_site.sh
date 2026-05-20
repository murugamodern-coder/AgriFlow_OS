#!/usr/bin/env bash
# Wire host frappe-bench to Docker MariaDB/Redis and configure AgriFlow staging site.
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/../.." && pwd)}"
DOCKER_DIR="$REPO/infra/docker"
ENV_FILE="${ENV_FILE:-$DOCKER_DIR/.env.staging}"
BENCH="${BENCH_PATH:-$HOME/workspace/frappe-bench}"

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

SITE="${FRAPPE_SITE:?FRAPPE_SITE required}"
JWT_FILE="${JWT_FILE:-$DOCKER_DIR/.jwt_secret}"

cd "$BENCH"

if ! bench --site "$SITE" list-apps &>/dev/null 2>&1; then
  echo "Creating site $SITE (adjust if site exists)..."
  bench new-site "$SITE" \
    --db-name "${MARIADB_DATABASE}" \
    --db-password "${MARIADB_PASSWORD}" \
    --admin-password "${ADMIN_PASSWORD:-admin}" \
    --mariadb-root-password "${MARIADB_ROOT_PASSWORD}" \
    --db-host 127.0.0.1 \
    --db-port "${MARIADB_PUBLISH_PORT:-3307}" \
    --no-mariadb-socket || true
fi

bench --site "$SITE" install-app agriflow 2>/dev/null || true

if [ -f "$JWT_FILE" ]; then
  bench --site "$SITE" set-config agriflow_jwt_secret "$(cat "$JWT_FILE")"
fi
bench --site "$SITE" set-config agriflow_auth_mode jwt
bench --site "$SITE" set-config agriflow_min_app_version "${AGRIFLOW_MIN_APP_VERSION:-0.24.0}"
bench --site "$SITE" set-config agriflow_rollout_wave "${AGRIFLOW_ROLLOUT_WAVE:-staging}"
bench --site "$SITE" set-config agriflow_fcm_server_key "${AGRIFLOW_FCM_SERVER_KEY:-simulate}"
bench --site "$SITE" set-config agriflow_telemetry_retention_days 90
bench --site "$SITE" set-config agriflow_dashboard_bundle_ttl 120

# Redis (common_site_config)
REDIS_URL="redis://:${REDIS_PASSWORD}@127.0.0.1:${REDIS_PUBLISH_PORT:-6380}"
python3 - "$BENCH/sites/common_site_config.json" "$REDIS_URL" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
url = sys.argv[2]
cfg = json.loads(p.read_text()) if p.exists() else {}
for k in ("redis_cache", "redis_queue", "redis_socketio"):
    cfg[k] = url
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(cfg, indent=1))
PY

bench --site "$SITE" migrate
echo "Site $SITE configured. Start: bench start && bench schedule"
