# Copyright (c) 2026, Murugan and contributors
"""Phase 10b — verify Task API layer."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import task as task_api
from agriflow.task_engine.services.lifecycle import TaskLifecycleService

PROJECT = "FP-2026-00007"


def execute():
    frappe.only_for("Administrator")
    errors: list[str] = []
    report: dict = {"project": PROJECT}

    # --- task.list pagination ---
    p1 = task_api.list({"farmer_project": PROJECT, "limit": 2})
    if not p1.get("ok"):
        errors.append(f"list page1: {p1}")
    else:
        ids1 = {i["name"] for i in p1["data"]["items"]}
        cursor = p1["data"]["pagination"].get("next_cursor")
        report["page1_count"] = len(ids1)
        report["has_more_p1"] = p1["data"]["pagination"].get("has_more")
        if cursor:
            p2 = task_api.list({"farmer_project": PROJECT, "limit": 2, "cursor": cursor})
            if p2.get("ok"):
                ids2 = {i["name"] for i in p2["data"]["items"]}
                overlap = ids1 & ids2
                report["page2_count"] = len(ids2)
                report["pagination_overlap"] = list(overlap)
                if overlap:
                    errors.append(f"pagination overlap: {overlap}")
            else:
                errors.append(f"list page2: {p2}")

    # --- overdue indicator ---
    if p1.get("ok") and p1["data"]["items"]:
        report["sample_is_overdue"] = p1["data"]["items"][0].get("is_overdue")
        report["sample_sla"] = p1["data"]["items"][0].get("sla")

    # --- due_before alias ---
    alias = task_api.list({"farmer_project": PROJECT, "due_before": "2099-12-31", "limit": 5})
    alias2 = task_api.list({"farmer_project": PROJECT, "due_date_lte": "2099-12-31", "limit": 5})
    if alias.get("ok") and alias2.get("ok"):
        report["due_alias_match"] = len(alias["data"]["items"]) == len(alias2["data"]["items"])

    # --- task.get ---
    sample = frappe.db.get_value(
        "Project Task",
        {"farmer_project": PROJECT, "is_deleted": 0},
        "name",
        order_by="modified desc",
    )
    if sample:
        got = task_api.get({"name": sample})
        if not got.get("ok"):
            errors.append(f"get failed: {got}")
        else:
            d = got["data"]
            report["get_keys"] = sorted(d.keys())
            for key in ("assignment_history", "timeline_preview", "sla", "allowed_transitions", "task"):
                if key not in d:
                    errors.append(f"get missing {key}")
            if d.get("assignment_history") is not None and len(d["assignment_history"]) < 1:
                errors.append("assignment_history empty")
            tevents = [e["event_type"] for e in d.get("timeline_preview", {}).get("items", [])]
            report["timeline_preview_types"] = tevents

    # --- task.create idempotent ---
    cid = "phase10b-api-create-test"
    c1 = task_api.create(
        {
            "client_id": cid,
            "subject": "API test task",
            "farmer_project": PROJECT,
            "task_type": "follow_up",
            "due_date": "2099-06-01",
            "priority": "medium",
        }
    )
    c2 = task_api.create(
        {
            "client_id": cid,
            "subject": "API test task",
            "farmer_project": PROJECT,
            "task_type": "follow_up",
            "due_date": "2099-06-01",
        }
    )
    if c1.get("ok") and c2.get("ok"):
        report["create_idempotent"] = c1["data"]["task"]["name"] == c2["data"]["task"]["name"]
        report["create_priority"] = c2["data"]["task"]["priority"]
        if c2["data"]["task"]["priority"] != "normal":
            errors.append("medium not mapped to normal")

    # --- auto-step complete from assigned ---
    officer = frappe.db.get_value("Farmer Project", PROJECT, "officer") or "OFF01"
    tdoc = TaskLifecycleService().create_task(
        subject="Phase10b complete auto-step",
        farmer_project=PROJECT,
        task_type="verification",
        due_date="2099-07-01",
        client_id="phase10b-autostep-complete",
    )
    TaskLifecycleService  # noqa — keep import
    from agriflow.task_engine.services.assignment import TaskAssignmentService

    TaskAssignmentService().assign(tdoc.name, officer, reason="initial")
    tdoc.reload()
    before_events = frappe.db.count(
        "Timeline Event",
        {
            "farmer_project": PROJECT,
            "event_type": ("in", ["task_status_changed", "task_completed"]),
            "reference_name": tdoc.name,
        },
    )
    comp = task_api.complete(
        {"name": tdoc.name, "doc_version": tdoc.doc_version, "visit_outcome": "Done via API"}
    )
    if not comp.get("ok"):
        errors.append(f"complete failed: {comp}")
    else:
        report["complete_status"] = comp["data"]["task"]["status"]
        if comp["data"]["task"]["status"] != "completed":
            errors.append("complete did not set completed")
        after_events = frappe.db.count(
            "Timeline Event",
            {
                "farmer_project": PROJECT,
                "event_type": ("in", ["task_status_changed", "task_completed"]),
                "reference_name": tdoc.name,
            },
        )
        report["timeline_events_delta"] = after_events - before_events
        if after_events - before_events < 2:
            errors.append("expected >=2 timeline events for auto-step complete")

    # --- stale doc_version ---
    open_task = frappe.db.get_value(
        "Project Task",
        {"farmer_project": PROJECT, "status": ("in", ["assigned", "in_progress"]), "is_deleted": 0},
        ["name", "doc_version"],
        as_dict=True,
    )
    if open_task:
        stale = task_api.update(
            {
                "name": open_task.name,
                "doc_version": int(open_task.doc_version or 1) - 1,
                "description": "stale test",
            }
        )
        report["stale_ok"] = stale.get("ok") is False
        report["stale_code"] = (stale.get("error") or {}).get("code")
        if report.get("stale_code") != "SYNC_CONFLICT_LWW":
            errors.append(f"expected SYNC_CONFLICT_LWW got {report.get('stale_code')}")

    # --- terminal transition blocked ---
    done = frappe.db.get_value(
        "Project Task",
        {"farmer_project": PROJECT, "status": "completed", "is_deleted": 0},
        "name",
    )
    if done:
        bad = task_api.update({"name": done, "doc_version": 1, "status": "in_progress"})
        if bad.get("ok"):
            errors.append("terminal transition allowed via API")

    # --- assignment via update routes to service (history grows) ---
    if open_task and officer:
        hist_before = frappe.db.count(
            "Project Task Assignment History", {"project_task": open_task.name}
        )
        reassigned = task_api.update(
            {
                "name": open_task.name,
                "doc_version": frappe.db.get_value("Project Task", open_task.name, "doc_version"),
                "assigned_officer": officer,
            }
        )
        hist_after = frappe.db.count(
            "Project Task Assignment History", {"project_task": open_task.name}
        )
        report["assignment_history_grew"] = hist_after >= hist_before
        if reassigned.get("ok") and hist_after <= hist_before:
            errors.append("assignment did not append history")

    report["ok"] = len(errors) == 0
    report["errors"] = errors
    print(report)
