#!/usr/bin/env bash
# Phase 24 performance deployment (WSL, LF endings).
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
APP="$BENCH/apps/agriflow/agriflow"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cp "$REPO/scripts/phase24_observability_api.py" "$APP/api/v1/observability.py"
cp "$REPO/scripts/phase24_perf_analytics.py" "$APP/project_lifecycle/install/phase24_perf_analytics.py"
cp "$REPO/scripts/phase24_indexes.py" "$APP/project_lifecycle/install/phase24_indexes.py"
cp "$REPO/scripts/phase24_telemetry_aggregate.py" "$APP/project_lifecycle/install/phase24_telemetry_aggregate.py"
cp "$REPO/scripts/phase24_retention_batch.py" "$APP/project_lifecycle/install/phase24_retention_batch.py"
cp "$REPO/scripts/phase24_cache_tuning.py" "$APP/project_lifecycle/install/phase24_cache_tuning.py"
cp "$REPO/scripts/phase24_self_check.py" "$APP/project_lifecycle/install/phase24_self_check.py"
cp "$REPO/scripts/phase24_benchmark.py" "$APP/project_lifecycle/install/phase24_benchmark.py"
cp "$REPO/scripts/phase24_install.py" "$APP/project_lifecycle/install/phase24_install.py"
cp "$REPO/scripts/phase24_verify_perf.py" "$APP/project_lifecycle/install/phase24_verify_perf.py"

cp "$REPO/scripts/deploy/observability_console.html" "$APP/www/observability_console.html"

cd "$BENCH"
bench --site "$SITE" set-config agriflow_min_app_version "0.24.0"
bench --site "$SITE" set-config agriflow_dashboard_bundle_ttl "120"
bench --site "$SITE" set-config agriflow_sla_cache_ttl "300"
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase24_install.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase24_benchmark.execute
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase24_verify_perf.execute

echo "Phase 24 deployed. Console: /observability_console"
