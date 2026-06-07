# Copyright (c) 2026, Murugan and contributors
"""Smoke-test billing APIs via bench execute."""

from __future__ import annotations

import frappe

from agriflow.install.bootstrap_billing_setup import ensure_item_stock


def run():
	ensure_item_stock(
		[
			"DRIP-16MM-100M",
			"DRIPPER-2LPH",
			"DRIP-12MM-50M",
			"DRIPPER-4LPH",
			"SPR-IMPACT",
			"SPR-MICRO",
			"PIPE-PVC-2INCH-6M",
			"PIPE-HDPE-32MM-100M",
			"FIT-ELBOW-2INCH",
			"FIT-TEE-2INCH",
			"MOTOR-1HP-SUBMERSIBLE",
			"MOTOR-2HP-OPENWELL",
			"FILTER-SAND-2INCH",
			"FILTER-SCREEN-2INCH",
			"VALVE-BALL-2INCH",
			"CAPACITOR-25MFD",
			"FERT-NPK-50KG",
			"SERVICE-LABOUR-HR",
		]
	)

	frappe.db.set_value(
		"Farmer Project",
		"FP-2026-00007",
		"workflow_state",
		"Quotation Generated",
		update_modified=False,
	)
	frappe.db.commit()

	from agriflow.api.v1 import billing

	cash = billing.create_cash_carry_invoice(
		items=[
			{"item_code": "DRIP-16MM-100M", "qty": 2, "rate": 850},
			{"item_code": "DRIPPER-2LPH", "qty": 50, "rate": 4},
		],
		customer_name="Selvam",
		customer_mobile="9876543210",
		payment_mode="Cash",
	)
	recent = billing.list_recent_invoices(limit=5)
	search = billing.get_item_search(search="Drip", limit=10)
	project = billing.create_project_invoice(
		project_name="FP-2026-00007",
		items=[{"item_code": "DRIP-16MM-100M", "qty": 10, "rate": 850}],
		subsidy_amount=6000,
		farmer_portion=2500,
		payment_mode="Cash",
	)

	print("CASH", cash)
	print("RECENT_COUNT", len(recent))
	print("SEARCH_COUNT", len(search))
	print("PROJECT", project)
