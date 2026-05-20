#!/usr/bin/env bash
# Phase 21 pilot operations deployment (WSL, LF endings).
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
APP="$BENCH/apps/agriflow/agriflow"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cp "$REPO/scripts/phase21_pilot_api.py" "$APP/api/v1/pilot.py"
cp "$REPO/scripts/phase21_analytics.py" "$APP/project_lifecycle/install/phase21_analytics.py"
cp "$REPO/scripts/phase21_install.py" "$APP/project_lifecycle/install/phase21_install.py"
cp "$REPO/scripts/phase21_verify_pilot_ops.py" "$APP/project_lifecycle/install/phase21_verify_pilot_ops.py"
cp "$REPO/scripts/phase21_simulation.py" "$APP/project_lifecycle/install/phase21_simulation.py"
cp "$REPO/scripts/phase20_customer_onboarding.py" "$APP/project_lifecycle/install/phase20_customer_onboarding.py"
cp "$REPO/scripts/phase20_analytics.py" "$APP/project_lifecycle/install/phase20_analytics.py"
cp "$REPO/scripts/phase19_fcm_delivery.py" "$APP/project_lifecycle/install/phase19_fcm_delivery.py"

cp "$REPO/scripts/deploy/pilot_ops_dashboard.html" "$APP/www/pilot_ops_dashboard.html"

cd "$BENCH"
bench --site "$SITE" set-config agriflow_min_app_version "0.21.0"
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase21_install.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase21_simulation.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase21_verify_pilot_ops.execute

echo "Phase 21 deployed. Dashboard: /pilot_ops_dashboard"
