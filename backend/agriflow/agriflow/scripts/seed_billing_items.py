# Copyright (c) 2026, Murugan and contributors
"""Seed sample agriculture items for billing demos."""

from __future__ import annotations

import click
import frappe


@click.command()
def seed_billing_items():
	"""Seed sample agriculture items for billing demos."""
	items = [
		{"item_code": "DRIP-16MM-100M", "item_name": "16mm Drip Pipe (100m roll)", "stock_uom": "Nos", "standard_rate": 850},
		{"item_code": "DRIP-12MM-50M", "item_name": "12mm Drip Pipe (50m roll)", "stock_uom": "Nos", "standard_rate": 420},
		{"item_code": "DRIPPER-2LPH", "item_name": "Online Dripper 2 LPH", "stock_uom": "Nos", "standard_rate": 4},
		{"item_code": "DRIPPER-4LPH", "item_name": "Online Dripper 4 LPH", "stock_uom": "Nos", "standard_rate": 5},
		{"item_code": "SPR-IMPACT", "item_name": "Impact Sprinkler (Brass)", "stock_uom": "Nos", "standard_rate": 320},
		{"item_code": "SPR-MICRO", "item_name": "Micro Sprinkler 70L/hr", "stock_uom": "Nos", "standard_rate": 28},
		{"item_code": "PIPE-PVC-2INCH-6M", "item_name": "PVC Pipe 2 inch x 6m", "stock_uom": "Nos", "standard_rate": 580},
		{"item_code": "PIPE-HDPE-32MM-100M", "item_name": "HDPE Pipe 32mm (100m)", "stock_uom": "Nos", "standard_rate": 1850},
		{"item_code": "FIT-ELBOW-2INCH", "item_name": "PVC Elbow 2 inch", "stock_uom": "Nos", "standard_rate": 35},
		{"item_code": "FIT-TEE-2INCH", "item_name": "PVC Tee 2 inch", "stock_uom": "Nos", "standard_rate": 42},
		{"item_code": "MOTOR-1HP-SUBMERSIBLE", "item_name": "Submersible Motor 1HP", "stock_uom": "Nos", "standard_rate": 8500},
		{"item_code": "MOTOR-2HP-OPENWELL", "item_name": "Open Well Motor 2HP", "stock_uom": "Nos", "standard_rate": 12500},
		{"item_code": "FILTER-SAND-2INCH", "item_name": "Sand Filter 2 inch", "stock_uom": "Nos", "standard_rate": 4500},
		{"item_code": "FILTER-SCREEN-2INCH", "item_name": "Screen Filter 2 inch", "stock_uom": "Nos", "standard_rate": 1200},
		{"item_code": "VALVE-BALL-2INCH", "item_name": "Ball Valve 2 inch", "stock_uom": "Nos", "standard_rate": 280},
		{"item_code": "CAPACITOR-25MFD", "item_name": "Motor Capacitor 25 MFD", "stock_uom": "Nos", "standard_rate": 180},
		{"item_code": "FERT-NPK-50KG", "item_name": "NPK Fertilizer 50kg bag", "stock_uom": "Bag", "standard_rate": 1450},
		{"item_code": "SERVICE-LABOUR-HR", "item_name": "Service Labour (per hour)", "stock_uom": "Hour", "standard_rate": 250},
	]

	count = 0
	for item_data in items:
		if not frappe.db.exists("Item", item_data["item_code"]):
			doc = frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_data["item_code"],
					"item_name": item_data["item_name"],
					"item_group": "Products",
					"stock_uom": item_data["stock_uom"],
					"standard_rate": item_data["standard_rate"],
					"is_stock_item": 1,
					"include_item_in_manufacturing": 0,
				}
			)
			doc.insert(ignore_permissions=True)
			count += 1

	frappe.db.commit()
	click.echo(f"Seeded {count} new items (total in catalog: {frappe.db.count('Item')})")
	from agriflow.install.bootstrap_billing_setup import ensure_item_stock

	ensure_item_stock([row["item_code"] for row in items])


def run():
	seed_billing_items.callback()


commands = [seed_billing_items]
