# Copyright (c) 2026, Murugan and contributors
"""Install Farmer cascading geography Client Script for Frappe Desk."""

from __future__ import annotations

from pathlib import Path

import frappe

SCRIPT_NAME = "Farmer Cascading Geography"
SCRIPT_PATH = (
	Path(__file__).resolve().parent.parent / "client_scripts" / "farmer_cascading_geography.js"
)


def _script_body() -> str:
	return SCRIPT_PATH.read_text(encoding="utf-8")


def ensure_farmer_cascading_client_script() -> None:
	"""Create or update the Farmer Client Script (Desk form filters)."""
	body = _script_body()
	if frappe.db.exists("Client Script", SCRIPT_NAME):
		doc = frappe.get_doc("Client Script", SCRIPT_NAME)
		if doc.script == body and doc.enabled and doc.dt == "Farmer":
			return
		doc.script = body
		doc.enabled = 1
		doc.dt = "Farmer"
		doc.view = "Form"
		doc.module = "Farmer Registry"
		doc.save(ignore_permissions=True)
		return

	doc = frappe.get_doc(
		{
			"doctype": "Client Script",
			"name": SCRIPT_NAME,
			"dt": "Farmer",
			"view": "Form",
			"enabled": 1,
			"module": "Farmer Registry",
			"script": body,
		}
	)
	doc.insert(ignore_permissions=True)


def after_migrate() -> None:
	ensure_farmer_cascading_client_script()
