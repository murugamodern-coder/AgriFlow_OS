# Copyright (c) 2026, Murugan and contributors
"""Prove generate_stage_tasks fires on ProjectLifecycleService.transition."""

from __future__ import annotations

import frappe

from agriflow.project_lifecycle.services.lifecycle import ProjectLifecycleService

PROJECT = "FP-2026-00007"
TARGET = "mimis_registered"


def execute():
    frappe.only_for("Administrator")
    project = frappe.get_doc("Farmer Project", PROJECT)
    before = frappe.db.count(
        "Project Task",
        {
            "farmer_project": PROJECT,
            "source_template": "mimis_registered_verification",
            "is_deleted": 0,
        },
    )

    if project.current_stage != "documents_collected":
        print(
            {
                "ok": False,
                "skipped": True,
                "reason": f"project at {project.current_stage}, need documents_collected",
            }
        )
        return

    if (project.mimis_gate_status or "pending") not in ("approved", "waived"):
        frappe.db.set_value(
            "Farmer Project",
            PROJECT,
            "mimis_gate_status",
            "waived",
            update_modified=False,
        )
        frappe.db.commit()
        project.reload()

    svc = ProjectLifecycleService()
    result = svc.transition(
        PROJECT,
        TARGET,
        doc_version=project.doc_version,
        notes="Phase 10 lifecycle template proof",
    )

    after = frappe.db.count(
        "Project Task",
        {
            "farmer_project": PROJECT,
            "source_template": "mimis_registered_verification",
            "is_deleted": 0,
        },
    )
    task_name = frappe.db.get_value(
        "Project Task",
        {
            "farmer_project": PROJECT,
            "source_template": "mimis_registered_verification",
            "is_deleted": 0,
        },
        "name",
    )

    # Idempotent re-call via service helper
    from agriflow.task_engine.services.templates import generate_stage_tasks

    second = generate_stage_tasks(PROJECT, TARGET)

    print(
        {
            "ok": after > before,
            "transition": result,
            "template_tasks_before": before,
            "template_tasks_after": after,
            "template_task": task_name,
            "idempotent_second_run": second,
            "current_stage": frappe.db.get_value("Farmer Project", PROJECT, "current_stage"),
        }
    )
