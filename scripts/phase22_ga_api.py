# Copyright (c) 2026, Murugan and contributors
"""Phase 22 — GA readiness & scale operations API."""

from __future__ import annotations

import csv
import io
import json

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.response import fail, parse_data, success
from agriflow.api.v1 import commercial as commercial_api
from agriflow.api.v1 import pilot as pilot_api
from agriflow.project_lifecycle.install.phase22_backup_verify import verify_backup_readiness
from agriflow.project_lifecycle.install.phase22_ga_analytics import (
	cross_customer_sla,
	customer_health_scores,
	customer_readiness_score,
	onboarding_completion_metrics,
	pilot_to_production_conversion,
	push_anomaly_detection,
	queue_anomaly_detection,
	support_workload_dashboard,
)
from agriflow.project_lifecycle.install.phase22_ga_escalations import (
	assign_support_ticket,
	auto_escalate_sla_breaches,
	auto_escalate_stale_devices,
	bulk_assign_support_tickets,
	run_anomaly_escalations,
)
from agriflow.project_lifecycle.install.phase22_release_governance import (
	approve_release_signoff,
	go_live_checklist,
	production_rollout_checklist,
	record_release_deployed,
	record_rollback,
	request_upgrade_approval,
)


def _admin_only():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)


@frappe.whitelist(allow_guest=False)
def ga_operations_dashboard():
	"""Cross-customer GA ops dashboard (cached SLA block)."""
	_admin_only()
	pilot = pilot_api.pilot_status_dashboard().get("data") or {}
	return success(
		{
			"generated_at": str(now_datetime()),
			"cross_customer_sla": cross_customer_sla(),
			"customer_health": customer_health_scores(),
			"customer_readiness": customer_readiness_score(),
			"onboarding_metrics": onboarding_completion_metrics(),
			"pilot_conversion": pilot_to_production_conversion(),
			"queue_anomaly": queue_anomaly_detection(),
			"push_anomaly": push_anomaly_detection(),
			"support_workload": support_workload_dashboard(),
			"pilot_snapshot": pilot,
		}
	)


@frappe.whitelist(allow_guest=False)
def cross_customer_sla_dashboard():
	_admin_only()
	return success(cross_customer_sla())


@frappe.whitelist(allow_guest=False)
def customer_readiness(onboarding_id=None):
	_admin_only()
	return success(customer_readiness_score(onboarding_id=onboarding_id))


@frappe.whitelist(allow_guest=False)
def production_rollout_checklist_api():
	_admin_only()
	return success(production_rollout_checklist())


@frappe.whitelist(allow_guest=False)
def customer_go_live_checklist():
	_admin_only()
	return success(go_live_checklist())


@frappe.whitelist(allow_guest=False)
def request_upgrade_approval_api(data=None):
	_admin_only()
	payload = parse_data(data)
	version = (payload.get("release_version") or "").strip()
	min_v = (payload.get("min_app_version") or "0.22.0").strip()
	if not version:
		return fail("VAL_INVALID", "release_version required")
	return success(request_upgrade_approval(version, min_v, payload.get("wave") or "ga"))


@frappe.whitelist(allow_guest=False)
def approve_release_api(data=None):
	_admin_only()
	payload = parse_data(data)
	sid = payload.get("signoff_id")
	if not sid:
		return fail("VAL_INVALID", "signoff_id required")
	return success(approve_release_signoff(sid, payload.get("approve", True)))


@frappe.whitelist(allow_guest=False)
def deploy_release_api(data=None):
	_admin_only()
	payload = parse_data(data)
	sid = payload.get("signoff_id")
	if not sid:
		return fail("VAL_INVALID", "signoff_id required")
	return success(record_release_deployed(sid))


@frappe.whitelist(allow_guest=False)
def rollback_release_api(data=None):
	_admin_only()
	payload = parse_data(data)
	sid = payload.get("signoff_id")
	if not sid:
		return fail("VAL_INVALID", "signoff_id required")
	return success(record_rollback(sid, payload.get("notes") or ""))


@frappe.whitelist(allow_guest=False)
def run_backup_verification():
	_admin_only()
	return success(verify_backup_readiness())


@frappe.whitelist(allow_guest=False)
def run_ga_escalations():
	_admin_only()
	from agriflow.project_lifecycle.install.phase22_ga_escalations import execute as esc

	return success(esc())


@frappe.whitelist(allow_guest=False)
def assign_support(data=None):
	_admin_only()
	payload = parse_data(data)
	tid = payload.get("ticket_id")
	user = payload.get("assigned_to")
	if not tid or not user:
		return fail("VAL_INVALID", "ticket_id and assigned_to required")
	return success(assign_support_ticket(tid, user))


@frappe.whitelist(allow_guest=False)
def bulk_assign_support(data=None):
	_admin_only()
	payload = parse_data(data)
	ids = payload.get("ticket_ids") or []
	user = payload.get("assigned_to")
	if not ids or not user:
		return fail("VAL_INVALID", "ticket_ids and assigned_to required")
	return success(bulk_assign_support_tickets(ids, user))


@frappe.whitelist(allow_guest=False)
def incident_review_export(format="json", days: int = 30):
	_admin_only()
	if not frappe.db.exists("DocType", "Operational Incident"):
		return success({"incidents": []})
	since = frappe.utils.add_days(now_datetime(), -int(days))
	rows = frappe.get_all(
		"Operational Incident",
		filters={"recorded_on": (">=", since)},
		fields=["name", "incident_type", "severity", "status", "summary", "recorded_on"],
		order_by="recorded_on desc",
		limit=500,
	)
	payload = {"window_days": days, "incidents": rows, "count": len(rows)}
	if (format or "json").lower() == "csv":
		buf = io.StringIO()
		w = csv.writer(buf)
		w.writerow(["name", "type", "severity", "status", "summary", "recorded_on"])
		for r in rows:
			w.writerow([r.name, r.incident_type, r.severity, r.status, r.summary, r.recorded_on])
		frappe.response["type"] = "download"
		frappe.response["filename"] = f"agriflow_incidents_{frappe.local.site}.csv"
		frappe.response["filecontent"] = buf.getvalue()
		return
	return success(payload)


@frappe.whitelist(allow_guest=False)
def export_ga_operations_summary(format="json"):
	_admin_only()
	payload = ga_operations_dashboard().get("data") or {}
	if (format or "json").lower() == "csv":
		buf = io.StringIO()
		w = csv.writer(buf)
		w.writerow(["section", "json"])
		for k, v in payload.items():
			w.writerow([k, json.dumps(v) if isinstance(v, (dict, list)) else v])
		frappe.response["type"] = "download"
		frappe.response["filename"] = f"agriflow_ga_ops_{frappe.local.site}.csv"
		frappe.response["filecontent"] = buf.getvalue()
		return
	return success(payload)


@frappe.whitelist(allow_guest=False)
def support_performance_metrics(days: int = 14):
	_admin_only()
	from agriflow.project_lifecycle.install.phase21_analytics import support_response_metrics

	return success(
		{
			"metrics": support_response_metrics(days),
			"workload": support_workload_dashboard(),
		}
	)
