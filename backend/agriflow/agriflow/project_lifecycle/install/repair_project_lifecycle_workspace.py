# Copyright (c) 2026, Murugan and contributors
"""Repair Project Lifecycle Workspace UI."""

from __future__ import annotations

import frappe

from agriflow.project_lifecycle.workspace_data import project_lifecycle_workspace_doc
from agriflow.workspaces.common import repair_workspace


def execute() -> dict:
	result = repair_workspace(project_lifecycle_workspace_doc())
	frappe.clear_cache()
	return result
