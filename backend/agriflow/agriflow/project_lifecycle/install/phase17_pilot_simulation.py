# Copyright (c) 2026, Murugan and contributors
"""Simulate multi-device pilot telemetry and return dashboard snapshot."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import pilot_ops as pilot_api

DEVICES = ("pilot-sim-01", "pilot-sim-02", "pilot-sim-03")


def execute():
	frappe.set_user("Administrator")
	out = {"devices": [], "dashboard": None}

	for i, device in enumerate(DEVICES):
		frappe.set_user("Administrator")
		hb = pilot_api.heartbeat(
			{
				"device_id": device,
				"app_version": f"0.17.{i}",
				"build_number": str(100 + i),
				"platform": "simulation",
				"queue_pending": i,
				"queue_conflict": 1 if i == 2 else 0,
				"queue_failed": 0,
				"diagnostics": {"sim": True, "index": i},
			}
		)
		out["devices"].append({"device_id": device, "heartbeat_ok": hb.get("ok")})

	frappe.set_user("Administrator")
	out["dashboard"] = pilot_api.dashboard()
	return out
