# Copyright (c) 2026, Murugan and contributors
"""Inventory validation helpers."""

from __future__ import annotations

import frappe
from frappe import _

MIN_STAGE_SEQUENCE_FOR_MATERIAL = 9
MOVEMENT_TYPES = frozenset({"inward", "outward", "reserve", "release", "consume", "adjust"})
PROJECT_MOVEMENTS = frozenset({"reserve", "release", "consume"})
WRITE_ROLES = frozenset({"Store Keeper", "Office Manager", "Owner", "System Manager", "Administrator"})


def assert_inventory_writer() -> None:
	if not set(frappe.get_roles()) & WRITE_ROLES:
		frappe.throw(_("Not permitted for inventory write"), exc=frappe.PermissionError)


def assert_warehouse_access(warehouse: str) -> dict:
	from agriflow.api.v1.permissions import assert_block_scope, get_allowed_blocks

	row = frappe.db.get_value(
		"Warehouse",
		warehouse,
		["name", "warehouse_code", "block", "is_active"],
		as_dict=True,
	)
	if not row or not row.is_active:
		frappe.throw(_("Warehouse not found or inactive"))
	if row.block:
		assert_block_scope(row.block)
	else:
		allowed = get_allowed_blocks()
		if allowed is not None and len(allowed) == 0:
			frappe.throw(_("Not permitted for any block"), exc=frappe.PermissionError)
	return row


def assert_project_material_eligible(project_name: str) -> dict:
	project = frappe.db.get_value(
		"Farmer Project",
		project_name,
		["name", "block", "stage_sequence", "status", "is_deleted", "current_stage"],
		as_dict=True,
	)
	if not project or project.is_deleted:
		frappe.throw(_("Farmer Project not found"))
	if project.status == "cancelled":
		frappe.throw(_("Cannot move stock for cancelled project"))
	if int(project.stage_sequence or 0) < MIN_STAGE_SEQUENCE_FOR_MATERIAL:
		frappe.throw(
			_("Material operations require stage sequence >= {0}").format(
				MIN_STAGE_SEQUENCE_FOR_MATERIAL
			)
		)
	return project


def validate_item_line(
	item_code: str,
	qty: float,
	*,
	batch_no: str | None = None,
	serial_no: str | None = None,
) -> dict:
	if qty <= 0:
		frappe.throw(_("Quantity must be positive"))
	item = frappe.db.get_value(
		"Inventory Item",
		item_code,
		["name", "item_code", "uom", "has_batch_no", "has_serial_no", "is_active", "is_stock_item"],
		as_dict=True,
	)
	if not item or not item.is_active or not item.is_stock_item:
		frappe.throw(_("Inventory Item not found or inactive"))
	if item.has_batch_no and not batch_no:
		frappe.throw(_("batch_no required for this item"))
	if item.has_serial_no:
		if not serial_no:
			frappe.throw(_("serial_no required for this item"))
		if float(qty) != 1.0:
			frappe.throw(_("Serial-tracked items must have qty = 1 per ledger row"))
	if serial_no and "," in serial_no:
		frappe.throw(_("Only one serial_no per ledger row"))
	return item
