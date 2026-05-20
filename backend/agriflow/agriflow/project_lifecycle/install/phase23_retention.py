# Copyright (c) 2026, Murugan and contributors
"""Phase 23 — telemetry/sync retention and archival policies."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime

DEFAULT_TELEMETRY_DAYS = 90
DEFAULT_SYNC_LOG_DAYS = 180
DEFAULT_PUSH_LOG_DAYS = 60


def retention_policy_summary() -> dict:
	return {
		"telemetry_days": int(frappe.conf.get("agriflow_telemetry_retention_days") or DEFAULT_TELEMETRY_DAYS),
		"sync_log_days": int(frappe.conf.get("agriflow_sync_log_retention_days") or DEFAULT_SYNC_LOG_DAYS),
		"push_log_days": int(frappe.conf.get("agriflow_push_log_retention_days") or DEFAULT_PUSH_LOG_DAYS),
		"queue_archive_note": "Mobile queue is device-local; server tracks Sync Mutation Log",
	}


def archive_old_telemetry(days: int | None = None) -> dict:
	days = days or int(frappe.conf.get("agriflow_telemetry_retention_days") or DEFAULT_TELEMETRY_DAYS)
	if not frappe.db.exists("DocType", "Pilot Device Telemetry"):
		return {"archived": 0, "reason": "no_doctype"}
	cutoff = add_days(now_datetime(), -days)
	names = frappe.get_all(
		"Pilot Device Telemetry",
		filters={"reported_at": ("<", cutoff)},
		pluck="name",
		limit=5000,
	)
	for name in names:
		frappe.delete_doc("Pilot Device Telemetry", name, force=True, ignore_permissions=True)
	frappe.db.commit()
	return {"archived": len(names), "cutoff_days": days}


def archive_sync_mutation_logs(days: int | None = None) -> dict:
	days = days or int(frappe.conf.get("agriflow_sync_log_retention_days") or DEFAULT_SYNC_LOG_DAYS)
	if not frappe.db.exists("DocType", "Sync Mutation Log"):
		return {"archived": 0}
	cutoff = add_days(now_datetime(), -days)
	names = frappe.get_all(
		"Sync Mutation Log",
		filters={"processed_on": ("<", cutoff)},
		pluck="name",
		limit=5000,
	)
	for name in names:
		frappe.delete_doc("Sync Mutation Log", name, force=True, ignore_permissions=True)
	frappe.db.commit()
	return {"archived": len(names), "cutoff_days": days}


def cleanup_push_delivery_logs(days: int | None = None) -> dict:
	days = days or int(frappe.conf.get("agriflow_push_log_retention_days") or DEFAULT_PUSH_LOG_DAYS)
	if not frappe.db.exists("DocType", "Push Delivery Log"):
		return {"archived": 0}
	cutoff = add_days(now_datetime(), -days)
	names = frappe.get_all(
		"Push Delivery Log",
		filters={"recorded_on": ("<", cutoff), "status": ("in", ("sent", "failed"))},
		pluck="name",
		limit=5000,
	)
	for name in names:
		frappe.delete_doc("Push Delivery Log", name, force=True, ignore_permissions=True)
	frappe.db.commit()
	return {"archived": len(names), "cutoff_days": days}


def execute():
	"""Weekly retention job."""
	frappe.set_user("Administrator")
	return {
		"policy": retention_policy_summary(),
		"telemetry": archive_old_telemetry(),
		"sync_logs": archive_sync_mutation_logs(),
		"push_logs": cleanup_push_delivery_logs(),
	}
