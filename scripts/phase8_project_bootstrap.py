#!/usr/bin/env python3
"""Phase 8 — Generate Project Lifecycle (Farmer Project aggregate root) in frappe-bench."""
from __future__ import annotations

import json
from pathlib import Path

APP_ROOT = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
FIXTURES_ROOT = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/fixtures")
HOOKS_PATH = APP_ROOT / "hooks.py"
MODULE = "Project Lifecycle"

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

STAGES = [
    (1, "lead_captured", "project.stage.lead_captured"),
    (2, "eligibility_check", "project.stage.eligibility_check"),
    (3, "documents_collected", "project.stage.documents_collected"),
    (4, "mimis_registered", "project.stage.mimis_registered"),
    (5, "field_survey", "project.stage.field_survey"),
    (6, "quotation_generated", "project.stage.quotation_generated"),
    (7, "pre_inspection_approval", "project.stage.pre_inspection_approval"),
    (8, "work_order_received", "project.stage.work_order_received"),
    (9, "material_dispatched", "project.stage.material_dispatched"),
    (10, "installation_done", "project.stage.installation_done"),
    (11, "post_inspection_approval", "project.stage.post_inspection_approval"),
    (12, "subsidy_released", "project.stage.subsidy_released"),
]

STAGE_KEYS = [s[1] for s in STAGES]
STAGE_OPTIONS = "\n".join(STAGE_KEYS)

ROLE_MATRIX = {
    "eligibility_check": ["Office Staff", "Field Staff", "Office Manager", "Owner"],
    "documents_collected": ["Office Staff", "Field Staff", "Office Manager", "Owner"],
    "mimis_registered": ["Office Manager", "Owner"],
    "field_survey": ["Field Staff", "Office Manager", "Owner"],
    "quotation_generated": ["Office Staff", "Office Manager", "Owner"],
    "pre_inspection_approval": ["Office Manager", "Owner"],
    "work_order_received": ["Office Staff", "Office Manager", "Owner"],
    "material_dispatched": ["Store Keeper", "Office Manager", "Owner"],
    "installation_done": ["Installer Team", "Office Manager", "Owner"],
    "post_inspection_approval": ["Office Manager", "Owner"],
    "subsidy_released": ["Office Manager", "Owner"],
}

BYPASS_ROLES = {"Administrator", "System Manager"}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path}")


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
    length: int | None = None,
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
        "unique": 0,
    }
    if options:
        f["options"] = options
    if default is not None:
        f["default"] = default
    if fetch_from:
        f["fetch_from"] = fetch_from
    if length is not None:
        f["length"] = length
    return f


def doctype_json(
    name: str,
    fields: list[dict],
    *,
    autoname: str,
    title_field: str,
    track_changes: int = 1,
    allow_rename: int = 0,
    istable: int = 0,
    search_fields: str | None = None,
) -> dict:
    doc = {
        "actions": [],
        "allow_import": 0,
        "allow_rename": allow_rename,
        "autoname": autoname,
        "creation": "2026-05-20 00:00:00.000000",
        "doctype": "DocType",
        "engine": "InnoDB",
        "field_order": [f["fieldname"] for f in fields],
        "fields": fields,
        "index_web_pages_for_search": 1,
        "links": [],
        "modified": "2026-05-20 00:00:00.000000",
        "modified_by": "Administrator",
        "module": MODULE,
        "name": name,
        "owner": "Administrator",
        "permissions": [] if istable else PERMS_SM,
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


def write_fixtures() -> None:
    stage_rows = []
    for seq, key, label_key in STAGES:
        stage_rows.append(
            {
                "doctype": "Project Stage",
                "name": key,
                "stage_key": key,
                "sequence": seq,
                "label_i18n_key": label_key,
                "is_active": 1,
            }
        )
    write(
        FIXTURES_ROOT / "project_stage.json",
        json.dumps(stage_rows, indent=1) + "\n",
    )
    write(
        FIXTURES_ROOT / "project_stage_role_matrix.json",
        json.dumps(ROLE_MATRIX, indent=2) + "\n",
    )


def write_seed_hook() -> None:
    write(
        APP_ROOT / "project_lifecycle" / "install" / "__init__.py",
        "",
    )
    write(
        APP_ROOT / "project_lifecycle" / "install" / "seed_project_stages.py",
        '''# Copyright (c) 2026, Murugan and contributors

def after_migrate():
\timport frappe
\tfrom frappe.core.doctype.data_import.data_import import import_doc

\tif frappe.db.count("Project Stage", {"is_active": 1}) >= 12:
\t\treturn
\tpath = frappe.get_app_path("agriflow", "fixtures", "project_stage.json")
\timport_doc(path)
''',
    )


def write_hooks() -> None:
    text = HOOKS_PATH.read_text(encoding="utf-8")
    old = 'fixtures = [\n    {"dt": "District"},\n    {"dt": "Block"},\n]'
    new = 'fixtures = [\n    {"dt": "District"},\n    {"dt": "Block"},\n    {"dt": "Project Stage"},\n]'
    if old in text:
        text = text.replace(old, new)
    elif '{"dt": "Project Stage"}' not in text:
        raise SystemExit("hooks.py fixtures block not found — update manually")

    after_migrate_hook = (
        'after_migrate = ["agriflow.project_lifecycle.install.seed_project_stages.after_migrate"]\n'
    )
    if "seed_project_stages.after_migrate" not in text:
        if "after_migrate = [" in text:
            text = text.replace(
                "after_migrate = [",
                'after_migrate = [\n\t"agriflow.project_lifecycle.install.seed_project_stages.after_migrate",',
                1,
            )
        else:
            insert_at = text.find("doc_events = {")
            if insert_at == -1:
                text = text + "\n" + after_migrate_hook
            else:
                text = text[:insert_at] + after_migrate_hook + "\n" + text[insert_at:]
    write(HOOKS_PATH, text)


def write_stages_util() -> None:
    write(
        APP_ROOT / "project_lifecycle" / "utils" / "__init__.py",
        "",
    )
    write(
        APP_ROOT / "project_lifecycle" / "utils" / "stages.py",
        '''# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Project stage fixture loader (DB-backed, not hardcoded-only)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import frappe
from frappe import _

FIXTURES_DIR = Path(frappe.get_app_path("agriflow")) / "fixtures"


@lru_cache(maxsize=1)
def get_stage_map() -> dict[str, dict]:
\t"""Return stage_key -> {sequence, label_i18n_key}."""
\trows = frappe.get_all(
\t\t"Project Stage",
\t\tfilters={"is_active": 1},
\t\tfields=["stage_key", "sequence", "label_i18n_key"],
\t\torder_by="sequence asc",
\t)
\tif not rows:
\t\tfrappe.throw(_("Project Stage fixtures are not loaded. Run migrate."))
\treturn {r.stage_key: r for r in rows}


def get_stage_by_sequence(sequence: int) -> str | None:
\tfor key, row in get_stage_map().items():
\t\tif row.sequence == sequence:
\t\t\treturn key
\treturn None


def get_next_stage_key(current_stage: str) -> str | None:
\tcurrent = get_stage_map().get(current_stage)
\tif not current:
\t\treturn None
\treturn get_stage_by_sequence(current.sequence + 1)


def validate_stage_key(stage_key: str) -> None:
\tif stage_key not in get_stage_map():
\t\tfrappe.throw(_("Invalid stage: {0}").format(stage_key))


@lru_cache(maxsize=1)
def get_role_matrix() -> dict[str, list[str]]:
\tpath = FIXTURES_DIR / "project_stage_role_matrix.json"
\tif not path.exists():
\t\treturn {}
\twith path.open(encoding="utf-8") as handle:
\t\treturn json.load(handle)


def user_may_transition_to(user: str, target_stage: str) -> bool:
\troles = set(frappe.get_roles(user))
\tif roles & {"Administrator", "System Manager"}:
\t\treturn True
\tallowed = get_role_matrix().get(target_stage) or []
\treturn bool(roles & set(allowed))
''',
    )


def write_lifecycle_service() -> None:
    write(APP_ROOT / "project_lifecycle" / "services" / "__init__.py", "")
    write(
        APP_ROOT / "project_lifecycle" / "services" / "lifecycle.py",
        '''# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Farmer Project aggregate root — create and stage transitions."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import now_datetime

from agriflow.project_lifecycle.utils.stages import (
\tget_next_stage_key,
\tget_stage_map,
\tuser_may_transition_to,
\tvalidate_stage_key,
)

LIFECYCLE_FLAG = "agriflow_lifecycle_write"
MIMIS_GATE_APPROVED = frozenset({"approved", "waived"})


class ProjectLifecycleService:
\tdef create_project(
\t\tself,
\t\tfarmer: str,
\t\t*,
\t\tproject_type: str = "subsidy",
\t\tdistrict: str | None = None,
\t\tblock: str | None = None,
\t\tcluster: str | None = None,
\t\tvillage: str | None = None,
\t\tofficer: str | None = None,
\t\tassigned_to: str | None = None,
\t\tpriority: str = "medium",
\t\tremarks: str | None = None,
\t\tclient_id: str | None = None,
\t\tcreated_via: str = "desk",
\t) -> frappe.model.document.Document:
\t\tself._ensure_one_active_subsidy_project(farmer)
\t\tfarmer_doc = frappe.get_doc("Farmer", farmer)
\t\tdistrict = district or farmer_doc.district
\t\tblock = block or farmer_doc.block
\t\tvillage = village or farmer_doc.village
\t\tcluster = cluster or farmer_doc.cluster
\t\tvillage_name = frappe.db.get_value("Village", village, "village_name") or village
\t\tproject_title = f"{farmer_doc.farmer_name} - {village_name}"

\t\tdoc = frappe.get_doc(
\t\t\t{
\t\t\t\t"doctype": "Farmer Project",
\t\t\t\t"project_title": project_title,
\t\t\t\t"farmer": farmer,
\t\t\t\t"project_type": project_type,
\t\t\t\t"current_stage": "lead_captured",
\t\t\t\t"stage_sequence": 1,
\t\t\t\t"district": district,
\t\t\t\t"block": block,
\t\t\t\t"cluster": cluster,
\t\t\t\t"village": village,
\t\t\t\t"officer": officer,
\t\t\t\t"status": "active",
\t\t\t\t"started_on": frappe.utils.today(),
\t\t\t\t"assigned_to": assigned_to,
\t\t\t\t"priority": priority,
\t\t\t\t"remarks": remarks,
\t\t\t\t"mimis_gate_status": "pending",
\t\t\t\t"client_id": client_id,
\t\t\t\t"doc_version": 1,
\t\t\t\t"created_via": created_via,
\t\t\t\t"stage_history": [
\t\t\t\t\t{
\t\t\t\t\t\t"from_stage": "",
\t\t\t\t\t\t"to_stage": "lead_captured",
\t\t\t\t\t\t"from_sequence": 0,
\t\t\t\t\t\t"to_sequence": 1,
\t\t\t\t\t\t"transitioned_on": now_datetime(),
\t\t\t\t\t\t"transitioned_by": frappe.session.user,
\t\t\t\t\t\t"notes": _("Project created"),
\t\t\t\t\t}
\t\t\t\t],
\t\t\t}
\t\t)
\t\tfrappe.flags[LIFECYCLE_FLAG] = True
\t\ttry:
\t\t\tdoc.insert(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags[LIFECYCLE_FLAG] = False
\t\treturn doc

\tdef transition(
\t\tself,
\t\tproject_name: str,
\t\ttarget_stage: str,
\t\t*,
\t\tdoc_version: int | None = None,
\t\tnotes: str | None = None,
\t\tclient_id: str | None = None,
\t\tuser: str | None = None,
\t\tis_correction: bool = False,
\t) -> dict[str, Any]:
\t\tuser = user or frappe.session.user
\t\tvalidate_stage_key(target_stage)
\t\tif not user_may_transition_to(user, target_stage):
\t\t\tfrappe.throw(_("You do not have permission to transition to stage {0}").format(target_stage))

\t\tproject = frappe.get_doc("Farmer Project", project_name)
\t\tif project.is_deleted:
\t\t\tfrappe.throw(_("Project is deleted"))

\t\tif project.status == "cancelled":
\t\t\tfrappe.throw(_("Cancelled projects cannot transition"))
\t\tif project.status == "on_hold":
\t\t\tfrappe.throw(_("On-hold projects cannot transition until resumed"))
\t\tif project.status == "completed":
\t\t\tfrappe.throw(_("Completed projects cannot transition"))

\t\tif doc_version is not None and int(project.doc_version or 0) != int(doc_version):
\t\t\tfrappe.throw(
\t\t\t\t_("Stale doc_version. Server has {0}, client sent {1}").format(
\t\t\t\t\tproject.doc_version, doc_version
\t\t\t\t)
\t\t\t)

\t\texpected_next = get_next_stage_key(project.current_stage)
\t\tif not is_correction and target_stage != expected_next:
\t\t\tfrappe.throw(
\t\t\t\t_("Invalid transition. Expected next stage {0}, got {1}").format(
\t\t\t\t\texpected_next, target_stage
\t\t\t\t)
\t\t\t)

\t\tstage_map = get_stage_map()
\t\ttarget_seq = stage_map[target_stage].sequence
\t\tif not is_correction and target_seq != (project.stage_sequence or 0) + 1:
\t\t\tfrappe.throw(_("Stage sequence must advance by exactly 1"))

\t\tself._validate_mimis_gate(project, target_stage)
\t\tself._validate_officer_for_stage(project, target_seq)

\t\tfrom_stage = project.current_stage
\t\tfrom_sequence = project.stage_sequence or 0
\t\thistory_row = {
\t\t\t"from_stage": from_stage or "",
\t\t\t"to_stage": target_stage,
\t\t\t"from_sequence": from_sequence,
\t\t\t"to_sequence": target_seq,
\t\t\t"transitioned_on": now_datetime(),
\t\t\t"transitioned_by": user,
\t\t\t"notes": notes or "",
\t\t\t"client_id": client_id,
\t\t\t"is_correction": 1 if is_correction else 0,
\t\t}
\t\tproject.append("stage_history", history_row)
\t\tproject.current_stage = target_stage
\t\tproject.stage_sequence = target_seq
\t\tproject.doc_version = (project.doc_version or 1) + 1

\t\tif target_stage == "subsidy_released":
\t\t\tproject.status = "completed"

\t\tfrappe.flags[LIFECYCLE_FLAG] = True
\t\ttry:
\t\t\tproject.save(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags[LIFECYCLE_FLAG] = False

\t\tself._log_transition(project.name, from_stage, target_stage, user)
\t\t# Phase 10: enqueue generate_stage_tasks
\t\treturn {
\t\t\t"name": project.name,
\t\t\t"current_stage": project.current_stage,
\t\t\t"stage_sequence": project.stage_sequence,
\t\t\t"doc_version": project.doc_version,
\t\t\t"status": project.status,
\t\t\t"stage_history_row": history_row,
\t\t}

\tdef _ensure_one_active_subsidy_project(self, farmer: str, exclude: str | None = None) -> None:
\t\tfilters = {
\t\t\t"farmer": farmer,
\t\t\t"project_type": "subsidy",
\t\t\t"status": "active",
\t\t\t"is_deleted": 0,
\t\t}
\t\tif exclude:
\t\t\tfilters["name"] = ("!=", exclude)
\t\tif frappe.db.exists("Farmer Project", filters):
\t\t\tfrappe.throw(_("Farmer already has an active subsidy project"))

\tdef _validate_mimis_gate(self, project, target_stage: str) -> None:
\t\tif target_stage != "mimis_registered":
\t\t\treturn
\t\tif (project.mimis_gate_status or "pending") not in MIMIS_GATE_APPROVED:
\t\t\tfrappe.throw(
\t\t\t\t_("MIMIS gate not passed. Set mimis_gate_status to approved or waived before MIMIS registration stage.")
\t\t\t)

\tdef _validate_officer_for_stage(self, project, target_seq: int) -> None:
\t\tif target_seq < 4:
\t\t\treturn
\t\tif not project.officer:
\t\t\tfrappe.throw(_("Officer is required from MIMIS Registered stage onward"))
\t\tif not project.cluster:
\t\t\treturn
\t\tactive = frappe.db.get_value(
\t\t\t"Officer Assignment History",
\t\t\t{"cluster": project.cluster, "is_active": 1},
\t\t\t"officer",
\t\t)
\t\tif active and active != project.officer:
\t\t\tmsg = _("Officer {0} does not match active assignment for cluster {1}").format(
\t\t\t\tproject.officer, project.cluster
\t\t\t)
\t\t\tif target_seq >= 7:
\t\t\t\tfrappe.throw(msg)
\t\t\tfrappe.msgprint(msg, indicator="orange", alert=True)

\tdef _log_transition(self, project_name: str, from_stage: str, to_stage: str, user: str) -> None:
\t\tfrappe.logger("agriflow.lifecycle").info(
\t\t\t"transition %s %s -> %s by %s", project_name, from_stage, to_stage, user
\t\t)


def get_lifecycle_service() -> ProjectLifecycleService:
\treturn ProjectLifecycleService()
''',
    )


def write_desk_api() -> None:
    write(APP_ROOT / "project_lifecycle" / "api" / "__init__.py", "")
    write(
        APP_ROOT / "project_lifecycle" / "api" / "desk.py",
        '''# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Desk-only helpers for manual lifecycle testing (not public REST v1)."""

from __future__ import annotations

import frappe
from frappe import _

from agriflow.project_lifecycle.services.lifecycle import get_lifecycle_service


@frappe.whitelist()
def transition_for_desk(project: str, target_stage: str, notes: str | None = None, doc_version: int | None = None):
\t"""Advance project stage — internal testing; System Manager / Administrator only."""
\tfrappe.only_for(("System Manager", "Administrator"))
\tif not project or not target_stage:
\t\tfrappe.throw(_("project and target_stage are required"))
\tversion = int(doc_version) if doc_version not in (None, "") else None
\tif version is None:
\t\tversion = frappe.db.get_value("Farmer Project", project, "doc_version")
\treturn get_lifecycle_service().transition(
\t\tproject,
\t\ttarget_stage,
\t\tdoc_version=version,
\t\tnotes=notes,
\t)


@frappe.whitelist()
def create_project_for_desk(
\tfarmer: str,
\tproject_type: str = "subsidy",
\tstatus: str = "active",
\tremarks: str | None = None,
):
\t"""Create subsidy project — desk testing only."""
\tfrappe.only_for(("System Manager", "Administrator"))
\tsvc = get_lifecycle_service()
\tdoc = svc.create_project(farmer, project_type=project_type, remarks=remarks, created_via="desk")
\tif status and status != "active":
\t\tfrappe.flags.agriflow_lifecycle_write = True
\t\ttry:
\t\t\tdoc.status = status
\t\t\tdoc.save(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags.agriflow_lifecycle_write = False
\treturn {"name": doc.name, "current_stage": doc.current_stage, "stage_sequence": doc.stage_sequence}
''',
    )


def write_doctypes() -> None:
    base = APP_ROOT / "project_lifecycle" / "doctype"
    write(base / "__init__.py", "")

    # Project Stage
    ps_slug = "project_stage"
    ps_fields = [
        field("stage_key", "Data", "Stage Key", reqd=1, in_list_view=1, search_index=1),
        field("sequence", "Int", "Sequence", reqd=1, in_list_view=1, in_standard_filter=1),
        field("label_i18n_key", "Data", "Label i18n Key", reqd=1, in_list_view=1),
        field("is_active", "Check", "Is Active", default="1", in_list_view=1),
    ]
    ps_dir = base / ps_slug
    write(ps_dir / "__init__.py", "")
    write(ps_dir / f"{ps_slug}.json", json.dumps(
        doctype_json("Project Stage", ps_fields, autoname="field:stage_key", title_field="stage_key", allow_rename=0),
        indent=1,
    ) + "\n")
    write(ps_dir / f"{ps_slug}.py", '''# Copyright (c) 2026, Murugan and contributors
from frappe.model.document import Document

class ProjectStage(Document):
\tpass
''')

    # Project Stage History (child)
    psh_slug = "project_stage_history"
    psh_fields = [
        field("from_stage", "Select", "From Stage", options=STAGE_OPTIONS),
        field("to_stage", "Select", "To Stage", reqd=1, options=STAGE_OPTIONS, in_list_view=1),
        field("from_sequence", "Int", "From Sequence", in_list_view=1),
        field("to_sequence", "Int", "To Sequence", reqd=1, in_list_view=1),
        field("transitioned_on", "Datetime", "Transitioned On", reqd=1, in_list_view=1),
        field("transitioned_by", "Link", "Transitioned By", options="User", reqd=1, in_list_view=1),
        field("notes", "Small Text", "Notes"),
        field("attachment", "Attach", "Attachment"),
        field("is_correction", "Check", "Is Correction", default="0"),
        field("corrects_row", "Data", "Corrects Row"),
        field("client_id", "Data", "Client ID", length=36),
    ]
    psh_dir = base / psh_slug
    write(psh_dir / "__init__.py", "")
    write(psh_dir / f"{psh_slug}.json", json.dumps(
        doctype_json(
            "Project Stage History",
            psh_fields,
            autoname="hash",
            title_field="to_stage",
            istable=1,
            track_changes=0,
        ),
        indent=1,
    ) + "\n")
    write(psh_dir / f"{psh_slug}.py", '''# Copyright (c) 2026, Murugan and contributors
from frappe.model.document import Document

class ProjectStageHistory(Document):
\tpass
''')

    # Farmer Project
    fp_slug = "farmer_project"
    fp_fields = [
        field("project_section", "Section Break", "Project"),
        field("project_title", "Data", "Title", reqd=1, in_list_view=1, search_index=1),
        field("farmer", "Link", "Farmer", options="Farmer", reqd=1, in_list_view=1, in_standard_filter=1),
        field("project_type", "Select", "Project Type", options="subsidy", reqd=1, default="subsidy", in_standard_filter=1),
        field("lifecycle_section", "Section Break", "Lifecycle"),
        field(
            "current_stage",
            "Select",
            "Current Stage",
            options=STAGE_OPTIONS,
            reqd=1,
            default="lead_captured",
            in_list_view=1,
            in_standard_filter=1,
            read_only=1,
        ),
        field("stage_sequence", "Int", "Stage Sequence", reqd=1, default="1", in_list_view=1, read_only=1),
        field(
            "status",
            "Select",
            "Status",
            options="\n".join(["active", "on_hold", "completed", "cancelled"]),
            reqd=1,
            default="active",
            in_list_view=1,
            in_standard_filter=1,
        ),
        field("started_on", "Date", "Started On"),
        field("geography_section", "Section Break", "Geography"),
        field("district", "Link", "District", options="District", reqd=1, in_standard_filter=1),
        field("block", "Link", "Block", options="Block", reqd=1, in_list_view=1, in_standard_filter=1),
        field("cluster", "Link", "Cluster", options="Cluster", reqd=1, in_standard_filter=1),
        field("village", "Link", "Village", options="Village", reqd=1, in_list_view=1, in_standard_filter=1),
        field("officer", "Link", "Officer", options="Officer", in_standard_filter=1),
        field("assignment_section", "Section Break", "Assignment"),
        field("assigned_to", "Link", "Assigned To", options="User"),
        field("priority", "Select", "Priority", options="\n".join(["low", "medium", "high"]), default="medium"),
        field("financial_section", "Section Break", "Financial"),
        field("expected_subsidy_amount", "Currency", "Expected Subsidy"),
        field("quoted_amount", "Currency", "Quoted Amount"),
        field("total_expense", "Currency", "Total Expense", read_only=1),
        field("references_section", "Section Break", "References"),
        field("mimis_registration_number", "Data", "MIMIS Registration No."),
        field("work_order_number", "Data", "Work Order No."),
        field("mimis_section", "Section Break", "MIMIS Gate"),
        field(
            "mimis_gate_status",
            "Select",
            "MIMIS Gate Status",
            options="\n".join(["pending", "approved", "waived", "rejected"]),
            default="pending",
            in_standard_filter=1,
        ),
        field("mimis_approved_on", "Datetime", "MIMIS Approved On", read_only=1),
        field("mimis_reconciliation_ref", "Data", "MIMIS Reconciliation Ref"),
        field("remarks", "Text", "Remarks"),
        field("timeline_section", "Section Break", "Stage History"),
        field("stage_history", "Table", "Stage History", options="Project Stage History"),
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
    fp_dir = base / fp_slug
    write(fp_dir / "__init__.py", "")
    write(fp_dir / f"{fp_slug}.json", json.dumps(
        doctype_json(
            "Farmer Project",
            fp_fields,
            autoname="format:FP-{YYYY}-{#####}",
            title_field="project_title",
            search_fields="name,farmer,village,current_stage",
            allow_rename=0,
        ),
        indent=1,
    ) + "\n")
    write(
        fp_dir / f"{fp_slug}.py",
        '''# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe.model.document import Document

from agriflow.farmer_registry.utils.validation import validate_geography_chain
from agriflow.project_lifecycle.services.lifecycle import LIFECYCLE_FLAG

class FarmerProject(Document):
\tdef validate(self):
\t\tif self.is_deleted:
\t\t\tself.status = "cancelled" if self.status == "active" else self.status

\t\tvalidate_geography_chain(self.district, self.block, self.village, self.cluster)
\t\tif self.cluster and self.village:
\t\t\tvc = frappe.db.get_value("Village", self.village, "cluster")
\t\t\tif vc and vc != self.cluster:
\t\t\t\tfrappe.throw(frappe._("Cluster must match Village"))

\t\tif self.status == "active" and self.project_type == "subsidy" and self.farmer:
\t\t\texisting = frappe.db.exists(
\t\t\t\t"Farmer Project",
\t\t\t\t{
\t\t\t\t\t"farmer": self.farmer,
\t\t\t\t\t"project_type": "subsidy",
\t\t\t\t\t"status": "active",
\t\t\t\t\t"is_deleted": 0,
\t\t\t\t\t"name": ("!=", self.name or ""),
\t\t\t\t},
\t\t\t)
\t\t\tif existing:
\t\t\t\tfrappe.throw(frappe._("Only one active subsidy project per farmer"))

\t\tif not frappe.flags.get(LIFECYCLE_FLAG):
\t\t\tself._block_direct_stage_mutation()
\t\t\tself._block_history_tampering()

\t\tif self.client_id:
\t\t\tdup = frappe.db.exists(
\t\t\t\t"Farmer Project",
\t\t\t\t{"client_id": self.client_id, "name": ("!=", self.name or "")},
\t\t\t)
\t\t\tif dup:
\t\t\t\tfrappe.throw(frappe._("Client ID already exists"))

\tdef _block_direct_stage_mutation(self):
\t\tif self.is_new():
\t\t\treturn
\t\tprev = frappe.db.get_value(
\t\t\t"Farmer Project",
\t\t\tself.name,
\t\t\t["current_stage", "stage_sequence"],
\t\t\tas_dict=True,
\t\t)
\t\tif not prev:
\t\t\treturn
\t\tif self.current_stage != prev.current_stage or int(self.stage_sequence or 0) != int(
\t\t\tprev.stage_sequence or 0
\t\t):
\t\t\tfrappe.throw(
\t\t\t\tfrappe._("Stage changes must use ProjectLifecycleService or transition_for_desk")
\t\t\t)

\tdef _block_history_tampering(self):
\t\tif frappe.session.user == "Administrator":
\t\t\treturn
\t\tprev_len = frappe.db.count("Project Stage History", {"parent": self.name})
\t\tnew_len = len(self.stage_history or [])
\t\tif new_len < prev_len:
\t\t\tfrappe.throw(frappe._("Stage history rows cannot be deleted"))
\t\tif new_len > prev_len + 1:
\t\t\tfrappe.throw(frappe._("Stage history rows can only be appended via lifecycle service"))
''',
    )


def main() -> None:
    print("Phase 8 — Project Lifecycle bootstrap")
    write_fixtures()
    write_stages_util()
    write_lifecycle_service()
    write_desk_api()
    write_doctypes()
    write_seed_hook()
    write_hooks()
    print("Done.")


if __name__ == "__main__":
    main()
