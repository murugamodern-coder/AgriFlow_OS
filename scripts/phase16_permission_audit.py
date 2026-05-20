# Copyright (c) 2026, Murugan and contributors
"""Permission boundary audit for Phase 16."""

from __future__ import annotations

import frappe

from agriflow.api.v1.permissions import assert_block_scope, ensure_authenticated, get_allowed_blocks


def execute():
	findings = []
	checks = {}

	# Guest blocked
	frappe.set_user("Guest")
	try:
		ensure_authenticated()
		checks["guest_blocked"] = False
		findings.append("Guest was not blocked by ensure_authenticated")
	except frappe.AuthenticationError:
		checks["guest_blocked"] = True

	# Demo officer scope
	demo = "field.officer@agriflow.local"
	if frappe.db.exists("User", demo):
		frappe.set_user(demo)
		blocks = get_allowed_blocks()
		checks["demo_blocks_type"] = isinstance(blocks, (set, type(None)))
		project_block = frappe.db.get_value("Farmer Project", "FP-2026-00007", "block")
		if blocks is not None and project_block and project_block not in blocks:
			try:
				assert_block_scope(project_block)
				checks["demo_block_denied"] = False
				findings.append(f"Officer accessed block {project_block} without permission")
			except frappe.PermissionError:
				checks["demo_block_denied"] = True
		else:
			checks["demo_block_denied"] = "skipped"

	# Inventory writer roles
	from agriflow.inventory.services.validation import assert_inventory_writer

	frappe.set_user("Guest")
	try:
		assert_inventory_writer()
		checks["inventory_guest_denied"] = False
	except Exception:
		checks["inventory_guest_denied"] = True

	ok = len(findings) == 0
	return {"ok": ok, "checks": checks, "findings": findings}
