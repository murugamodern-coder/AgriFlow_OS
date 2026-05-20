#!/usr/bin/env python3
"""Verify Timeline Event foundation."""


def execute():
    import frappe

    from agriflow.project_lifecycle.services.timeline import get_timeline_service

    frappe.set_user("Administrator")
    errors = []
    timeline = get_timeline_service()
    immutable_ok = False

    if not frappe.db.exists("DocType", "Timeline Event"):
        errors.append("Timeline Event DocType missing")

    mod = frappe.db.get_value("DocType", "Timeline Event", "module")
    if mod != "Project Lifecycle":
        errors.append(f"Timeline Event module is {mod}")

    for project in ("FP-2026-00007", "FP-2026-00008"):
        count = frappe.db.count("Timeline Event", {"farmer_project": project, "is_deleted": 0})
        if count < 1:
            errors.append(f"No timeline events for {project}")

    active_events = frappe.get_all(
        "Timeline Event",
        filters={"farmer_project": "FP-2026-00007", "is_deleted": 0},
        fields=["name", "event_type", "created_on"],
        order_by="created_on asc",
    )
    prev_on = None
    for ev in active_events:
        if prev_on and ev.created_on < prev_on:
            errors.append("Timeline ordering broken for FP-2026-00007")
        prev_on = ev.created_on

    feed = timeline.query(farmer_project="FP-2026-00007", limit=20)
    types = {i["event_type"] for i in feed["items"]}
    if "project_created" not in types:
        errors.append("Missing project_created in feed")
    if "stage_transition" not in types:
        errors.append("Missing stage_transition in feed")

    farmer_feed = timeline.query(farmer="FR-00001", limit=10)
    if not farmer_feed["items"]:
        errors.append("Farmer-level query returned no items")

    if active_events:
        row = frappe.get_doc("Timeline Event", active_events[0].name)
        try:
            row.payload_json = {"tamper": True}
            row.save(ignore_permissions=True)
            errors.append("Timeline event mutation should have failed")
        except frappe.ValidationError:
            immutable_ok = True
    else:
        errors.append("No events for immutability test")

    try:
        e1 = timeline.emit_manual_note(
            "FP-2026-00007",
            "dup test",
            client_id="phase9-idem-test",
        )
        e2 = timeline.emit_manual_note(
            "FP-2026-00007",
            "dup test",
            client_id="phase9-idem-test",
        )
        if e1 != e2:
            errors.append("Idempotent client_id failed")
    except Exception as exc:
        errors.append(f"Idempotency test error: {exc}")

    if errors:
        frappe.throw("Phase 9 verification failed: " + "; ".join(errors))

    return {
        "ok": True,
        "fp00007_event_count": len(active_events),
        "fp00007_event_types": list(types),
        "immutable_validation": immutable_ok,
        "feed_sample": feed["items"][:5],
        "farmer_feed_count": len(farmer_feed["items"]),
    }
