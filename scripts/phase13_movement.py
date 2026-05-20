# Copyright (c) 2026, Murugan and contributors
"""Inward / outward / adjust / transfer movements."""

from __future__ import annotations

from typing import Any

import frappe

from agriflow.inventory.services.ledger import post_ledger
from agriflow.inventory.services.validation import assert_inventory_writer, assert_warehouse_access


def post_movement(payload: dict) -> dict[str, Any]:
	assert_inventory_writer()
	movement_type = payload.get("movement_type")
	warehouse = payload.get("warehouse")
	qty = float(payload.get("qty") or 0)
	if movement_type not in ("inward", "outward", "adjust"):
		frappe.throw(frappe._("movement_type must be inward, outward, or adjust"))
	assert_warehouse_access(warehouse)
	ledger = post_ledger(
		movement_type=movement_type,
		warehouse=warehouse,
		inventory_item=payload.get("inventory_item"),
		qty=qty,
		adjustment_sign=payload.get("adjustment_sign"),
		batch_no=payload.get("batch_no"),
		serial_no=payload.get("serial_no"),
		farmer_project=payload.get("farmer_project"),
		project_task=payload.get("project_task"),
		remarks=payload.get("remarks"),
		client_id=payload.get("client_id"),
		client_mutation_id=payload.get("client_mutation_id"),
	)
	return {"ledger": ledger, "movement_type": movement_type}


def transfer(
	*,
	from_warehouse: str,
	to_warehouse: str,
	inventory_item: str,
	qty: float,
	client_id: str | None = None,
	remarks: str | None = None,
	batch_no: str | None = None,
) -> dict[str, Any]:
	assert_inventory_writer()
	assert_warehouse_access(from_warehouse)
	assert_warehouse_access(to_warehouse)
	if from_warehouse == to_warehouse:
		frappe.throw(frappe._("Transfer requires different warehouses"))

	out_id = f"{client_id}-out" if client_id else None
	in_id = f"{client_id}-in" if client_id else None

	savepoint = f"inv_transfer_{frappe.generate_hash(length=10)}"
	frappe.db.savepoint(savepoint)
	try:
		out_ledger = post_ledger(
			movement_type="outward",
			warehouse=from_warehouse,
			inventory_item=inventory_item,
			qty=qty,
			batch_no=batch_no,
			remarks=remarks,
			client_id=out_id,
			client_mutation_id=client_id,
		)
		in_ledger = post_ledger(
			movement_type="inward",
			warehouse=to_warehouse,
			inventory_item=inventory_item,
			qty=qty,
			batch_no=batch_no,
			remarks=remarks,
			client_id=in_id,
			client_mutation_id=client_id,
			skip_availability_check=True,
		)
	except Exception:
		frappe.db.rollback(save_point=savepoint)
		raise

	return {"outward_ledger": out_ledger, "inward_ledger": in_ledger}
