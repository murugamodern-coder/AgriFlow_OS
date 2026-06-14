"""Seed sample government officers for demo."""

from __future__ import annotations
import frappe


SAMPLE_OFFICERS = [
    {"name": "\u0baa\u0bbf\u0bb2\u0bc7\u0bb2\u0bbf\u0baf\u0bc7 \u0bai\u0bc1\u0bb5\u0baa\u0bcd", "designation": "AE - Assistant Engineer", "mobile": "9445566778", "office": "Polur Office"},
    {"name": "\u0bb0\u0bbe\u0bae\u0bb2\u0bbf\u0b99\u0bcd\u0b95\u0bae\u0bcd", "designation": "AEE - Assistant Executive Engineer", "mobile": "9445566779", "office": "Tiruvannamalai HQ"},
    {"name": "K. \u0b9a\u0bc6\u0bb2\u0bcd\u0bb5\u0bb0\u0bbe\u0b9a\u0bc1", "designation": "JDA - Joint Director Agriculture", "mobile": "9445566780", "office": "District Collectorate"},
    {"name": "\u0bae\u0ba3\u0bbf \u0b95\u0ba3\u0bcd\u0b9f\u0ba9\u0bcd", "designation": "DAO - District Agriculture Officer", "mobile": "9445566781", "office": "Tiruvannamalai HQ"},
    {"name": "\u0bb0\u0bbe\u0b9c\u0bc6\u0ba8\u0bcd\u0ba4\u0bbf\u0bb0\u0ba9\u0bcd", "designation": "Block Officer", "mobile": "9445566782", "office": "Polur Block"},
    {"name": "\u0bb5\u0b9f\u0bbf\u0bb5\u0bc7\u0b95\u0bcd\u0bb0\u0bcd", "designation": "Field Officer", "mobile": "9445566783", "office": "Chetpet"},
    {"name": "\u0b9a\u0ba3\u0bcd\u0bae\u0bc1\u0b95\u0bae\u0bcd", "designation": "AE - Assistant Engineer", "mobile": "9445566784", "office": "Arani"},
    {"name": "\u0bb2\u099f\u0bcd\u0b9a\u0bc1\u0bae\u0bbf \u0ba8\u0bbe\u0bb0\u0bbe\u0baf\u0ba3\u0ba9\u0bcd", "designation": "AEE - Assistant Executive Engineer", "mobile": "9445566785", "office": "Cheyyar"},
]


def run():
    """Seed officers."""
    print("=" * 50)
    print("Seeding Government Officers...")
    print("=" * 50)

    district = frappe.db.get_value("Geo District", {"district_code": "593"}, "name")

    created = []
    for o in SAMPLE_OFFICERS:
        if frappe.db.exists("Government Officer", {"mobile": o["mobile"]}):
            print(f"  - Skipping {o['name']} (exists)")
            continue

        try:
            officer = frappe.get_doc({
                "doctype": "Government Officer",
                "officer_name": o["name"],
                "designation": o["designation"],
                "mobile": o["mobile"],
                "office_location": o["office"],
                "district": district,
                "is_active": 1,
            }).insert(ignore_permissions=True)
            created.append(officer.name)
            print(f"  ✓ {officer.name} - {o['name']} ({o['designation']})")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    frappe.db.commit()
    print("=" * 50)
    print(f"✅ Created {len(created)} officers")
    return {"created": len(created), "officers": created}