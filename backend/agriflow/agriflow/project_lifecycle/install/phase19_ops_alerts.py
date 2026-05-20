# Copyright (c) 2026, Murugan and contributors
"""Automated ops alerts — queue, sync, inventory → Operational Incident."""

from __future__ import annotations

import json
from datetime import date, datetime

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.pilot_ops import _queue_backlog_metrics, _sync_health_window
from agriflow.project_lifecycle.install.phase16_inventory_reconcile import execute as inventory_reconcile


def _json_safe(obj):
	return json.loads(frappe.as_json(obj))


def _open_incident(
	*,
	incident_type: str,
	severity: str,
	summary: str,
	details: dict,
) -> str | None:
	"""Dedupe: skip if same type+summary open in last 24h."""
	existing = frappe.db.sql(
		"""
		SELECT name FROM `tabOperational Incident`
		WHERE incident_type = %(t)s AND summary = %(s)s
		  AND status IN ('open', 'investigating')
		  AND recorded_on >= DATE_SUB(NOW(), INTERVAL 1 DAY)
		LIMIT 1
		""",
		{"t": incident_type, "s": summary},
	)
	if existing:
		return None
	if not frappe.db.exists("DocType", "Operational Incident"):
		return None
	doc = frappe.get_doc(
		{
			"doctype": "Operational Incident",
			"incident_type": incident_type,
			"severity": severity,
			"status": "open",
			"summary": summary,
			"details_json": _json_safe(details),
			"recorded_on": now_datetime(),
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def execute():
	alerts = []
	incidents = []

	backlog = _queue_backlog_metrics()
	if backlog.get("total_pending", 0) > 10:
		alerts.append({"code": "QUEUE_BACKLOG_HIGH", "pending": backlog["total_pending"]})
		iid = _open_incident(
			incident_type="queue_backlog",
			severity="high",
			summary=f"Queue backlog {backlog['total_pending']} pending",
			details=backlog,
		)
		if iid:
			incidents.append(iid)

	if backlog.get("total_conflicts", 0) > 0:
		alerts.append({"code": "QUEUE_CONFLICTS", "conflicts": backlog["total_conflicts"]})
		iid = _open_incident(
			incident_type="queue_backlog",
			severity="medium",
			summary=f"Queue conflicts {backlog['total_conflicts']}",
			details=backlog,
		)
		if iid:
			incidents.append(iid)

	sync = _sync_health_window()
	if sync.get("failure_rate", 0) > 0.15 and sync.get("mutations_total", 0) > 5:
		alerts.append({"code": "SYNC_FAILURE_RATE", "rate": sync["failure_rate"]})
		iid = _open_incident(
			incident_type="sync_failure",
			severity="high",
			summary=f"Sync failure rate {sync['failure_rate']}",
			details=sync,
		)
		if iid:
			incidents.append(iid)

	inv = inventory_reconcile()
	if not inv.get("ok"):
		alerts.append({"code": "INVENTORY_MISMATCH", "mismatches": inv.get("mismatches")})
		iid = _open_incident(
			incident_type="inventory_mismatch",
			severity="critical",
			summary="Inventory ledger mismatch detected",
			details=inv,
		)
		if iid:
			incidents.append(iid)

	since = frappe.utils.add_days(now_datetime(), -1)
	push_failed = frappe.db.sql(
		"""
		SELECT COUNT(*) FROM `tabPush Delivery Log`
		WHERE status = 'failed' AND recorded_on >= %(since)s
		""",
		{"since": since},
	)[0][0]
	if push_failed > 3:
		alerts.append({"code": "PUSH_FAILURES", "count": push_failed})
		iid = _open_incident(
			incident_type="push_failure",
			severity="medium",
			summary=f"Push failures in 24h: {push_failed}",
			details={"count": push_failed},
		)
		if iid:
			incidents.append(iid)

	frappe.db.commit()
	return {
		"ok": len(alerts) == 0,
		"alerts": alerts,
		"incidents_created": incidents,
		"checked_at": str(now_datetime()),
	}
