# Copyright (c) 2026, Murugan and contributors
"""One-off geography API verification for cleanup report."""

from __future__ import annotations

import json

import frappe

from agriflow.api.v1 import geography


def run_api_tests() -> dict:
	frappe.set_user("Administrator")
	state = frappe.db.get_value("Geo State", {"is_active": 1}, "name")

	r1 = geography.get_districts(state=state)
	items = r1.get("data", {}).get("items", [])
	tvm = [d for d in items if (d.get("district_name") or "").upper() == "TIRUVANNAMALAI"]

	r2 = geography.get_blocks(district="593")
	blocks = r2.get("data", {}).get("items", [])
	block_names = {(b.get("block_name") or "").upper() for b in blocks}
	polur = [b for b in blocks if (b.get("block_name") or "").upper() == "POLUR"]

	r3 = geography.get_villages(block="5724", limit=500)
	villages = r3.get("data", {}).get("items", [])

	r4 = geography.get_villages(block="5724", search="Ven", limit=100)
	ven = r4.get("data", {}).get("items", [])

	farmers = frappe.get_all(
		"Farmer",
		filters={"is_deleted": 0},
		fields=["name", "district", "block", "village"],
	)

	result = {
		"state": state,
		"get_districts_count": len(items),
		"tiruvannamalai": tvm,
		"get_blocks_593_count": len(blocks),
		"has_polur": "POLUR" in block_names,
		"has_chetpet": "CHETPET" in block_names,
		"polur_block": polur,
		"get_villages_5724_count": len(villages),
		"get_villages_5724_search_ven_count": len(ven),
		"ven_sample": ven[:5],
		"farmers": farmers,
		"get_districts_full": r1,
		"get_blocks_593_full": r2,
		"get_villages_5724_full": {"count": len(villages), "first_3": villages[:3]},
		"get_villages_5724_ven_full": r4,
	}

	print("=== API TEST RESULTS ===")
	print(json.dumps(result, indent=2, default=str))
	return result
