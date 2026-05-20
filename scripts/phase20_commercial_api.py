# Copyright (c) 2026, Murugan and contributors
"""Phase 20 — commercial ops console, SLA, exports, onboarding."""

from __future__ import annotations

import csv
import io
import json

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.api.v1 import ops as ops_api
from agriflow.api.v1 import push as push_api
from agriflow.api.v1.pilot_ops import _app_version_matrix, _officer_activity, _queue_backlog_metrics, _sync_health_window
from agriflow.project_lifecycle.install.phase16_inventory_reconcile import execute as inventory_reconcile
from agriflow.project_lifecycle.install.phase20_analytics import (
	device_health_scores,
	inventory_utilization_summary,
	officer_productivity,
	push_success_rate,
	queue_growth_trend,
	sla_summary,
	sync_trend_days,
)


def _admin_only():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)


@frappe.whitelist(allow_guest=False)
def sla_dashboard():
	"""SLA + trend analytics for commercial ops."""
	_admin_only()
	return success(
		{
			"generated_at": str(now_datetime()),
			"sla": sla_summary(),
			"sync_trends": sync_trend_days(14),
			"queue_trends": queue_growth_trend(14),
			"push_success": push_success_rate(7),
			"inventory": inventory_utilization_summary(),
			"device_health": device_health_scores()[:30],
			"officer_productivity": officer_productivity(7),
			"app_versions": _app_version_matrix(),
			"sync_health_7d": _sync_health_window(7),
			"queue_backlog": _queue_backlog_metrics(),
		}
	)


@frappe.whitelist(allow_guest=False)
def operations_console():
	"""Admin operations console — superset of live dashboard + Phase 20 analytics."""
	_admin_only()
	live = ops_api.live_dashboard().get("data") or {}
	sla = sla_dashboard().get("data") or {}
	return success({**live, "commercial": sla})


@frappe.whitelist(allow_guest=False)
def export_operational_summary(format="json"):
	"""Exportable operational summary (json or csv)."""
	_admin_only()
	payload = operations_console().get("data") or {}
	if (format or "json").lower() == "csv":
		buf = io.StringIO()
		w = csv.writer(buf)
		w.writerow(["section", "key", "value"])
		for section, data in payload.items():
			if isinstance(data, dict):
				for k, v in data.items():
					w.writerow([section, k, json.dumps(v) if isinstance(v, (dict, list)) else v])
			else:
				w.writerow([section, "-", data])
		frappe.response["type"] = "download"
		frappe.response["filename"] = f"agriflow_ops_{frappe.local.site}.csv"
		frappe.response["filecontent"] = buf.getvalue()
		return
	return success(payload)


@frappe.whitelist(allow_guest=False)
def pilot_health_report():
	_admin_only()
	return success(
		{
			"report_type": "pilot_health",
			"generated_at": str(now_datetime()),
			"sla": sla_summary(),
			"incidents_open": frappe.db.count(
				"Operational Incident",
				{"status": ("in", ("open", "investigating"))},
			)
			if frappe.db.exists("DocType", "Operational Incident")
			else 0,
			"feedback_open": frappe.db.count("Pilot Operational Feedback", {"workflow_status": "new"})
			if frappe.db.exists("DocType", "Pilot Operational Feedback")
			else 0,
			"device_health_bottom": sorted(device_health_scores(), key=lambda x: x["health_score"])[:5],
		}
	)


@frappe.whitelist(allow_guest=False)
def sync_sla_report(days: int = 7):
	_admin_only()
	return success(
		{
			"window_days": days,
			"sync_health": _sync_health_window(days),
			"daily_trends": sync_trend_days(days),
			"failure_categories": frappe.get_attr(
				"agriflow.api.v1.readiness.sync_failure_categories"
			)().get("data"),
		}
	)


@frappe.whitelist(allow_guest=False)
def inventory_movement_summary():
	_admin_only()
	inv = inventory_reconcile()
	util = inventory_utilization_summary()
	return success({"reconcile": inv, "utilization": util})


@frappe.whitelist(allow_guest=False)
def create_support_ticket(data=None):
	"""Link support case to operational incident."""
	ensure_authenticated()
	payload = parse_data(data)
	subject = (payload.get("subject") or "").strip()
	if not subject:
		return fail("VAL_INVALID", "subject required")
	if not frappe.db.exists("DocType", "Support Ticket"):
		return fail("VAL_INVALID", "Support Ticket DocType missing")
	doc = frappe.get_doc(
		{
			"doctype": "Support Ticket",
			"subject": subject,
			"status": "open",
			"priority": payload.get("priority") or "medium",
			"incident": payload.get("incident"),
			"officer_user": payload.get("officer_user") or frappe.session.user,
			"device_id": payload.get("device_id") or "",
			"description": payload.get("description") or "",
			"opened_on": now_datetime(),
		}
	)
	doc.insert(ignore_permissions=True)
	if payload.get("incident") and frappe.db.exists("Operational Incident", payload["incident"]):
		frappe.db.set_value("Operational Incident", payload["incident"], "status", "investigating")
	return success({"ticket_id": doc.name})


@frappe.whitelist(allow_guest=False)
def escalate_incident(data=None):
	_admin_only()
	payload = parse_data(data)
	incident = payload.get("incident")
	if not incident:
		return fail("VAL_INVALID", "incident required")
	frappe.db.set_value("Operational Incident", incident, "severity", payload.get("severity") or "high")
	frappe.db.set_value("Operational Incident", incident, "status", "investigating")
	ticket = create_support_ticket(
		{
			"subject": payload.get("subject") or f"Escalation: {incident}",
			"incident": incident,
			"priority": "high",
			"description": payload.get("notes"),
		}
	)
	return success({"incident": incident, "ticket": ticket.get("data")})


@frappe.whitelist(allow_guest=False)
def onboarding_checklist_admin():
	_admin_only()
	from agriflow.project_lifecycle.install.phase20_customer_onboarding import (
		onboarding_checklist_admin as _admin_checklist,
	)

	return _admin_checklist()


@frappe.whitelist(allow_guest=False)
def device_health_for_officer():
	"""Officer — own device health score (latest telemetry)."""
	ensure_authenticated()
	scores = device_health_scores(stale_hours=72)
	mine = [s for s in scores if s.get("user") == frappe.session.user]
	return success(mine[0] if mine else {"health_score": None, "stale": True})
