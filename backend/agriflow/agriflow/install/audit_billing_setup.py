# Copyright (c) 2026, Murugan and contributors
"""Phase 1 audit: Sales Invoice / Customer / Item counts and agriflow doctypes."""

from __future__ import annotations

import os

import frappe


def run():
	doctypes = ("Sales Invoice", "Customer", "Item")
	counts = {}
	for dt in doctypes:
		counts[dt] = frappe.db.count(dt) if frappe.db.table_exists(dt) else None

	app_root = frappe.get_app_path("agriflow")
	entries = []
	for root, _dirs, files in os.walk(app_root):
		if "/doctype/" not in root.replace("\\", "/"):
			continue
		folder = os.path.basename(root)
		if any(k in folder.lower() for k in ("invoice", "sales", "customer", "item")):
			entries.append(folder)
	entries = sorted(set(entries))

	print("COUNTS", counts)
	print("AGRI_DOCTYPES", entries)
	print("ERPNext_INSTALLED", bool(frappe.db.exists("Module Def", "Accounts")))
