#!/usr/bin/env python3
"""Phase 7 — Generate Farmer Registry DocTypes in frappe-bench agriflow app."""
from __future__ import annotations

import json
from pathlib import Path

APP_ROOT = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
MODULE = "Farmer Registry"

PERMS_SM = [
    {
        "role": "System Manager",
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 1,
        "export": 1,
        "print": 1,
        "email": 1,
        "report": 1,
        "share": 1,
    }
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(APP_ROOT)}")


def field(
    fieldname: str,
    fieldtype: str,
    label: str,
    *,
    options: str | None = None,
    reqd: int = 0,
    default: str | None = None,
    read_only: int = 0,
    fetch_from: str | None = None,
    in_list_view: int = 0,
    in_standard_filter: int = 0,
    search_index: int = 0,
    unique: int = 0,
    length: int | None = None,
    hidden: int = 0,
) -> dict:
    f = {
        "fieldname": fieldname,
        "fieldtype": fieldtype,
        "label": label,
        "reqd": reqd,
        "read_only": read_only,
        "in_list_view": in_list_view,
        "in_standard_filter": in_standard_filter,
        "search_index": search_index,
        "unique": unique,
    }
    if options:
        f["options"] = options
    if default is not None:
        f["default"] = default
    if fetch_from:
        f["fetch_from"] = fetch_from
    if length is not None:
        f["length"] = length
    if hidden:
        f["hidden"] = hidden
    return f


def doctype_json(
    name: str,
    fields: list[dict],
    *,
    autoname: str,
    title_field: str,
    module: str = MODULE,
    track_changes: int = 1,
    allow_rename: int = 0,
    allow_import: int = 0,
    istable: int = 0,
    search_fields: str | None = None,
) -> dict:
    field_order = [f["fieldname"] for f in fields]
    doc = {
        "actions": [],
        "allow_import": allow_import,
        "allow_rename": allow_rename,
        "autoname": autoname,
        "creation": "2026-05-20 00:00:00.000000",
        "doctype": "DocType",
        "engine": "InnoDB",
        "field_order": field_order,
        "fields": fields,
        "index_web_pages_for_search": 1,
        "links": [],
        "modified": "2026-05-20 00:00:00.000000",
        "modified_by": "Administrator",
        "module": module,
        "name": name,
        "owner": "Administrator",
        "permissions": PERMS_SM if not istable else [],
        "sort_field": "modified",
        "sort_order": "DESC",
        "states": [],
        "track_changes": track_changes,
    }
    if istable:
        doc["istable"] = 1
    if title_field:
        doc["title_field"] = title_field
    if search_fields:
        doc["search_fields"] = search_fields
    return doc


def main() -> None:
    print("Phase 7 — Farmer Registry bootstrap")
    write_utils()
    write_farmer_land_parcel()
    write_farmer()
    print("Done.")


def write_utils() -> None:
    write(
        APP_ROOT / "farmer_registry" / "utils" / "__init__.py",
        "",
    )
    write(
        APP_ROOT / "farmer_registry" / "utils" / "validation.py",
        '''# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Farmer validation helpers."""

from __future__ import annotations

import re

import frappe
from frappe import _


_MOBILE_RE = re.compile(r"\\D+")


def normalize_mobile(value: str | None) -> str:
\t"""Strip non-digits; return digits-only string (may be empty)."""
\tif not value:
\t\treturn ""
\treturn _MOBILE_RE.sub("", str(value).strip())


def validate_mobile_digits(mobile: str, field_label: str = "Mobile") -> None:
\tdigits = normalize_mobile(mobile)
\tif len(digits) != 10:
\t\tfrappe.throw(_("{0} must be exactly 10 digits").format(field_label))


def validate_aadhaar_last4(value: str | None) -> None:
\tif not value:
\t\treturn
\tclean = str(value).strip()
\tif not clean.isdigit() or len(clean) > 4:
\t\tfrappe.throw(_("Aadhaar (last 4) must be up to 4 digits only"))


def validate_geography_chain(district: str, block: str, village: str, cluster: str | None = None) -> None:
\tif not (district and block and village):
\t\treturn

\tif not frappe.db.exists("District", district):
\t\tfrappe.throw(_("District not found"))
\tif not frappe.db.get_value("District", district, "is_active"):
\t\tfrappe.throw(_("District is inactive"))

\tif not frappe.db.exists("Block", block):
\t\tfrappe.throw(_("Block not found"))
\tblock_district = frappe.db.get_value("Block", block, "district")
\tif block_district != district:
\t\tfrappe.throw(_("Block must belong to the selected District"))
\tif not frappe.db.get_value("Block", block, "is_active"):
\t\tfrappe.throw(_("Block is inactive"))

\tif not frappe.db.exists("Village", village):
\t\tfrappe.throw(_("Village not found"))
\tvillage_block = frappe.db.get_value("Village", village, "block")
\tif village_block != block:
\t\tfrappe.throw(_("Village must belong to the selected Block"))
\tif not frappe.db.get_value("Village", village, "is_active"):
\t\tfrappe.throw(_("Village is inactive"))

\tif cluster:
\t\tvillage_cluster = frappe.db.get_value("Village", village, "cluster")
\t\tif village_cluster and village_cluster != cluster:
\t\t\tfrappe.throw(_("Cluster must match the selected Village"))


def validate_mobile_unique_per_district(mobile_normalized: str, district: str, name: str | None) -> None:
\tif not mobile_normalized or not district:
\t\treturn
\tfilters = {
\t\t"mobile_normalized": mobile_normalized,
\t\t"district": district,
\t\t"is_deleted": 0,
\t}
\tif name:
\t\tfilters["name"] = ("!=", name)
\texisting = frappe.db.exists("Farmer", filters)
\tif existing:
\t\tfrappe.throw(_("Mobile number already registered for this district"))


def has_active_farmer_project(farmer_name: str) -> bool:
\tif not frappe.db.table_exists("tabFarmer Project"):
\t\treturn False
\treturn bool(
\t\tfrappe.db.exists(
\t\t\t"Farmer Project",
\t\t\t{"farmer": farmer_name, "status": "active"},
\t\t)
\t)
''',
    )


def write_farmer_land_parcel() -> None:
    slug = "farmer_land_parcel"
    fields = [
        field("survey_number", "Data", "Survey Number", in_list_view=1),
        field("extent_acres", "Float", "Extent (acres)", in_list_view=1),
        field("crop", "Data", "Crop"),
    ]
    base = APP_ROOT / "farmer_registry" / "doctype" / slug
    write(base / "__init__.py", "")
    write(
        base / f"{slug}.json",
        json.dumps(
            doctype_json(
                "Farmer Land Parcel",
                fields,
                autoname="hash",
                title_field="survey_number",
                istable=1,
                track_changes=0,
            ),
            indent=1,
        )
        + "\n",
    )
    write(
        base / f"{slug}.py",
        '''# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FarmerLandParcel(Document):
\tpass
''',
    )


def write_farmer() -> None:
    slug = "farmer"
    fields = [
        field("identity_section", "Section Break", "Identity"),
        field("farmer_name", "Data", "Farmer Name", reqd=1, in_list_view=1, search_index=1),
        field("father_name", "Data", "Father / Spouse Name"),
        field("mobile", "Data", "Mobile", reqd=1, in_list_view=1, in_standard_filter=1, search_index=1),
        field("alternate_mobile", "Data", "Alternate Mobile"),
        field(
            "mobile_normalized",
            "Data",
            "Mobile Normalized",
            read_only=1,
            hidden=1,
            search_index=1,
        ),
        field("aadhaar_last4", "Data", "Aadhaar (last 4)", length=4),
        field("geography_section", "Section Break", "Geography"),
        field(
            "district",
            "Link",
            "District",
            options="District",
            reqd=1,
            in_list_view=1,
            in_standard_filter=1,
        ),
        field(
            "block",
            "Link",
            "Block",
            options="Block",
            reqd=1,
            in_list_view=1,
            in_standard_filter=1,
        ),
        field(
            "village",
            "Link",
            "Village",
            options="Village",
            reqd=1,
            in_list_view=1,
            in_standard_filter=1,
        ),
        field(
            "cluster",
            "Link",
            "Cluster",
            options="Cluster",
            read_only=1,
            fetch_from="village.cluster",
            in_standard_filter=1,
        ),
        field("land_section", "Section Break", "Land"),
        field("primary_survey_number", "Data", "Survey Number"),
        field("land_extent_acres", "Float", "Land Extent (acres)"),
        field("land_parcels", "Table", "Land Parcels", options="Farmer Land Parcel"),
        field("address_section", "Section Break", "Address & Status"),
        field("address_line", "Small Text", "Address"),
        field("pincode", "Data", "Pincode"),
        field("is_active", "Check", "Active", default="1", in_list_view=1, in_standard_filter=1),
        field("tags", "Small Text", "Tags"),
        field("notes", "Text", "Notes"),
        field("sync_section", "Section Break", "Sync"),
        field("client_id", "Data", "Client ID", length=36, search_index=1),
        field("doc_version", "Int", "Doc Version", default="1", read_only=1),
        field("is_deleted", "Check", "Is Deleted", default="0"),
        field(
            "sync_status",
            "Select",
            "Sync Status",
            options="\n".join(["synced", "pending"]),
            default="synced",
        ),
        field(
            "created_via",
            "Select",
            "Created Via",
            options="\n".join(["mobile", "desk", "import", "system"]),
            default="desk",
        ),
    ]
    base = APP_ROOT / "farmer_registry" / "doctype" / slug
    write(APP_ROOT / "farmer_registry" / "doctype" / "__init__.py", "")
    write(base / "__init__.py", "")
    write(
        base / f"{slug}.json",
        json.dumps(
            doctype_json(
                "Farmer",
                fields,
                autoname="format:FR-{#####}",
                title_field="farmer_name",
                allow_import=1,
                search_fields="farmer_name,mobile,aadhaar_last4,village",
            ),
            indent=1,
        )
        + "\n",
    )
    write(
        base / f"{slug}.py",
        '''# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from agriflow.farmer_registry.utils.validation import (
\thas_active_farmer_project,
\tnormalize_mobile,
\tvalidate_aadhaar_last4,
\tvalidate_geography_chain,
\tvalidate_mobile_digits,
\tvalidate_mobile_unique_per_district,
)


class Farmer(Document):
\tdef before_validate(self):
\t\tself.mobile_normalized = normalize_mobile(self.mobile)
\t\tif self.alternate_mobile:
\t\t\tself.alternate_mobile = normalize_mobile(self.alternate_mobile) or None

\tdef before_save(self):
\t\tif not self.is_new():
\t\t\tself.doc_version = (self.doc_version or 1) + 1
\t\telif not self.doc_version:
\t\t\tself.doc_version = 1

\tdef validate(self):
\t\tvalidate_mobile_digits(self.mobile)
\t\tif self.alternate_mobile:
\t\t\tvalidate_mobile_digits(self.alternate_mobile, "Alternate Mobile")

\t\tvalidate_aadhaar_last4(self.aadhaar_last4)
\t\tvalidate_geography_chain(self.district, self.block, self.village, self.cluster)
\t\tvalidate_mobile_unique_per_district(self.mobile_normalized, self.district, self.name)

\t\tif self.is_deleted:
\t\t\tself.is_active = 0

\t\tif not self.is_active and self.name and has_active_farmer_project(self.name):
\t\t\tfrappe.throw(
\t\t\t\tfrappe._("Cannot deactivate farmer with an active Farmer Project"),
\t\t\t\tfrappe.ValidationError,
\t\t\t)

\t\tif self.client_id:
\t\t\texisting_client = frappe.db.exists(
\t\t\t\t"Farmer",
\t\t\t\t{"client_id": self.client_id, "name": ("!=", self.name or "")},
\t\t\t)
\t\t\tif existing_client:
\t\t\t\tfrappe.throw(frappe._("Client ID already exists"))
''',
    )


if __name__ == "__main__":
    main()
