# Copyright (c) 2026, Murugan and contributors
"""Phase 23 — enterprise operations API."""

from __future__ import annotations

import csv
import io
import json

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.response import fail, parse_data, success
from agriflow.api.v1 import ga as ga_api
from agriflow.project_lifecycle.install.phase23_automation import execute as run_automation
from agriflow.project_lifecycle.install.phase23_bootstrap import (
	enterprise_onboarding_pack,
	environment_template,
	register_tenant,
)
from agriflow.project_lifecycle.install.phase23_enterprise_analytics import (
	cross_tenant_governance,
	customer_segment_report,
	list_tenant_ops_records,
	retry_analytics,
	scheduler_health_summary,
	tenant_health_scores,
	tenant_readiness_summaries,
	tenant_sla_dashboard,
)
from agriflow.project_lifecycle.install.phase23_retention import (
	execute as run_retention,
	retention_policy_summary,
)


def _admin_only():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)


@frappe.whitelist(allow_guest=False)
def enterprise_operations_dashboard():
	_admin_only()
	ga = ga_api.ga_operations_dashboard().get("data") or {}
	return success(
		{
			"generated_at": str(now_datetime()),
			"governance": cross_tenant_governance(),
			"tenant_health": tenant_health_scores()[:30],
			"readiness": tenant_readiness_summaries()[:15],
			"segment_report": customer_segment_report(),
			"retry_analytics": retry_analytics(7),
			"retention_policy": retention_policy_summary(),
			"ga_snapshot": ga,
		}
	)


@frappe.whitelist(allow_guest=False)
def tenant_sla_dashboard_api(tenant_key=None):
	_admin_only()
	return success(tenant_sla_dashboard(tenant_key=tenant_key))


@frappe.whitelist(allow_guest=False)
def tenant_readiness_summary():
	_admin_only()
	return success({"tenants": tenant_readiness_summaries()})


@frappe.whitelist(allow_guest=False)
def cross_tenant_governance_api():
	_admin_only()
	return success(cross_tenant_governance())


@frappe.whitelist(allow_guest=False)
def register_tenant_api(data=None):
	_admin_only()
	payload = parse_data(data)
	key = (payload.get("tenant_key") or "").strip()
	name = (payload.get("customer_name") or "").strip()
	if not key or not name:
		return fail("VAL_INVALID", "tenant_key and customer_name required")
	return success(
		register_tenant(
			tenant_key=key,
			customer_name=name,
			site_name=payload.get("site_name"),
			segment=payload.get("segment") or "ga",
			sla_tier=payload.get("sla_tier") or "standard",
			onboarding_id=payload.get("onboarding_id"),
		)
	)


@frappe.whitelist(allow_guest=False)
def enterprise_onboarding_pack_api(data=None):
	_admin_only()
	payload = parse_data(data)
	return success(
		enterprise_onboarding_pack(
			template=payload.get("template") or "enterprise",
			customer_name=payload.get("customer_name") or "",
		)
	)


@frappe.whitelist(allow_guest=False)
def environment_template_api(template="ga"):
	_admin_only()
	return success(environment_template(template))


@frappe.whitelist(allow_guest=False)
def run_enterprise_automation():
	_admin_only()
	return success(run_automation())


@frappe.whitelist(allow_guest=False)
def run_retention_policy(dry_run: int = 0):
	_admin_only()
	if dry_run:
		return success({"dry_run": True, "policy": retention_policy_summary()})
	return success(run_retention())


@frappe.whitelist(allow_guest=False)
def bulk_maintenance():
	_admin_only()
	return success(
		{
			"automation": run_automation(),
			"retention": run_retention(),
		}
	)


@frappe.whitelist(allow_guest=False)
def scheduler_health_dashboard():
	_admin_only()
	return success(scheduler_health_summary())


@frappe.whitelist(allow_guest=False)
def background_job_monitoring():
	_admin_only()
	return success(
		{
			"scheduler": scheduler_health_summary(),
			"retry": retry_analytics(14),
			"errors_24h": frappe.db.count(
				"Error Log",
				{"creation": (">=", frappe.utils.add_days(now_datetime(), -1))},
			),
		}
	)


@frappe.whitelist(allow_guest=False)
def export_enterprise_audit(format="json", days: int = 30):
	_admin_only()
	from agriflow.project_lifecycle.install.phase23_automation import run_operational_audit

	payload = {
		"audit": run_operational_audit(),
		"tenants": list_tenant_ops_records(200),
		"health": tenant_health_scores(),
		"governance": cross_tenant_governance(),
		"incidents": ga_api.incident_review_export(format="json", days=days).get("data"),
		"retention": retention_policy_summary(),
	}
	if (format or "json").lower() == "csv":
		buf = io.StringIO()
		w = csv.writer(buf)
		w.writerow(["tenant_key", "customer", "segment", "status", "health_score", "sla_tier"])
		for t in payload.get("health") or []:
			w.writerow(
				[
					t.get("tenant_key"),
					t.get("customer_name"),
					t.get("segment"),
					t.get("status"),
					t.get("health_score"),
					t.get("sla_tier"),
				]
			)
		frappe.response["type"] = "download"
		frappe.response["filename"] = f"agriflow_enterprise_audit_{frappe.local.site}.csv"
		frappe.response["filecontent"] = buf.getvalue()
		return
	return success(payload)


@frappe.whitelist(allow_guest=False)
def assign_enterprise_support(data=None):
	"""Bulk assign open tickets to enterprise support owner."""
	_admin_only()
	payload = parse_data(data)
	user = payload.get("assigned_to")
	if not user:
		return fail("VAL_INVALID", "assigned_to required")
	tickets = frappe.get_all(
		"Support Ticket",
		filters={"status": ("in", ("open", "escalated"))},
		pluck="name",
		limit=100,
	)
	from agriflow.project_lifecycle.install.phase22_ga_escalations import bulk_assign_support_tickets

	return success(bulk_assign_support_tickets(tickets, user))
