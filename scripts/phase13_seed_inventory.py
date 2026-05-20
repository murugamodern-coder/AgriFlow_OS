# Copyright (c) 2026, Murugan and contributors
"""Seed warehouses and sample inventory items after migrate."""

from __future__ import annotations

import frappe


def execute():
	frappe.only_for("Administrator")
	seed = [
		{
			"doctype": "Warehouse",
			"warehouse_code": "WH-CENTRAL-01",
			"warehouse_name": "Central Godown 1",
			"warehouse_type": "central",
			"legacy_godown_key": "godown_1",
			"is_active": 1,
		},
		{
			"doctype": "Warehouse",
			"warehouse_code": "WH-CENTRAL-02",
			"warehouse_name": "Central Godown 2",
			"warehouse_type": "central",
			"legacy_godown_key": "godown_2",
			"is_active": 1,
		},
		{
			"doctype": "Inventory Item",
			"item_code": "ITEM-DRIP-001",
			"item_name": "Drip Kit Standard",
			"item_group": "drip",
			"uom": "Nos",
			"is_stock_item": 1,
			"has_batch_no": 1,
			"is_active": 1,
			"reorder_level": 10,
		},
		{
			"doctype": "Inventory Item",
			"item_code": "ITEM-FILTER-001",
			"item_name": "Disc Filter Unit",
			"item_group": "filter",
			"uom": "Nos",
			"is_stock_item": 1,
			"has_serial_no": 1,
			"is_active": 1,
			"reorder_level": 5,
		},
	]
	created = []
	for row in seed:
		if frappe.db.exists(row["doctype"], row.get("warehouse_code") or row.get("item_code")):
			continue
		doc = frappe.get_doc(row)
		doc.insert(ignore_permissions=True)
		created.append(doc.name)
	print({"seeded": created})
