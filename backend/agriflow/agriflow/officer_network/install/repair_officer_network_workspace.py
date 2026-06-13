# Copyright (c) 2026, Murugan and contributors
"""Repair Officer Network Workspace UI."""

from __future__ import annotations

import frappe

from agriflow.officer_network.workspace_data import officer_network_workspace_doc
from agriflow.workspaces.common import repair_workspace


def execute() -> dict:
	result = repair_workspace(officer_network_workspace_doc())
	frappe.clear_cache()
	return result
