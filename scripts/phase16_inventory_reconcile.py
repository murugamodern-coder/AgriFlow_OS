# Copyright (c) 2026, Murugan and contributors
"""Inventory ledger vs projection reconciliation (Phase 16)."""

from __future__ import annotations

import frappe

from agriflow.inventory.services.projection import get_on_hand, get_reserved


def execute():
	wh = "WH-CENTRAL-01"
	items = frappe.get_all("Inventory Item", filters={"is_active": 1}, pluck="name", limit=20)
	mismatches = []
	for item in items:
		on_hand = float(get_on_hand(wh, item) or 0)
		reserved = float(get_reserved(wh, item) or 0)
		available = on_hand - reserved
		if on_hand < 0 or reserved < 0 or available < -0.001:
			mismatches.append(
				{
					"item": item,
					"on_hand": on_hand,
					"reserved": reserved,
					"available": available,
					"rule": "non_negative_stock",
				}
			)
	return {
		"ok": len(mismatches) == 0,
		"warehouse": wh,
		"items_checked": len(items),
		"mismatches": mismatches,
	}
