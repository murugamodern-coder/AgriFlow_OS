# Copyright (c) 2026, Murugan and contributors
"""Phase 20 commercial readiness verification."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import commercial as commercial_api
from agriflow.project_lifecycle.install.phase19_verify_rollout import execute as p19
from agriflow.project_lifecycle.install.phase20_install import execute as install20
from agriflow.project_lifecycle.install.phase20_demo_customer import execute as demo
from agriflow.project_lifecycle.install import phase20_customer_onboarding as onboarding_mod

DEMO_USER = "field.officer@agriflow.local"


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	out["install20"] = install20()
	out["phase19"] = p19()
	if not out["phase19"].get("ok"):
		errors.append("phase19 regression")

	frappe.set_user("Administrator")
	out["demo_customer"] = demo()

	onboard = onboarding_mod.start_onboarding(
		{"customer_name": "Phase 20 Verify Customer", "role_template": "demo"}
	)
	out["onboarding_start_ok"] = onboard.get("ok")
	if onboard.get("ok"):
		oid = onboard["data"]["onboarding_id"]
		for step in ("site_config", "demo_seed", "verify"):
			r = onboarding_mod.complete_step({"onboarding_id": oid, "step_id": step})
			if not r.get("ok"):
				errors.append(f"step {step}")

	sla = commercial_api.sla_dashboard()
	out["sla_dashboard_ok"] = sla.get("ok")
	if sla.get("ok"):
		data = sla.get("data") or {}
		out["sla_keys"] = list((data.get("sla") or {}).keys())
		out["device_health_count"] = len(data.get("device_health") or [])

	console = commercial_api.operations_console()
	out["operations_console_ok"] = console.get("ok")

	report = commercial_api.pilot_health_report()
	out["pilot_report_ok"] = report.get("ok")

	frappe.set_user(DEMO_USER)
	ticket = commercial_api.create_support_ticket(
		{
			"subject": "Phase 20 verify ticket",
			"description": "Commercial verify",
			"device_id": "phase20-verify",
		}
	)
	out["support_ticket_ok"] = ticket.get("ok")

	health = commercial_api.device_health_for_officer()
	out["officer_health_ok"] = health.get("ok")

	frappe.set_user("Administrator")
	export = commercial_api.export_operational_summary(format="json")
	out["export_ok"] = export.get("ok")

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
