#!/usr/bin/env bash
# Phase 23 enterprise deployment (WSL, LF endings).
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
APP="$BENCH/apps/agriflow/agriflow"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cp "$REPO/scripts/phase23_enterprise_api.py" "$APP/api/v1/enterprise.py"
cp "$REPO/scripts/phase23_enterprise_analytics.py" "$APP/project_lifecycle/install/phase23_enterprise_analytics.py"
cp "$REPO/scripts/phase23_automation.py" "$APP/project_lifecycle/install/phase23_automation.py"
cp "$REPO/scripts/phase23_retention.py" "$APP/project_lifecycle/install/phase23_retention.py"
cp "$REPO/scripts/phase23_bootstrap.py" "$APP/project_lifecycle/install/phase23_bootstrap.py"
cp "$REPO/scripts/phase23_install.py" "$APP/project_lifecycle/install/phase23_install.py"
cp "$REPO/scripts/phase23_verify_enterprise.py" "$APP/project_lifecycle/install/phase23_verify_enterprise.py"
cp "$REPO/scripts/phase23_simulation.py" "$APP/project_lifecycle/install/phase23_simulation.py"

mkdir -p "$APP/project_lifecycle/doctype/tenant_ops_record"
cp "$REPO/scripts/phase23_doctypes/tenant_ops_record/tenant_ops_record.json" \
  "$APP/project_lifecycle/doctype/tenant_ops_record/tenant_ops_record.json"
touch "$APP/project_lifecycle/doctype/tenant_ops_record/__init__.py"

cp "$REPO/scripts/deploy/enterprise_ops_console.html" "$APP/www/enterprise_ops_console.html"

cd "$BENCH"
bench --site "$SITE" set-config agriflow_min_app_version "0.23.0"
bench --site "$SITE" set-config agriflow_telemetry_retention_days "90"
bench --site "$SITE" migrate
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase23_install.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase23_simulation.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase23_verify_enterprise.execute

echo "Phase 23 deployed. Console: /enterprise_ops_console"
