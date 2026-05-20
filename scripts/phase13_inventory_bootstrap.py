#!/usr/bin/env python3
"""Phase 13 — Inventory & material logistics bootstrap."""
from __future__ import annotations

import json
from pathlib import Path

APP = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
FIXTURES = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/fixtures")
MODULE = "Inventory"
MOVEMENT_OPTS = "inward\noutward\nreserve\nrelease\nconsume\nadjust"
PERMS_SM = [
	{
		"role": "System Manager",
		"read": 1,
		"write": 1,
		"create": 1,
		"delete": 0,
		"export": 1,
		"print": 1,
		"email": 1,
		"report": 1,
		"share": 1,
	}
]
SCRIPTS = Path(__file__).resolve().parent

SERVICE_MAP = {
	"phase13_validation.py": "validation.py",
	"phase13_idempotency.py": "idempotency.py",
	"phase13_projection.py": "projection.py",
	"phase13_timeline_hook.py": "timeline_hook.py",
	"phase13_ledger.py": "ledger.py",
	"phase13_movement.py": "movement.py",
	"phase13_reservation.py": "reservation.py",
	"phase13_consumption.py": "consumption.py",
	"phase13_serializers.py": "../api/serializers.py",
}


def write(path: Path, content: str) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(content, encoding="utf-8")
	print(f"  wrote {path.relative_to(APP.parent)}")


def field(fn, ft, label, **kw) -> dict:
	f = {
		"fieldname": fn,
		"fieldtype": ft,
		"label": label,
		"reqd": kw.get("reqd", 0),
		"read_only": kw.get("read_only", 0),
		"in_list_view": kw.get("in_list_view", 0),
		"in_standard_filter": kw.get("in_standard_filter", 0),
		"search_index": kw.get("search_index", 0),
		"unique": kw.get("unique", 0),
	}
	for k in ("options", "default", "length"):
		if k in kw and kw[k] is not None:
			f[k] = kw[k]
	return f


def doctype(name, fields, *, autoname, title_field="", track_changes=0, sort_field="modified"):
	return {
		"actions": [],
		"allow_rename": 0,
		"autoname": autoname,
		"creation": "2026-05-20 00:00:00.000000",
		"doctype": "DocType",
		"engine": "InnoDB",
		"field_order": [f["fieldname"] for f in fields],
		"fields": fields,
		"module": MODULE,
		"name": name,
		"owner": "Administrator",
		"permissions": PERMS_SM,
		"sort_field": sort_field,
		"sort_order": "DESC",
		"track_changes": track_changes,
		"title_field": title_field,
	}


def write_doctypes() -> None:
	# Inventory Item
	item_fields = [
		field("item_code", "Data", "Item Code", reqd=1, unique=1, in_list_view=1),
		field("item_name", "Data", "Item Name", reqd=1, in_list_view=1),
		field("item_group", "Data", "Item Group"),
		field("uom", "Data", "UOM", default="Nos", reqd=1),
		field("is_stock_item", "Check", "Is Stock Item", default="1"),
		field("has_batch_no", "Check", "Has Batch No"),
		field("has_serial_no", "Check", "Has Serial No"),
		field("reorder_level", "Float", "Reorder Level"),
		field("standard_rate", "Currency", "Standard Rate"),
		field("is_active", "Check", "Is Active", default="1", in_list_view=1),
	]
	ibase = APP / "inventory" / "doctype" / "inventory_item"
	write(ibase / "__init__.py", "")
	write(
		ibase / "inventory_item.json",
		json.dumps(
			doctype("Inventory Item", item_fields, autoname="field:item_code", title_field="item_name"),
			indent=1,
		)
		+ "\n",
	)
	write(
		ibase / "inventory_item.py",
		"# Copyright (c) 2026\nimport frappe\nfrom frappe.model.document import Document\n\nclass InventoryItem(Document):\n\tpass\n",
	)

	wh_fields = [
		field("warehouse_code", "Data", "Warehouse Code", reqd=1, unique=1, in_list_view=1),
		field("warehouse_name", "Data", "Warehouse Name", reqd=1, in_list_view=1),
		field("warehouse_type", "Select", "Type", options="central\nblock\ntransit", default="central", reqd=1),
		field("block", "Link", "Block", options="Block"),
		field("district", "Link", "District", options="District"),
		field("legacy_godown_key", "Data", "Legacy Godown Key"),
		field("is_active", "Check", "Is Active", default="1", in_list_view=1),
	]
	wbase = APP / "inventory" / "doctype" / "warehouse"
	write(wbase / "__init__.py", "")
	write(
		wbase / "warehouse.json",
		json.dumps(
			doctype("Warehouse", wh_fields, autoname="field:warehouse_code", title_field="warehouse_name"),
			indent=1,
		)
		+ "\n",
	)
	write(
		wbase / "warehouse.py",
		"# Copyright (c) 2026\nimport frappe\nfrom frappe.model.document import Document\n\nclass Warehouse(Document):\n\tpass\n",
	)

	sle_fields = [
		field("movement_type", "Select", "Movement Type", options=MOVEMENT_OPTS, reqd=1, in_list_view=1),
		field("inventory_item", "Link", "Inventory Item", options="Inventory Item", reqd=1, in_list_view=1),
		field("warehouse", "Link", "Warehouse", options="Warehouse", reqd=1, in_list_view=1),
		field("qty", "Float", "Qty", reqd=1, in_list_view=1),
		field("uom", "Data", "UOM", default="Nos"),
		field("adjustment_sign", "Select", "Adjustment Sign", options="\n+\n-"),
		field("batch_no", "Data", "Batch No"),
		field("serial_no", "Data", "Serial No", length=140),
		field("farmer_project", "Link", "Farmer Project", options="Farmer Project"),
		field("project_task", "Link", "Project Task", options="Project Task"),
		field(
			"project_material_allocation",
			"Link",
			"Project Material Allocation",
			options="Project Material Allocation",
		),
		field("posting_datetime", "Datetime", "Posting Datetime", reqd=1, in_list_view=1),
		field("remarks", "Small Text", "Remarks"),
		field("block", "Link", "Block", options="Block", in_standard_filter=1),
		field("client_id", "Data", "Client ID", length=36, search_index=1),
		field("client_mutation_id", "Data", "Client Mutation ID", length=36),
		field("compensates_ledger", "Link", "Compensates Ledger", options="Stock Ledger Entry"),
		field("created_by", "Link", "Created By", options="User", read_only=1),
	]
	sbase = APP / "inventory" / "doctype" / "stock_ledger_entry"
	write(sbase / "__init__.py", "")
	write(
		sbase / "stock_ledger_entry.json",
		json.dumps(
			doctype(
				"Stock Ledger Entry",
				sle_fields,
				autoname="hash",
				title_field="movement_type",
				sort_field="posting_datetime",
			),
			indent=1,
		)
		+ "\n",
	)
	write(
		sbase / "stock_ledger_entry.py",
		'''# Copyright (c) 2026
import frappe
from frappe import _
from frappe.model.document import Document

from agriflow.inventory.services.ledger import LEDGER_WRITE_FLAG


class StockLedgerEntry(Document):
	def validate(self):
		if not self.is_new() and not frappe.flags.get(LEDGER_WRITE_FLAG):
			frappe.throw(_("Stock Ledger Entry is immutable"))

	def on_update(self):
		if not frappe.flags.get(LEDGER_WRITE_FLAG):
			frappe.throw(_("Stock Ledger Entry cannot be updated"))

	def on_trash(self):
		frappe.throw(_("Stock Ledger Entry cannot be deleted"))
''',
	)

	pma_fields = [
		field("farmer_project", "Link", "Farmer Project", options="Farmer Project", reqd=1, in_list_view=1),
		field("project_task", "Link", "Project Task", options="Project Task"),
		field("inventory_item", "Link", "Inventory Item", options="Inventory Item", reqd=1, in_list_view=1),
		field("warehouse", "Link", "Warehouse", options="Warehouse", reqd=1),
		field("qty_reserved", "Float", "Qty Reserved", reqd=1),
		field("qty_released", "Float", "Qty Released", read_only=1),
		field("qty_consumed", "Float", "Qty Consumed", read_only=1),
		field(
			"status",
			"Select",
			"Status",
			options="draft\nreserved\npartially_consumed\nconsumed\nreleased\ncancelled",
			default="draft",
			in_list_view=1,
		),
		field("block", "Link", "Block", options="Block"),
		field("reserved_on", "Datetime", "Reserved On"),
		field("released_on", "Datetime", "Released On"),
		field("consumed_on", "Datetime", "Consumed On"),
		field("doc_version", "Int", "Doc Version", default="1"),
		field("client_id", "Data", "Client ID", length=36, search_index=1),
		field("sync_status", "Select", "Sync Status", options="synced\npending", default="synced"),
	]
	pbase = APP / "inventory" / "doctype" / "project_material_allocation"
	write(pbase / "__init__.py", "")
	write(
		pbase / "project_material_allocation.json",
		json.dumps(
			doctype(
				"Project Material Allocation",
				pma_fields,
				autoname="format:PMA-{YYYY}-{#####}",
				title_field="farmer_project",
			),
			indent=1,
		)
		+ "\n",
	)
	write(
		pbase / "project_material_allocation.py",
		"# Copyright (c) 2026\nimport frappe\nfrom frappe.model.document import Document\n\nclass ProjectMaterialAllocation(Document):\n\tpass\n",
	)


def copy_services() -> None:
	dest = APP / "inventory"
	for sub in ("", "services", "api"):
		(dest / sub).mkdir(parents=True, exist_ok=True)
	write(dest / "__init__.py", "")
	write(dest / "services" / "__init__.py", "")
	write(dest / "api" / "__init__.py", "")
	for src, dst_name in SERVICE_MAP.items():
		if dst_name.startswith("../"):
			dst = dest / "api" / "serializers.py"
		else:
			dst = dest / "services" / dst_name
		write(dst, (SCRIPTS / src).read_text(encoding="utf-8"))
	write(APP / "api" / "v1" / "inventory.py", (SCRIPTS / "phase13_inventory_api.py").read_text(encoding="utf-8"))


def write_seed_fixtures() -> None:
	warehouses = [
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
	]
	items = [
		{
			"doctype": "Inventory Item",
			"item_code": "ITEM-DRIP-001",
			"item_name": "Drip Kit Standard",
			"item_group": "drip",
			"uom": "Nos",
			"is_stock_item": 1,
			"has_batch_no": 1,
			"has_serial_no": 0,
			"reorder_level": 10,
			"is_active": 1,
		},
		{
			"doctype": "Inventory Item",
			"item_code": "ITEM-FILTER-001",
			"item_name": "Disc Filter Unit",
			"item_group": "filter",
			"uom": "Nos",
			"is_stock_item": 1,
			"has_serial_no": 1,
			"reorder_level": 5,
			"is_active": 1,
		},
	]
	FIXTURES.mkdir(parents=True, exist_ok=True)
	(FIXTURES / "warehouse.json").write_text(json.dumps(warehouses, indent=1) + "\n", encoding="utf-8")
	(FIXTURES / "inventory_item.json").write_text(json.dumps(items, indent=1) + "\n", encoding="utf-8")
	print("  wrote fixtures warehouse.json + inventory_item.json")


def patch_hooks_fixtures() -> None:
	path = APP / "hooks.py"
	text = path.read_text(encoding="utf-8")
	if '{"dt": "Warehouse"}' not in text:
		text = text.replace(
			"fixtures = [",
			'fixtures = [\n    {"dt": "Warehouse"},\n    {"dt": "Inventory Item"},',
			1,
		)
		path.write_text(text, encoding="utf-8")
		print("  updated hooks fixtures")
	else:
		print("  hooks fixtures already include Warehouse")


def main() -> None:
	print("Phase 13 Inventory bootstrap")
	write_doctypes()
	copy_services()
	write_seed_fixtures()
	patch_hooks_fixtures()
	print("Done. Run: bench migrate && bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase13_seed_inventory.execute")


if __name__ == "__main__":
	main()
