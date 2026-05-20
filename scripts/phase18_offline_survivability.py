# Copyright (c) 2026, Murugan and contributors
"""Long-offline survivability — JWT refresh + sync replay + watermarks."""

from __future__ import annotations

import uuid

import frappe

from agriflow.api.v1 import auth as auth_api
from agriflow.api.v1 import sync as sync_api

DEMO_USER = "field.officer@agriflow.local"
DEMO_PASSWORD = "AgriFlow@2026"


def execute():
	errors = []
	out = {"ok": False, "errors": errors}
	frappe.conf.agriflow_auth_mode = "jwt"

	# Simulate officer returning after 3+ days: fresh login + push replay
	frappe.set_user("Guest")
	login = auth_api.login({"username": DEMO_USER, "password": DEMO_PASSWORD})
	out["jwt_login_after_offline"] = login.get("ok")
	if not login.get("ok"):
		errors.append(f"login: {login.get('error')}")
		out["errors"] = errors
		return out

	frappe.set_user(DEMO_USER)
	cmid = str(uuid.uuid4())
	task = frappe.get_all(
		"Project Task",
		filters={"farmer_project": "FP-2026-00007", "is_deleted": 0},
		fields=["name"],
		limit=1,
	)
	if task:
		doc_version = int(frappe.db.get_value("Project Task", task[0].name, "doc_version") or 1)
		op = {
			"client_mutation_id": cmid,
			"entity": "task",
			"op_type": "update",
			"payload": {"name": task[0].name, "doc_version": doc_version, "description": "phase18 offline replay"},
		}
		p1 = sync_api.push({"device_id": "phase18-offline", "operations": [op]})
		p2 = sync_api.push({"device_id": "phase18-offline", "operations": [op]})
		r2 = (p2.get("data") or {}).get("results") or []
		out["replay_after_offline"] = r2[0].get("status") if r2 else None
		if out.get("replay_after_offline") != "skipped":
			errors.append(f"expected skipped replay got {out.get('replay_after_offline')}")

	# Pull with empty watermarks (full catch-up shape)
	pull = sync_api.pull(
		{
			"device_id": "phase18-offline",
			"modified_since": {},
		}
	)
	out["full_pull_ok"] = pull.get("ok")
	if not pull.get("ok"):
		errors.append(f"pull: {pull.get('error')}")

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
