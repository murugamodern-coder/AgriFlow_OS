#!/usr/bin/env python3
"""Generate workspace fixture JSON files from workspace_data modules (no Frappe required)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "backend" / "agriflow"
sys.path.insert(0, str(ROOT))

from agriflow.farmer_registry.workspace_data import farmer_registry_workspace_doc
from agriflow.inventory.workspace_data import inventory_workspace_doc
from agriflow.notification_engine.workspace_data import notification_engine_workspace_doc
from agriflow.officer_network.workspace_data import officer_network_workspace_doc
from agriflow.project_lifecycle.workspace_data import project_lifecycle_workspace_doc
from agriflow.sync_engine.workspace_data import sync_engine_workspace_doc
from agriflow.task_engine.workspace_data import task_engine_workspace_doc

FIXTURES = ROOT / "fixtures"

DOCS = {
	"workspace_inventory.json": inventory_workspace_doc,
	"workspace_farmer_registry.json": farmer_registry_workspace_doc,
	"workspace_officer_network.json": officer_network_workspace_doc,
	"workspace_project_lifecycle.json": project_lifecycle_workspace_doc,
	"workspace_sync_engine.json": sync_engine_workspace_doc,
	"workspace_task_engine.json": task_engine_workspace_doc,
	"workspace_notification_engine.json": notification_engine_workspace_doc,
}


def main() -> None:
	FIXTURES.mkdir(parents=True, exist_ok=True)
	for filename, builder in DOCS.items():
		payload = [builder()]
		path = FIXTURES / filename
		path.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
		print(f"wrote {path}")


if __name__ == "__main__":
	main()
