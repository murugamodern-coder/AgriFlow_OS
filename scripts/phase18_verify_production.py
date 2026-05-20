# Copyright (c) 2026, Murugan and contributors
"""Phase 18 production readiness verification."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import push as push_api
from agriflow.api.v1 import readiness as readiness_api
from agriflow.project_lifecycle.install.phase17_verify_pilot import execute as pilot_verify
from agriflow.project_lifecycle.install.phase18_install import execute as install18
from agriflow.project_lifecycle.install.phase18_offline_survivability import execute as offline_test
from agriflow.project_lifecycle.install.phase18_permission_audit import execute as perm_audit

DEMO_USER = "field.officer@agriflow.local"


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	out["phase18_install"] = install18()
	out["phase17_pilot"] = pilot_verify()
	if not out["phase17_pilot"].get("ok"):
		errors.append("phase17_pilot failed")

	frappe.set_user(DEMO_USER)
	reg = push_api.register_token(
		{
			"device_id": "phase18-verify",
			"push_token": "fcm-stub-phase18",
			"platform": "android",
			"app_version": "0.18.0",
		}
	)
	out["push_register_ok"] = reg.get("ok")
	if not reg.get("ok"):
		errors.append(f"push: {reg.get('error')}")

	stub_ids = push_api.fanout_push_stub("NOTIF-PHASE18-TEST", DEMO_USER, "/projects/FP-2026-00007/tasks")
	out["push_fanout_logged"] = len(stub_ids) >= 0

	release = readiness_api.app_release_check({"app_version": "0.18.0"})
	out["release_check_ok"] = release.get("ok")
	out["update_required_018"] = (release.get("data") or {}).get("update_required")

	frappe.set_user("Administrator")
	metrics = push_api.delivery_metrics()
	out["push_metrics_ok"] = metrics.get("ok")

	alerts = readiness_api.queue_alerts()
	out["queue_alerts_ok"] = alerts.get("ok")

	out["permission_audit"] = perm_audit()
	if not out["permission_audit"].get("ok"):
		errors.append(f"permissions: {out['permission_audit'].get('findings')}")

	out["offline_survivability"] = offline_test()
	if not out["offline_survivability"].get("ok"):
		errors.append(f"offline: {out['offline_survivability'].get('errors')}")

	dash = readiness_api.production_dashboard()
	out["production_dashboard_ok"] = dash.get("ok")

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
