# Copyright (c) 2026, Murugan and contributors
"""Inventory APIs — ledger-first (API_CONTRACTS §21)."""

from __future__ import annotations

import frappe
from frappe import _

from agriflow.api.v1.permissions import ensure_authenticated, get_allowed_blocks
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.inventory.api.serializers import (
	to_allocation_summary,
	to_item_summary,
	to_ledger_row,
	to_warehouse_summary,
)
from agriflow.inventory.services.consumption import consume as do_consume
from agriflow.inventory.services.movement import post_movement, transfer
from agriflow.inventory.services.projection import get_available, get_on_hand, get_reserved
from agriflow.inventory.services.reservation import release as do_release
from agriflow.inventory.services.reservation import reserve as do_reserve
from agriflow.inventory.services.validation import assert_inventory_writer


@frappe.whitelist()
def items(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		filters = {"is_active": 1}
		if payload.get("search"):
			filters["item_name"] = ("like", f"%{payload['search']}%")
		rows = frappe.get_all(
			"Inventory Item",
			filters=filters,
			fields=[
				"name",
				"item_code",
				"item_name",
				"uom",
				"has_batch_no",
				"has_serial_no",
				"reorder_level",
				"is_active",
			],
			limit=min(max(int(payload.get("limit") or 100), 1), 500),
			order_by="item_name asc",
		)
		return success({"items": [to_item_summary(r) for r in rows]})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def warehouses(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		filters = {"is_active": 1}
		allowed = get_allowed_blocks()
		if allowed is not None:
			filters["block"] = ("in", list(allowed)) if allowed else ("in", [""])
			# include central warehouses (no block)
		rows = frappe.get_all(
			"Warehouse",
			filters=filters,
			fields=["name", "warehouse_code", "warehouse_name", "warehouse_type", "block", "is_active"],
			limit=100,
			order_by="warehouse_code asc",
		)
		if allowed is not None:
			central = frappe.get_all(
				"Warehouse",
				filters={"is_active": 1, "block": ("is", "not set")},
				fields=["name", "warehouse_code", "warehouse_name", "warehouse_type", "block", "is_active"],
			)
			seen = {r.name for r in rows}
			for c in central:
				if c.name not in seen:
					rows.append(c)
		return success({"warehouses": [to_warehouse_summary(r) for r in rows]})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def stock_on_hand(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		wh = payload.get("warehouse")
		item = payload.get("inventory_item")
		if not wh or not item:
			return fail("VAL_INVALID", _("warehouse and inventory_item required"), http_status=400)
		return success(
			{
				"warehouse": wh,
				"inventory_item": item,
				"on_hand": get_on_hand(wh, item),
				"reserved": get_reserved(wh, item),
				"available": get_available(wh, item),
			}
		)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def ledger_list(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		filters = {}
		if payload.get("warehouse"):
			filters["warehouse"] = payload["warehouse"]
		if payload.get("inventory_item"):
			filters["inventory_item"] = payload["inventory_item"]
		if payload.get("farmer_project"):
			filters["farmer_project"] = payload["farmer_project"]
		allowed = get_allowed_blocks()
		if allowed is not None and allowed:
			filters["block"] = ("in", list(allowed))
		limit = min(max(int(payload.get("limit") or 50), 1), 100)
		rows = frappe.get_all(
			"Stock Ledger Entry",
			filters=filters,
			fields=[
				"name",
				"movement_type",
				"inventory_item",
				"warehouse",
				"qty",
				"adjustment_sign",
				"batch_no",
				"serial_no",
				"farmer_project",
				"project_task",
				"project_material_allocation",
				"posting_datetime",
				"client_id",
			],
			order_by="posting_datetime desc, name desc",
			limit=limit,
		)
		return success({"items": [to_ledger_row(r) for r in rows]})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def movement_post(data=None):
	try:
		ensure_authenticated()
		out = post_movement(parse_data(data))
		return success(out)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)


@frappe.whitelist()
def transfer_post(data=None):
	try:
		ensure_authenticated()
		p = parse_data(data)
		out = transfer(
			from_warehouse=p["from_warehouse"],
			to_warehouse=p["to_warehouse"],
			inventory_item=p["inventory_item"],
			qty=float(p["qty"]),
			client_id=p.get("client_id"),
			remarks=p.get("remarks"),
			batch_no=p.get("batch_no"),
		)
		return success(out)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)


@frappe.whitelist()
def allocation_reserve(data=None):
	try:
		ensure_authenticated()
		return success(do_reserve(parse_data(data)))
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)


@frappe.whitelist()
def allocation_release(data=None):
	try:
		ensure_authenticated()
		return success(do_release(parse_data(data)))
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)


@frappe.whitelist()
def allocation_consume(data=None):
	try:
		ensure_authenticated()
		return success(do_consume(parse_data(data)))
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)


@frappe.whitelist()
def allocation_list(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		filters = {}
		if payload.get("farmer_project"):
			filters["farmer_project"] = payload["farmer_project"]
		allowed = get_allowed_blocks()
		if allowed is not None and allowed:
			filters["block"] = ("in", list(allowed))
		rows = frappe.get_all(
			"Project Material Allocation",
			filters=filters,
			fields=[
				"name",
				"farmer_project",
				"inventory_item",
				"warehouse",
				"qty_reserved",
				"qty_released",
				"qty_consumed",
				"status",
				"doc_version",
				"project_task",
			],
			order_by="modified desc",
			limit=min(max(int(payload.get("limit") or 50), 1), 100),
		)
		return success({"items": [to_allocation_summary(r) for r in rows]})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


# Legacy alias (API_CONTRACTS stock_entry.create → inward/outward)
@frappe.whitelist()
def stock_entry_create(data=None):
	return movement_post(data)
