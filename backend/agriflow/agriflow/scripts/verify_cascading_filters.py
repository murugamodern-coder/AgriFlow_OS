# Copyright (c) 2026, Murugan and contributors
"""Verify cascading geography filters on Farmer DocType and APIs."""

from __future__ import annotations

import json

import frappe

from agriflow.api.v1 import geography


def run_verification() -> dict:
	frappe.set_user("Administrator")

	meta = frappe.get_meta("Farmer")
	link_filters = {
		df.fieldname: df.link_filters
		for df in meta.fields
		if df.fieldname in ("district", "block", "village")
	}

	client_script = frappe.db.get_value(
		"Client Script",
		"Farmer Cascading Geography",
		["enabled", "dt", "view"],
		as_dict=True,
	)

	block_count = frappe.db.count("Block", {"district": "593", "is_active": 1})
	village_count = frappe.db.count("Village", {"block": "5724", "is_active": 1})

	r_blocks = geography.get_blocks(district="593")
	r_villages = geography.get_villages(block="5724", limit=500)
	api_blocks = len(r_blocks.get("data", {}).get("items", []))
	api_villages = len(r_villages.get("data", {}).get("items", []))

	# Bad hierarchy should throw
	bad_threw = False
	bad_msg = ""
	try:
		doc = frappe.get_doc(
			{
				"doctype": "Farmer",
				"farmer_name": "Cascade Test",
				"mobile": "9999900001",
				"state": "Tamil Nadu",
				"district": "593",
				"block": "5724",
				"village": "630559",
			}
		)
		doc.insert(ignore_permissions=True)
		frappe.db.rollback()
	except frappe.ValidationError as exc:
		bad_threw = True
		bad_msg = str(exc)
		frappe.db.rollback()

	result = {
		"link_filters": link_filters,
		"client_script": client_script,
		"db_block_count_593": block_count,
		"db_village_count_5724": village_count,
		"api_block_count_593": api_blocks,
		"api_village_count_5724": api_villages,
		"bad_hierarchy_rejected": bad_threw,
		"bad_hierarchy_message": bad_msg,
	}
	print(json.dumps(result, indent=2, default=str))
	return result
