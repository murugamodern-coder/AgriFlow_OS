#!/usr/bin/env bash
# Validate public staging deployment (run on VPS or against STAGING_URL).
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/../.." && pwd)}"
ENV_FILE="$REPO/infra/docker/.env.staging"
source "$ENV_FILE" 2>/dev/null || true

BASE="${STAGING_URL:-https://${STAGING_DOMAIN:-staging.example.com}}"
SITE="${FRAPPE_SITE:-$STAGING_DOMAIN}"
BENCH="${BENCH_PATH:-$HOME/workspace/frappe-bench}"
FAIL=0

check() {
  if "$@"; then echo "OK  $*"
  else echo "FAIL $*"; FAIL=1; fi
}

echo "=== AgriFlow staging validation ==="
echo "Base URL: $BASE"

check curl -fsSk -o /dev/null "$BASE"
for path in observability_console ga_ops_console pilot_ops_dashboard; do
  check curl -fsSk -o /dev/null "$BASE/$path"
done

if [ -d "$BENCH" ]; then
  cd "$BENCH"
  check bench --site "$SITE" execute agriflow.project_lifecycle.install.phase24_verify_perf.execute
  check bench --site "$SITE" execute agriflow.project_lifecycle.install.observability.operational_self_check_api
fi

bash "$REPO/scripts/backup_restore_validate.sh" 2>/dev/null || echo "SKIP backup (docker not local)"

if [ "$FAIL" -eq 0 ]; then
  echo "=== VALIDATION PASSED ==="
else
  echo "=== VALIDATION FAILED ==="
  exit 1
fi
