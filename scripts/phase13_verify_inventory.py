# Copyright (c) 2026, Murugan and contributors
"""Phase 13 — verify inventory ledger, reserve, consume, transfer."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import inventory as inv_api
from agriflow.inventory.services.idempotency import find_ledger_by_client_id
from agriflow.inventory.services.projection import get_available, get_on_hand, get_reserved

PROJECT = "FP-2026-00007"
WH1 = "WH-CENTRAL-01"
WH2 = "WH-CENTRAL-02"
ITEM = "ITEM-DRIP-001"


def execute():
	frappe.only_for("Administrator")
	errors: list[str] = []
	report: dict = {}
	run_id = frappe.generate_hash(length=8)

	seq = int(frappe.db.get_value("Farmer Project", PROJECT, "stage_sequence") or 0)
	report["project_stage_sequence_before"] = seq
	if seq < 9:
		frappe.db.set_value(
			"Farmer Project",
			PROJECT,
			{"stage_sequence": 9, "current_stage": "material_dispatched"},
			update_modified=False,
		)
		report["project_stage_bumped_for_verify"] = True

	# --- inward + derived stock ---
	cid_in = f"phase13-inward-{run_id}"
	inv_api.movement_post(
		{
			"movement_type": "inward",
			"warehouse": WH1,
			"inventory_item": ITEM,
			"qty": 100,
			"batch_no": "BATCH-001",
			"client_id": cid_in,
		}
	)
	on_hand = get_on_hand(WH1, ITEM)
	report["on_hand_after_inward"] = on_hand
	if on_hand < 100:
		errors.append(f"expected on_hand >= 100 got {on_hand}")
	report["ledger_rows_for_item"] = frappe.db.count(
		"Stock Ledger Entry", {"inventory_item": ITEM, "warehouse": WH1}
	)

	# --- idempotent replay ---
	ledger2 = find_ledger_by_client_id(cid_in)
	count_cid = frappe.db.count("Stock Ledger Entry", {"client_id": cid_in})
	report["ledger_replay_count"] = count_cid
	if count_cid != 1:
		errors.append(f"expected 1 ledger for client_id got {count_cid}")
	if not ledger2:
		errors.append("ledger replay lookup failed")

	# --- reserve ---
	cid_res = f"phase13-reserve-{run_id}"
	res = inv_api.allocation_reserve(
		{
			"farmer_project": PROJECT,
			"warehouse": WH1,
			"inventory_item": ITEM,
			"qty": 30,
			"batch_no": "BATCH-001",
			"client_id": cid_res,
		}
	)
	if not res.get("ok"):
		errors.append(f"reserve failed: {res}")
	else:
		allocation = res["data"]["allocation"]
		report["allocation"] = allocation
		avail = get_available(WH1, ITEM)
		reserved = get_reserved(WH1, ITEM)
		report["available_after_reserve"] = avail
		report["reserved_after_reserve"] = reserved
		if avail < 70 - 0.01:
			errors.append(f"expected available ~70 got {avail}")
		if reserved < 30 - 0.01:
			errors.append(f"expected reserved 30 got {reserved}")

	# --- consume partial ---
	if res.get("ok"):
		doc_ver = res["data"].get("doc_version")
		con = inv_api.allocation_consume(
			{
				"allocation": allocation,
				"qty": 10,
				"doc_version": doc_ver,
				"batch_no": "BATCH-001",
				"client_id": f"phase13-consume-{run_id}",
			}
		)
		if not con.get("ok"):
			errors.append(f"consume failed: {con}")
		else:
			report["consume_status"] = con["data"].get("status")
			on_hand2 = get_on_hand(WH1, ITEM)
			reserved2 = get_reserved(WH1, ITEM)
			report["on_hand_after_consume"] = on_hand2
			report["reserved_after_consume"] = reserved2
			if on_hand2 < 90 - 0.01:
				errors.append(f"expected on_hand ~90 got {on_hand2}")
			if reserved2 < 20 - 0.01:
				errors.append(f"expected reserved ~20 got {reserved2}")

	# --- negative stock block ---
	blocked = inv_api.movement_post(
		{
			"movement_type": "outward",
			"warehouse": WH1,
			"inventory_item": ITEM,
			"qty": 500,
			"client_id": f"phase13-block-{run_id}",
		}
	)
	report["negative_stock_blocked"] = blocked.get("ok") is False
	if blocked.get("ok"):
		errors.append("outward 500 should fail when insufficient available")

	# --- transfer atomic ---
	before_wh2 = get_on_hand(WH2, ITEM)
	tfr = inv_api.transfer_post(
		{
			"from_warehouse": WH1,
			"to_warehouse": WH2,
			"inventory_item": ITEM,
			"qty": 5,
			"batch_no": "BATCH-001",
			"client_id": f"phase13-transfer-{run_id}",
		}
	)
	if not tfr.get("ok"):
		errors.append(f"transfer failed: {tfr}")
	else:
		out_l = tfr["data"]["outward_ledger"]
		in_l = tfr["data"]["inward_ledger"]
		report["transfer_ledgers"] = [out_l, in_l]
		if not out_l or not in_l:
			errors.append("transfer missing ledger rows")
		after_wh2 = get_on_hand(WH2, ITEM)
		report["wh2_on_hand_delta"] = after_wh2 - before_wh2
		if after_wh2 < before_wh2 + 5 - 0.01:
			errors.append("transfer inward not reflected on WH2")

	# --- ledger immutability ---
	if ledger2:
		doc = frappe.get_doc("Stock Ledger Entry", ledger2)
		try:
			doc.qty = 999
			doc.save(ignore_permissions=True)
			errors.append("ledger save should fail")
		except Exception:
			report["ledger_immutable"] = True

	# --- timeline off ---
	from agriflow.inventory.services.timeline_hook import EMIT_TIMELINE_MATERIAL

	report["timeline_emit_enabled"] = EMIT_TIMELINE_MATERIAL
	if EMIT_TIMELINE_MATERIAL:
		errors.append("timeline material emit should be off")

	report["ok"] = len(errors) == 0
	report["errors"] = errors
	print(report)
