# Copyright (c) 2026, Murugan and contributors
"""Phase 22 GA readiness verification."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import ga as ga_api
from agriflow.project_lifecycle.install.phase21_verify_pilot_ops import execute as p21
from agriflow.project_lifecycle.install.phase22_install import execute as install22
from agriflow.project_lifecycle.install.phase22_simulation import execute as sim


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	out["install22"] = install22()
	out["phase21"] = p21()
	if not out["phase21"].get("ok"):
		errors.append("phase21 regression")

	frappe.set_user("Administrator")
	dash = ga_api.ga_operations_dashboard()
	out["ga_dashboard_ok"] = dash.get("ok")
	if dash.get("ok"):
		data = dash.get("data") or {}
		out["customer_health_count"] = len(data.get("customer_health") or [])
		out["queue_anomaly"] = (data.get("queue_anomaly") or {}).get("anomaly")

	out["sla_ok"] = ga_api.cross_customer_sla_dashboard().get("ok")
	out["readiness_ok"] = ga_api.customer_readiness().get("ok")
	out["backup_ok"] = ga_api.run_backup_verification().get("ok")
	out["checklist_ok"] = ga_api.production_rollout_checklist_api().get("ok")
	out["go_live_ok"] = ga_api.customer_go_live_checklist().get("ok")

	approval = ga_api.request_upgrade_approval_api(
		{"release_version": "0.22.0-verify", "min_app_version": "0.22.0"}
	)
	out["release_governance_ok"] = approval.get("ok")
	if approval.get("ok"):
		sid = (approval.get("data") or {}).get("signoff_id")
		ga_api.approve_release_api({"signoff_id": sid})
		out["signoff_approved"] = True

	out["escalations_ok"] = ga_api.run_ga_escalations().get("ok")
	out["incident_export_ok"] = ga_api.incident_review_export(format="json").get("ok")
	out["export_ok"] = ga_api.export_ga_operations_summary(format="json").get("ok")
	out["simulation"] = sim()

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
