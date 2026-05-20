#!/usr/bin/env python3
"""Phase 7 — Verify Farmer DocType, validations, and geography chain."""
from __future__ import annotations

import frappe


def execute() -> dict:
    frappe.set_user("Administrator")

    errors: list[str] = []

    if not frappe.db.exists("DocType", "Farmer"):
        errors.append("Farmer DocType missing")
    else:
        meta = frappe.get_meta("Farmer")
        mod = frappe.db.get_value("DocType", "Farmer", "module")
        if mod != "Farmer Registry":
            errors.append(f"Farmer module is {mod!r}, expected Farmer Registry")
        for fname in ("mobile_normalized", "cluster", "land_parcels", "doc_version"):
            if not meta.has_field(fname):
                errors.append(f"Farmer missing field {fname}")

    if not frappe.db.exists("DocType", "Farmer Land Parcel"):
        errors.append("Farmer Land Parcel child DocType missing")

    farmer_count = frappe.db.count("Farmer", {"is_deleted": 0})
    parcel_count = frappe.db.count("Farmer Land Parcel")
    print(f"Farmers (not deleted): {farmer_count}")
    print(f"Land parcel rows: {parcel_count}")
    if farmer_count < 2:
        errors.append(f"Expected at least 2 farmers, found {farmer_count}")
    if parcel_count < 2:
        errors.append(f"Expected at least 2 land parcel rows, found {parcel_count}")

    farmers = frappe.get_all(
        "Farmer",
        filters={"is_deleted": 0},
        fields=["name", "farmer_name", "mobile_normalized", "district", "block", "village", "cluster"],
        limit=5,
    )
    for f in farmers:
        print(f"  {f.name}: {f.farmer_name} mobile={f.mobile_normalized} cluster={f.cluster}")
        vb = frappe.db.get_value("Village", f.village, "block")
        bd = frappe.db.get_value("Block", f.block, "district")
        vc = frappe.db.get_value("Village", f.village, "cluster")
        if vb != f.block:
            errors.append(f"{f.name}: village.block mismatch")
        if bd != f.district:
            errors.append(f"{f.name}: block.district mismatch")
        if vc and f.cluster and vc != f.cluster:
            errors.append(f"{f.name}: cluster fetch mismatch")

    # Duplicate mobile should fail
    if farmers:
        ref = farmers[0]
        try:
            dup = frappe.get_doc(
                {
                    "doctype": "Farmer",
                    "farmer_name": "Duplicate Test",
                    "mobile": ref.mobile_normalized,
                    "district": ref.district,
                    "block": ref.block,
                    "village": ref.village,
                }
            )
            dup.insert(ignore_permissions=True)
            errors.append("Duplicate mobile validation did not throw")
            dup.delete(ignore_permissions=True)
        except frappe.ValidationError:
            print("  duplicate mobile validation: OK")
        except Exception as exc:
            errors.append(f"duplicate mobile unexpected error: {exc}")

    if errors:
        frappe.throw("Phase 7 verification failed: " + "; ".join(errors))

    module = frappe.db.get_value("Module Def", {"module_name": "Farmer Registry"}, "name")
    if not module:
        errors.append("Module Def 'Farmer Registry' missing")

    return {
        "ok": True,
        "farmer_count": farmer_count,
        "land_parcel_count": parcel_count,
        "module_def": module,
        "farmers": farmers,
        "duplicate_mobile_validation": "ok",
    }
