# Copyright (c) 2026, Murugan and contributors
"""Phase 21 — real pilot operations API."""

from __future__ import annotations

import csv
import io
import json

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.response import fail, parse_data, success
from agriflow.api.v1 import commercial as commercial_api
from agriflow.api.v1 import ops as ops_api
from agriflow.project_lifecycle.install.phase21_analytics import (
	deployment_readiness_score,
	multi_customer_onboarding_status,
	rollout_status_summary,
	stale_device_followups,
	support_response_metrics,
)


def _admin_only():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)


@frappe.whitelist(allow_guest=False)
def pilot_status_dashboard():
	"""Pilot-status dashboard — readiness, customers, SLA, support."""
	_admin_only()
	live = ops_api.live_dashboard().get("data") or {}
	return success(
		{
			"generated_at": str(now_datetime()),
			"readiness": deployment_readiness_score(),
			"customers": multi_customer_onboarding_status(),
			"support_metrics": support_response_metrics(),
			"stale_followups": stale_device_followups()[:20],
			"rollout": rollout_status_summary(),
			"live": live,
		}
	)


@frappe.whitelist(allow_guest=False)
def list_pilot_customers(status=None, search=None):
	"""Multi-customer onboarding list with optional filter."""
	_admin_only()
	customers = multi_customer_onboarding_status(limit=100)
	if status:
		customers = [c for c in customers if c.get("status") == status]
	if search:
		q = (search or "").strip().lower()
		customers = [
			c
			for c in customers
			if q in (c.get("customer_name") or "").lower()
			or q in (c.get("onboarding_id") or "").lower()
		]
	return success({"customers": customers, "count": len(customers)})


@frappe.whitelist(allow_guest=False)
def customer_level_report(onboarding_id=None):
	_admin_only()
	if not onboarding_id:
		return fail("VAL_INVALID", "onboarding_id required")
	if not frappe.db.exists("Customer Onboarding", onboarding_id):
		return fail("VAL_NOT_FOUND", "onboarding not found")
	doc = frappe.get_doc("Customer Onboarding", onboarding_id)
	customers = [c for c in multi_customer_onboarding_status() if c["onboarding_id"] == onboarding_id]
	sla = commercial_api.sla_dashboard().get("data") or {}
	return success(
		{
			"customer": customers[0] if customers else {},
			"onboarding": {
				"name": doc.name,
				"customer_name": doc.customer_name,
				"site_name": doc.site_name,
				"status": doc.status,
			},
			"sla_snapshot": sla.get("sla"),
			"device_health": (sla.get("device_health") or [])[:10],
			"support_metrics": support_response_metrics(7),
		}
	)


@frappe.whitelist(allow_guest=False)
def acknowledge_stale_followup(data=None):
	"""Mark stale-device follow-up as acknowledged (ops workflow)."""
	_admin_only()
	payload = parse_data(data)
	device_id = (payload.get("device_id") or "").strip()
	if not device_id:
		return fail("VAL_INVALID", "device_id required")
	frappe.cache().set_value(f"agriflow_stale_ack:{device_id}", "acknowledged")
	notes = payload.get("notes") or ""
	if frappe.db.exists("DocType", "Operational Log"):
		frappe.get_doc(
			{
				"doctype": "Operational Log",
				"event_type": "stale_device_followup",
				"source": "pilot_ops",
				"device_id": device_id,
				"user": frappe.session.user,
				"payload_json": {"notes": notes, "status": "acknowledged"},
				"recorded_on": now_datetime(),
			}
		).insert(ignore_permissions=True)
	return success({"device_id": device_id, "status": "acknowledged"})


@frappe.whitelist(allow_guest=False)
def track_pilot_issue(data=None):
	"""Pilot issue tracking — creates support ticket with pilot tag."""
	_admin_only()
	payload = parse_data(data)
	payload = dict(payload)
	payload["description"] = (
		f"[PILOT] {payload.get('description') or ''} "
		f"customer={payload.get('customer_name') or ''}"
	).strip()
	return commercial_api.create_support_ticket(payload)


@frappe.whitelist(allow_guest=False)
def escalate_pilot_issue(data=None):
	"""Escalate with SLA breach flag + support ticket."""
	_admin_only()
	payload = parse_data(data)
	incident = payload.get("incident")
	result = commercial_api.escalate_incident(
		{
			"incident": incident,
			"subject": payload.get("subject") or f"Pilot escalation: {incident}",
			"severity": payload.get("severity") or "high",
			"notes": payload.get("notes"),
		}
	)
	if payload.get("sla_breach"):
		frappe.cache().set_value(f"agriflow_sla_breach:{incident}", "1")
	return result


@frappe.whitelist(allow_guest=False)
def export_pilot_audit(format="json"):
	"""Operational audit export for pilot reviews."""
	_admin_only()
	payload = pilot_status_dashboard().get("data") or {}
	if (format or "json").lower() == "csv":
		buf = io.StringIO()
		w = csv.writer(buf)
		w.writerow(["section", "key", "value"])
		for section, data in payload.items():
			if isinstance(data, (dict, list)):
				w.writerow([section, "json", json.dumps(data)])
			else:
				w.writerow([section, "-", data])
		frappe.response["type"] = "download"
		frappe.response["filename"] = f"agriflow_pilot_audit_{frappe.local.site}.csv"
		frappe.response["filecontent"] = buf.getvalue()
		return
	return success(payload)


@frappe.whitelist(allow_guest=False)
def rollout_cadence_summary():
	_admin_only()
	return success(rollout_status_summary())
