# Copyright (c) 2026, Murugan and contributors
"""Repair empty Inventory Workspace after manual recreate or partial restore."""

from __future__ import annotations

import frappe

from agriflow.inventory.workspace_data import inventory_workspace_doc
from agriflow.workspaces.common import repair_workspace


def execute() -> dict:
	"""Populate Inventory workspace blocks, shortcuts, and sidebar links."""
	result = repair_workspace(inventory_workspace_doc())
	frappe.clear_cache()
	return result