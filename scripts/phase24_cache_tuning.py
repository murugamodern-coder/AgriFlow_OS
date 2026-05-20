# Copyright (c) 2026, Murugan and contributors
"""Phase 24 — Redis/cache TTL recommendations and apply."""

from __future__ import annotations

import frappe

DEFAULT_TTLS = {
	"agriflow_sla_cache_ttl": 300,
	"agriflow_tenant_sla_cache_ttl": 180,
	"agriflow_dashboard_bundle_ttl": 120,
	"agriflow_telemetry_rollup_ttl": 3600,
}


def cache_tuning_summary() -> dict:
	applied = {}
	for key, default in DEFAULT_TTLS.items():
		applied[key] = int(frappe.conf.get(key) or default)
	return {
		"ttls_sec": applied,
		"redis_cache_enabled": bool(frappe.cache()),
		"notes": [
			"Increase SLA TTL when dashboard traffic is high",
			"Telemetry rollup TTL 3600s avoids full table scans",
			"Invalidate on major data fixes via bench clear-cache",
		],
	}


def apply_recommended_site_config() -> dict:
	"""Set recommended TTLs on current site (non-destructive)."""
	for key, val in DEFAULT_TTLS.items():
		frappe.conf[key] = val
	return cache_tuning_summary()


def execute():
	return apply_recommended_site_config()
