#!/usr/bin/env bash
# Deploy full AgriFlow backend (Phases 17–24) to bench staging/production site.
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
SITE="${FRAPPE_SITE:-staging.example.com}"

export FRAPPE_SITE="$SITE"
export FRAPPE_BENCH="$BENCH"
export AGRIFLOW_REPO="$REPO"

bash "$REPO/scripts/phase17_deploy_to_bench.sh" || true
bash "$REPO/scripts/phase18_deploy_staging.sh" || true
bash "$REPO/scripts/phase19_deploy_rollout.sh" 2>/dev/null || true
bash "$REPO/scripts/phase20_deploy_commercial.sh" 2>/dev/null || true
bash "$REPO/scripts/phase21_deploy_pilot.sh" 2>/dev/null || true
bash "$REPO/scripts/phase22_deploy_ga.sh" 2>/dev/null || true
bash "$REPO/scripts/phase24_deploy_perf.sh" 2>/dev/null || true

# Copy ops HTML consoles
APP="$BENCH/apps/agriflow/agriflow"
for page in pilot_dashboard commercial_ops_console ops_live_dashboard pilot_ops_dashboard ga_ops_console enterprise_ops_console observability_console; do
  src="$REPO/scripts/deploy/${page}.html"
  [ -f "$src" ] && cp "$src" "$APP/www/${page}.html" || true
done

cd "$BENCH"
bench --site "$SITE" set-config agriflow_min_app_version "0.24.0"
bench --site "$SITE" migrate
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase24_verify_perf.execute

echo "Backend deployed for $SITE"
