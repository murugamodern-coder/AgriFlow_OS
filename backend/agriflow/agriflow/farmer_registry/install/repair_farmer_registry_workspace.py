# Copyright (c) 2026, Murugan and contributors
"""Repair Farmer Registry Workspace UI."""

from __future__ import annotations

import frappe

from agriflow.farmer_registry.workspace_data import farmer_registry_workspace_doc
from agriflow.workspaces.common import repair_workspace


def execute() -> dict:
	result = repair_workspace(farmer_registry_workspace_doc())
	frappe.clear_cache()
	return result
