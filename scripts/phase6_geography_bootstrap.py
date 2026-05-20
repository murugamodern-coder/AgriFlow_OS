#!/usr/bin/env python3
"""Phase 6 — Generate Officer Network geography DocTypes in frappe-bench agriflow app."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

APP_ROOT = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
MODULE = "Officer Network"

MODULES = [
    "Farmer Registry",
    "Inventory",
    "Billing",
    "MIMIS Sync",
    "Project Lifecycle",
    "Task Engine",
    "Service",
    "Officer Network",
    "Profit",
]

MODULE_SLUGS = {
    "Farmer Registry": "farmer_registry",
    "Inventory": "inventory",
    "Billing": "billing",
    "MIMIS Sync": "mimis_sync",
    "Project Lifecycle": "project_lifecycle",
    "Task Engine": "task_engine",
    "Service": "service",
    "Officer Network": "officer_network",
    "Profit": "profit",
}

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
    return f


def doctype_json(
    name: str,
    fields: list[dict],
    *,
    autoname: str,
    title_field: str,
    track_changes: int = 1,
    allow_rename: int = 0,
    allow_import: int = 0,
) -> dict:
    field_order = [f["fieldname"] for f in fields]
    return {
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
        "module": MODULE,
        "name": name,
        "owner": "Administrator",
        "permissions": PERMS_SM,
        "sort_field": "modified",
        "sort_order": "DESC",
        "states": [],
        "track_changes": track_changes,
    }


def controller_py(class_name: str, body: str) -> str:
    return f"""# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class {class_name}(Document):
{body}
"""


def init_py() -> str:
    return ""


def build_doctypes() -> dict[str, dict]:
    district_fields = [
        field("district_code", "Data", "District Code", reqd=1, unique=1, in_list_view=1, in_standard_filter=1, search_index=1),
        field("district_name", "Data", "District Name", reqd=1, in_list_view=1),
        field("state", "Data", "State", reqd=1, default="Tamil Nadu"),
        field("is_active", "Check", "Is Active", default="1", in_list_view=1, in_standard_filter=1),
    ]
    block_fields = [
        field("block_code", "Data", "Block Code", reqd=1, in_list_view=1, in_standard_filter=1, search_index=1),
        field("block_name", "Data", "Block Name", reqd=1, in_list_view=1),
        field("district", "Link", "District", options="District", reqd=1, in_list_view=1, in_standard_filter=1),
        field("is_active", "Check", "Is Active", default="1", in_list_view=1, in_standard_filter=1),
    ]
    cluster_fields = [
        field("cluster_code", "Data", "Cluster Code", reqd=1, in_list_view=1, search_index=1),
        field("cluster_name", "Data", "Cluster Name", reqd=1, in_list_view=1),
        field("block", "Link", "Block", options="Block", reqd=1, in_list_view=1, in_standard_filter=1),
        field("district", "Link", "District", options="District", fetch_from="block.district", read_only=1),
        field("is_active", "Check", "Is Active", default="1", in_list_view=1),
    ]
    village_fields = [
        field("village_code", "Data", "Village Code", reqd=1, in_list_view=1, search_index=1),
        field("village_name", "Data", "Village Name", reqd=1, in_list_view=1),
        field("cluster", "Link", "Cluster", options="Cluster", reqd=1, in_list_view=1, in_standard_filter=1),
        field("block", "Link", "Block", options="Block", reqd=1, in_standard_filter=1),
        field("district", "Link", "District", options="District", fetch_from="block.district", read_only=1),
        field("pincode", "Data", "Pincode"),
        field("is_active", "Check", "Is Active", default="1", in_list_view=1),
    ]
    officer_fields = [
        field("officer_code", "Data", "Officer Code", reqd=1, unique=1, in_list_view=1, search_index=1),
        field("officer_name", "Data", "Officer Name", reqd=1, in_list_view=1),
        field("department", "Select", "Department", options="agriculture\nhorticulture", reqd=1, in_standard_filter=1),
        field("mobile", "Data", "Mobile"),
        field("email", "Data", "Email"),
        field("is_active", "Check", "Is Active", default="1", in_list_view=1, in_standard_filter=1),
        field("current_cluster", "Link", "Current Cluster", options="Cluster", read_only=1),
    ]
    oah_fields = [
        field("officer", "Link", "Officer", options="Officer", reqd=1, in_list_view=1),
        field("cluster", "Link", "Cluster", options="Cluster", reqd=1, in_list_view=1, in_standard_filter=1),
        field("block", "Link", "Block", options="Block", fetch_from="cluster.block", read_only=1),
        field("district", "Link", "District", options="District", fetch_from="cluster.district", read_only=1),
        field("valid_from", "Date", "Valid From", reqd=1, in_list_view=1),
        field("valid_to", "Date", "Valid To", in_list_view=1),
        field("assignment_reason", "Select", "Assignment Reason", options="initial\ntransfer\ncorrection", reqd=1),
        field("notes", "Small Text", "Notes"),
        field("is_active", "Check", "Is Active", read_only=1, in_list_view=1),
    ]
    return {
        "district": {
            "json": doctype_json("District", district_fields, autoname="field:district_code", title_field="district_name", allow_import=1),
            "class": "District",
            "validate": """
\tdef validate(self):
\t\tif not self.district_code:
\t\t\tfrappe.throw(frappe._("District Code is required"))
""",
        },
        "block": {
            "json": doctype_json("Block", block_fields, autoname="field:block_code", title_field="block_name", allow_import=1),
            "class": "Block",
            "validate": """
\tdef validate(self):
\t\tif self.district and frappe.db.exists("District", self.district):
\t\t\tif not frappe.db.get_value("District", self.district, "is_active"):
\t\t\t\tfrappe.throw(frappe._("District is inactive"))
\t\tif self.block_code and self.district:
\t\t\texisting = frappe.db.exists(
\t\t\t\t"Block",
\t\t\t\t{"block_code": self.block_code, "district": self.district, "name": ("!=", self.name)},
\t\t\t)
\t\t\tif existing:
\t\t\t\tfrappe.throw(frappe._("Block Code must be unique within the District"))
""",
        },
        "cluster": {
            "json": doctype_json("Cluster", cluster_fields, autoname="field:cluster_code", title_field="cluster_name", allow_import=1),
            "class": "Cluster",
            "validate": """
\tdef validate(self):
\t\tif self.block and self.district:
\t\t\tblock_district = frappe.db.get_value("Block", self.block, "district")
\t\t\tif block_district != self.district:
\t\t\t\tfrappe.throw(frappe._("District must match the selected Block"))
\t\tif self.cluster_code and self.block:
\t\t\texisting = frappe.db.exists(
\t\t\t\t"Cluster",
\t\t\t\t{"cluster_code": self.cluster_code, "block": self.block, "name": ("!=", self.name)},
\t\t\t)
\t\t\tif existing:
\t\t\t\tfrappe.throw(frappe._("Cluster Code must be unique within the Block"))
""",
        },
        "village": {
            "json": doctype_json("Village", village_fields, autoname="field:village_code", title_field="village_name", allow_import=1),
            "class": "Village",
            "validate": """
\tdef validate(self):
\t\tif self.cluster and self.block:
\t\t\tcluster_block = frappe.db.get_value("Cluster", self.cluster, "block")
\t\t\tif cluster_block != self.block:
\t\t\t\tfrappe.throw(frappe._("Block must match the selected Cluster"))
\t\tif self.village_code and self.block:
\t\t\texisting = frappe.db.exists(
\t\t\t\t"Village",
\t\t\t\t{"village_code": self.village_code, "block": self.block, "name": ("!=", self.name)},
\t\t\t)
\t\t\tif existing:
\t\t\t\tfrappe.throw(frappe._("Village Code must be unique within the Block"))
""",
        },
        "officer": {
            "json": doctype_json("Officer", officer_fields, autoname="field:officer_code", title_field="officer_name"),
            "class": "Officer",
            "validate": """
\tdef validate(self):
\t\tif self.officer_code:
\t\t\texisting = frappe.db.exists("Officer", {"officer_code": self.officer_code, "name": ("!=", self.name)})
\t\t\tif existing:
\t\t\t\tfrappe.throw(frappe._("Officer Code must be unique"))
""",
        },
        "officer_assignment_history": {
            "json": doctype_json(
                "Officer Assignment History",
                oah_fields,
                autoname="hash",
                title_field="officer",
            ),
            "class": "OfficerAssignmentHistory",
            "validate": """
\tdef validate(self):
\t\tfrom agriflow.officer_network.services.officer_assignment import validate_assignment

\t\tvalidate_assignment(self)

\tdef before_save(self):
\t\tself.is_active = 0 if self.valid_to else 1
""",
        },
    }


def write_doctype(slug: str, spec: dict) -> None:
    base = APP_ROOT / "officer_network" / "doctype" / slug
    write(base / "__init__.py", init_py())
    write(base / f"{slug}.json", json.dumps(spec["json"], indent=1) + "\n")
    write(base / f"{slug}.py", controller_py(spec["class"], spec["validate"]))


def write_services() -> None:
    write(APP_ROOT / "officer_network" / "services" / "__init__.py", init_py())
    write(
        APP_ROOT / "officer_network" / "services" / "officer_assignment.py",
        '''# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Officer assignment validation and officer current_cluster sync."""

from __future__ import annotations

import frappe
from frappe import _


def validate_assignment(doc) -> None:
\tif doc.valid_from and doc.valid_to and doc.valid_to < doc.valid_from:
\t\tfrappe.throw(_("Valid To cannot be before Valid From"))

\tif not doc.cluster:
\t\treturn

\t# One active officer per cluster at a time.
\tif not doc.valid_to:
\t\toverlap = frappe.db.exists(
\t\t\t"Officer Assignment History",
\t\t\t{
\t\t\t\t"cluster": doc.cluster,
\t\t\t\t"valid_to": ("is", "not set"),
\t\t\t\t"name": ("!=", doc.name or ""),
\t\t\t},
\t\t)
\t\tif overlap:
\t\t\tfrappe.throw(_("Cluster already has an active officer assignment"))


def on_assignment_change(doc, method=None) -> None:
\t"""Sync Officer.current_cluster from active assignment."""
\tif not doc.officer:
\t\treturn

\tactive_cluster = frappe.db.get_value(
\t\t"Officer Assignment History",
\t\t{"officer": doc.officer, "valid_to": ("is", "not set")},
\t\t"cluster",
\t)
\tfrappe.db.set_value("Officer", doc.officer, "current_cluster", active_cluster, update_modified=False)
''',
    )


def write_fixtures() -> None:
    fixtures_dir = APP_ROOT.parent / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    district = [
        {
            "doctype": "District",
            "district_code": "TVM",
            "district_name": "Tiruvannamalai",
            "state": "Tamil Nadu",
            "is_active": 1,
        }
    ]
    blocks = []
    for i in range(1, 13):
        code = f"BLK{i:02d}"
        blocks.append(
            {
                "doctype": "Block",
                "block_code": code,
                "block_name": f"Block {i:02d}",
                "district": "TVM",
                "is_active": 1,
            }
        )
    write(fixtures_dir / "district.json", json.dumps(district, indent=1) + "\n")
    write(fixtures_dir / "block.json", json.dumps(blocks, indent=1) + "\n")


def patch_hooks() -> None:
    hooks_path = APP_ROOT / "hooks.py"
    content = hooks_path.read_text(encoding="utf-8")
    content = content.replace('app_title = "yes"', 'app_title = "AgriFlow OS"')
    if "fixtures = [" not in content:
        insert = '''

# Fixtures
# --------
fixtures = [
    {"dt": "District"},
    {"dt": "Block"},
]

# Document Events
# ---------------
doc_events = {
    "Officer Assignment History": {
        "after_insert": "agriflow.officer_network.services.officer_assignment.on_assignment_change",
        "on_update": "agriflow.officer_network.services.officer_assignment.on_assignment_change",
    },
}

'''
        content = content.rstrip() + insert
    hooks_path.write_text(content, encoding="utf-8")
    print("  updated hooks.py")


def main() -> None:
    print(f"APP_ROOT: {APP_ROOT}")
    if not APP_ROOT.exists():
        raise SystemExit(f"App path not found: {APP_ROOT}")

    yes_dir = APP_ROOT / "yes"
    if yes_dir.exists():
        print("DESTRUCTIVE: removing placeholder module directory apps/agriflow/agriflow/yes/")
        shutil.rmtree(yes_dir)

    write(APP_ROOT / "modules.txt", "\n".join(MODULES) + "\n")

    for mod in MODULES:
        slug = MODULE_SLUGS[mod]
        write(APP_ROOT / slug / "__init__.py", init_py())

    write(APP_ROOT / "officer_network" / "__init__.py", init_py())
    write(APP_ROOT / "officer_network" / "doctype" / "__init__.py", init_py())

    specs = build_doctypes()
    for slug, spec in specs.items():
        write_doctype(slug, spec)

    write_services()
    write_fixtures()
    patch_hooks()
    print("Phase 6 file generation complete.")


if __name__ == "__main__":
    main()
