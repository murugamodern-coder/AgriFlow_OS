# Copyright (c) 2026, Murugan and contributors
"""Phase 23 enterprise operations verification."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import enterprise as ent_api
from agriflow.project_lifecycle.install.phase22_verify_ga import execute as p22
from agriflow.project_lifecycle.install.phase23_install import execute as install23
from agriflow.project_lifecycle.install.phase23_simulation import execute as sim


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	out["install23"] = install23()
	if not out["install23"].get("ok"):
		errors.append("install23")

	out["phase22"] = p22()
	if not out["phase22"].get("ok"):
		errors.append("phase22 regression")

	frappe.set_user("Administrator")
	dash = ent_api.enterprise_operations_dashboard()
	out["enterprise_dashboard_ok"] = dash.get("ok")
	if dash.get("ok"):
		data = dash.get("data") or {}
		out["tenant_health_count"] = len(data.get("tenant_health") or [])

	out["governance_ok"] = ent_api.cross_tenant_governance_api().get("ok")
	out["readiness_ok"] = ent_api.tenant_readiness_summary().get("ok")
	out["scheduler_ok"] = ent_api.scheduler_health_dashboard().get("ok")
	out["automation_ok"] = ent_api.run_enterprise_automation().get("ok")
	out["retention_dry_ok"] = ent_api.run_retention_policy(dry_run=1).get("ok")
	out["audit_export_ok"] = ent_api.export_enterprise_audit(format="json").get("ok")
	out["bulk_ok"] = ent_api.bulk_maintenance().get("ok")
	out["simulation"] = sim()

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
