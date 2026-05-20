#!/usr/bin/env bash
# End-to-end public staging deployment (run on VPS after setup_vps.sh).
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/../.." && pwd)}"
DOCKER_DIR="$REPO/infra/docker"
ENV_FILE="$DOCKER_DIR/.env.staging"

cd "$DOCKER_DIR"

if [ ! -f "$ENV_FILE" ]; then
  STAGING_DOMAIN="${STAGING_DOMAIN:-staging.example.com}" \
    bash "$REPO/infra/scripts/generate_secrets.sh" "$ENV_FILE"
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

echo "==> Starting infrastructure stack"
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d

echo "==> Deploy backend to bench"
export FRAPPE_SITE FRAPPE_BENCH="${BENCH_PATH:-$HOME/workspace/frappe-bench}"
bash "$REPO/scripts/production_deploy_backend.sh"

echo "==> Configure bench site"
bash "$REPO/infra/scripts/setup_bench_staging_site.sh"

echo "==> Install backup cron"
bash "$REPO/infra/scripts/install_backup_cron.sh"

echo ""
echo "Next steps:"
echo "  1. Point DNS A record: $STAGING_DOMAIN -> this server IP"
echo "  2. STAGING_DOMAIN=$STAGING_DOMAIN bash $REPO/infra/scripts/certbot_vps.sh"
echo "  3. bench start && bench schedule (or systemd units)"
echo "  4. bash $REPO/infra/scripts/validate_staging_deployment.sh"
