# Copyright (c) 2026, Murugan and contributors
"""Phase 24 — batched retention deletes (lower memory, steady throughput)."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime

BATCH_SIZE = 500
MAX_PER_RUN = 5000


def _delete_in_batches(doctype: str, filters: dict) -> int:
	total = 0
	while total < MAX_PER_RUN:
		names = frappe.get_all(doctype, filters=filters, pluck="name", limit=BATCH_SIZE)
		if not names:
			break
		for name in names:
			frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
		total += len(names)
		frappe.db.commit()
	return total


def batched_archive_telemetry(days: int = 90) -> dict:
	if not frappe.db.exists("DocType", "Pilot Device Telemetry"):
		return {"archived": 0}
	cutoff = add_days(now_datetime(), -days)
	n = _delete_in_batches("Pilot Device Telemetry", {"reported_at": ("<", cutoff)})
	return {"archived": n, "batched": True, "cutoff_days": days}


def batched_archive_sync_logs(days: int = 180) -> dict:
	if not frappe.db.exists("DocType", "Sync Mutation Log"):
		return {"archived": 0}
	cutoff = add_days(now_datetime(), -days)
	n = _delete_in_batches("Sync Mutation Log", {"processed_on": ("<", cutoff)})
	return {"archived": n, "batched": True, "cutoff_days": days}


def execute():
	frappe.set_user("Administrator")
	return {
		"telemetry": batched_archive_telemetry(),
		"sync_logs": batched_archive_sync_logs(),
	}
