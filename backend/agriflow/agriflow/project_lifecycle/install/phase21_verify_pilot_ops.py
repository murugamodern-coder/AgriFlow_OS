# Copyright (c) 2026, Murugan and contributors
"""Phase 21 pilot operations verification."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import pilot as pilot_api
from agriflow.project_lifecycle.install.phase20_verify_commercial import execute as p20
from agriflow.project_lifecycle.install.phase21_install import execute as install21
from agriflow.project_lifecycle.install.phase21_simulation import execute as sim


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	out["install21"] = install21()
	if not out["install21"].get("ok"):
		errors.append("install21")

	out["phase20"] = p20()
	if not out["phase20"].get("ok"):
		errors.append("phase20 regression")

	frappe.set_user("Administrator")
	dash = pilot_api.pilot_status_dashboard()
	out["pilot_dashboard_ok"] = dash.get("ok")
	if dash.get("ok"):
		data = dash.get("data") or {}
		out["readiness_score"] = (data.get("readiness") or {}).get("score")
		out["stale_followups"] = len(data.get("stale_followups") or [])

	out["rollout_ok"] = pilot_api.rollout_cadence_summary().get("ok")
	out["export_ok"] = pilot_api.export_pilot_audit(format="json").get("ok")
	out["simulation"] = sim()

	ack = pilot_api.acknowledge_stale_followup(
		{"device_id": "phase21-verify-device", "notes": "verify"}
	)
	out["stale_ack_ok"] = ack.get("ok")

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
