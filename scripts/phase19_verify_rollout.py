# Copyright (c) 2026, Murugan and contributors
"""Phase 19 controlled rollout verification."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import ops as ops_api
from agriflow.api.v1 import push as push_api
from agriflow.project_lifecycle.install.phase18_verify_production import execute as p18
from agriflow.project_lifecycle.install.phase19_install import execute as install19
from agriflow.project_lifecycle.install.phase19_ops_alerts import execute as alerts
from agriflow.project_lifecycle.install.phase19_fcm_delivery import process_queued_pushes

DEMO_USER = "field.officer@agriflow.local"


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	frappe.conf.agriflow_fcm_server_key = frappe.conf.get("agriflow_fcm_server_key") or "simulate"
	out["install19"] = install19()
	out["phase18"] = p18()
	if not out["phase18"].get("ok"):
		errors.append("phase18 regression failed")

	frappe.set_user(DEMO_USER)
	deliveries = push_api.fanout_push(
		"NOTIF-PHASE19",
		DEMO_USER,
		"/projects/FP-2026-00007/tasks",
		title="Phase 19 push test",
		body="Pilot validation",
	)
	out["fcm_deliveries"] = deliveries
	out["fcm_sent"] = sum(1 for d in deliveries if d.get("status") == "sent")
	if out["fcm_sent"] < 1 and len(deliveries) < 1:
		errors.append("no push deliveries recorded")

	frappe.set_user("Administrator")
	out["fcm_queue"] = process_queued_pushes()
	out["ops_alerts"] = alerts()
	out["alert_codes"] = [a["code"] for a in out["ops_alerts"].get("alerts") or []]

	dash = ops_api.live_dashboard()
	out["live_dashboard_ok"] = dash.get("ok")
	if dash.get("ok"):
		data = dash.get("data") or {}
		out["open_incidents"] = len(data.get("open_incidents") or [])
		out["rollout_wave"] = data.get("rollout_wave")

	roll = ops_api.rollout_status()
	out["rollout_ok"] = roll.get("ok")

	frappe.set_user(DEMO_USER)
	ack = ops_api.background_sync_ack(
		{"device_id": "phase19-headless", "success": True, "phase": "verify"}
	)
	out["headless_ack_ok"] = ack.get("ok")

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
