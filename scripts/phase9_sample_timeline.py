#!/usr/bin/env python3
"""Add sample manual_note timeline events."""


def execute():
    import frappe

    from agriflow.project_lifecycle.services.timeline import get_timeline_service

    frappe.set_user("Administrator")
    timeline = get_timeline_service()
    notes = []
    for project, text in (
        ("FP-2026-00007", "Phase 9 sample: office verified documents."),
        ("FP-2026-00008", "Phase 9 sample: project on hold pending farmer visit."),
    ):
        if frappe.db.exists("Farmer Project", project):
            eid = timeline.emit_manual_note(
                project,
                text,
                client_id=f"phase9-sample-note-{project}",
            )
            notes.append({"project": project, "event_id": eid})
    frappe.db.commit()
    return {"manual_notes": notes}
