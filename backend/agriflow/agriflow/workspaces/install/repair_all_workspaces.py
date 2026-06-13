# Copyright (c) 2026, Murugan and contributors
"""Repair all AgriFlow module Workspaces in one bench execute call."""

from __future__ import annotations

import frappe

from agriflow.farmer_registry.install.repair_farmer_registry_workspace import (
	execute as repair_farmer_registry,
)
from agriflow.inventory.install.repair_inventory_workspace import execute as repair_inventory
from agriflow.notification_engine.install.repair_notification_engine_workspace import (
	execute as repair_notification_engine,
)
from agriflow.officer_network.install.repair_officer_network_workspace import (
	execute as repair_officer_network,
)
from agriflow.project_lifecycle.install.repair_project_lifecycle_workspace import (
	execute as repair_project_lifecycle,
)
from agriflow.sync_engine.install.repair_sync_engine_workspace import (
	execute as repair_sync_engine,
)
from agriflow.task_engine.install.repair_task_engine_workspace import (
	execute as repair_task_engine,
)


def execute() -> dict:
	"""Repair Inventory + six module workspaces (UI definitions only)."""
	repairers = (
		repair_inventory,
		repair_farmer_registry,
		repair_officer_network,
		repair_project_lifecycle,
		repair_sync_engine,
		repair_task_engine,
		repair_notification_engine,
	)
	results = [repair() for repair in repairers]
	frappe.clear_cache()
	return {"ok": True, "count": len(results), "results": results}
