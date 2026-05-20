#!/usr/bin/env python3
"""Phase 8 — Verify Farmer Project lifecycle foundation."""


def execute():
    import frappe

    from agriflow.project_lifecycle.services.lifecycle import get_lifecycle_service
    from agriflow.project_lifecycle.utils.stages import get_stage_map

    frappe.set_user("Administrator")
    errors = []
    results = {}

    stage_count = frappe.db.count("Project Stage", {"is_active": 1})
    results["project_stage_count"] = stage_count
    if stage_count != 12:
        errors.append(f"Expected 12 Project Stage rows, got {stage_count}")

    if not frappe.db.exists("DocType", "Farmer Project"):
        errors.append("Farmer Project DocType missing")
    if not frappe.db.exists("DocType", "Project Stage History"):
        errors.append("Project Stage History child missing")

    mod = frappe.db.get_value("Module Def", {"module_name": "Project Lifecycle"}, "name")
    results["module_def"] = mod
    if not mod:
        errors.append("Module Def Project Lifecycle missing")

    active = frappe.db.get_value(
        "Farmer Project",
        {"farmer": "FR-00001", "status": "active", "is_deleted": 0},
        ["name", "current_stage", "stage_sequence"],
        as_dict=True,
    )
    results["active_project"] = active
    if not active:
        errors.append("No active project for FR-00001")
    elif active.current_stage != "documents_collected" or active.stage_sequence != 3:
        errors.append(
            f"Active project should be stage 3 documents_collected, got {active.current_stage} seq {active.stage_sequence}"
        )

    hold = frappe.db.get_value(
        "Farmer Project",
        {"farmer": "FR-00002", "is_deleted": 0},
        ["name", "status", "current_stage"],
        as_dict=True,
    )
    results["on_hold_project"] = hold
    if not hold or hold.status != "on_hold":
        errors.append("FR-00002 on_hold project missing or wrong status")

    if active:
        history = frappe.get_all(
            "Project Stage History",
            filters={"parent": active.name},
            fields=["name", "to_stage", "to_sequence", "from_sequence"],
            order_by="to_sequence asc",
        )
        results["stage_history"] = history
        if len(history) != 3:
            errors.append(f"Expected 3 history rows on active project, got {len(history)}")
        for idx, row in enumerate(history):
            if row.to_sequence != idx + 1:
                errors.append(f"History sequence gap at row {row.name}")
        prev_seq = 0
        for row in history:
            if row.from_sequence != prev_seq:
                errors.append(f"from_sequence mismatch on {row.name}")
            prev_seq = row.to_sequence

    svc = get_lifecycle_service()
    if active:
        doc_version = frappe.db.get_value("Farmer Project", active.name, "doc_version")
        try:
            svc.transition(active.name, "field_survey", doc_version=doc_version, notes="skip test")
            errors.append("Stage skip to field_survey should have failed")
        except frappe.ValidationError:
            results["skip_transition_blocked"] = True

        try:
            svc.transition(active.name, "mimis_registered", doc_version=doc_version, notes="mimis gate test")
            errors.append("MIMIS transition without gate should have failed")
        except frappe.ValidationError:
            results["mimis_gate_blocked"] = True

        hold_doc_version = frappe.db.get_value("Farmer Project", hold.name, "doc_version") if hold else None
        if hold and hold_doc_version is not None:
            try:
                svc.transition(hold.name, "eligibility_check", doc_version=hold_doc_version)
                errors.append("on_hold project transition should have failed")
            except frappe.ValidationError:
                results["on_hold_transition_blocked"] = True

    stage_map = get_stage_map()
    results["stage_keys_loaded"] = len(stage_map)

    if errors:
        frappe.throw("Phase 8 verification failed: " + "; ".join(errors))

    return {"ok": True, **results}
