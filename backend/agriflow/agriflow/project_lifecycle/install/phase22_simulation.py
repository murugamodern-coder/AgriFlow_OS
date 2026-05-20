# Copyright (c) 2026, Murugan and contributors
"""Phase 22 GA multi-customer + governance simulation."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import ga as ga_api
from agriflow.project_lifecycle.install import phase20_customer_onboarding as onboarding_mod


def execute():
	frappe.set_user("Administrator")
	out = {"ok": True, "steps": []}

	for name in ("GA Sim Customer X", "GA Sim Customer Y"):
		r = onboarding_mod.start_onboarding(
			{"customer_name": name, "role_template": "pilot_block"}
		)
		out["steps"].append({"customer": name, "start": r.get("ok")})
		if r.get("ok"):
			oid = r["data"]["onboarding_id"]
			frappe.db.set_value("Customer Onboarding", oid, "status", "ready")

	approval = ga_api.request_upgrade_approval_api(
		{"release_version": "0.22.0-ga-sim", "min_app_version": "0.22.0"}
	)
	out["upgrade_request_ok"] = approval.get("ok")
	if approval.get("ok"):
		sid = (approval.get("data") or {}).get("signoff_id")
		ga_api.approve_release_api({"signoff_id": sid, "approve": True})
		out["signoff_id"] = sid

	out["dashboard_ok"] = ga_api.ga_operations_dashboard().get("ok")
	out["backup_ok"] = ga_api.run_backup_verification().get("ok")
	out["escalations"] = ga_api.run_ga_escalations().get("ok")
	out["readiness"] = ga_api.customer_readiness().get("ok")
	return out
