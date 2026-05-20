#!/usr/bin/env python3
"""Verify project.timeline and project.timeline_since APIs."""

PROJECT = "FP-2026-00007"
FARMER = "FR-00001"


def execute():
    import frappe

    from agriflow.api.v1 import project as project_api
    from agriflow.project_lifecycle.services.timeline import get_timeline_service

    frappe.set_user("Administrator")
    errors = []
    proof = {}

    page1 = project_api.timeline({"name": PROJECT, "limit": 2})
    if not page1.get("ok"):
        errors.append(f"timeline failed: {page1}")
    else:
        data1 = page1["data"]
        proof["timeline_page1_count"] = len(data1["timeline"]["items"])
        proof["timeline_has_more_p1"] = data1["timeline"]["has_more"]
        proof["timeline_has_stage_history"] = len(data1.get("stage_history", [])) >= 1
        proof["timeline_has_project"] = data1.get("project", {}).get("name") == PROJECT
        cursor = data1["timeline"]["next_cursor"]
        if cursor:
            page2 = project_api.timeline({"name": PROJECT, "limit": 2, "cursor": cursor})
            if not page2.get("ok"):
                errors.append("timeline page2 failed")
            else:
                ids1 = {i["id"] for i in data1["timeline"]["items"]}
                ids2 = {i["id"] for i in page2["data"]["timeline"]["items"]}
                if ids1 & ids2:
                    errors.append("timeline cursor overlap between pages")
                proof["timeline_page2_count"] = len(ids2)

    filtered = project_api.timeline(
        {"name": PROJECT, "event_types": ["manual_note"], "limit": 20}
    )
    if filtered.get("ok"):
        types = {i["event_type"] for i in filtered["data"]["timeline"]["items"]}
        if types - {"manual_note"}:
            errors.append(f"event_types filter leaked: {types}")
        proof["filter_manual_note_count"] = len(types)

    since = "2026-05-20T00:00:00"
    delta = project_api.timeline_since({"project": PROJECT, "since": since, "limit": 50})
    if not delta.get("ok"):
        errors.append(f"timeline_since failed: {delta}")
    else:
        items = delta["data"]["items"]
        proof["since_item_count"] = len(items)
        times = [i["created_on"] for i in items]
        if times != sorted(times):
            errors.append("timeline_since not ASC ordered")
        proof["since_ordered_asc"] = times == sorted(times)
        for item in items:
            if str(item["created_on"]) <= since:
                errors.append(f"timeline_since included event before since: {item['id']}")

    farmer_delta = project_api.timeline_since({"farmer": FARMER, "since": since, "limit": 50})
    if farmer_delta.get("ok"):
        proof["farmer_since_count"] = len(farmer_delta["data"]["items"])

    frappe.set_user("Guest")
    guest = project_api.timeline({"name": PROJECT})
    if guest.get("ok"):
        errors.append("Guest should not access timeline")
    proof["guest_denied"] = not guest.get("ok")

    frappe.set_user("Administrator")

    svc = get_timeline_service()
    if svc.query(farmer_project=PROJECT, limit=1)["items"]:
        row = frappe.get_doc("Timeline Event", svc.query(farmer_project=PROJECT, limit=1)["items"][0]["id"])
        try:
            row.payload_json = {"tamper": True}
            row.save(ignore_permissions=True)
            errors.append("timeline event should remain immutable")
        except frappe.ValidationError:
            proof["immutable_ok"] = True

    if errors:
        frappe.throw("Phase 9b API verification failed: " + "; ".join(errors))

    return {"ok": True, **proof}
