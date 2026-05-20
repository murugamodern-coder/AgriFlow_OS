# Copyright (c) 2026, Murugan and contributors
"""Phase 15 E2E verification — auth, sync replay, inventory consume."""

from __future__ import annotations

import json
import uuid

import frappe
from frappe.utils import random_string
from frappe.auth import LoginManager

from agriflow.api.v1 import auth as auth_api
from agriflow.api.v1 import sync as sync_api
from agriflow.inventory.services.consumption import consume as do_consume
from agriflow.inventory.services.reservation import reserve as do_reserve

DEMO_USER = "field.officer@agriflow.local"
DEMO_PASSWORD = "AgriFlow@2026"
DEMO_PROJECT = "FP-2026-00007"


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	# 1) auth.login
	frappe.set_user("Guest")
	login_resp = auth_api.login({"username": DEMO_USER, "password": DEMO_PASSWORD})
	out["auth_ok"] = login_resp.get("ok")
	if not login_resp.get("ok"):
		errors.append(f"auth.login: {login_resp.get('error')}")
	else:
		out["auth_blocks"] = login_resp["data"]["permissions"].get("blocks")
		frappe.set_user(DEMO_USER)

	# 2) sync.push task complete + replay (session user)
	if not login_resp.get("ok"):
		frappe.set_user("Administrator")
	cmid = str(uuid.uuid4())  # 36 chars — ledger client_id limit
	task = frappe.get_all(
		"Project Task",
		filters={
			"farmer_project": DEMO_PROJECT,
			"status": ("in", ["open", "assigned", "in_progress"]),
			"is_deleted": 0,
		},
		fields=["name", "doc_version"],
		limit=1,
	)
	if not task:
		errors.append("no open task for sync test")
	else:
		t = task[0]
		doc_version = int(
			frappe.db.get_value("Project Task", t.name, "doc_version") or 1
		)
		op = {
			"client_mutation_id": cmid,
			"entity": "task",
			"op_type": "update",
			"payload": {
				"name": t.name,
				"doc_version": doc_version,
				"status": "in_progress",
			},
		}
		push1 = sync_api.push(
			{
				"device_id": "phase15-verify",
				"operations": [op],
			}
		)
		out["push1_ok"] = push1.get("ok")
		r1 = (push1.get("data") or {}).get("results") or []
		out["push1_status"] = [x.get("status") for x in r1]

		push2 = sync_api.push(
			{
				"device_id": "phase15-verify",
				"operations": [op],
			}
		)
		r2 = (push2.get("data") or {}).get("results") or []
		out["replay_status"] = r2[0].get("status") if r2 else None
		out["replay_flag"] = r2[0].get("replay") if r2 else None
		logs = frappe.db.count("Sync Mutation Log", {"client_mutation_id": cmid})
		out["mutation_log_count"] = logs
		if out.get("replay_status") != "skipped":
			errors.append(f"replay expected skipped, got {out.get('replay_status')}")

	# 3) inventory reserve + consume (Store Keeper / Administrator)
	frappe.set_user("Administrator")
	try:
		alloc_name = _inventory_smoke()
		out["inventory_allocation"] = alloc_name
	except Exception as exc:
		errors.append(f"inventory: {exc}")

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out


def _inventory_smoke() -> str:
	item = frappe.db.get_value(
		"Inventory Item",
		{"item_code": "DRIP-001"},
		["name", "has_serial_no", "has_batch_no"],
		as_dict=True,
	)
	if not item:
		item = frappe.db.get_value(
			"Inventory Item",
			{"has_serial_no": 0},
			["name", "has_serial_no", "has_batch_no"],
			as_dict=True,
		)
	if not item:
		raise frappe.ValidationError("No inventory item seeded")
	item_name = item.name
	wh = "WH-CENTRAL-01"
	batch_no = "BATCH-001" if item.has_batch_no else None
	short_client = random_string(28)
	reserve_payload = {
		"farmer_project": DEMO_PROJECT,
		"warehouse": wh,
		"inventory_item": item_name,
		"qty": 5,
		"client_id": short_client,
	}
	if batch_no:
		reserve_payload["batch_no"] = batch_no
	res = do_reserve(reserve_payload)
	alloc = res.get("allocation") or res.get("name")
	consume_payload = {
		"allocation": alloc,
		"qty": 2,
		"doc_version": 1,
		"client_id": random_string(28),
	}
	if batch_no:
		consume_payload["batch_no"] = batch_no
	cons = do_consume(consume_payload)
	if cons.get("status") not in ("partially_consumed", "consumed"):
		raise frappe.ValidationError(f"unexpected consume status: {cons}")
	return alloc
