#!/usr/bin/env bash
# Phase 19 — deploy rollout backend to bench (WSL, LF endings).
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
APP="$BENCH/apps/agriflow/agriflow"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cp "$REPO/scripts/phase19_push_api.py" "$APP/api/v1/push.py"
cp "$REPO/scripts/phase19_fcm_delivery.py" "$APP/project_lifecycle/install/phase19_fcm_delivery.py"
cp "$REPO/scripts/phase19_ops_api.py" "$APP/api/v1/ops.py"
cp "$REPO/scripts/phase19_ops_alerts.py" "$APP/project_lifecycle/install/phase19_ops_alerts.py"
cp "$REPO/scripts/phase19_install.py" "$APP/project_lifecycle/install/phase19_install.py"
cp "$REPO/scripts/phase19_verify_rollout.py" "$APP/project_lifecycle/install/phase19_verify_rollout.py"
cp "$REPO/scripts/phase19_concurrent_pilot.py" "$APP/project_lifecycle/install/phase19_concurrent_pilot.py"
cp "$REPO/scripts/phase19_backup_drill.py" "$APP/project_lifecycle/install/phase19_backup_drill.py"

mkdir -p "$APP/project_lifecycle/doctype/operational_incident"
cp "$REPO/scripts/phase19_doctypes/operational_incident/operational_incident.json" \
  "$APP/project_lifecycle/doctype/operational_incident/operational_incident.json"
touch "$APP/project_lifecycle/doctype/operational_incident/__init__.py"

mkdir -p "$APP/www"
cp "$REPO/scripts/deploy/ops_live_dashboard.html" "$APP/www/ops_live_dashboard.html"

cd "$BENCH"
bench --site "$SITE" set-config agriflow_fcm_server_key simulate
bench --site "$SITE" set-config agriflow_rollout_wave pilot_a
bench --site "$SITE" set-config agriflow_min_app_version "0.19.0"
bench --site "$SITE" migrate
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase19_install.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase19_verify_rollout.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase19_concurrent_pilot.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase19_backup_drill.execute

echo "Phase 19 deployed. Live dashboard: /ops_live_dashboard"
