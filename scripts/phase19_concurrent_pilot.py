# Copyright (c) 2026, Murugan and contributors
"""Simulate 5–10 concurrent pilot devices — telemetry + sync sessions."""

from __future__ import annotations

import uuid

import frappe

from agriflow.api.v1 import auth as auth_api
from agriflow.api.v1 import pilot_ops as pilot_api
from agriflow.api.v1 import sync as sync_api

DEMO_USER = "field.officer@agriflow.local"
DEMO_PASSWORD = "AgriFlow@2026"
DEVICE_COUNT = 8


def execute():
	frappe.set_user("Guest")
	login = auth_api.login({"username": DEMO_USER, "password": DEMO_PASSWORD})
	if not login.get("ok"):
		return {"ok": False, "error": login.get("error")}

	frappe.set_user(DEMO_USER)
	devices = []
	for i in range(DEVICE_COUNT):
		device_id = f"pilot-concurrent-{i:02d}"
		hb = pilot_api.heartbeat(
			{
				"device_id": device_id,
				"app_version": f"0.19.{i}",
				"build_number": str(200 + i),
				"platform": "pilot",
				"queue_pending": i % 4,
				"queue_conflict": 1 if i == 7 else 0,
				"queue_failed": 0,
			}
		)
		cmid = str(uuid.uuid4())
		task = frappe.get_all(
			"Project Task",
			filters={"farmer_project": "FP-2026-00007", "is_deleted": 0},
			fields=["name"],
			limit=1,
		)
		sync_ok = False
		if task and i % 2 == 0:
			dv = int(frappe.db.get_value("Project Task", task[0].name, "doc_version") or 1)
			push = sync_api.push(
				{
					"device_id": device_id,
					"operations": [
						{
							"client_mutation_id": cmid,
							"entity": "task",
							"op_type": "update",
							"payload": {
								"name": task[0].name,
								"doc_version": dv,
								"description": f"concurrent pilot {i}",
							},
						}
					],
				}
			)
			sync_ok = push.get("ok", False)
		devices.append(
			{
				"device_id": device_id,
				"heartbeat_ok": hb.get("ok"),
				"sync_push_ok": sync_ok,
			}
		)

	frappe.set_user("Administrator")
	from agriflow.api.v1 import ops as ops_api

	dash = ops_api.live_dashboard()
	return {
		"ok": all(d["heartbeat_ok"] for d in devices),
		"devices": devices,
		"device_count": DEVICE_COUNT,
		"dashboard_queue_devices": (dash.get("data") or {})
		.get("queue_backlog", {})
		.get("devices_reporting_24h"),
	}
