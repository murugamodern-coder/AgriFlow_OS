# Copyright (c) 2026, Murugan and contributors
"""Repair Sync Engine Workspace UI."""

from __future__ import annotations

import frappe

from agriflow.sync_engine.workspace_data import sync_engine_workspace_doc
from agriflow.workspaces.common import repair_workspace


def execute() -> dict:
	result = repair_workspace(sync_engine_workspace_doc())
	frappe.clear_cache()
	return result
