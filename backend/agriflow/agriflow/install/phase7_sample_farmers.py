#!/usr/bin/env python3
"""Phase 7 — Ensure geography test rows and create 2 sample farmers."""
from __future__ import annotations

import frappe


def ensure_geography() -> str:
    """Return village name for sample farmers (create cluster/village if needed)."""
    district = "TVM"
    block = frappe.db.get_value("Block", {"block_code": "BLK01", "district": district}, "name")
    if not block:
        block = frappe.db.get_value("Block", {"district": district}, "name")
    if not block:
        frappe.throw("No Block found for district TVM — run Phase 6 fixtures first")

    cluster = frappe.db.get_value("Cluster", {"cluster_code": "CLU01", "block": block}, "name")
    if not cluster:
        doc = frappe.get_doc(
            {
                "doctype": "Cluster",
                "cluster_code": "CLU01",
                "cluster_name": "Sample Cluster 01",
                "block": block,
                "is_active": 1,
            }
        )
        doc.insert(ignore_permissions=True)
        cluster = doc.name
        print(f"  created Cluster {cluster}")

    village = frappe.db.get_value("Village", {"village_code": "VLG01", "block": block}, "name")
    if not village:
        doc = frappe.get_doc(
            {
                "doctype": "Village",
                "village_code": "VLG01",
                "village_name": "Sample Village 01",
                "cluster": cluster,
                "block": block,
                "pincode": "606601",
                "is_active": 1,
            }
        )
        doc.insert(ignore_permissions=True)
        village = doc.name
        print(f"  created Village {village}")

    return village


def create_farmer(
    farmer_name: str,
    mobile: str,
    district: str,
    block: str,
    village: str,
    *,
    father_name: str,
    survey: str,
    acres: float,
    parcel_survey: str,
) -> str:
    existing = frappe.db.exists(
        "Farmer",
        {"mobile_normalized": mobile, "district": district, "is_deleted": 0},
    )
    if existing:
        print(f"  farmer exists: {existing}")
        return existing

    doc = frappe.get_doc(
        {
            "doctype": "Farmer",
            "farmer_name": farmer_name,
            "father_name": father_name,
            "mobile": mobile,
            "district": district,
            "block": block,
            "village": village,
            "primary_survey_number": survey,
            "land_extent_acres": acres,
            "address_line": "Sample address for verification",
            "pincode": "606601",
            "tags": "phase7,sample",
            "is_active": 1,
            "created_via": "system",
            "land_parcels": [
                {
                    "survey_number": parcel_survey,
                    "extent_acres": acres / 2,
                    "crop": "paddy",
                }
            ],
        }
    )
    doc.insert(ignore_permissions=True)
    print(f"  created Farmer {doc.name} — {doc.farmer_name}")
    return doc.name


def execute() -> None:
    frappe.set_user("Administrator")

    district = "TVM"
    block = frappe.db.get_value("Block", {"block_code": "BLK01", "district": district}, "name")
    if not block:
        block = frappe.db.get_value("Block", {"district": district}, "name")
    village = ensure_geography()

    create_farmer(
        "Ravi Kumar",
        "9876543210",
        district,
        block,
        village,
        father_name="Murugan",
        survey="123/1A",
        acres=2.5,
        parcel_survey="123/1B",
    )
    create_farmer(
        "Lakshmi Devi",
        "9876543211",
        district,
        block,
        village,
        father_name="Raman",
        survey="456/2A",
        acres=1.75,
        parcel_survey="456/2B",
    )

    frappe.db.commit()
    return {
        "village": village,
        "block": block,
        "district": district,
        "farmers": frappe.db.count("Farmer", {"is_deleted": 0}),
    }
