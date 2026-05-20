# Copyright (c) 2026, Murugan and contributors
"""Phase 24 — performance & observability metrics."""

from __future__ import annotations

import time

import frappe
from frappe.utils import add_days, now_datetime

from agriflow.project_lifecycle.install.phase20_analytics import push_success_rate, sync_trend_days
from agriflow.project_lifecycle.install.phase23_enterprise_analytics import retry_analytics, scheduler_health_summary
from agriflow.project_lifecycle.install.phase24_indexes import slow_query_hints
from agriflow.project_lifecycle.install.phase24_telemetry_aggregate import get_cached_rollup


def _timed(label: str, fn) -> tuple[any, float]:
	start = time.perf_counter()
	result = fn()
	ms = round((time.perf_counter() - start) * 1000, 2)
	return result, ms


def dashboard_latency_probe() -> dict:
	"""Measure key dashboard building blocks (ms)."""
	probes = {}

	_, probes["sla_summary_ms"] = _timed(
		"sla",
		lambda: frappe.get_attr(
			"agriflow.project_lifecycle.install.phase20_analytics.sla_summary"
		)(),
	)
	_, probes["sync_trends_ms"] = _timed("sync_trends", lambda: sync_trend_days(7))
	_, probes["push_rate_ms"] = _timed("push", lambda: push_success_rate(7))
	_, probes["telemetry_rollup_ms"] = _timed("rollup", lambda: get_cached_rollup(14))
	return probes


def queue_depth_trends(days: int = 14) -> list[dict]:
	return get_cached_rollup(days)


def push_sync_timing_analytics(days: int = 7) -> dict:
	since = add_days(now_datetime(), -days)
	sync_sessions = (
		frappe.db.count("Sync Session", {"started_on": (">=", since)})
		if frappe.db.exists("DocType", "Sync Session")
		else 0
	)
	push = push_success_rate(days)
	sync_trends = sync_trend_days(days)
	return {
		"sync_sessions": sync_sessions,
		"push_success": push,
		"daily_sync_volume": sync_trends,
	}


def centralized_ops_metrics() -> dict:
	"""Single payload for observability console."""
	latency = dashboard_latency_probe()
	return {
		"generated_at": str(now_datetime()),
		"latency_ms": latency,
		"queue_depth_trends": queue_depth_trends(14),
		"push_sync_timing": push_sync_timing_analytics(7),
		"retry_analytics": retry_analytics(7),
		"scheduler": scheduler_health_summary(),
		"slow_query_hints": slow_query_hints(),
	}


def infrastructure_cost_estimate() -> dict:
	"""Rough monthly cost drivers (relative units, not billing integration)."""
	telemetry_rows = (
		frappe.db.count("Pilot Device Telemetry")
		if frappe.db.exists("DocType", "Pilot Device Telemetry")
		else 0
	)
	sync_rows = (
		frappe.db.count("Sync Mutation Log")
		if frappe.db.exists("DocType", "Sync Mutation Log")
		else 0
	)
	push_rows = (
		frappe.db.count("Push Delivery Log")
		if frappe.db.exists("DocType", "Push Delivery Log")
		else 0
	)
	# Relative cost units for ops review (DB storage dominant)
	db_units = round((telemetry_rows * 0.5 + sync_rows * 0.3 + push_rows * 0.2) / 1000, 2)
	return {
		"telemetry_rows": telemetry_rows,
		"sync_mutation_rows": sync_rows,
		"push_log_rows": push_rows,
		"relative_db_cost_units": db_units,
		"recommendations": [
			"Run weekly phase23_retention to cap row growth",
			"Use telemetry daily rollup cache for dashboards",
			"Set Redis/cache TTL 120-300s on SLA aggregates",
			"MinIO lifecycle: expire attachments > 365d (see docs)",
		],
	}
