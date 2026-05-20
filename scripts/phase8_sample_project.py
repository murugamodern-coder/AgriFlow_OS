#!/usr/bin/env python3
"""Phase 8 — Sample Farmer Projects for verification."""


def execute():
    import frappe

    from agriflow.project_lifecycle.services.lifecycle import get_lifecycle_service

    frappe.set_user("Administrator")

    if frappe.db.count("Project Stage", {"is_active": 1}) < 12:
        from frappe.core.doctype.data_import.data_import import import_doc

        path = frappe.get_app_path("agriflow", "fixtures", "project_stage.json")
        import_doc(path)
        frappe.db.commit()

    svc = get_lifecycle_service()

    farmer_active = "FR-00001"
    farmer_hold = "FR-00002"

    if not frappe.db.exists("Farmer", farmer_active):
        frappe.throw("FR-00001 missing — run Phase 7 sample farmers first")

    active_name = frappe.db.get_value(
        "Farmer Project",
        {"farmer": farmer_active, "status": "active", "is_deleted": 0},
        "name",
    )
    if not active_name:
        doc = svc.create_project(farmer_active, created_via="system", remarks="Phase 8 sample active project")
        active_name = doc.name
        print(f"  created active project {active_name}")
        svc.transition(active_name, "eligibility_check", doc_version=1, notes="Phase 8 sample")
        doc_version = frappe.db.get_value("Farmer Project", active_name, "doc_version")
        svc.transition(
            active_name,
            "documents_collected",
            doc_version=doc_version,
            notes="Advanced to stage 3 for verification",
        )
        print(f"  advanced {active_name} to documents_collected (stage 3)")
    else:
        stage = frappe.db.get_value("Farmer Project", active_name, "current_stage")
        if stage != "documents_collected":
            doc_version = frappe.db.get_value("Farmer Project", active_name, "doc_version")
            stage_map = {
                "lead_captured": ("eligibility_check", None),
                "eligibility_check": ("documents_collected", None),
            }
            while stage in stage_map:
                next_stage, _ = stage_map[stage]
                doc_version = frappe.db.get_value("Farmer Project", active_name, "doc_version")
                svc.transition(active_name, next_stage, doc_version=doc_version, notes="Phase 8 catch-up")
                stage = frappe.db.get_value("Farmer Project", active_name, "current_stage")
        print(f"  active project exists: {active_name} stage={stage}")

    hold_name = frappe.db.get_value(
        "Farmer Project",
        {"farmer": farmer_hold, "is_deleted": 0},
        "name",
    )
    if not hold_name:
        hold_doc = svc.create_project(farmer_hold, created_via="system", remarks="Phase 8 on_hold sample")
        hold_name = hold_doc.name
        frappe.flags.agriflow_lifecycle_write = True
        try:
            hold_doc.status = "on_hold"
            hold_doc.save(ignore_permissions=True)
        finally:
            frappe.flags.agriflow_lifecycle_write = False
        print(f"  created on_hold project {hold_name}")
    else:
        print(f"  hold project exists: {hold_name}")

    frappe.db.commit()

    active = frappe.get_doc("Farmer Project", active_name)
    hold = frappe.get_doc("Farmer Project", hold_name)
    return {
        "active_project": active.name,
        "active_stage": active.current_stage,
        "active_sequence": active.stage_sequence,
        "active_history_count": len(active.stage_history),
        "on_hold_project": hold.name,
        "on_hold_status": hold.status,
        "on_hold_stage": hold.current_stage,
    }
