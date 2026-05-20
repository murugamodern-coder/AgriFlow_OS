#!/usr/bin/env python3

def execute():
    import frappe

    expected = [
        "District",
        "Block",
        "Cluster",
        "Village",
        "Officer",
        "Officer Assignment History",
    ]
    found = frappe.get_all(
        "DocType",
        filters={"module": "Officer Network", "istable": 0},
        pluck="name",
        order_by="name asc",
    )
    modules = frappe.get_all(
        "Module Def",
        filters={"app_name": "agriflow"},
        fields=["name", "module_name"],
        order_by="module_name asc",
    )
    district_count = frappe.db.count("District")
    block_count = frappe.db.count("Block")
    return {
        "doctypes": found,
        "expected": expected,
        "all_present": sorted(found) == sorted(expected),
        "modules": modules,
        "fixture_counts": {"district": district_count, "block": block_count},
    }
