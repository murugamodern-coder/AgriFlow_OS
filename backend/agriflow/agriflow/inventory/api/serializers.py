# Copyright (c) 2026, Murugan and contributors
"""Inventory API serializers."""

from __future__ import annotations

from typing import Any


def to_item_summary(row: dict) -> dict[str, Any]:
	return {
		"name": row.get("name"),
		"item_code": row.get("item_code") or row.get("name"),
		"item_name": row.get("item_name"),
		"uom": row.get("uom"),
		"has_batch_no": bool(row.get("has_batch_no")),
		"has_serial_no": bool(row.get("has_serial_no")),
		"reorder_level": row.get("reorder_level"),
		"is_active": bool(row.get("is_active")),
	}


def to_warehouse_summary(row: dict) -> dict[str, Any]:
	return {
		"name": row.get("name"),
		"warehouse_code": row.get("warehouse_code") or row.get("name"),
		"warehouse_name": row.get("warehouse_name"),
		"warehouse_type": row.get("warehouse_type"),
		"block": row.get("block"),
		"is_active": bool(row.get("is_active")),
	}


def to_ledger_row(row: dict) -> dict[str, Any]:
	posted = row.get("posting_datetime")
	if hasattr(posted, "isoformat"):
		posted = posted.isoformat()
	return {
		"name": row.get("name"),
		"movement_type": row.get("movement_type"),
		"inventory_item": row.get("inventory_item"),
		"warehouse": row.get("warehouse"),
		"qty": row.get("qty"),
		"adjustment_sign": row.get("adjustment_sign") or None,
		"batch_no": row.get("batch_no") or None,
		"serial_no": row.get("serial_no") or None,
		"farmer_project": row.get("farmer_project") or None,
		"project_task": row.get("project_task") or None,
		"project_material_allocation": row.get("project_material_allocation") or None,
		"posting_datetime": posted,
		"client_id": row.get("client_id") or None,
	}


def to_allocation_summary(row: dict) -> dict[str, Any]:
	return {
		"name": row.get("name"),
		"farmer_project": row.get("farmer_project"),
		"inventory_item": row.get("inventory_item"),
		"warehouse": row.get("warehouse"),
		"qty_reserved": row.get("qty_reserved"),
		"qty_released": row.get("qty_released"),
		"qty_consumed": row.get("qty_consumed"),
		"status": row.get("status"),
		"doc_version": row.get("doc_version"),
		"project_task": row.get("project_task") or None,
	}
