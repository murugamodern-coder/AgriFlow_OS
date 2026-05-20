# Copyright (c) 2026, Murugan and contributors
"""Project material reservation."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime

from agriflow.inventory.services.ledger import PMA_WRITE_FLAG, post_ledger, refresh_allocation_status
from agriflow.inventory.services.projection import assert_available
from agriflow.inventory.services.timeline_hook import maybe_emit_material_event
from agriflow.inventory.services.validation import (
	assert_inventory_writer,
	assert_project_material_eligible,
	assert_warehouse_access,
	validate_item_line,
)


def reserve(payload: dict) -> dict[str, Any]:
	assert_inventory_writer()
	project_name = payload.get("farmer_project")
	project = assert_project_material_eligible(project_name)
	warehouse = payload.get("warehouse")
	assert_warehouse_access(warehouse)
	qty = float(payload.get("qty") or 0)
	item = validate_item_line(
		payload.get("inventory_item"),
		qty,
		batch_no=payload.get("batch_no"),
		serial_no=payload.get("serial_no"),
	)
	assert_available(warehouse, item.name, qty)

	client_id = payload.get("client_id")
	if client_id and frappe.db.exists("Project Material Allocation", {"client_id": client_id}):
		name = frappe.db.get_value("Project Material Allocation", {"client_id": client_id}, "name")
		refresh_allocation_status(name)
		return {"allocation": name, "replay": True}

	pma = frappe.get_doc(
		{
			"doctype": "Project Material Allocation",
			"farmer_project": project_name,
			"project_task": payload.get("project_task") or "",
			"inventory_item": item.name,
			"warehouse": warehouse,
			"qty_reserved": qty,
			"qty_released": 0,
			"qty_consumed": 0,
			"status": "reserved",
			"block": project.block,
			"reserved_on": now_datetime(),
			"doc_version": 1,
			"client_id": client_id or "",
			"sync_status": "synced",
		}
	)
	frappe.flags[PMA_WRITE_FLAG] = True
	try:
		pma.insert(ignore_permissions=True)
	finally:
		frappe.flags[PMA_WRITE_FLAG] = False

	ledger = post_ledger(
		movement_type="reserve",
		warehouse=warehouse,
		inventory_item=item.name,
		qty=qty,
		batch_no=payload.get("batch_no"),
		serial_no=payload.get("serial_no"),
		farmer_project=project_name,
		project_task=payload.get("project_task"),
		project_material_allocation=pma.name,
		remarks=payload.get("remarks"),
		block=project.block,
		client_id=f"{client_id}-reserve" if client_id else None,
		client_mutation_id=payload.get("client_mutation_id"),
	)

	refresh_allocation_status(pma.name)
	maybe_emit_material_event(
		"material_reserved",
		project_name,
		payload={"allocation": pma.name, "qty": qty, "item": item.item_code},
	)

	return {
		"allocation": pma.name,
		"ledger": ledger,
		"doc_version": pma.doc_version,
		"status": pma.status,
	}


def release(payload: dict) -> dict[str, Any]:
	assert_inventory_writer()
	allocation_name = payload.get("allocation") or payload.get("name")
	pma = frappe.get_doc("Project Material Allocation", allocation_name)
	if int(payload.get("doc_version") or 0) != int(pma.doc_version or 0):
		frappe.throw(frappe._("Stale doc_version on allocation"))

	from agriflow.inventory.services.projection import allocation_balances

	stats = allocation_balances(allocation_name)
	qty = float(payload.get("qty") or stats["remaining"])
	if qty <= 0:
		frappe.throw(frappe._("Nothing to release"))
	if qty > stats["remaining"]:
		frappe.throw(frappe._("Release qty exceeds remaining reserved"))

	ledger = post_ledger(
		movement_type="release",
		warehouse=pma.warehouse,
		inventory_item=pma.inventory_item,
		qty=qty,
		farmer_project=pma.farmer_project,
		project_material_allocation=pma.name,
		remarks=payload.get("remarks"),
		block=pma.block,
		client_id=payload.get("client_id"),
		client_mutation_id=payload.get("client_mutation_id"),
	)

	pma.doc_version = (pma.doc_version or 1) + 1
	frappe.flags[PMA_WRITE_FLAG] = True
	try:
		pma.save(ignore_permissions=True)
	finally:
		frappe.flags[PMA_WRITE_FLAG] = False
	refresh_allocation_status(allocation_name)
	pma.reload()

	return {"allocation": pma.name, "ledger": ledger, "status": pma.status, "doc_version": pma.doc_version}
