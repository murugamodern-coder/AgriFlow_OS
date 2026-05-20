#!/usr/bin/env bash
# Multi-device pilot simulation — server-side telemetry + dashboard snapshot.
set -euo pipefail

BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"

cd "$BENCH"

echo "=== Phase 17 verify ==="
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase17_verify_pilot.execute

echo "=== Dashboard snapshot (Administrator) ==="
bench --site "$SITE" execute agriflow.project_lifecycle.install.phase17_pilot_simulation.execute
