#!/usr/bin/env bash
# Phase 18 — deploy backend + staging stack hints (WSL). LF line endings required.
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
APP="$BENCH/apps/agriflow/agriflow"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cp "$REPO/scripts/phase18_push_api.py" "$APP/api/v1/push.py"
cp "$REPO/scripts/phase18_readiness_api.py" "$APP/api/v1/readiness.py"
cp "$REPO/scripts/phase18_install.py" "$APP/project_lifecycle/install/phase18_install.py"
cp "$REPO/scripts/phase18_verify_production.py" "$APP/project_lifecycle/install/phase18_verify_production.py"
cp "$REPO/scripts/phase18_permission_audit.py" "$APP/project_lifecycle/install/phase18_permission_audit.py"
cp "$REPO/scripts/phase18_offline_survivability.py" "$APP/project_lifecycle/install/phase18_offline_survivability.py"

for dt in device_push_token push_delivery_log; do
  mkdir -p "$APP/project_lifecycle/doctype/$dt"
  cp "$REPO/scripts/phase18_doctypes/$dt/$dt.json" "$APP/project_lifecycle/doctype/$dt/$dt.json"
  touch "$APP/project_lifecycle/doctype/$dt/__init__.py"
done

cd "$BENCH"
bench --site "$SITE" set-config agriflow_min_app_version "0.18.0" || true
bench --site "$SITE" migrate
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase18_install.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase18_verify_production.execute

echo "Phase 18 backend deployed. Optional: docker compose -f $REPO/infra/docker/docker-compose.staging.yml up -d"
