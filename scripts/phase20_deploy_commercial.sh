#!/usr/bin/env bash
# Phase 20 commercial deployment (WSL, LF endings).
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
APP="$BENCH/apps/agriflow/agriflow"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cp "$REPO/scripts/phase20_commercial_api.py" "$APP/api/v1/commercial.py"
cp "$REPO/scripts/phase20_analytics.py" "$APP/project_lifecycle/install/phase20_analytics.py"
cp "$REPO/scripts/phase20_customer_onboarding.py" "$APP/project_lifecycle/install/phase20_customer_onboarding.py"
cp "$REPO/scripts/phase20_demo_customer.py" "$APP/project_lifecycle/install/phase20_demo_customer.py"
cp "$REPO/scripts/phase20_install.py" "$APP/project_lifecycle/install/phase20_install.py"
cp "$REPO/scripts/phase20_verify_commercial.py" "$APP/project_lifecycle/install/phase20_verify_commercial.py"
cp "$REPO/scripts/phase19_fcm_delivery.py" "$APP/project_lifecycle/install/phase19_fcm_delivery.py"
cp "$REPO/scripts/phase19_push_api.py" "$APP/api/v1/push.py"

mkdir -p "$APP/project_lifecycle/doctype/customer_onboarding"
cp "$REPO/scripts/phase20_doctypes/customer_onboarding/customer_onboarding.json" \
  "$APP/project_lifecycle/doctype/customer_onboarding/customer_onboarding.json"
touch "$APP/project_lifecycle/doctype/customer_onboarding/__init__.py"

mkdir -p "$APP/project_lifecycle/doctype/support_ticket"
cp "$REPO/scripts/phase20_doctypes/support_ticket/support_ticket.json" \
  "$APP/project_lifecycle/doctype/support_ticket/support_ticket.json"
touch "$APP/project_lifecycle/doctype/support_ticket/__init__.py"

cp "$REPO/scripts/deploy/commercial_ops_console.html" "$APP/www/commercial_ops_console.html"

cd "$BENCH"
bench --site "$SITE" set-config agriflow_min_app_version "0.20.0"
bench --site "$SITE" migrate
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase20_install.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase20_demo_customer.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase20_verify_commercial.execute

echo "Phase 20 deployed. Console: /commercial_ops_console"
