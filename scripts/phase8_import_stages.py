#!/usr/bin/env python3
"""Import Project Stage fixtures if missing (run after migrate)."""


def execute():
    import frappe
    from frappe.core.doctype.data_import.data_import import import_doc

    count = frappe.db.count("Project Stage", {"is_active": 1})
    if count >= 12:
        return {"imported": False, "count": count}
    path = frappe.get_app_path("agriflow", "fixtures", "project_stage.json")
    import_doc(path)
    frappe.db.commit()
    return {"imported": True, "count": frappe.db.count("Project Stage", {"is_active": 1})}
