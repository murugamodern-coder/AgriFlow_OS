#!/usr/bin/env python3

def execute():
    import frappe
    from frappe.modules.utils import sync_modules

    sync_modules("agriflow")
    frappe.db.commit()
    return frappe.get_all(
        "Module Def",
        filters={"app_name": "agriflow"},
        pluck="name",
        order_by="name asc",
    )
