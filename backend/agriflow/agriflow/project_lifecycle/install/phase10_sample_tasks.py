# Copyright (c) 2026, Murugan and contributors
"""Phase 10 — sample Project Task rows."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, today

from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.lifecycle import TaskLifecycleService
from agriflow.task_engine.services.templates import generate_stage_tasks

PROJECT = "FP-2026-00007"
OFFICER_CODE = "OFF01"


def _ensure_officer(project_name: str) -> str:
    project = frappe.get_doc("Farmer Project", project_name)
    if project.officer:
        return project.officer

    officer_name = frappe.db.get_value("Officer", {"officer_code": OFFICER_CODE}, "name")
    if not officer_name:
        officer_name = OFFICER_CODE
        frappe.get_doc(
            {
                "doctype": "Officer",
                "officer_code": OFFICER_CODE,
                "officer_name": "Sample Officer Phase 10",
                "department": "agriculture",
                "is_active": 1,
            }
        ).insert(ignore_permissions=True)

    frappe.flags.agriflow_lifecycle_write = True
    try:
        project.officer = officer_name
        project.save(ignore_permissions=True)
    finally:
        frappe.flags.agriflow_lifecycle_write = False
    frappe.db.commit()
    return officer_name


def execute():
    frappe.only_for("Administrator")
    officer = _ensure_officer(PROJECT)

    lifecycle = TaskLifecycleService()
    created = []

    t1 = lifecycle.create_task(
        subject="Follow up land records",
        farmer_project=PROJECT,
        task_type="follow_up",
        due_date=add_days(today(), 7),
        priority="normal",
        client_id="phase10-sample-follow-up",
    )
    created.append(t1.name)

    TaskAssignmentService().assign(
        t1.name,
        officer,
        assigned_to=frappe.session.user,
        reason="initial",
    )
    t1.reload()
    lifecycle.transition_status(t1.name, "in_progress", doc_version=t1.doc_version)
    created.append(t1.name)

    t2 = lifecycle.create_task(
        subject="Collect Aadhaar copy",
        farmer_project=PROJECT,
        task_type="document_collection",
        due_date=add_days(today(), 3),
        priority="high",
        client_id="phase10-sample-doc",
    )
    TaskAssignmentService().assign(t2.name, officer, reason="initial")
    created.append(t2.name)

    stage = frappe.db.get_value("Farmer Project", PROJECT, "current_stage")
    tpl_created = generate_stage_tasks(PROJECT, stage)
    created.extend(tpl_created)

    print(
        {
            "ok": True,
            "project": PROJECT,
            "officer": officer,
            "tasks": list(dict.fromkeys(created)),
            "templates": tpl_created,
        }
    )
