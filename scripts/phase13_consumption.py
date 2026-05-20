# Copyright (c) 2026, Murugan and contributors
"""Project material consumption."""

from __future__ import annotations

from typing import Any

import frappe

from agriflow.inventory.services.ledger import PMA_WRITE_FLAG, post_ledger, refresh_allocation_status
from agriflow.inventory.services.projection import allocation_balances
from agriflow.inventory.services.timeline_hook import maybe_emit_material_event
from agriflow.inventory.services.validation import assert_inventory_writer


def consume(payload: dict) -> dict[str, Any]:
	assert_inventory_writer()
	allocation_name = payload.get("allocation") or payload.get("name")
	pma = frappe.get_doc("Project Material Allocation", allocation_name)
	if int(payload.get("doc_version") or 0) != int(pma.doc_version or 0):
		frappe.throw(frappe._("Stale doc_version on allocation"))

	stats = allocation_balances(allocation_name)
	qty = float(payload.get("qty") or stats["remaining"])
	if qty <= 0:
		frappe.throw(frappe._("Nothing to consume"))
	if qty > stats["remaining"]:
		frappe.throw(frappe._("Consume qty exceeds remaining reserved"))

	ledger = post_ledger(
		movement_type="consume",
		warehouse=pma.warehouse,
		inventory_item=pma.inventory_item,
		qty=qty,
		batch_no=payload.get("batch_no"),
		serial_no=payload.get("serial_no"),
		farmer_project=pma.farmer_project,
		project_task=payload.get("project_task") or pma.project_task,
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

	maybe_emit_material_event(
		"material_consumed",
		pma.farmer_project,
		payload={"allocation": pma.name, "qty": qty},
	)

	return {"allocation": pma.name, "ledger": ledger, "status": pma.status, "doc_version": pma.doc_version}
