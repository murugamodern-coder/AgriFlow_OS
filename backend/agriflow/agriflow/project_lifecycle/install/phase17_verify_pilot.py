# Copyright (c) 2026, Murugan and contributors
"""Phase 17 pilot ops verification — telemetry, feedback, dashboard."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import auth as auth_api
from agriflow.api.v1 import pilot_ops as pilot_api
from agriflow.project_lifecycle.install.phase17_install import execute as install_doctypes

DEMO_USER = "field.officer@agriflow.local"
DEMO_PASSWORD = "AgriFlow@2026"


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	out["install"] = install_doctypes()
	for line in out["install"].get("doctypes") or []:
		if str(line).startswith("missing:"):
			errors.append(line)

	frappe.set_user(DEMO_USER)
	hb = pilot_api.heartbeat(
		{
			"device_id": "phase17-verify",
			"app_version": "0.17.0",
			"build_number": "1",
			"platform": "verify",
			"queue_pending": 2,
			"queue_conflict": 0,
			"queue_failed": 0,
			"diagnostics": {"phase": "verify"},
		}
	)
	out["heartbeat_ok"] = hb.get("ok")
	if not hb.get("ok"):
		errors.append(f"heartbeat: {hb.get('error')}")

	fb = pilot_api.feedback_submit(
		{
			"device_id": "phase17-verify",
			"app_version": "0.17.0",
			"category": "ux",
			"severity": "low",
			"body": "Phase 17 pilot verify feedback",
		}
	)
	out["feedback_ok"] = fb.get("ok")
	if not fb.get("ok"):
		errors.append(f"feedback: {fb.get('error')}")

	diag = pilot_api.diagnostic_upload(
		{
			"device_id": "phase17-verify",
			"kind": "verify",
			"diagnostics": {"sync_runs": 1, "errors": []},
		}
	)
	out["diagnostic_ok"] = diag.get("ok")
	if not diag.get("ok"):
		errors.append(f"diagnostic: {diag.get('error')}")

	onboard = pilot_api.onboarding_checklist()
	out["onboarding_ok"] = onboard.get("ok") and len((onboard.get("data") or {}).get("steps") or []) >= 3

	frappe.set_user("Administrator")
	dash = pilot_api.dashboard()
	out["dashboard_ok"] = dash.get("ok")
	if dash.get("ok"):
		data = dash.get("data") or {}
		out["sync_health_keys"] = list((data.get("sync_health") or {}).keys())
		out["queue_devices"] = (data.get("queue_backlog") or {}).get("devices_reporting_24h")
		out["feedback_open"] = (data.get("feedback") or {}).get("open")
	else:
		errors.append(f"dashboard: {dash.get('error')}")

	# JWT path still works alongside pilot ops
	frappe.set_user("Guest")
	login = auth_api.login({"username": DEMO_USER, "password": DEMO_PASSWORD})
	out["jwt_still_ok"] = login.get("ok")
	if not login.get("ok"):
		errors.append(f"jwt: {login.get('error')}")

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
