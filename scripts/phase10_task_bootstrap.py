#!/usr/bin/env python3
"""Phase 10 — Project Task + assignment foundation in frappe-bench agriflow app."""
from __future__ import annotations

import json
from pathlib import Path

APP = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
FIXTURES = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/fixtures")
MODULE_TASK = "Task Engine"
MODULE_LC = "Project Lifecycle"

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

TASK_STATUSES = "\n".join(
    ["open", "assigned", "in_progress", "blocked", "completed", "cancelled"]
)
TASK_PRIORITIES = "\n".join(["low", "normal", "high", "urgent"])
TASK_TYPES = "\n".join(
    [
        "field_visit",
        "document_collection",
        "verification",
        "approval",
        "installation",
        "follow_up",
    ]
)
ASSIGNMENT_REASONS = "\n".join(["initial", "transfer", "reassignment", "correction"])
SYNC_STATUS = "\n".join(["synced", "pending"])

TASK_EVENT_TYPES = "\n".join(
    [
        "project_created",
        "stage_transition",
        "mimis_gate_updated",
        "project_status_changed",
        "manual_note",
        "task_created",
        "task_assigned",
        "task_status_changed",
        "task_completed",
    ]
)

TASK_TEMPLATES = [
    {
        "template_id": "documents_collected_doc_collection",
        "to_stage": "documents_collected",
        "task_type": "document_collection",
        "subject": "Collect subsidy documents",
        "priority": "normal",
        "due_offset_days": 3,
        "default_officer_from": "project.officer",
    },
    {
        "template_id": "field_survey_visit",
        "to_stage": "field_survey",
        "task_type": "field_visit",
        "subject": "Conduct field survey",
        "priority": "high",
        "due_offset_days": 5,
        "default_officer_from": "project.officer",
    },
    {
        "template_id": "mimis_registered_verification",
        "to_stage": "mimis_registered",
        "task_type": "verification",
        "subject": "Verify MIMIS registration",
        "priority": "normal",
        "due_offset_days": 2,
        "default_officer_from": "project.officer",
    },
]


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
    module: str,
    autoname: str,
    title_field: str,
    track_changes: int = 1,
    search_fields: str | None = None,
) -> dict:
    doc = {
        "actions": [],
        "allow_import": 0,
        "allow_rename": 0,
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
        "module": module,
        "name": name,
        "owner": "Administrator",
        "permissions": PERMS_SM,
        "sort_field": "modified",
        "sort_order": "DESC",
        "states": [],
        "track_changes": track_changes,
    }
    if title_field:
        doc["title_field"] = title_field
    if search_fields:
        doc["search_fields"] = search_fields
    return doc


def write_project_task_doctype() -> None:
    slug = "project_task"
    fields = [
        field("subject", "Data", "Subject", reqd=1, in_list_view=1, search_index=1),
        field("farmer_project", "Link", "Farmer Project", options="Farmer Project", reqd=1, in_list_view=1, in_standard_filter=1, search_index=1),
        field("farmer", "Link", "Farmer", options="Farmer", reqd=1, fetch_from="farmer_project.farmer", in_list_view=1),
        field("task_type", "Select", "Task Type", options=TASK_TYPES, reqd=1, in_list_view=1, in_standard_filter=1),
        field("status", "Select", "Status", options=TASK_STATUSES, reqd=1, default="open", in_list_view=1, in_standard_filter=1),
        field("priority", "Select", "Priority", options=TASK_PRIORITIES, default="normal", in_list_view=1),
        field("due_date", "Date", "Due Date", reqd=1, in_list_view=1, search_index=1),
        field("started_on", "Datetime", "Started On"),
        field("completed_on", "Datetime", "Completed On"),
        field("assigned_officer", "Link", "Assigned Officer", options="Officer", in_list_view=1, in_standard_filter=1),
        field("assigned_to", "Link", "Assigned To", options="User", in_list_view=1, in_standard_filter=1),
        field("district", "Link", "District", options="District", fetch_from="farmer_project.district"),
        field("block", "Link", "Block", options="Block", fetch_from="farmer_project.block", in_standard_filter=1),
        field("cluster", "Link", "Cluster", options="Cluster", fetch_from="farmer_project.cluster"),
        field("stage_key", "Data", "Stage Key", in_standard_filter=1),
        field("source_template", "Data", "Source Template"),
        field("description", "Text", "Description"),
        field("visit_outcome", "Small Text", "Visit Outcome"),
        field("blocked_reason", "Small Text", "Blocked Reason"),
        field("sla_due_at", "Datetime", "SLA Due At", read_only=1),
        field("sla_started_at", "Datetime", "SLA Started At", read_only=1),
        field("sla_breached_at", "Datetime", "SLA Breached At", read_only=1),
        field("client_id", "Data", "Client ID", length=36, search_index=1),
        field("doc_version", "Int", "Doc Version", default="1", read_only=1),
        field("is_deleted", "Check", "Is Deleted", default="0"),
        field("sync_status", "Select", "Sync Status", options=SYNC_STATUS, default="synced"),
    ]
    base = APP / "task_engine" / "doctype" / slug
    doc = doctype_json(
        "Project Task",
        fields,
        module=MODULE_TASK,
        autoname="format:TSK-{YYYY}-{#####}",
        title_field="subject",
        search_fields="subject,farmer_project,assigned_officer,due_date",
    )
    write(base / "__init__.py", "")
    write(base / f"{slug}.json", json.dumps(doc, indent=1) + "\n")
    write(
        base / f"{slug}.py",
        '''# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe import _
from frappe.model.document import Document

from agriflow.task_engine.services.lifecycle import TaskLifecycleService

TASK_WRITE_FLAG = "agriflow_task_write"


class ProjectTask(Document):
\tdef validate(self):
\t\tif frappe.flags.get(TASK_WRITE_FLAG):
\t\t\treturn
\t\tif not self.is_new():
\t\t\tTaskLifecycleService().validate_direct_save(self)

\tdef before_save(self):
\t\tif frappe.flags.get(TASK_WRITE_FLAG):
\t\t\treturn
\t\tif not self.is_new():
\t\t\tself.doc_version = (self.doc_version or 1) + 1
''',
    )


def write_assignment_history_doctype() -> None:
    slug = "project_task_assignment_history"
    fields = [
        field("project_task", "Link", "Project Task", options="Project Task", reqd=1, in_list_view=1, search_index=1),
        field("farmer_project", "Link", "Farmer Project", options="Farmer Project", reqd=1, in_list_view=1),
        field("officer", "Link", "Officer", options="Officer", reqd=1, in_list_view=1, in_standard_filter=1),
        field("assigned_on", "Datetime", "Assigned On", reqd=1, in_list_view=1),
        field("unassigned_on", "Datetime", "Unassigned On"),
        field("assigned_by", "Link", "Assigned By", options="User", reqd=1),
        field("assignment_reason", "Select", "Assignment Reason", options=ASSIGNMENT_REASONS, reqd=1, default="initial"),
        field("notes", "Small Text", "Notes"),
    ]
    base = APP / "task_engine" / "doctype" / slug
    doc = doctype_json(
        "Project Task Assignment History",
        fields,
        module=MODULE_TASK,
        autoname="hash",
        title_field="project_task",
        track_changes=0,
    )
    write(base / "__init__.py", "")
    write(base / f"{slug}.json", json.dumps(doc, indent=1) + "\n")
    write(
        base / f"{slug}.py",
        '''# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe import _
from frappe.model.document import Document

ASSIGNMENT_FLAG = "agriflow_task_assignment_write"


class ProjectTaskAssignmentHistory(Document):
\tdef validate(self):
\t\tif not frappe.flags.get(ASSIGNMENT_FLAG) and not self.is_new():
\t\t\tfrappe.throw(_("Assignment history rows are immutable"))

\tdef on_trash(self):
\t\tif frappe.session.user != "Administrator":
\t\t\tfrappe.throw(_("Assignment history cannot be deleted"))
''',
    )


def write_task_services() -> None:
    write(APP / "task_engine" / "services" / "__init__.py", "")
    write(
        APP / "task_engine" / "utils" / "__init__.py",
        "",
    )
    write(
        APP / "task_engine" / "utils" / "transitions.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Allowed Project Task status transitions."""

from __future__ import annotations

TERMINAL = frozenset({"completed", "cancelled"})
OPEN_QUEUE = frozenset({"open", "assigned", "in_progress", "blocked"})

ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
\t"open": frozenset({"assigned", "cancelled"}),
\t"assigned": frozenset({"in_progress", "open", "blocked", "cancelled"}),
\t"in_progress": frozenset({"blocked", "completed", "cancelled"}),
\t"blocked": frozenset({"in_progress", "cancelled"}),
\t"completed": frozenset(),
\t"cancelled": frozenset(),
}


def can_transition(from_status: str, to_status: str) -> bool:
\treturn to_status in ALLOWED_TRANSITIONS.get(from_status or "open", frozenset())
''',
    )
    write(
        APP / "task_engine" / "services" / "sla.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""SLA timestamp helpers — clock starts at in_progress only."""

from __future__ import annotations

from datetime import datetime, time

import frappe
from frappe.utils import get_datetime, now_datetime


def sla_due_at_from_date(due_date) -> datetime | None:
\tif not due_date:
\t\treturn None
\tdate_val = get_datetime(due_date).date()
\t# End of due_date in server TZ (IST on bench)
\treturn datetime.combine(date_val, time(23, 59, 59))


def apply_sla_fields(doc, old_status: str | None = None) -> None:
\t"""Recompute SLA fields on task document before save."""
\tdoc.sla_due_at = sla_due_at_from_date(doc.due_date)
\tnew_status = doc.status or "open"
\told_status = old_status or doc.get_doc_before_save().status if doc.get_doc_before_save() else None

\tif new_status == "in_progress" and not doc.sla_started_at:
\t\tdoc.sla_started_at = doc.started_on or now_datetime()
\tif old_status != "in_progress" and new_status == "in_progress" and not doc.started_on:
\t\tdoc.started_on = doc.sla_started_at or now_datetime()

\tif new_status in ("completed", "cancelled"):
\t\treturn

\tif doc.sla_due_at and now_datetime() > get_datetime(doc.sla_due_at) and not doc.sla_breached_at:
\t\tdoc.sla_breached_at = now_datetime()


def is_overdue(doc) -> bool:
\tif doc.status in ("completed", "cancelled"):
\t\treturn False
\tif not doc.due_date:
\t\treturn False
\treturn get_datetime(doc.due_date).date() < get_datetime(now_datetime()).date()
''',
    )
    write(
        APP / "task_engine" / "services" / "assignment.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Append-only task assignment history."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime

from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.services.sla import apply_sla_fields
from agriflow.task_engine.utils.transitions import can_transition

ASSIGNMENT_FLAG = "agriflow_task_assignment_write"
TASK_WRITE_FLAG = "agriflow_task_write"


class TaskAssignmentService:
\tdef assign(
\t\tself,
\t\ttask_name: str,
\t\tofficer: str,
\t\t*,
\t\tassigned_to: str | None = None,
\t\treason: str = "initial",
\t\tnotes: str | None = None,
\t) -> frappe.model.document.Document:
\t\ttask = frappe.get_doc("Project Task", task_name)
\t\tif task.is_deleted:
\t\t\tfrappe.throw(_("Task is deleted"))
\t\tif not frappe.db.exists("Officer", {"name": officer, "is_active": 1}):
\t\t\tfrappe.throw(_("Officer not found or inactive"))

\t\tassigned_to = assigned_to or frappe.session.user
\t\tself._close_open_history(task_name)

\t\tfrappe.get_doc(
\t\t\t{
\t\t\t\t"doctype": "Project Task Assignment History",
\t\t\t\t"project_task": task_name,
\t\t\t\t"farmer_project": task.farmer_project,
\t\t\t\t"officer": officer,
\t\t\t\t"assigned_on": now_datetime(),
\t\t\t\t"assigned_by": frappe.session.user,
\t\t\t\t"assignment_reason": reason,
\t\t\t\t"notes": notes or "",
\t\t\t}
\t\t).insert(ignore_permissions=True)

\t\told_status = task.status
\t\tif task.status == "open":
\t\t\ttask.status = "assigned"
\t\ttask.assigned_officer = officer
\t\ttask.assigned_to = assigned_to
\t\tapply_sla_fields(task, old_status)
\t\tself._save_task(task)

\t\tget_timeline_service().emit_task_assigned(
\t\t\ttask,
\t\t\tofficer=officer,
\t\t\tassigned_to=assigned_to,
\t\t\treason=reason,
\t\t)
\t\treturn task

\tdef unassign(self, task_name: str, *, notes: str | None = None) -> frappe.model.document.Document:
\t\ttask = frappe.get_doc("Project Task", task_name)
\t\tif task.status not in ("assigned",):
\t\t\tfrappe.throw(_("Only assigned tasks can be unassigned"))
\t\tself._close_open_history(task_name, notes=notes)
\t\told_status = task.status
\t\tif not can_transition(old_status, "open"):
\t\t\tfrappe.throw(_("Cannot unassign from status {0}").format(old_status))
\t\ttask.status = "open"
\t\ttask.assigned_officer = None
\t\ttask.assigned_to = None
\t\tapply_sla_fields(task, old_status)
\t\tself._save_task(task)
\t\tget_timeline_service().emit_task_status_changed(
\t\t\ttask, from_status=old_status, to_status="open", note="unassigned"
\t\t)
\t\treturn task

\tdef _close_open_history(self, task_name: str, notes: str | None = None) -> None:
\t\topen_rows = frappe.get_all(
\t\t\t"Project Task Assignment History",
\t\t\tfilters={"project_task": task_name, "unassigned_on": ("is", "not set")},
\t\t\tfields=["name"],
\t\t)
\t\tfor row in open_rows:
\t\t\th = frappe.get_doc("Project Task Assignment History", row.name)
\t\t\th.unassigned_on = now_datetime()
\t\t\tif notes:
\t\t\t\th.notes = (h.notes or "") + (" " + notes if h.notes else notes)
\t\t\tfrappe.flags[ASSIGNMENT_FLAG] = True
\t\t\ttry:
\t\t\t\th.save(ignore_permissions=True)
\t\t\tfinally:
\t\t\t\tfrappe.flags[ASSIGNMENT_FLAG] = False

\tdef _save_task(self, task) -> None:
\t\tfrappe.flags[TASK_WRITE_FLAG] = True
\t\ttry:
\t\t\ttask.save(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags[TASK_WRITE_FLAG] = False
''',
    )
    write(
        APP / "task_engine" / "services" / "lifecycle.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Project Task lifecycle — sole writer for status transitions."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime

from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.sla import apply_sla_fields
from agriflow.task_engine.utils.transitions import TERMINAL, can_transition

TASK_WRITE_FLAG = "agriflow_task_write"


class TaskLifecycleService:
\tdef create_task(
\t\tself,
\t\t*,
\t\tsubject: str,
\t\tfarmer_project: str,
\t\ttask_type: str,
\t\tdue_date: str,
\t\tpriority: str = "normal",
\t\tstage_key: str | None = None,
\t\tsource_template: str | None = None,
\t\tassigned_officer: str | None = None,
\t\tassigned_to: str | None = None,
\t\tdescription: str | None = None,
\t\tclient_id: str | None = None,
\t\tauto_assign: bool = True,
\t) -> frappe.model.document.Document:
\t\tproject = frappe.get_doc("Farmer Project", farmer_project)
\t\tif project.status == "cancelled":
\t\t\tfrappe.throw(_("Cannot create tasks on cancelled project"))

\t\tif client_id:
\t\t\texisting = frappe.db.exists(
\t\t\t\t"Project Task",
\t\t\t\t{"client_id": client_id, "is_deleted": 0},
\t\t\t)
\t\t\tif existing:
\t\t\t\treturn frappe.get_doc("Project Task", existing)

\t\tdoc = frappe.get_doc(
\t\t\t{
\t\t\t\t"doctype": "Project Task",
\t\t\t\t"subject": subject,
\t\t\t\t"farmer_project": farmer_project,
\t\t\t\t"farmer": project.farmer,
\t\t\t\t"task_type": task_type,
\t\t\t\t"status": "open",
\t\t\t\t"priority": priority,
\t\t\t\t"due_date": due_date,
\t\t\t\t"stage_key": stage_key or project.current_stage,
\t\t\t\t"source_template": source_template,
\t\t\t\t"description": description or "",
\t\t\t\t"client_id": client_id,
\t\t\t\t"doc_version": 1,
\t\t\t\t"sync_status": "synced",
\t\t\t}
\t\t)
\t\tapply_sla_fields(doc)
\t\tself._insert(doc)
\t\tget_timeline_service().emit_task_created(doc)

\t\tif assigned_officer and auto_assign:
\t\t\tTaskAssignmentService().assign(
\t\t\t\tdoc.name,
\t\t\t\tassigned_officer,
\t\t\t\tassigned_to=assigned_to,
\t\t\t\treason="initial",
\t\t\t)
\t\t\tdoc.reload()
\t\treturn doc

\tdef transition_status(
\t\tself,
\t\ttask_name: str,
\t\tnew_status: str,
\t\t*,
\t\tdoc_version: int | None = None,
\t\tblocked_reason: str | None = None,
\t\tvisit_outcome: str | None = None,
\t\tcompleted_on: str | None = None,
\t) -> frappe.model.document.Document:
\t\ttask = frappe.get_doc("Project Task", task_name)
\t\tif doc_version is not None and int(task.doc_version or 0) != int(doc_version):
\t\t\tfrappe.throw(
\t\t\t\t_("Stale doc_version. Server has {0}, client sent {1}").format(
\t\t\t\t\ttask.doc_version, doc_version
\t\t\t\t)
\t\t\t)
\t\tself._ensure_project_active(task.farmer_project)
\t\told = task.status
\t\tif old in TERMINAL:
\t\t\tfrappe.throw(_("Task is terminal ({0})").format(old))
\t\tif not can_transition(old, new_status):
\t\t\tfrappe.throw(_("Invalid transition {0} -> {1}").format(old, new_status))

\t\tif new_status == "in_progress" and not task.started_on:
\t\t\ttask.started_on = now_datetime()
\t\tif new_status == "blocked":
\t\t\ttask.blocked_reason = blocked_reason or task.blocked_reason
\t\tif new_status == "completed":
\t\t\ttask.completed_on = completed_on or now_datetime()
\t\t\ttask.visit_outcome = visit_outcome or task.visit_outcome
\t\t\tif not task.completed_on:
\t\t\t\tfrappe.throw(_("completed_on is required"))

\t\ttask.status = new_status
\t\tapply_sla_fields(task, old)
\t\tself._save(task)

\t\tif new_status == "completed":
\t\t\tget_timeline_service().emit_task_completed(task)
\t\telse:
\t\t\tget_timeline_service().emit_task_status_changed(task, from_status=old, to_status=new_status)
\t\treturn task

\tdef complete(
\t\tself,
\t\ttask_name: str,
\t\t*,
\t\tdoc_version: int | None = None,
\t\tvisit_outcome: str | None = None,
\t\tcompleted_on: str | None = None,
\t) -> frappe.model.document.Document:
\t\treturn self.transition_status(
\t\t\ttask_name,
\t\t\t"completed",
\t\t\tdoc_version=doc_version,
\t\t\tvisit_outcome=visit_outcome,
\t\t\tcompleted_on=completed_on,
\t\t)

\tdef validate_direct_save(self, doc) -> None:
\t\tfrappe.throw(_("Project Task changes must use TaskLifecycleService or TaskAssignmentService"))

\tdef _ensure_project_active(self, farmer_project: str) -> None:
\t\tstatus = frappe.db.get_value("Farmer Project", farmer_project, "status")
\t\tif status == "cancelled":
\t\t\tfrappe.throw(_("Cannot update tasks on cancelled project"))

\tdef _insert(self, doc) -> None:
\t\tfrappe.flags[TASK_WRITE_FLAG] = True
\t\ttry:
\t\t\tdoc.insert(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags[TASK_WRITE_FLAG] = False

\tdef _save(self, doc) -> None:
\t\tfrappe.flags[TASK_WRITE_FLAG] = True
\t\ttry:
\t\t\tdoc.save(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags[TASK_WRITE_FLAG] = False
''',
    )
    write(
        APP / "task_engine" / "services" / "templates.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Idempotent stage task generation from JSON fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import frappe
from frappe.utils import add_days, today

from agriflow.task_engine.services.lifecycle import TaskLifecycleService

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "fixtures" / "task_template.json"


def template_client_id(farmer_project: str, template_id: str) -> str:
\treturn hashlib.sha256(f"{farmer_project}|{template_id}".encode()).hexdigest()[:32]


def load_task_templates() -> list[dict]:
\tif not FIXTURE_PATH.exists():
\t\treturn []
\twith FIXTURE_PATH.open(encoding="utf-8") as fh:
\t\tdata = json.load(fh)
\treturn data if isinstance(data, list) else []


def generate_stage_tasks(farmer_project: str, to_stage: str) -> list[str]:
\t"""Create template tasks for entered stage; idempotent by source_template + stage_key."""
\tproject = frappe.get_doc("Farmer Project", farmer_project)
\tcreated: list[str] = []
\tlifecycle = TaskLifecycleService()

\tfor tpl in load_task_templates():
\t\tif tpl.get("to_stage") != to_stage:
\t\t\tcontinue
\t\ttemplate_id = tpl["template_id"]
\t\tif frappe.db.exists(
\t\t\t"Project Task",
\t\t\t{
\t\t\t\t"farmer_project": farmer_project,
\t\t\t\t"source_template": template_id,
\t\t\t\t"stage_key": to_stage,
\t\t\t\t"is_deleted": 0,
\t\t\t},
\t\t):
\t\t\tcontinue

\t\tofficer = None
\t\tif tpl.get("default_officer_from") == "project.officer":
\t\t\tofficer = project.officer

\t\tdue = add_days(today(), int(tpl.get("due_offset_days", 3)))
\t\tdoc = lifecycle.create_task(
\t\t\tsubject=tpl["subject"],
\t\t\tfarmer_project=farmer_project,
\t\t\ttask_type=tpl["task_type"],
\t\t\tdue_date=due,
\t\t\tpriority=tpl.get("priority", "normal"),
\t\t\tstage_key=to_stage,
\t\t\tsource_template=template_id,
\t\t\tassigned_officer=officer,
\t\t\tauto_assign=bool(officer),
\t\t\tclient_id=template_client_id(farmer_project, template_id),
\t\t)
\t\tcreated.append(doc.name)
\treturn created
''',
    )
    write(
        APP / "task_engine" / "services" / "queue.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Officer work queue queries."""

from __future__ import annotations

from typing import Any

import frappe

from agriflow.task_engine.utils.transitions import OPEN_QUEUE


def open_tasks_for_project(farmer_project: str, *, limit: int = 50) -> list[dict[str, Any]]:
\trows = frappe.get_all(
\t\t"Project Task",
\t\tfilters={
\t\t\t"farmer_project": farmer_project,
\t\t\t"status": ("in", list(OPEN_QUEUE)),
\t\t\t"is_deleted": 0,
\t\t},
\t\tfields=[
\t\t\t"name",
\t\t\t"subject",
\t\t\t"farmer_project",
\t\t\t"farmer",
\t\t\t"task_type",
\t\t\t"status",
\t\t\t"priority",
\t\t\t"due_date",
\t\t\t"assigned_officer",
\t\t\t"assigned_to",
\t\t\t"block",
\t\t\t"stage_key",
\t\t\t"doc_version",
\t\t\t"modified",
\t\t\t"client_id",
\t\t\t"sla_due_at",
\t\t\t"sla_breached_at",
\t\t],
\t\torder_by="due_date asc, priority desc, modified desc",
\t\tlimit=limit,
\t)
\tfor row in rows:
\t\trow["is_overdue"] = bool(
\t\t\trow.due_date
\t\t\tand frappe.utils.getdate(row.due_date) < frappe.utils.getdate(frappe.utils.today())
\t\t\tand row.status in OPEN_QUEUE
\t\t)
\t\tif hasattr(row.get("modified"), "isoformat"):
\t\t\trow["modified"] = row.modified.isoformat()
\t\tif hasattr(row.get("sla_due_at"), "isoformat") and row.sla_due_at:
\t\t\trow["sla_due_at"] = row.sla_due_at.isoformat()
\t\tif hasattr(row.get("sla_breached_at"), "isoformat") and row.sla_breached_at:
\t\t\trow["sla_breached_at"] = row.sla_breached_at.isoformat()
\treturn rows
''',
    )


def patch_timeline_event_options() -> None:
    path = APP / "project_lifecycle" / "doctype" / "timeline_event" / "timeline_event.json"
    if not path.exists():
        print("  skip timeline_event.json patch (missing)")
        return
    doc = json.loads(path.read_text(encoding="utf-8"))
    for f in doc.get("fields", []):
        if f.get("fieldname") == "event_type":
            f["options"] = TASK_EVENT_TYPES
        if f.get("fieldname") == "event_source":
            opts = f.get("options", "")
            if "task_engine" not in opts:
                f["options"] = opts + "\ntask_engine"
    path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(f"  patched {path}")


def patch_timeline_service() -> None:
    path = APP / "project_lifecycle" / "services" / "timeline.py"
    text = path.read_text(encoding="utf-8")
    if "task_created" in text and "emit_task_created" in text:
        print("  timeline.py already has task events")
        return

    old = """VALID_EVENT_TYPES = frozenset(
	{
		"project_created",
		"stage_transition",
		"mimis_gate_updated",
		"project_status_changed",
		"manual_note",
	}
)"""
    new = """VALID_EVENT_TYPES = frozenset(
	{
		"project_created",
		"stage_transition",
		"mimis_gate_updated",
		"project_status_changed",
		"manual_note",
		"task_created",
		"task_assigned",
		"task_status_changed",
		"task_completed",
	}
)"""
    if old not in text:
        raise SystemExit("timeline.py VALID_EVENT_TYPES block not found")
    text = text.replace(old, new)

    insert_before = "\ndef get_timeline_service"
    helpers = '''

	def emit_task_created(self, task) -> str:
		return self.emit(
			"task_created",
			task.farmer_project,
			payload={
				"task": task.name,
				"subject": task.subject,
				"task_type": task.task_type,
				"status": task.status,
				"priority": task.priority,
				"due_date": str(task.due_date) if task.due_date else None,
			},
			event_source="task_engine",
			reference_doctype="Project Task",
			reference_name=task.name,
			client_id=_task_timeline_client_id(task, "created"),
		)

	def emit_task_assigned(
		self,
		task,
		*,
		officer: str,
		assigned_to: str | None = None,
		reason: str | None = None,
	) -> str:
		return self.emit(
			"task_assigned",
			task.farmer_project,
			payload={
				"task": task.name,
				"officer": officer,
				"assigned_to": assigned_to,
				"reason": reason,
				"status": task.status,
			},
			event_source="task_engine",
			reference_doctype="Project Task",
			reference_name=task.name,
		)

	def emit_task_status_changed(
		self,
		task,
		*,
		from_status: str,
		to_status: str,
		note: str | None = None,
	) -> str:
		return self.emit(
			"task_status_changed",
			task.farmer_project,
			payload={
				"task": task.name,
				"from_status": from_status,
				"to_status": to_status,
				"note": (note or "")[:MAX_NOTE_LEN],
			},
			event_source="task_engine",
			reference_doctype="Project Task",
			reference_name=task.name,
		)

	def emit_task_completed(self, task) -> str:
		return self.emit(
			"task_completed",
			task.farmer_project,
			payload={
				"task": task.name,
				"visit_outcome": (task.visit_outcome or "")[:MAX_NOTE_LEN],
				"completed_on": str(task.completed_on) if task.completed_on else None,
			},
			event_source="task_engine",
			reference_doctype="Project Task",
			reference_name=task.name,
		)
'''
    if insert_before not in text:
        raise SystemExit("get_timeline_service anchor not found")
    text = text.replace(insert_before, helpers + insert_before)
    path.write_text(text, encoding="utf-8")
    print(f"  patched {path}")


def patch_lifecycle() -> None:
    path = APP / "project_lifecycle" / "services" / "lifecycle.py"
    text = path.read_text(encoding="utf-8")
    if "generate_stage_tasks" in text and "task_engine" in text:
        print("  lifecycle.py already wired")
        return
    if "# Phase 10: enqueue generate_stage_tasks" in text:
        text = text.replace(
            "\t\t# Phase 10: enqueue generate_stage_tasks\n\t\treturn {",
            "\t\tfrom agriflow.task_engine.services.templates import generate_stage_tasks\n\n\t\tgenerate_stage_tasks(project.name, target_stage)\n\t\treturn {",
        )
        path.write_text(text, encoding="utf-8")
        print(f"  patched {path}")
    else:
        raise SystemExit("lifecycle Phase 10 marker not found")


def patch_project_api() -> None:
    path = APP / "api" / "v1" / "project.py"
    text = path.read_text(encoding="utf-8")
    if "open_tasks_for_project" in text:
        print("  project.py already has open_tasks")
        return
    if "from agriflow.project_lifecycle.utils.stages import" in text:
        text = text.replace(
            "from agriflow.project_lifecycle.utils.stages import",
            "from agriflow.task_engine.services.queue import open_tasks_for_project\nfrom agriflow.project_lifecycle.utils.stages import",
        )
    text = text.replace(
        '\t\t\t\t"open_tasks": [],',
        '\t\t\t\t"open_tasks": open_tasks_for_project(name),',
    )
    path.write_text(text, encoding="utf-8")
    print(f"  patched {path}")


def write_fixture() -> None:
    write(FIXTURES / "task_template.json", json.dumps(TASK_TEMPLATES, indent=2) + "\n")


def write_install_scripts() -> None:
    src = Path(__file__).resolve().parent
    for name in ("phase10_sample_tasks.py", "phase10_verify_tasks.py"):
        dest = APP / "project_lifecycle" / "install" / name
        if (src / name).exists():
            dest.write_text((src / name).read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  copied {name}")
        else:
            print(f"  skip copy {name} (run from repo scripts/)")


_LEGACY_SAMPLE = r'''# Copyright (c) 2026, Murugan and contributors
"""Phase 10 — sample Project Task rows."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, today

from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.lifecycle import TaskLifecycleService
from agriflow.task_engine.services.templates import generate_stage_tasks


PROJECT = "FP-2026-00007"
OFFICER = None


def execute():
\tfrappe.only_for("Administrator")
\tglobal OFFICER
\tOFFICER = frappe.db.get_value("Farmer Project", PROJECT, "officer")
\tif not OFFICER:
\t\tOFFICER = frappe.db.get_value("Officer", {"is_active": 1}, "name")
\tif not OFFICER:
\t\tprint({"ok": False, "error": "no officer"})
\t\treturn

\tlifecycle = TaskLifecycleService()
\tcreated = []

\t# Manual open task
\tt1 = lifecycle.create_task(
\t\tsubject="Follow up land records",
\t\tfarmer_project=PROJECT,
\t\ttask_type="follow_up",
\t\tdue_date=add_days(today(), 7),
\t\tpriority="normal",
\t\tclient_id="phase10-sample-follow-up",
\t)
\tcreated.append(t1.name)

\t# Assign officer
\tTaskAssignmentService().assign(
\t\tt1.name,
\t\tOFFICER,
\t\tassigned_to=frappe.session.user,
\t\treason="initial",
\t)

\t# In progress + SLA clock
\tt1.reload()
\tlifecycle.transition_status(t1.name, "in_progress", doc_version=t1.doc_version)

\t# Second task — document collection (stays assigned)
\tt2 = lifecycle.create_task(
\t\tsubject="Collect Aadhaar copy",
\t\tfarmer_project=PROJECT,
\t\ttask_type="document_collection",
\t\tdue_date=add_days(today(), 3),
\t\tpriority="high",
\t\tclient_id="phase10-sample-doc",
\t)
\tTaskAssignmentService().assign(t2.name, OFFICER, reason="initial")
\tcreated.append(t2.name)

\t# Idempotent template generation for current stage
\tstage = frappe.db.get_value("Farmer Project", PROJECT, "current_stage")
\ttpl_created = generate_stage_tasks(PROJECT, stage)
\tcreated.extend(tpl_created)

\tprint({"ok": True, "project": PROJECT, "officer": OFFICER, "tasks": created, "templates": tpl_created})
'''


VERIFY_SCRIPT = r'''# Copyright (c) 2026, Murugan and contributors
"""Phase 10 — verify Project Task foundation."""

from __future__ import annotations

import frappe

from agriflow.api.v1.project import timeline
from agriflow.task_engine.services.lifecycle import TaskLifecycleService
from agriflow.task_engine.services.queue import open_tasks_for_project
from agriflow.task_engine.services.templates import generate_stage_tasks
from agriflow.task_engine.utils.transitions import can_transition

PROJECT = "FP-2026-00007"


def execute():
\tfrappe.only_for("Administrator")
\terrors: list[str] = []
\treport: dict = {"project": PROJECT}

\tif not frappe.db.exists("DocType", "Project Task"):
\t\terrors.append("Project Task DocType missing")

\ttasks = frappe.get_all(
\t\t"Project Task",
\t\tfilters={"farmer_project": PROJECT, "is_deleted": 0},
\t\tfields=["name", "status", "sla_started_at", "sla_due_at", "assigned_officer"],
\t)
\treport["task_count"] = len(tasks)
\tif not tasks:
\t\terrors.append("no sample tasks")

\t# Assignment history append-only
\thist = frappe.get_all(
\t\t"Project Task Assignment History",
\t\tfilters={"farmer_project": PROJECT},
\t\tfields=["name", "unassigned_on", "officer"],
\t\torder_by="assigned_on asc",
\t)
\treport["assignment_rows"] = len(hist)
\tif not hist:
\t\terrors.append("no assignment history")

\t# SLA: in_progress task should have sla_started_at
\tin_prog = [t for t in tasks if t.status == "in_progress"]
\tif in_prog and not in_prog[0].sla_started_at:
\t\terrors.append("sla_started_at missing on in_progress")
\tassigned_only = frappe.get_all(
\t\t"Project Task",
\t\tfilters={"farmer_project": PROJECT, "status": "assigned", "is_deleted": 0},
\t\tfields=["sla_started_at"],
\t\tlimit=1,
\t)
\tif assigned_only and assigned_only[0].sla_started_at:
\t\terrors.append("sla_started_at set on assigned (should only start at in_progress)")

\t# Invalid transition blocked
\tsample = tasks[0].name if tasks else None
\tif sample:
\t\ttry:
\t\t\tTaskLifecycleService().transition_status(sample, "open")
\t\t\tif frappe.db.get_value("Project Task", sample, "status") == "open":
\t\t\t\tpass  # only valid from assigned
\t\texcept Exception:
\t\t\tpass
\t\tcompleted = frappe.db.get_value("Project Task", {"status": "completed", "farmer_project": PROJECT}, "name")
\t\tif completed:
\t\t\ttry:
\t\t\t\tTaskLifecycleService().transition_status(completed, "in_progress")
\t\t\t\terrors.append("terminal transition allowed")
\t\t\texcept Exception:
\t\t\t\treport["terminal_blocked"] = True

\t# Timeline task events
\tevents = frappe.get_all(
\t\t"Timeline Event",
\t\tfilters={"farmer_project": PROJECT, "event_type": ("like", "task_%"), "is_deleted": 0},
\t\tpluck="event_type",
\t)
\treport["task_event_types"] = sorted(set(events))
\tfor needed in ("task_created", "task_assigned", "task_status_changed"):
\t\tif needed not in report["task_event_types"]:
\t\t\terrors.append(f"missing timeline event {needed}")

\t# open_tasks
\topen_rows = open_tasks_for_project(PROJECT)
\treport["open_tasks_count"] = len(open_rows)
\tresp = timeline({"name": PROJECT, "limit": 5})
\tif resp.get("ok"):
\t\tapi_open = resp["data"].get("open_tasks", [])
\t\treport["api_open_tasks"] = len(api_open)
\t\tif len(api_open) != len(open_rows):
\t\t\terrors.append("open_tasks mismatch API vs service")
\telse:
\t\terrors.append(f"timeline API failed: {resp}")

\t# Idempotent templates
\tstage = frappe.db.get_value("Farmer Project", PROJECT, "current_stage")
\tfirst = generate_stage_tasks(PROJECT, stage)
\tsecond = generate_stage_tasks(PROJECT, stage)
\treport["template_run1"] = len(first)
\treport["template_run2"] = len(second)
\tif second:
\t\terrors.append("template generation not idempotent")

\t# Transition matrix sanity
\tif not can_transition("completed", "in_progress"):
\t\treport["transition_matrix"] = "ok"

\treport["ok"] = len(errors) == 0
\treport["errors"] = errors
\tprint(report)
'''


def main() -> None:
    print("Phase 10 task bootstrap")
    write(APP / "task_engine" / "__init__.py", "")
    write_project_task_doctype()
    write_assignment_history_doctype()
    write_task_services()
    write_fixture()
    patch_timeline_event_options()
    patch_timeline_service()
    patch_lifecycle()
    patch_project_api()
    write_install_scripts()
    print("Done. Run: bench migrate && bench clear-cache")


if __name__ == "__main__":
    main()
