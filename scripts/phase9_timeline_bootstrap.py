#!/usr/bin/env python3
"""Phase 9 — Timeline Event foundation in frappe-bench agriflow app."""
from __future__ import annotations

import json
from pathlib import Path

APP_ROOT = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
MODULE = "Project Lifecycle"

PERMS_READ = [
    {
        "role": "System Manager",
        "read": 1,
        "write": 0,
        "create": 0,
        "delete": 0,
        "export": 1,
        "print": 1,
        "email": 1,
        "report": 1,
        "share": 1,
    }
]

EVENT_TYPES = "\n".join(
    [
        "project_created",
        "stage_transition",
        "mimis_gate_updated",
        "project_status_changed",
        "manual_note",
    ]
)

EVENT_SOURCES = "\n".join(["lifecycle", "mimis", "desk", "mobile", "system"])


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(APP_ROOT.parent.parent)}")


def field(
    fieldname: str,
    fieldtype: str,
    label: str,
    *,
    options: str | None = None,
    reqd: int = 0,
    default: str | None = None,
    read_only: int = 0,
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
    if length is not None:
        f["length"] = length
    return f


def write_timeline_doctype() -> None:
    slug = "timeline_event"
    fields = [
        field("farmer_project", "Link", "Farmer Project", options="Farmer Project", reqd=1, in_list_view=1, in_standard_filter=1, search_index=1),
        field("farmer", "Link", "Farmer", options="Farmer", reqd=1, in_list_view=1, in_standard_filter=1, search_index=1),
        field("event_type", "Select", "Event Type", options=EVENT_TYPES, reqd=1, in_list_view=1, in_standard_filter=1, search_index=1),
        field("event_source", "Select", "Event Source", options=EVENT_SOURCES, reqd=1, default="lifecycle", in_standard_filter=1),
        field("created_on", "Datetime", "Created On", reqd=1, in_list_view=1, search_index=1),
        field("actor", "Link", "Actor", options="User", in_list_view=1),
        field("actor_name", "Data", "Actor Name", in_list_view=1),
        field("payload_json", "JSON", "Payload"),
        field("reference_doctype", "Data", "Reference DocType"),
        field("reference_name", "Data", "Reference Name"),
        field("district", "Link", "District", options="District", in_standard_filter=1),
        field("block", "Link", "Block", options="Block", in_standard_filter=1),
        field("client_id", "Data", "Client ID", length=36, search_index=1),
        field("is_deleted", "Check", "Is Deleted", default="0"),
    ]
    base = APP_ROOT / "project_lifecycle" / "doctype" / slug
    doc = {
        "actions": [],
        "allow_import": 0,
        "allow_rename": 0,
        "autoname": "hash",
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
        "name": "Timeline Event",
        "owner": "Administrator",
        "permissions": PERMS_READ,
        "sort_field": "created_on",
        "sort_order": "DESC",
        "states": [],
        "title_field": "event_type",
        "track_changes": 0,
    }
    write(base / "__init__.py", "")
    write(base / f"{slug}.json", json.dumps(doc, indent=1) + "\n")
    write(
        base / f"{slug}.py",
        '''# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe import _
from frappe.model.document import Document

TIMELINE_FLAG = "agriflow_timeline_write"


class TimelineEvent(Document):
\tdef validate(self):
\t\tif not self.is_new() and not frappe.flags.get(TIMELINE_FLAG):
\t\t\tfrappe.throw(_("Timeline events are immutable and cannot be modified"))

\tdef on_trash(self):
\t\tif frappe.session.user != "Administrator":
\t\t\tfrappe.throw(_("Timeline events cannot be deleted"))
''',
    )


def write_timeline_service() -> None:
    write(APP_ROOT / "project_lifecycle" / "services" / "timeline.py", '''# Copyright (c) 2026, Murugan and contributors
"""Unified timeline activity stream — append-only Timeline Event rows."""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _
from frappe.utils import cstr, get_fullname, now_datetime

TIMELINE_FLAG = "agriflow_timeline_write"
MAX_NOTE_LEN = 2000
MAX_PAYLOAD_KEYS = 32


class TimelineService:
\tdef emit(
\t\tself,
\t\tevent_type: str,
\t\tfarmer_project: str,
\t\t*,
\t\tpayload: dict | None = None,
\t\tevent_source: str = "lifecycle",
\t\treference_doctype: str | None = None,
\t\treference_name: str | None = None,
\t\tclient_id: str | None = None,
\t\tcreated_on: str | None = None,
\t\tactor: str | None = None,
\t\tskip_idempotency: bool = False,
\t) -> str:
\t\t"""Insert one immutable timeline event; returns event name."""
\t\tself._validate_payload(payload)
\t\tproject = frappe.db.get_value(
\t\t\t"Farmer Project",
\t\t\tfarmer_project,
\t\t\t["farmer", "district", "block", "name"],
\t\t\tas_dict=True,
\t\t)
\t\tif not project:
\t\t\tfrappe.throw(_("Farmer Project not found"))

\t\tif client_id and not skip_idempotency:
\t\t\texisting = frappe.db.exists(
\t\t\t\t"Timeline Event",
\t\t\t\t{
\t\t\t\t\t"client_id": client_id,
\t\t\t\t\t"event_type": event_type,
\t\t\t\t\t"farmer_project": farmer_project,
\t\t\t\t\t"is_deleted": 0,
\t\t\t\t},
\t\t\t)
\t\t\tif existing:
\t\t\t\treturn existing

\t\tactor = actor or frappe.session.user
\t\tactor_name = get_fullname(actor) or actor

\t\tdoc = frappe.get_doc(
\t\t\t{
\t\t\t\t"doctype": "Timeline Event",
\t\t\t\t"farmer_project": farmer_project,
\t\t\t\t"farmer": project.farmer,
\t\t\t\t"event_type": event_type,
\t\t\t\t"event_source": event_source,
\t\t\t\t"created_on": created_on or now_datetime(),
\t\t\t\t"actor": actor,
\t\t\t\t"actor_name": actor_name,
\t\t\t\t"payload_json": payload or {},
\t\t\t\t"reference_doctype": reference_doctype,
\t\t\t\t"reference_name": reference_name,
\t\t\t\t"district": project.district,
\t\t\t\t"block": project.block,
\t\t\t\t"client_id": client_id,
\t\t\t\t"is_deleted": 0,
\t\t\t}
\t\t)
\t\tfrappe.flags[TIMELINE_FLAG] = True
\t\ttry:
\t\t\tdoc.insert(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags[TIMELINE_FLAG] = False
\t\treturn doc.name

\tdef query(
\t\tself,
\t\t*,
\t\tfarmer_project: str | None = None,
\t\tfarmer: str | None = None,
\t\tevent_types: list[str] | None = None,
\t\tsince: str | None = None,
\t\tlimit: int = 50,
\t\tcursor: str | None = None,
\t) -> dict[str, Any]:
\t\t"""Chronological feed (newest first) with keyset cursor."""
\t\tlimit = min(max(int(limit or 50), 1), 100)
\t\tfilters: dict[str, Any] = {"is_deleted": 0}
\t\tif farmer_project:
\t\t\tfilters["farmer_project"] = farmer_project
\t\tif farmer:
\t\t\tfilters["farmer"] = farmer
\t\tif event_types:
\t\t\tfilters["event_type"] = ("in", event_types)
\t\tif since:
\t\t\tfilters["created_on"] = (">=", since)

\t\tif cursor:
\t\t\tcursor_row = frappe.db.get_value(
\t\t\t\t"Timeline Event",
\t\t\t\tcursor,
\t\t\t\t["created_on", "name"],
\t\t\t\tas_dict=True,
\t\t\t)
\t\t\tif cursor_row:
\t\t\t\tfilters["name"] = ("<", cursor_row.name)

\t\trows = frappe.get_all(
\t\t\t"Timeline Event",
\t\t\tfilters=filters,
\t\t\tfields=[
\t\t\t\t"name",
\t\t\t\t"farmer_project",
\t\t\t\t"farmer",
\t\t\t\t"event_type",
\t\t\t\t"event_source",
\t\t\t\t"created_on",
\t\t\t\t"actor",
\t\t\t\t"actor_name",
\t\t\t\t"payload_json",
\t\t\t\t"reference_doctype",
\t\t\t\t"reference_name",
\t\t\t\t"client_id",
\t\t\t],
\t\t\torder_by="created_on desc, name desc",
\t\t\tlimit=limit + 1,
\t\t)

\t\tnext_cursor = None
\t\tif len(rows) > limit:
\t\t\tnext_cursor = rows[limit - 1].name
\t\t\trows = rows[:limit]

\t\treturn {
\t\t\t"items": [self.to_mobile_event(r) for r in rows],
\t\t\t"pagination": {"next_cursor": next_cursor, "limit": limit},
\t\t\t"open_tasks": [],
\t\t}

\tdef build_project_feed(self, farmer_project: str, *, limit: int = 100) -> list[dict[str, Any]]:
\t\tresult = self.query(farmer_project=farmer_project, limit=limit)
\t\treturn result["items"]

\tdef to_mobile_event(self, row) -> dict[str, Any]:
\t\tpayload = row.payload_json
\t\tif isinstance(payload, str):
\t\t\ttry:
\t\t\t\tpayload = json.loads(payload)
\t\t\texcept json.JSONDecodeError:
\t\t\t\tpayload = {}
\t\tif not isinstance(payload, dict):
\t\t\tpayload = {}
\t\treturn {
\t\t\t"id": row.name,
\t\t\t"event_type": row.event_type,
\t\t\t"event_source": row.event_source,
\t\t\t"created_on": row.created_on,
\t\t\t"actor": {"user": row.actor, "display_name": row.actor_name or row.actor},
\t\t\t"farmer_project": row.farmer_project,
\t\t\t"farmer": row.farmer,
\t\t\t"payload": payload,
\t\t\t"reference": {
\t\t\t\t"doctype": row.reference_doctype,
\t\t\t\t"name": row.reference_name,
\t\t\t},
\t\t\t"client_id": row.client_id,
\t\t}

\tdef emit_project_created(self, project) -> str:
\t\treturn self.emit(
\t\t\t"project_created",
\t\t\tproject.name,
\t\t\tpayload={
\t\t\t\t"project_type": project.project_type,
\t\t\t\t"current_stage": project.current_stage,
\t\t\t\t"stage_sequence": project.stage_sequence,
\t\t\t},
\t\t\tevent_source=project.created_via or "lifecycle",
\t\t\treference_doctype="Farmer Project",
\t\t\treference_name=project.name,
\t\t\tclient_id=f"{project.client_id}-created" if project.client_id else None,
\t\t)

\tdef emit_stage_transition(
\t\tself,
\t\tproject,
\t\t*,
\t\tfrom_stage: str,
\t\tto_stage: str,
\t\tfrom_sequence: int,
\t\tto_sequence: int,
\t\thistory_row_name: str | None,
\t\tnotes: str | None = None,
\t\tclient_id: str | None = None,
\t\tactor: str | None = None,
\t\tcreated_on: str | None = None,
\t) -> str:
\t\treturn self.emit(
\t\t\t"stage_transition",
\t\t\tproject.name,
\t\t\tpayload={
\t\t\t\t"from_stage": from_stage or "",
\t\t\t\t"to_stage": to_stage,
\t\t\t\t"from_sequence": from_sequence,
\t\t\t\t"to_sequence": to_sequence,
\t\t\t\t"history_row": history_row_name,
\t\t\t\t"notes": (notes or "")[:MAX_NOTE_LEN],
\t\t\t},
\t\t\tevent_source="lifecycle",
\t\t\treference_doctype="Project Stage History",
\t\t\treference_name=history_row_name,
\t\t\tclient_id=client_id,
\t\t\tactor=actor,
\t\t\tcreated_on=created_on,
\t\t)

\tdef emit_mimis_gate_updated(
\t\tself,
\t\tproject_name: str,
\t\t*,
\t\tfrom_status: str,
\t\tto_status: str,
\t\tmimis_reconciliation_ref: str | None = None,
\t) -> str:
\t\treturn self.emit(
\t\t\t"mimis_gate_updated",
\t\t\tproject_name,
\t\t\tpayload={
\t\t\t\t"from_status": from_status,
\t\t\t\t"to_status": to_status,
\t\t\t\t"mimis_reconciliation_ref": mimis_reconciliation_ref,
\t\t\t},
\t\t\tevent_source="mimis",
\t\t)

\tdef emit_project_status_changed(
\t\tself,
\t\tproject_name: str,
\t\t*,
\t\tfrom_status: str,
\t\tto_status: str,
\t\tcurrent_stage: str,
\t\tstage_sequence: int,
\t) -> str:
\t\treturn self.emit(
\t\t\t"project_status_changed",
\t\t\tproject_name,
\t\t\tpayload={
\t\t\t\t"from_status": from_status,
\t\t\t\t"to_status": to_status,
\t\t\t\t"current_stage": current_stage,
\t\t\t\t"stage_sequence": stage_sequence,
\t\t\t},
\t\t\tevent_source="lifecycle",
\t\t)

\tdef emit_manual_note(self, farmer_project: str, text: str, *, client_id: str | None = None) -> str:
\t\treturn self.emit(
\t\t\t"manual_note",
\t\t\tfarmer_project,
\t\t\tpayload={"text": cstr(text)[:MAX_NOTE_LEN], "visibility": "internal"},
\t\t\tevent_source="desk",
\t\t\tclient_id=client_id,
\t\t)

\tdef _validate_payload(self, payload: dict | None) -> None:
\t\tif not payload:
\t\t\treturn
\t\tif len(payload) > MAX_PAYLOAD_KEYS:
\t\t\tfrappe.throw(_("Timeline payload has too many keys"))
\t\tencoded = json.dumps(payload, default=str)
\t\tif len(encoded) > 8000:
\t\t\tfrappe.throw(_("Timeline payload is too large"))


def get_timeline_service() -> TimelineService:
\treturn TimelineService()
''')


def write_lifecycle_patch() -> None:
    path = APP_ROOT / "project_lifecycle" / "services" / "lifecycle.py"
    text = path.read_text(encoding="utf-8")
    if "get_timeline_service" in text:
        print("  lifecycle.py already integrated")
        return

    import_block = "from agriflow.project_lifecycle.utils.stages import (\n"
    new_import = (
        "from agriflow.project_lifecycle.services.timeline import get_timeline_service\n"
        "from agriflow.project_lifecycle.utils.stages import (\n"
    )
    text = text.replace(import_block, new_import)

    insert_emit = (
        "\t\tfrappe.flags[LIFECYCLE_FLAG] = True\n"
        "\t\ttry:\n"
        "\t\t\tdoc.insert(ignore_permissions=True)\n"
        "\t\tfinally:\n"
        "\t\t\tfrappe.flags[LIFECYCLE_FLAG] = False\n"
        "\t\tget_timeline_service().emit_project_created(doc)\n"
        "\t\treturn doc"
    )
    text = text.replace(
        "\t\tfrappe.flags[LIFECYCLE_FLAG] = True\n"
        "\t\ttry:\n"
        "\t\t\tdoc.insert(ignore_permissions=True)\n"
        "\t\tfinally:\n"
        "\t\t\tfrappe.flags[LIFECYCLE_FLAG] = False\n"
        "\t\treturn doc",
        insert_emit,
        1,
    )

    transition_emit = (
        "\t\tfrappe.flags[LIFECYCLE_FLAG] = True\n"
        "\t\ttry:\n"
        "\t\t\tproject.save(ignore_permissions=True)\n"
        "\t\tfinally:\n"
        "\t\t\tfrappe.flags[LIFECYCLE_FLAG] = False\n\n"
        "\t\thistory_row_name = project.stage_history[-1].name if project.stage_history else None\n"
        "\t\tget_timeline_service().emit_stage_transition(\n"
        "\t\t\tproject,\n"
        "\t\t\tfrom_stage=from_stage,\n"
        "\t\t\tto_stage=target_stage,\n"
        "\t\t\tfrom_sequence=from_sequence,\n"
        "\t\t\tto_sequence=target_seq,\n"
        "\t\t\thistory_row_name=history_row_name,\n"
        "\t\t\tnotes=notes,\n"
        "\t\t\tclient_id=client_id,\n"
        "\t\t\tactor=user,\n"
        "\t\t\tcreated_on=history_row.get(\"transitioned_on\"),\n"
        "\t\t)\n"
        "\t\tself._log_transition(project.name, from_stage, target_stage, user)"
    )
    text = text.replace(
        "\t\tfrappe.flags[LIFECYCLE_FLAG] = True\n"
        "\t\ttry:\n"
        "\t\t\tproject.save(ignore_permissions=True)\n"
        "\t\tfinally:\n"
        "\t\t\tfrappe.flags[LIFECYCLE_FLAG] = False\n\n"
        "\t\tself._log_transition(project.name, from_stage, target_stage, user)",
        transition_emit,
        1,
    )
    write(path, text)


def write_farmer_project_patch() -> None:
    write(
        APP_ROOT / "project_lifecycle" / "doctype" / "farmer_project" / "farmer_project.py",
        '''# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe.model.document import Document

from agriflow.farmer_registry.utils.validation import validate_geography_chain
from agriflow.project_lifecycle.services.lifecycle import LIFECYCLE_FLAG
from agriflow.project_lifecycle.services.timeline import get_timeline_service


class FarmerProject(Document):
\tdef before_save(self):
\t\tif self.is_new():
\t\t\treturn
\t\tprev = frappe.db.get_value(
\t\t\t"Farmer Project",
\t\t\tself.name,
\t\t\t["status", "mimis_gate_status", "mimis_reconciliation_ref"],
\t\t\tas_dict=True,
\t\t)
\t\tself._timeline_prev = prev or {}

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

\tdef on_update(self):
\t\tif self.is_new() or frappe.flags.get(LIFECYCLE_FLAG):
\t\t\treturn
\t\tprev = getattr(self, "_timeline_prev", None) or {}
\t\ttimeline = get_timeline_service()

\t\tif prev.get("mimis_gate_status") != self.mimis_gate_status:
\t\t\tif self.mimis_gate_status in ("approved", "waived") and not self.mimis_approved_on:
\t\t\t\tself.db_set("mimis_approved_on", frappe.utils.now_datetime(), update_modified=False)
\t\t\ttimeline.emit_mimis_gate_updated(
\t\t\t\tself.name,
\t\t\t\tfrom_status=prev.get("mimis_gate_status") or "pending",
\t\t\t\tto_status=self.mimis_gate_status,
\t\t\t\tmimis_reconciliation_ref=self.mimis_reconciliation_ref,
\t\t\t)

\t\tif prev.get("status") != self.status:
\t\t\ttimeline.emit_project_status_changed(
\t\t\t\tself.name,
\t\t\t\tfrom_status=prev.get("status"),
\t\t\t\tto_status=self.status,
\t\t\t\tcurrent_stage=self.current_stage,
\t\t\t\tstage_sequence=self.stage_sequence or 0,
\t\t\t)

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


def write_desk_patch() -> None:
    write(
        APP_ROOT / "project_lifecycle" / "api" / "desk.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Desk-only helpers for manual lifecycle testing (not public REST v1)."""

from __future__ import annotations

import frappe
from frappe import _

from agriflow.project_lifecycle.services.lifecycle import LIFECYCLE_FLAG, get_lifecycle_service
from agriflow.project_lifecycle.services.timeline import get_timeline_service


@frappe.whitelist()
def transition_for_desk(project: str, target_stage: str, notes: str | None = None, doc_version: int | None = None):
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
\tfrappe.only_for(("System Manager", "Administrator"))
\tsvc = get_lifecycle_service()
\tdoc = svc.create_project(farmer, project_type=project_type, remarks=remarks, created_via="desk")
\tif status and status != "active":
\t\tfrappe.flags[LIFECYCLE_FLAG] = True
\t\ttry:
\t\t\tdoc.status = status
\t\t\tdoc.save(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags[LIFECYCLE_FLAG] = False
\treturn {"name": doc.name, "current_stage": doc.current_stage, "stage_sequence": doc.stage_sequence}


@frappe.whitelist()
def add_timeline_note_for_desk(project: str, text: str, client_id: str | None = None):
\t"""Append manual_note timeline event — desk testing only."""
\tfrappe.only_for(("System Manager", "Administrator"))
\tif not project or not text:
\t\tfrappe.throw(_("project and text are required"))
\tif not frappe.db.exists("Farmer Project", project):
\t\tfrappe.throw(_("Farmer Project not found"))
\tevent_id = get_timeline_service().emit_manual_note(project, text, client_id=client_id)
\treturn {"event_id": event_id, "event_type": "manual_note"}
''',
    )


def write_install_scripts() -> None:
    install = APP_ROOT / "project_lifecycle" / "install"
    write(
        install / "phase9_backfill_timeline.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Backfill Timeline Event rows from Project Stage History (idempotent)."""

PROJECTS = ("FP-2026-00007", "FP-2026-00008")


def execute():
\timport frappe
\tfrom agriflow.project_lifecycle.services.timeline import get_timeline_service

\tfrappe.set_user("Administrator")
\ttimeline = get_timeline_service()
\tcreated = []

\tfor project_name in PROJECTS:
\t\tif not frappe.db.exists("Farmer Project", project_name):
\t\t\tcontinue
\t\tproject = frappe.get_doc("Farmer Project", project_name)

\t\tif not frappe.db.exists(
\t\t\t"Timeline Event",
\t\t\t{"farmer_project": project_name, "event_type": "project_created", "is_deleted": 0},
\t\t):
\t\t\tfirst = project.stage_history[0] if project.stage_history else None
\t\t\teid = timeline.emit(
\t\t\t\t"project_created",
\t\t\t\tproject_name,
\t\t\t\tpayload={
\t\t\t\t\t"project_type": project.project_type,
\t\t\t\t\t"current_stage": "lead_captured",
\t\t\t\t\t"stage_sequence": 1,
\t\t\t\t\t"backfill": True,
\t\t\t\t},
\t\t\t\tevent_source="system",
\t\t\t\treference_doctype="Farmer Project",
\t\t\t\treference_name=project_name,
\t\t\t\tcreated_on=first.transitioned_on if first else project.creation,
\t\t\t\tskip_idempotency=True,
\t\t\t)
\t\t\tcreated.append(eid)

\t\tfor row in project.stage_history:
\t\t\tif not row.to_stage or row.to_sequence <= 1:
\t\t\t\tcontinue
\t\t\tclient_key = f"backfill-{project_name}-{row.name}"
\t\t\tif frappe.db.exists("Timeline Event", {"client_id": client_key}):
\t\t\t\tcontinue
\t\t\teid = timeline.emit_stage_transition(
\t\t\t\tproject,
\t\t\t\tfrom_stage=row.from_stage or "",
\t\t\t\tto_stage=row.to_stage,
\t\t\t\tfrom_sequence=row.from_sequence or 0,
\t\t\t\tto_sequence=row.to_sequence,
\t\t\t\thistory_row_name=row.name,
\t\t\t\tnotes=row.notes,
\t\t\t\tclient_id=client_key,
\t\t\t\tactor=row.transitioned_by,
\t\t\t\tcreated_on=row.transitioned_on,
\t\t\t)
\t\t\tcreated.append(eid)

\t\tif project.status == "on_hold":
\t\t\tkey = f"backfill-status-{project_name}"
\t\t\tif not frappe.db.exists("Timeline Event", {"client_id": key}):
\t\t\t\teid = timeline.emit(
\t\t\t\t\t"project_status_changed",
\t\t\t\t\tproject_name,
\t\t\t\t\tpayload={
\t\t\t\t\t\t"from_status": "active",
\t\t\t\t\t\t"to_status": "on_hold",
\t\t\t\t\t\t"current_stage": project.current_stage,
\t\t\t\t\t\t"stage_sequence": project.stage_sequence,
\t\t\t\t\t\t"backfill": True,
\t\t\t\t},
\t\t\t\t\tevent_source="system",
\t\t\t\t\tclient_id=key,
\t\t\t\t\tcreated_on=project.modified,
\t\t\t\t)
\t\t\t\tcreated.append(eid)

\tfrappe.db.commit()
\treturn {"projects": list(PROJECTS), "events_created": len(created), "created_ids": created[:20]}
''',
    )
    write(
        install / "phase9_sample_timeline.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Add sample manual_note timeline events."""


def execute():
\timport frappe
\tfrom agriflow.project_lifecycle.services.timeline import get_timeline_service

\tfrappe.set_user("Administrator")
\ttimeline = get_timeline_service()
\tnotes = []
\tfor project, text in (
\t\t("FP-2026-00007", "Phase 9 sample: office verified documents."),
\t\t("FP-2026-00008", "Phase 9 sample: project on hold pending farmer visit."),
\t):
\t\tif frappe.db.exists("Farmer Project", project):
\t\t\teid = timeline.emit_manual_note(
\t\t\t\tproject,
\t\t\t\ttext,
\t\t\t\tclient_id=f"phase9-sample-note-{project}",
\t\t\t)
\t\t\tnotes.append({"project": project, "event_id": eid})
\tfrappe.db.commit()
\treturn {"manual_notes": notes}
''',
    )
    write(
        install / "phase9_verify_timeline.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Verify Timeline Event foundation."""


def execute():
\timport frappe
\tfrom agriflow.project_lifecycle.services.timeline import get_timeline_service

\tfrappe.set_user("Administrator")
\terrors = []
\ttimeline = get_timeline_service()

\tif not frappe.db.exists("DocType", "Timeline Event"):
\t\terrors.append("Timeline Event DocType missing")

\tmod = frappe.db.get_value("DocType", "Timeline Event", "module")
\tif mod != "Project Lifecycle":
\t\terrors.append(f"Timeline Event module is {mod}")

\tfor project in ("FP-2026-00007", "FP-2026-00008"):
\t\tcount = frappe.db.count("Timeline Event", {"farmer_project": project, "is_deleted": 0})
\t\tif count < 1:
\t\t\t\terrors.append(f"No timeline events for {project}")

\tactive_events = frappe.get_all(
\t\t"Timeline Event",
\t\tfilters={"farmer_project": "FP-2026-00007", "is_deleted": 0},
\t\tfields=["name", "event_type", "created_on"],
\t\torder_by="created_on asc",
\t)
\tprev_on = None
\tfor ev in active_events:
\t\tif prev_on and ev.created_on < prev_on:
\t\t\terrors.append("Timeline ordering broken for FP-2026-00007")
\t\tprev_on = ev.created_on

\tfeed = timeline.query(farmer_project="FP-2026-00007", limit=20)
\ttypes = {i["event_type"] for i in feed["items"]}
\tif "project_created" not in types:
\t\terrors.append("Missing project_created in feed")
\tif "stage_transition" not in types:
\t\terrors.append("Missing stage_transition in feed")

\tfarmer_feed = timeline.query(farmer="FR-00001", limit=10)
\tif not farmer_feed["items"]:
\t\terrors.append("Farmer-level query returned no items")

\t# Immutable proof
\tif active_events:
\t\trow = frappe.get_doc("Timeline Event", active_events[0].name)
\t\ttry:
\t\t\trow.payload_json = {"tamper": True}
\t\t\trow.save(ignore_permissions=True)
\t\t\terrors.append("Timeline event mutation should have failed")
\t\texcept frappe.ValidationError:
\t\t\timmutable_ok = True
\telse:
\t\timmutable_ok = False
\t\t\terrors.append("No events for immutability test")

\t# Duplicate client_id idempotency
\ttry:
\t\ttimeline.emit_manual_note(
\t\t\t"FP-2026-00007",
\t\t\t"dup test",
\t\t\tclient_id="phase9-idem-test",
\t\t)
\t\te1 = timeline.emit_manual_note(
\t\t\t"FP-2026-00007",
\t\t\t"dup test",
\t\t\tclient_id="phase9-idem-test",
\t\t)
\t\te2 = timeline.emit_manual_note(
\t\t\t"FP-2026-00007",
\t\t\t"dup test",
\t\t\tclient_id="phase9-idem-test",
\t\t)
\t\tif e1 != e2:
\t\t\terrors.append("Idempotent client_id failed")
\texcept Exception as exc:
\t\terrors.append(f"Idempotency test error: {exc}")

\tif errors:
\t\tfrappe.throw("Phase 9 verification failed: " + "; ".join(errors))

\treturn {
\t\t"ok": True,
\t\t"fp00007_event_count": len(active_events),
\t\t"fp00007_event_types": list(types),
\t\t"immutable_validation": immutable_ok,
\t\t"feed_sample": feed["items"][:3],
\t\t"farmer_feed_count": len(farmer_feed["items"]),
\t}
''',
    )


def main() -> None:
    print("Phase 9 — Timeline bootstrap")
    write_timeline_doctype()
    write_timeline_service()
    write_lifecycle_patch()
    write_farmer_project_patch()
    write_desk_patch()
    write_install_scripts()
    print("Done.")


if __name__ == "__main__":
    main()
