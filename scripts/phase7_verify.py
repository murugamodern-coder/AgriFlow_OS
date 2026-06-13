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
        fields=["name", "farmer_name", "mobile_normalized", "district", "block", "village", "cluster", "state"],
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

    # Duplicate mobile in same district is allowed (warn only, no throw)
    duplicate_mobile_ok = False
    if farmers:
        ref = farmers[0]
        dup_name = None
        try:
            dup = frappe.get_doc(
                {
                    "doctype": "Farmer",
                    "farmer_name": "Duplicate Mobile Test",
                    "mobile": ref.mobile_normalized,
                    "state": ref.state or "Tamil Nadu",
                    "district": ref.district,
                    "block": ref.block,
                    "village": ref.village,
                }
            )
            dup.insert(ignore_permissions=True)
            dup_name = dup.name
            duplicate_mobile_ok = True
            print(f"  duplicate mobile in same district: OK (saved {dup_name})")
        except frappe.ValidationError as exc:
            errors.append(f"duplicate mobile should not throw: {exc}")
        except Exception as exc:
            errors.append(f"duplicate mobile unexpected error: {exc}")
        finally:
            if dup_name and frappe.db.exists("Farmer", dup_name):
                frappe.delete_doc("Farmer", dup_name, force=True, ignore_permissions=True)

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
        "duplicate_mobile_allowed": duplicate_mobile_ok,
    }
