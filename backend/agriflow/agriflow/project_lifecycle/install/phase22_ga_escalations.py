# Copyright (c) 2026, Murugan and contributors
"""Phase 22 — automated SLA / stale-device escalations."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime, time_diff_in_hours

from agriflow.project_lifecycle.install.phase19_ops_alerts import _open_incident
from agriflow.project_lifecycle.install.phase21_analytics import stale_device_followups
from agriflow.project_lifecycle.install.phase22_ga_analytics import (
	push_anomaly_detection,
	queue_anomaly_detection,
)
from agriflow.project_lifecycle.install.phase21_analytics import support_response_metrics


def _escalate_support_ticket(ticket_id: str, assign_to: str | None = None) -> None:
	updates = {"status": "escalated", "priority": "high"}
	if assign_to:
		updates["assigned_to"] = assign_to
	frappe.db.set_value("Support Ticket", ticket_id, updates)


def auto_escalate_sla_breaches(target_hours: float = 48.0) -> dict:
	"""Escalate open tickets older than target_hours."""
	if not frappe.db.exists("DocType", "Support Ticket"):
		return {"escalated": 0}
	rows = frappe.get_all(
		"Support Ticket",
		filters={"status": "open"},
		fields=["name", "opened_on", "priority"],
	)
	escalated = []
	for row in rows:
		if not row.opened_on:
			continue
		age = time_diff_in_hours(now_datetime(), row.opened_on)
		breach = age >= target_hours or (
			row.priority == "critical" and age >= min(target_hours / 2, 4.0)
		)
		if not breach:
			continue
		_escalate_support_ticket(row.name)
		escalated.append(row.name)
		if frappe.db.exists("DocType", "Operational Incident"):
			_open_incident(
				incident_type="sla_breach",
				severity="high",
				summary=f"SLA breach ticket {row.name}",
				details={"ticket": row.name, "age_hours": age},
			)
	return {"escalated": len(escalated), "ticket_ids": escalated}


def auto_escalate_stale_devices(stale_hours: int = 48) -> dict:
	"""Create incidents + optional tickets for stale devices."""
	followups = stale_device_followups(stale_hours=stale_hours)
	created = []
	for d in followups:
		if d.get("follow_up_status") == "acknowledged":
			continue
		iid = _open_incident(
			incident_type="stale_device",
			severity="medium",
			summary=f"Stale device {d.get('device_id')}",
			details=d,
		)
		if iid:
			created.append(iid)
	return {"incidents": created, "devices": len(followups)}


def run_anomaly_escalations() -> dict:
	"""Queue + push anomalies → incidents."""
	incidents = []
	q = queue_anomaly_detection()
	if q.get("anomaly"):
		iid = _open_incident(
			incident_type="queue_anomaly",
			severity=q.get("severity") or "medium",
			summary=f"Queue anomaly pending={q.get('pending')}",
			details=q,
		)
		if iid:
			incidents.append(iid)
	p = push_anomaly_detection()
	if p.get("anomaly"):
		iid = _open_incident(
			incident_type="push_anomaly",
			severity=p.get("severity") or "medium",
			summary=f"Push success rate {p.get('success_rate')}",
			details=p,
		)
		if iid:
			incidents.append(iid)
	return {"queue": q, "push": p, "incidents": incidents}


def assign_support_ticket(ticket_id: str, user: str) -> dict:
	if not frappe.db.exists("Support Ticket", ticket_id):
		return {"ok": False, "error": "not_found"}
	frappe.db.set_value("Support Ticket", ticket_id, "assigned_to", user)
	return {"ok": True, "ticket_id": ticket_id, "assigned_to": user}


def bulk_assign_support_tickets(ticket_ids: list[str], user: str) -> dict:
	assigned = []
	for tid in ticket_ids:
		r = assign_support_ticket(tid, user)
		if r.get("ok"):
			assigned.append(tid)
	return {"assigned": assigned, "count": len(assigned)}


def execute():
	"""Scheduler entry — run all GA escalations."""
	frappe.set_user("Administrator")
	return {
		"sla": auto_escalate_sla_breaches(),
		"stale": auto_escalate_stale_devices(),
		"anomalies": run_anomaly_escalations(),
		"support_snapshot": support_response_metrics(),
	}
