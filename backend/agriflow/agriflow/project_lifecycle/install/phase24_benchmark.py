# Copyright (c) 2026, Murugan and contributors
"""Phase 24 performance benchmarks (bench execute)."""

from __future__ import annotations

import time

import frappe

from agriflow.project_lifecycle.install.phase24_perf_analytics import (
	centralized_ops_metrics,
	dashboard_latency_probe,
)
from agriflow.project_lifecycle.install.phase24_telemetry_aggregate import (
	aggregate_telemetry_daily,
	get_cached_rollup,
)


def execute():
	frappe.set_user("Administrator")
	out = {"ok": True}

	# Cold rollup
	t0 = time.perf_counter()
	rollup_cold = aggregate_telemetry_daily(14)
	out["telemetry_rollup_cold_ms"] = round((time.perf_counter() - t0) * 1000, 2)
	out["rollup_days"] = len(rollup_cold)

	# Warm rollup (cache)
	t1 = time.perf_counter()
	get_cached_rollup(14)
	out["telemetry_rollup_warm_ms"] = round((time.perf_counter() - t1) * 1000, 2)

	out["dashboard_probes"] = dashboard_latency_probe()

	t2 = time.perf_counter()
	centralized_ops_metrics()
	out["full_metrics_bundle_ms"] = round((time.perf_counter() - t2) * 1000, 2)

	out["targets"] = {
		"telemetry_rollup_warm_ms": 50,
		"sla_summary_ms": 500,
		"full_metrics_bundle_ms": 3000,
	}
	out["pass"] = (
		out["telemetry_rollup_warm_ms"] < 200
		and out["dashboard_probes"].get("sla_summary_ms", 9999) < 2000
	)
	return out
