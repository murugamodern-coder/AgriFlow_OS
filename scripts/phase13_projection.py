# Copyright (c) 2026, Murugan and contributors
"""Derived stock — never authoritative on master rows."""

from __future__ import annotations

import frappe

ON_HAND_SQL = """
SELECT COALESCE(SUM(
	CASE
		WHEN movement_type = 'inward' THEN qty
		WHEN movement_type = 'outward' THEN -qty
		WHEN movement_type = 'consume' THEN -qty
		WHEN movement_type = 'adjust' AND adjustment_sign = '+' THEN qty
		WHEN movement_type = 'adjust' AND adjustment_sign = '-' THEN -qty
		ELSE 0
	END
), 0) AS on_hand
FROM `tabStock Ledger Entry`
WHERE warehouse = %(warehouse)s AND inventory_item = %(item)s
"""

RESERVED_SQL = """
SELECT COALESCE(SUM(
	CASE
		WHEN movement_type = 'reserve' THEN qty
		WHEN movement_type = 'release' THEN -qty
		WHEN movement_type = 'consume' THEN -qty
		ELSE 0
	END
), 0) AS reserved
FROM `tabStock Ledger Entry`
WHERE warehouse = %(warehouse)s AND inventory_item = %(item)s
"""


def get_on_hand(warehouse: str, inventory_item: str) -> float:
	row = frappe.db.sql(
		ON_HAND_SQL,
		{"warehouse": warehouse, "item": inventory_item},
		as_dict=True,
	)
	return float(row[0].on_hand if row else 0)


def get_reserved(warehouse: str, inventory_item: str) -> float:
	row = frappe.db.sql(
		RESERVED_SQL,
		{"warehouse": warehouse, "item": inventory_item},
		as_dict=True,
	)
	return float(row[0].reserved if row else 0)


def get_available(warehouse: str, inventory_item: str) -> float:
	return get_on_hand(warehouse, inventory_item) - get_reserved(warehouse, inventory_item)


def assert_available(warehouse: str, inventory_item: str, qty: float) -> None:
	available = get_available(warehouse, inventory_item)
	if available < float(qty):
		frappe.throw(
			frappe._("Insufficient available stock: have {0}, need {1}").format(available, qty)
		)


def allocation_balances(allocation_name: str) -> dict:
	rows = frappe.get_all(
		"Stock Ledger Entry",
		filters={"project_material_allocation": allocation_name},
		fields=["movement_type", "qty"],
	)
	reserved = released = consumed = 0.0
	for r in rows:
		q = float(r.qty or 0)
		if r.movement_type == "reserve":
			reserved += q
		elif r.movement_type == "release":
			released += q
		elif r.movement_type == "consume":
			consumed += q
	remaining = reserved - released - consumed
	return {
		"reserved": reserved,
		"released": released,
		"consumed": consumed,
		"remaining": remaining,
	}


def list_low_stock(warehouse: str | None = None, limit: int = 50) -> list[dict]:
	"""Items where on_hand <= reorder_level (foundation)."""
	wh_filter = ""
	values: dict = {"lim": limit}
	if warehouse:
		wh_filter = "AND sle.warehouse = %(warehouse)s"
		values["warehouse"] = warehouse
	return frappe.db.sql(
		f"""
		SELECT i.name AS inventory_item, i.item_code, i.item_name, i.reorder_level,
			sle.warehouse,
			COALESCE(SUM(
				CASE
					WHEN sle.movement_type = 'inward' THEN sle.qty
					WHEN sle.movement_type IN ('outward','consume') THEN -sle.qty
					WHEN sle.movement_type = 'adjust' AND sle.adjustment_sign = '+' THEN sle.qty
					WHEN sle.movement_type = 'adjust' AND sle.adjustment_sign = '-' THEN -sle.qty
					ELSE 0
				END
			), 0) AS on_hand
		FROM `tabInventory Item` i
		CROSS JOIN `tabStock Ledger Entry` sle
		WHERE i.is_active = 1 AND i.is_stock_item = 1
			AND sle.inventory_item = i.name
			{wh_filter}
		GROUP BY i.name, sle.warehouse
		HAVING on_hand <= i.reorder_level AND i.reorder_level > 0
		LIMIT %(lim)s
		""",
		values,
		as_dict=True,
	)
