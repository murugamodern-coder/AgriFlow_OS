# Copyright (c) 2026, Murugan and contributors
"""Repair Task Engine Workspace UI."""

from __future__ import annotations

import frappe

from agriflow.task_engine.workspace_data import task_engine_workspace_doc
from agriflow.workspaces.common import repair_workspace


def execute() -> dict:
	result = repair_workspace(task_engine_workspace_doc())
	frappe.clear_cache()
	return result
