# Copyright (c) 2026, Murugan and contributors
"""Fix templates.py indentation bug."""

from pathlib import Path

PATH = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow/task_engine/services/templates.py")

CONTENT = '''# Copyright (c) 2026, Murugan and contributors
"""Idempotent stage task generation from JSON fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import frappe
from frappe.utils import add_days, today


def template_client_id(farmer_project: str, template_id: str) -> str:
\t"""Deterministic idempotency key within 36 chars."""
\treturn hashlib.sha256(f"{farmer_project}|{template_id}".encode()).hexdigest()[:32]

from agriflow.task_engine.services.lifecycle import TaskLifecycleService

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "fixtures" / "task_template.json"


def load_task_templates() -> list[dict]:
\tif not FIXTURE_PATH.exists():
\t\treturn []
\twith FIXTURE_PATH.open(encoding="utf-8") as fh:
\t\tdata = json.load(fh)
\treturn data if isinstance(data, list) else []


def generate_stage_tasks(farmer_project: str, to_stage: str) -> list[str]:
\t"""Create template tasks for entered stage; idempotent by source_template + stage_key."""
\tproject = frappe.get_doc("Farmer Project", farmer_project)
\tcreated: list[str] = []
\tlifecycle = TaskLifecycleService()

\tfor tpl in load_task_templates():
\t\tif tpl.get("to_stage") != to_stage:
\t\t\tcontinue
\t\ttemplate_id = tpl["template_id"]
\t\tif frappe.db.exists(
\t\t\t"Project Task",
\t\t\t{
\t\t\t\t"farmer_project": farmer_project,
\t\t\t\t"source_template": template_id,
\t\t\t\t"stage_key": to_stage,
\t\t\t\t"is_deleted": 0,
\t\t\t},
\t\t):
\t\t\tcontinue

\t\tofficer = None
\t\tif tpl.get("default_officer_from") == "project.officer":
\t\t\tofficer = project.officer

\t\tdue = add_days(today(), int(tpl.get("due_offset_days", 3)))
\t\tdoc = lifecycle.create_task(
\t\t\tsubject=tpl["subject"],
\t\t\tfarmer_project=farmer_project,
\t\t\ttask_type=tpl["task_type"],
\t\t\tdue_date=due,
\t\t\tpriority=tpl.get("priority", "normal"),
\t\t\tstage_key=to_stage,
\t\t\tsource_template=template_id,
\t\t\tassigned_officer=officer,
\t\t\tauto_assign=bool(officer),
\t\t\tclient_id=template_client_id(farmer_project, template_id),
\t\t)
\t\tcreated.append(doc.name)
\treturn created
'''

PATH.write_text(CONTENT.replace("\\t", "\t"), encoding="utf-8")
print("fixed", PATH)
