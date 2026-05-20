# Copyright (c) 2026, Murugan and contributors
"""Phase 24 — recommended DB indexes for ops tables."""

from __future__ import annotations

import frappe

INDEX_DDL = [
	(
		"tabPilot Device Telemetry",
		"agriflow_pdt_reported_device",
		"(`reported_at`, `device_id`)",
	),
	(
		"tabSync Mutation Log",
		"agriflow_sml_processed_status",
		"(`processed_on`, `status`)",
	),
	(
		"tabPush Delivery Log",
		"agriflow_pdl_recorded_status",
		"(`recorded_on`, `status`)",
	),
	(
		"tabOperational Incident",
		"agriflow_oi_type_status",
		"(`incident_type`, `status`, `recorded_on`)",
	),
	(
		"tabSupport Ticket",
		"agriflow_st_status_opened",
		"(`status`, `opened_on`)",
	),
]


def _index_exists(table: str, index_name: str) -> bool:
	rows = frappe.db.sql(
		f"SHOW INDEX FROM `{table}` WHERE Key_name = %(name)s",
		{"name": index_name},
	)
	return bool(rows)


def ensure_performance_indexes() -> list[str]:
	results = []
	for table, index_name, columns in INDEX_DDL:
		if not frappe.db.sql(f"SHOW TABLES LIKE '{table}'", as_list=True):
			results.append(f"skip:{table}")
			continue
		if _index_exists(table, index_name):
			results.append(f"exists:{index_name}")
			continue
		try:
			frappe.db.sql_ddl(
				f"ALTER TABLE `{table}` ADD INDEX `{index_name}` {columns}"
			)
			results.append(f"created:{index_name}")
		except Exception as exc:
			results.append(f"failed:{index_name}:{str(exc)[:80]}")
	frappe.db.commit()
	return results


def slow_query_hints() -> list[dict]:
	"""Document known heavy queries and index coverage."""
	return [
		{
			"id": "device_health_latest",
			"table": "tabPilot Device Telemetry",
			"index": "agriflow_pdt_reported_device",
			"note": "MAX(reported_at) per device_id",
		},
		{
			"id": "sync_trend_daily",
			"table": "tabSync Mutation Log",
			"index": "agriflow_sml_processed_status",
			"note": "GROUP BY DATE(processed_on)",
		},
		{
			"id": "push_success_7d",
			"table": "tabPush Delivery Log",
			"index": "agriflow_pdl_recorded_status",
			"note": "status filter + recorded_on range",
		},
	]


def execute():
	return {"indexes": ensure_performance_indexes(), "hints": slow_query_hints()}
