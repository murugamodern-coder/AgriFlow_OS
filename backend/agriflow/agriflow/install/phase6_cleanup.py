#!/usr/bin/env python3
"""Remove orphan Module Def rows from placeholder scaffold. Run via bench execute."""
from __future__ import annotations

import frappe


def execute():
    orphans = ["Yes", "yes", "Agriflow"]
    removed = []
    for name in orphans:
        if frappe.db.exists("Module Def", name):
            frappe.delete_doc("Module Def", name, force=True, ignore_permissions=True)
            removed.append(name)
    frappe.db.commit()
    return {"removed": removed}
