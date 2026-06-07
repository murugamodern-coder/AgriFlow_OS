# Copyright (c) 2026, Murugan and contributors
"""Backfill workflow_state on existing Farmer Project rows."""

from __future__ import annotations

import frappe

from agriflow.project_lifecycle.workflow_bridge import workflow_state_for_stage


def after_migrate() -> None:
	rows = frappe.get_all(
		"Farmer Project",
		fields=["name", "workflow_state", "current_stage"],
		filters={"is_deleted": 0},
	)
	for row in rows:
		target = workflow_state_for_stage(row.current_stage)
		if row.workflow_state == target:
			print(f"{row.name} already at: {target}")
			continue
		frappe.db.set_value("Farmer Project", row.name, "workflow_state", target, update_modified=False)
		print(f"Migrated {row.name} → {target} (from {row.current_stage})")
	frappe.db.commit()
