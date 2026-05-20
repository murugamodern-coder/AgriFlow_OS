# Copyright (c) 2026, Murugan and contributors
"""Phase 21 pilot simulations — multi-customer, escalation drill."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import pilot as pilot_api
from agriflow.project_lifecycle.install import phase20_customer_onboarding as onboarding_mod


def execute():
	frappe.set_user("Administrator")
	results = {"ok": True, "steps": []}

	# Multi-customer onboarding simulation
	for name, template in (
		("Pilot Sim Customer A", "pilot_block"),
		("Pilot Sim Customer B", "multi_block"),
	):
		r = onboarding_mod.start_onboarding(
			{"customer_name": name, "role_template": template}
		)
		results["steps"].append({"customer": name, "start_ok": r.get("ok")})
		if r.get("ok"):
			oid = r["data"]["onboarding_id"]
			onboarding_mod.complete_step({"onboarding_id": oid, "step_id": "site_config"})

	dash = pilot_api.pilot_status_dashboard()
	results["dashboard_ok"] = dash.get("ok")
	results["customer_count"] = len((dash.get("data") or {}).get("customers") or [])

	# Support escalation drill
	ticket = pilot_api.track_pilot_issue(
		{
			"subject": "Phase 21 simulation issue",
			"description": "Escalation drill",
			"priority": "high",
		}
	)
	results["pilot_issue_ok"] = ticket.get("ok")

	list_r = pilot_api.list_pilot_customers(search="Pilot Sim")
	results["list_filter_ok"] = list_r.get("ok")

	return results
