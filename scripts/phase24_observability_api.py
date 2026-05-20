# Copyright (c) 2026, Murugan and contributors
"""Phase 24 — observability & performance API."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.response import success
from agriflow.project_lifecycle.install.phase22_backup_verify import verify_backup_readiness
from agriflow.project_lifecycle.install.phase24_cache_tuning import (
	apply_recommended_site_config,
	cache_tuning_summary,
)
from agriflow.project_lifecycle.install.phase24_indexes import ensure_performance_indexes, slow_query_hints
from agriflow.project_lifecycle.install.phase24_perf_analytics import (
	centralized_ops_metrics,
	dashboard_latency_probe,
	infrastructure_cost_estimate,
	push_sync_timing_analytics,
	queue_depth_trends,
)
from agriflow.project_lifecycle.install.phase24_retention_batch import (
	batched_archive_sync_logs,
	batched_archive_telemetry,
)
from agriflow.project_lifecycle.install.phase24_self_check import operational_self_check
from agriflow.project_lifecycle.install.phase24_telemetry_aggregate import execute as refresh_rollup


def _admin_only():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)


@frappe.whitelist(allow_guest=False)
def ops_metrics_dashboard():
	"""Centralized operational metrics (cached bundle)."""
	_admin_only()
	cache_key = "agriflow_ops_metrics_bundle"
	cached = frappe.cache().get_value(cache_key)
	if cached:
		return success(cached)
	payload = centralized_ops_metrics()
	frappe.cache().set_value(
		cache_key,
		payload,
		expires_in_sec=int(frappe.conf.get("agriflow_dashboard_bundle_ttl") or 120),
	)
	return success(payload)


@frappe.whitelist(allow_guest=False)
def dashboard_latency():
	_admin_only()
	return success(dashboard_latency_probe())


@frappe.whitelist(allow_guest=False)
def queue_throughput_metrics():
	_admin_only()
	return success(
		{
			"depth_trends": queue_depth_trends(14),
			"push_sync": push_sync_timing_analytics(7),
		}
	)


@frappe.whitelist(allow_guest=False)
def infrastructure_cost_summary():
	_admin_only()
	return success(infrastructure_cost_estimate())


@frappe.whitelist(allow_guest=False)
def ensure_db_indexes():
	_admin_only()
	return success({"indexes": ensure_performance_indexes(), "hints": slow_query_hints()})


@frappe.whitelist(allow_guest=False)
def refresh_telemetry_rollup():
	_admin_only()
	return success(refresh_rollup())


@frappe.whitelist(allow_guest=False)
def run_batched_retention():
	_admin_only()
	return success(
		{
			"telemetry": batched_archive_telemetry(),
			"sync_logs": batched_archive_sync_logs(),
		}
	)


@frappe.whitelist(allow_guest=False)
def cache_tuning():
	_admin_only()
	return success(cache_tuning_summary())


@frappe.whitelist(allow_guest=False)
def apply_cache_tuning():
	_admin_only()
	return success(apply_recommended_site_config())


@frappe.whitelist(allow_guest=False)
def operational_self_check_api():
	_admin_only()
	return success(operational_self_check())


@frappe.whitelist(allow_guest=False)
def recovery_drill_automation():
	_admin_only()
	result = verify_backup_readiness()
	result["drill_steps"] = [
		"bench --site <site> backup --with-files",
		"Restore on staging quarterly",
		"Verify login + sync after restore",
	]
	result["automated_at"] = str(now_datetime())
	return success(result)
