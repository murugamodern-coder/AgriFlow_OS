#!/usr/bin/env python3
"""Backfill Timeline Event rows from Project Stage History (idempotent)."""

PROJECTS = ("FP-2026-00007", "FP-2026-00008")


def execute():
    import frappe

    from agriflow.project_lifecycle.services.timeline import get_timeline_service

    frappe.set_user("Administrator")
    timeline = get_timeline_service()
    created = []

    for project_name in PROJECTS:
        if not frappe.db.exists("Farmer Project", project_name):
            continue
        project = frappe.get_doc("Farmer Project", project_name)

        if not frappe.db.exists(
            "Timeline Event",
            {"farmer_project": project_name, "event_type": "project_created", "is_deleted": 0},
        ):
            first = project.stage_history[0] if project.stage_history else None
            eid = timeline.emit(
                "project_created",
                project_name,
                payload={
                    "project_type": project.project_type,
                    "current_stage": "lead_captured",
                    "stage_sequence": 1,
                    "backfill": True,
                },
                event_source="system",
                reference_doctype="Farmer Project",
                reference_name=project_name,
                created_on=first.transitioned_on if first else project.creation,
                skip_idempotency=True,
            )
            created.append(eid)

        for row in project.stage_history:
            if not row.to_stage or row.to_sequence <= 1:
                continue
            client_key = f"backfill-{project_name}-{row.name}"
            if frappe.db.exists("Timeline Event", {"client_id": client_key}):
                continue
            eid = timeline.emit_stage_transition(
                project,
                from_stage=row.from_stage or "",
                to_stage=row.to_stage,
                from_sequence=row.from_sequence or 0,
                to_sequence=row.to_sequence,
                history_row_name=row.name,
                notes=row.notes,
                client_id=client_key,
                actor=row.transitioned_by,
                created_on=row.transitioned_on,
            )
            created.append(eid)

        if project.status == "on_hold":
            key = f"backfill-status-{project_name}"
            if not frappe.db.exists("Timeline Event", {"client_id": key}):
                eid = timeline.emit(
                    "project_status_changed",
                    project_name,
                    payload={
                        "from_status": "active",
                        "to_status": "on_hold",
                        "current_stage": project.current_stage,
                        "stage_sequence": project.stage_sequence,
                        "backfill": True,
                    },
                    event_source="system",
                    client_id=key,
                    created_on=project.modified,
                )
                created.append(eid)

    frappe.db.commit()
    return {"projects": list(PROJECTS), "events_created": len(created), "created_ids": created[:20]}
