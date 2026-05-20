# Copyright (c) 2026, Murugan and contributors
"""Immutable Stock Ledger Entry — sole stock mutation path."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime

from agriflow.inventory.services.idempotency import find_ledger_by_client_id
from agriflow.inventory.services.projection import assert_available
from agriflow.inventory.services.validation import (
	MOVEMENT_TYPES,
	PROJECT_MOVEMENTS,
	validate_item_line,
)

LEDGER_WRITE_FLAG = "agriflow_stock_ledger_write"
PMA_WRITE_FLAG = "agriflow_project_material_allocation_write"


def post_ledger(
	*,
	movement_type: str,
	warehouse: str,
	inventory_item: str,
	qty: float,
	adjustment_sign: str | None = None,
	batch_no: str | None = None,
	serial_no: str | None = None,
	farmer_project: str | None = None,
	project_task: str | None = None,
	project_material_allocation: str | None = None,
	posting_datetime: str | None = None,
	remarks: str | None = None,
	block: str | None = None,
	client_id: str | None = None,
	client_mutation_id: str | None = None,
	compensates_ledger: str | None = None,
	skip_availability_check: bool = False,
) -> str:
	if movement_type not in MOVEMENT_TYPES:
		frappe.throw(frappe._("Invalid movement_type: {0}").format(movement_type))

	existing = find_ledger_by_client_id(client_id)
	if existing:
		return existing

	item = validate_item_line(
		inventory_item, qty, batch_no=batch_no, serial_no=serial_no
	)

	if movement_type == "adjust":
		if adjustment_sign not in ("+", "-"):
			frappe.throw(frappe._("adjustment_sign must be + or - for adjust"))
	elif adjustment_sign:
		frappe.throw(frappe._("adjustment_sign only allowed for adjust"))

	if movement_type in PROJECT_MOVEMENTS and not farmer_project:
		frappe.throw(frappe._("farmer_project required for {0}").format(movement_type))

	if movement_type in ("outward", "reserve", "consume") and not skip_availability_check:
		assert_available(warehouse, item.name, qty)

	if not block and farmer_project:
		block = frappe.db.get_value("Farmer Project", farmer_project, "block")
	if not block:
		block = frappe.db.get_value("Warehouse", warehouse, "block")

	doc = frappe.get_doc(
		{
			"doctype": "Stock Ledger Entry",
			"movement_type": movement_type,
			"inventory_item": item.name,
			"warehouse": warehouse,
			"qty": float(qty),
			"uom": item.uom or "Nos",
			"adjustment_sign": adjustment_sign or "",
			"batch_no": batch_no or "",
			"serial_no": serial_no or "",
			"farmer_project": farmer_project or "",
			"project_task": project_task or "",
			"project_material_allocation": project_material_allocation or "",
			"posting_datetime": posting_datetime or now_datetime(),
			"remarks": remarks or "",
			"block": block or "",
			"client_id": client_id or "",
			"client_mutation_id": client_mutation_id or "",
			"compensates_ledger": compensates_ledger or "",
			"created_by": frappe.session.user,
		}
	)
	frappe.flags[LEDGER_WRITE_FLAG] = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags[LEDGER_WRITE_FLAG] = False
	return doc.name


def refresh_allocation_status(allocation_name: str) -> None:
	bal = frappe.db.get_value(
		"Project Material Allocation",
		allocation_name,
		["name", "qty_reserved", "doc_version"],
		as_dict=True,
	)
	if not bal:
		return
	from agriflow.inventory.services.projection import allocation_balances

	stats = allocation_balances(allocation_name)
	remaining = stats["remaining"]
	status = "reserved"
	if stats["consumed"] > 0 and remaining > 0:
		status = "partially_consumed"
	elif remaining <= 0 and stats["consumed"] > 0:
		status = "consumed"
	elif remaining <= 0 and stats["released"] >= stats["reserved"]:
		status = "released"

	doc = frappe.get_doc("Project Material Allocation", allocation_name)
	doc.qty_released = stats["released"]
	doc.qty_consumed = stats["consumed"]
	doc.status = status
	if status == "consumed":
		doc.consumed_on = doc.consumed_on or now_datetime()
	if status == "released":
		doc.released_on = doc.released_on or now_datetime()
	frappe.flags[PMA_WRITE_FLAG] = True
	try:
		doc.save(ignore_permissions=True)
	finally:
		frappe.flags[PMA_WRITE_FLAG] = False
