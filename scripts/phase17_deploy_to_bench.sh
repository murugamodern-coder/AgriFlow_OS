#!/usr/bin/env bash
# Deploy Phase 17 pilot ops to local Frappe bench (WSL). Use LF line endings.
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
APP="$BENCH/apps/agriflow/agriflow"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cp "$REPO/scripts/phase17_pilot_ops_api.py" "$APP/api/v1/pilot_ops.py"
cp "$REPO/scripts/phase17_install.py" "$APP/project_lifecycle/install/phase17_install.py"
cp "$REPO/scripts/phase17_verify_pilot.py" "$APP/project_lifecycle/install/phase17_verify_pilot.py"
cp "$REPO/scripts/phase17_pilot_simulation.py" "$APP/project_lifecycle/install/phase17_pilot_simulation.py"

for dt in pilot_device_telemetry pilot_operational_feedback operational_log; do
  mkdir -p "$APP/project_lifecycle/doctype/$dt"
  cp "$REPO/scripts/phase17_doctypes/$dt/$dt.json" "$APP/project_lifecycle/doctype/$dt/$dt.json"
  touch "$APP/project_lifecycle/doctype/$dt/__init__.py"
done

mkdir -p "$APP/www"
cp "$REPO/scripts/deploy/pilot_dashboard.html" "$APP/www/pilot_dashboard.html"

cd "$BENCH"
bench --site "$SITE" migrate
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase17_install.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase17_verify_pilot.execute

echo "Phase 17 deployed. Dashboard: http://${SITE}/pilot_dashboard"
