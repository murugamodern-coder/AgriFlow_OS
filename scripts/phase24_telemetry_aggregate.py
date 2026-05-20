# Copyright (c) 2026, Murugan and contributors
"""Phase 24 — daily telemetry rollup (reduces dashboard scan cost)."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime

CACHE_KEY = "agriflow_telemetry_daily_rollup"
CACHE_TTL = 3600


def aggregate_telemetry_daily(days: int = 14) -> list[dict]:
	if not frappe.db.exists("DocType", "Pilot Device Telemetry"):
		return []
	since = add_days(now_datetime(), -days)
	rows = frappe.db.sql(
		"""
		SELECT DATE(reported_at) AS day,
			COUNT(*) AS samples,
			COUNT(DISTINCT device_id) AS devices,
			ROUND(AVG(queue_pending), 2) AS avg_pending,
			ROUND(AVG(queue_conflict), 2) AS avg_conflict,
			ROUND(AVG(queue_failed), 2) AS avg_failed
		FROM `tabPilot Device Telemetry`
		WHERE reported_at >= %(since)s
		GROUP BY DATE(reported_at)
		ORDER BY day
		""",
		{"since": since},
		as_dict=True,
	)
	return rows


def get_cached_rollup(days: int = 14) -> list[dict]:
	cached = frappe.cache().get_value(CACHE_KEY)
	if cached is not None:
		return cached
	rows = aggregate_telemetry_daily(days)
	frappe.cache().set_value(CACHE_KEY, rows, expires_in_sec=CACHE_TTL)
	return rows


def execute():
	rows = aggregate_telemetry_daily()
	frappe.cache().set_value(CACHE_KEY, rows, expires_in_sec=CACHE_TTL)
	return {"days": len(rows), "rollup": rows}
