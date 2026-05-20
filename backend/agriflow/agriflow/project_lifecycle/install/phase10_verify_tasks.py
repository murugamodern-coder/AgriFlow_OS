# Copyright (c) 2026, Murugan and contributors
"""Phase 10 — verify Project Task foundation."""

from __future__ import annotations

import frappe

from agriflow.api.v1.project import timeline
from agriflow.task_engine.services.lifecycle import TaskLifecycleService
from agriflow.task_engine.services.queue import open_tasks_for_project
from agriflow.task_engine.services.templates import generate_stage_tasks
from agriflow.task_engine.utils.transitions import can_transition

PROJECT = "FP-2026-00007"


def execute():
    frappe.only_for("Administrator")
    errors: list[str] = []
    report: dict = {"project": PROJECT}

    if not frappe.db.exists("DocType", "Project Task"):
        errors.append("Project Task DocType missing")

    tasks = frappe.get_all(
        "Project Task",
        filters={"farmer_project": PROJECT, "is_deleted": 0},
        fields=["name", "status", "sla_started_at", "sla_due_at", "assigned_officer"],
    )
    report["task_count"] = len(tasks)
    if not tasks:
        errors.append("no sample tasks")

    hist = frappe.get_all(
        "Project Task Assignment History",
        filters={"farmer_project": PROJECT},
        fields=["name", "unassigned_on", "officer"],
        order_by="assigned_on asc",
    )
    report["assignment_rows"] = len(hist)
    if not hist:
        errors.append("no assignment history")

    in_prog = [t for t in tasks if t.status == "in_progress"]
    if in_prog and not in_prog[0].sla_started_at:
        errors.append("sla_started_at missing on in_progress")

    assigned_only = frappe.get_all(
        "Project Task",
        filters={"farmer_project": PROJECT, "status": "assigned", "is_deleted": 0},
        fields=["sla_started_at"],
        limit=1,
    )
    if assigned_only and assigned_only[0].sla_started_at:
        errors.append("sla_started_at set on assigned (should only start at in_progress)")

    completed = frappe.db.get_value(
        "Project Task", {"status": "completed", "farmer_project": PROJECT}, "name"
    )
    if completed:
        try:
            TaskLifecycleService().transition_status(completed, "in_progress")
            errors.append("terminal transition allowed")
        except Exception:
            report["terminal_blocked"] = True

    events = frappe.get_all(
        "Timeline Event",
        filters={"farmer_project": PROJECT, "event_type": ("like", "task_%"), "is_deleted": 0},
        pluck="event_type",
    )
    report["task_event_types"] = sorted(set(events))
    for needed in ("task_created", "task_assigned", "task_status_changed"):
        if needed not in report["task_event_types"]:
            errors.append(f"missing timeline event {needed}")

    open_rows = open_tasks_for_project(PROJECT)
    report["open_tasks_count"] = len(open_rows)
    resp = timeline({"name": PROJECT, "limit": 5})
    if resp.get("ok"):
        api_open = resp["data"].get("open_tasks", [])
        report["api_open_tasks"] = len(api_open)
        if len(api_open) != len(open_rows):
            errors.append("open_tasks mismatch API vs service")
    else:
        errors.append(f"timeline API failed: {resp}")

    # Idempotent template proof on a stage not yet generated
    tpl_stage = "field_survey"
    first = generate_stage_tasks(PROJECT, tpl_stage)
    second = generate_stage_tasks(PROJECT, tpl_stage)
    report["template_stage"] = tpl_stage
    report["template_run1"] = len(first)
    report["template_run2"] = len(second)
    report["template_task"] = first[0] if first else frappe.db.get_value(
        "Project Task",
        {
            "farmer_project": PROJECT,
            "source_template": "field_survey_visit",
            "stage_key": tpl_stage,
            "is_deleted": 0,
        },
        "name",
    )
    if not first and not report["template_task"]:
        errors.append("template task not created for field_survey")
    if second:
        errors.append("template generation not idempotent")

    if not can_transition("completed", "in_progress"):
        report["transition_matrix"] = "ok"

    report["ok"] = len(errors) == 0
    report["errors"] = errors
    print(report)
