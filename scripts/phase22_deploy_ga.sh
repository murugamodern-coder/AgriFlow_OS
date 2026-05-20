#!/usr/bin/env bash
# Phase 22 GA deployment (WSL, LF endings).
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
APP="$BENCH/apps/agriflow/agriflow"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cp "$REPO/scripts/phase22_ga_api.py" "$APP/api/v1/ga.py"
cp "$REPO/scripts/phase22_ga_analytics.py" "$APP/project_lifecycle/install/phase22_ga_analytics.py"
cp "$REPO/scripts/phase22_ga_escalations.py" "$APP/project_lifecycle/install/phase22_ga_escalations.py"
cp "$REPO/scripts/phase22_release_governance.py" "$APP/project_lifecycle/install/phase22_release_governance.py"
cp "$REPO/scripts/phase22_backup_verify.py" "$APP/project_lifecycle/install/phase22_backup_verify.py"
cp "$REPO/scripts/phase22_install.py" "$APP/project_lifecycle/install/phase22_install.py"
cp "$REPO/scripts/phase22_verify_ga.py" "$APP/project_lifecycle/install/phase22_verify_ga.py"
cp "$REPO/scripts/phase22_simulation.py" "$APP/project_lifecycle/install/phase22_simulation.py"

mkdir -p "$APP/project_lifecycle/doctype/ga_release_signoff"
cp "$REPO/scripts/phase22_doctypes/ga_release_signoff/ga_release_signoff.json" \
  "$APP/project_lifecycle/doctype/ga_release_signoff/ga_release_signoff.json"
touch "$APP/project_lifecycle/doctype/ga_release_signoff/__init__.py"

cp "$REPO/scripts/phase22_doctypes/support_ticket/support_ticket.json" \
  "$APP/project_lifecycle/doctype/support_ticket/support_ticket.json"

cp "$REPO/scripts/deploy/ga_ops_console.html" "$APP/www/ga_ops_console.html"

cd "$BENCH"
bench --site "$SITE" set-config agriflow_min_app_version "0.22.0"
bench --site "$SITE" migrate
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase22_install.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase22_simulation.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase22_verify_ga.execute

echo "Phase 22 deployed. Console: /ga_ops_console"
