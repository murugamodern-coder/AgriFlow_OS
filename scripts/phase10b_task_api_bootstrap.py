#!/usr/bin/env python3
"""Phase 10b — Task API layer bootstrap for frappe-bench agriflow."""
from __future__ import annotations

from pathlib import Path

APP = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
CONTRACTS = Path(
    "/mnt/c/Users/murug/OneDrive/Desktop/DOCUMENT/Projects/AgriFlow_OS/API_CONTRACTS.md"
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(APP.parent)}")


def patch_lifecycle_complete() -> None:
    path = APP / "task_engine" / "services" / "lifecycle.py"
    text = path.read_text(encoding="utf-8")
    old = '''\tdef complete(
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
\t\t)'''
    new = '''\tdef complete(
\t\tself,
\t\ttask_name: str,
\t\t*,
\t\tdoc_version: int | None = None,
\t\tvisit_outcome: str | None = None,
\t\tcompleted_on: str | None = None,
\t) -> frappe.model.document.Document:
\t\t"""Complete from in_progress, or auto-step assigned → in_progress → completed."""
\t\ttask = frappe.get_doc("Project Task", task_name)
\t\tif doc_version is not None and int(task.doc_version or 0) != int(doc_version):
\t\t\tfrappe.throw(
\t\t\t\t_("Stale doc_version. Server has {0}, client sent {1}").format(
\t\t\t\t\ttask.doc_version, doc_version
\t\t\t\t)
\t\t\t)
\t\tif task.status == "assigned":
\t\t\ttask = self.transition_status(
\t\t\t\ttask_name,
\t\t\t\t"in_progress",
\t\t\t\tdoc_version=task.doc_version,
\t\t\t)
\t\t\treturn self.transition_status(
\t\t\t\ttask_name,
\t\t\t\t"completed",
\t\t\t\tdoc_version=task.doc_version,
\t\t\t\tvisit_outcome=visit_outcome,
\t\t\t\tcompleted_on=completed_on,
\t\t\t)
\t\tif task.status not in ("in_progress",):
\t\t\tfrappe.throw(_("Cannot complete task in status {0}").format(task.status))
\t\treturn self.transition_status(
\t\t\ttask_name,
\t\t\t"completed",
\t\t\tdoc_version=doc_version if doc_version is not None else task.doc_version,
\t\t\tvisit_outcome=visit_outcome,
\t\t\tcompleted_on=completed_on,
\t\t)'''
    if old not in text:
        raise SystemExit("lifecycle.complete block not found")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("  patched lifecycle.complete")

    insert_method = '''
\tdef update_description(
\t\tself,
\t\ttask_name: str,
\t\t*,
\t\tdoc_version: int,
\t\tdescription: str,
\t) -> frappe.model.document.Document:
\t\ttask = frappe.get_doc("Project Task", task_name)
\t\tif int(task.doc_version or 0) != int(doc_version):
\t\t\tfrappe.throw(
\t\t\t\t_("Stale doc_version. Server has {0}, client sent {1}").format(
\t\t\t\t\ttask.doc_version, doc_version
\t\t\t\t)
\t\t\t)
\t\tself._ensure_project_active(task.farmer_project)
\t\ttask.description = description
\t\tself._save(task)
\t\treturn task

'''
    text = path.read_text(encoding="utf-8")
    if "def update_description" not in text:
        anchor = "\tdef validate_direct_save"
        text = text.replace(anchor, insert_method + anchor)
        path.write_text(text, encoding="utf-8")
        print("  patched lifecycle.update_description")


def main() -> None:
    print("Phase 10b task API bootstrap")
    write(APP / "task_engine" / "api" / "__init__.py", "")
    write(APP / "task_engine" / "api" / "serializers.py", SERIALIZERS)
    qraw = (Path(__file__).resolve().parent / "phase10b_query.py").read_text(encoding="utf-8")
    write(APP / "task_engine" / "services" / "query.py", qraw.split("CONTENT = '''", 1)[1].rsplit("'''", 1)[0])
    write(APP / "api" / "v1" / "errors.py", ERRORS)
    write(APP / "api" / "v1" / "permissions.py", PERMISSIONS)
    write(APP / "api" / "v1" / "task.py", TASK_API)
    patch_lifecycle_complete()
    src = Path(__file__).resolve().parent
    for name in ("phase10b_verify_task_api.py",):
        if (src / name).exists():
            write(
                APP / "project_lifecycle" / "install" / name,
                (src / name).read_text(encoding="utf-8"),
            )
    patch_api_contracts()
    print("Done. Run: bench clear-cache && phase10b_verify_task_api.execute")


def patch_api_contracts() -> None:
    if not CONTRACTS.exists():
        print("  skip API_CONTRACTS patch (path missing)")
        return
    text = CONTRACTS.read_text(encoding="utf-8")
    marker = "## 16. Task API contracts"
    if "assigned_officer" in text and "due_before" in text and marker in text:
        # patch §16 body if minimal
        old_snippet = '"due_date_lte": "2026-05-25",'
        if old_snippet in text and "due_before" not in text.split(marker)[1][:2500]:
            pass
    insert = '''
**Phase 10b updates:** Filters `assigned_officer`, `priority`, `due_before` (alias `due_date_lte`). TaskSummary includes `assigned_officer`, `is_overdue`, `sla`. `task.get` returns `assignment_history`, `timeline_preview`, `sla`, `allowed_transitions`. Priority `medium` accepted as alias for `normal`. `task.complete` supports `assigned` with internal auto-step to `in_progress`.

'''
    if "**Phase 10b updates:**" not in text and marker in text:
        text = text.replace(marker, marker + insert)
        CONTRACTS.write_text(text, encoding="utf-8")
        print("  patched API_CONTRACTS.md")


ERRORS = '''# Copyright (c) 2026, Murugan and contributors
"""API error codes — API_CONTRACTS §6."""

from __future__ import annotations

import frappe
from frappe import _

from agriflow.api.v1.response import fail

NOT_FOUND = "NOT_FOUND"
PERM_DENIED = "PERM_DENIED"
VAL_INVALID = "VAL_INVALID"
VAL_INVALID_CURSOR = "VAL_INVALID_CURSOR"
VAL_REQUIRED_FIELD = "VAL_REQUIRED_FIELD"
SYNC_CONFLICT_LWW = "SYNC_CONFLICT_LWW"


def throw_not_found(message: str = "Resource not found"):
	frappe.throw(message, exc=frappe.DoesNotExistError)


def throw_perm(message: str = "Permission denied"):
	frappe.throw(message, exc=frappe.PermissionError)


def throw_validation(message: str):
	frappe.throw(message, exc=frappe.ValidationError)


def is_stale_doc_version(exc: Exception) -> bool:
	return "Stale doc_version" in str(exc)


def conflict_from_stale(task_name: str, client_version: int | None, message: str | None = None):
	server = frappe.db.get_value("Project Task", task_name, "doc_version")
	return fail(
		SYNC_CONFLICT_LWW,
		message or _("Document was modified by another session"),
		http_status=409,
		details={
			"server_doc_version": server,
			"client_doc_version": client_version,
		},
	)
'''

PERMISSIONS = '''# Copyright (c) 2026, Murugan and contributors
"""Session-based scope checks; JWT stub for Phase 3/5."""

from __future__ import annotations

import frappe
from frappe import _

BYPASS_ROLES = frozenset({"Administrator", "System Manager"})


def ensure_authenticated() -> None:
	if frappe.session.user in ("Guest", ""):
		frappe.throw(_("Authentication required"), exc=frappe.AuthenticationError)


def get_allowed_blocks() -> set[str] | None:
	if set(frappe.get_roles()) & BYPASS_ROLES:
		return None
	perms = frappe.get_all(
		"User Permission",
		filters={"user": frappe.session.user, "allow": "Block"},
		pluck="for_value",
	)
	return set(perms) if perms else set()


def assert_block_scope(block: str | None) -> None:
	if not block:
		return
	allowed = get_allowed_blocks()
	if allowed is not None and block not in allowed:
		frappe.throw(_("Not permitted for block {0}").format(block), exc=frappe.PermissionError)


def assert_project_access(project_name: str) -> dict:
	ensure_authenticated()
	if not frappe.db.exists("Farmer Project", {"name": project_name, "is_deleted": 0}):
		frappe.throw(_("Farmer Project not found"), exc=frappe.DoesNotExistError)
	project = frappe.db.get_value(
		"Farmer Project",
		project_name,
		[
			"name",
			"farmer",
			"current_stage",
			"stage_sequence",
			"status",
			"doc_version",
			"block",
			"cluster",
			"village",
			"officer",
			"mimis_gate_status",
			"modified",
		],
		as_dict=True,
	)
	assert_block_scope(project.block)
	return project


def assert_farmer_timeline_access(farmer: str) -> None:
	ensure_authenticated()
	if not frappe.db.exists("Farmer", farmer):
		frappe.throw(_("Farmer not found"), exc=frappe.DoesNotExistError)
	allowed = get_allowed_blocks()
	if allowed is None:
		return
	block = frappe.db.get_value("Farmer", farmer, "block")
	if block and block not in allowed:
		frappe.throw(_("Not permitted for farmer block"), exc=frappe.PermissionError)


TASK_FIELDS = [
	"name",
	"subject",
	"farmer_project",
	"farmer",
	"task_type",
	"status",
	"priority",
	"due_date",
	"started_on",
	"completed_on",
	"assigned_officer",
	"assigned_to",
	"block",
	"cluster",
	"district",
	"stage_key",
	"source_template",
	"description",
	"visit_outcome",
	"blocked_reason",
	"sla_due_at",
	"sla_started_at",
	"sla_breached_at",
	"client_id",
	"doc_version",
	"sync_status",
	"is_deleted",
	"modified",
]


def assert_task_access(task_name: str) -> dict:
	ensure_authenticated()
	if not frappe.db.exists("Project Task", {"name": task_name, "is_deleted": 0}):
		frappe.throw(_("Project Task not found"), exc=frappe.DoesNotExistError)
	task = frappe.db.get_value("Project Task", task_name, TASK_FIELDS, as_dict=True)
	assert_block_scope(task.block)
	return task


def assert_task_create(farmer_project: str) -> dict:
	project = assert_project_access(farmer_project)
	if project.status == "cancelled":
		frappe.throw(_("Cannot create tasks on cancelled project"))
	return project
'''

SERIALIZERS = '''# Copyright (c) 2026, Murugan and contributors
"""Mobile-friendly task API serializers."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import getdate, today

from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.utils.transitions import ALLOWED_TRANSITIONS, OPEN_QUEUE

PRIORITY_RANK = {"urgent": 4, "high": 3, "normal": 2, "medium": 2, "low": 1}


def _iso(dt) -> str | None:
	if not dt:
		return None
	return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def _sla_block(row) -> dict[str, Any]:
	return {
		"sla_due_at": _iso(row.get("sla_due_at") if isinstance(row, dict) else getattr(row, "sla_due_at", None)),
		"sla_started_at": _iso(
			row.get("sla_started_at") if isinstance(row, dict) else getattr(row, "sla_started_at", None)
		),
		"sla_breached_at": _iso(
			row.get("sla_breached_at") if isinstance(row, dict) else getattr(row, "sla_breached_at", None)
		),
	}


def is_overdue(row) -> bool:
	status = row.get("status") if isinstance(row, dict) else row.status
	if status not in OPEN_QUEUE:
		return False
	due = row.get("due_date") if isinstance(row, dict) else row.due_date
	if not due:
		return False
	return getdate(due) < getdate(today())


def to_task_summary(row) -> dict[str, Any]:
	data = row if isinstance(row, dict) else row.as_dict()
	return {
		"name": data.name,
		"subject": data.subject,
		"farmer_project": data.farmer_project,
		"farmer": data.farmer,
		"task_type": data.task_type,
		"status": data.status,
		"priority": _normalize_priority_out(data.priority),
		"due_date": str(data.due_date) if data.due_date else None,
		"assigned_officer": data.assigned_officer,
		"assigned_to": data.assigned_to,
		"block": data.block,
		"stage_key": data.stage_key,
		"doc_version": data.doc_version,
		"modified": _iso(data.modified),
		"client_id": data.client_id,
		"is_overdue": is_overdue(data),
		"sla": _sla_block(data),
	}


def to_task_detail(row) -> dict[str, Any]:
	summary = to_task_summary(row)
	data = row if isinstance(row, dict) else row.as_dict()
	summary.update(
		{
			"description": data.get("description") or "",
			"visit_outcome": data.get("visit_outcome"),
			"blocked_reason": data.get("blocked_reason"),
			"started_on": _iso(data.get("started_on")),
			"completed_on": _iso(data.get("completed_on")),
			"cluster": data.get("cluster"),
			"district": data.get("district"),
			"source_template": data.get("source_template"),
			"sync_status": data.get("sync_status"),
			"is_deleted": data.get("is_deleted") or 0,
		}
	)
	return summary


def assignment_history(task_name: str) -> list[dict[str, Any]]:
	rows = frappe.get_all(
		"Project Task Assignment History",
		filters={"project_task": task_name},
		fields=[
			"name",
			"officer",
			"assigned_on",
			"unassigned_on",
			"assigned_by",
			"assignment_reason",
			"notes",
		],
		order_by="assigned_on asc",
	)
	for row in rows:
		row["assigned_on"] = _iso(row.assigned_on)
		row["unassigned_on"] = _iso(row.unassigned_on)
	return rows


def timeline_preview(task_name: str, farmer_project: str, *, limit: int = 10) -> dict[str, Any]:
	types = ["task_created", "task_assigned", "task_status_changed", "task_completed"]
	feed = get_timeline_service().query(
		farmer_project=farmer_project,
		event_types=types,
		limit=50,
		order="desc",
	)
	items = [e for e in feed["items"] if e.get("reference", {}).get("name") == task_name]
	return {"items": items[:limit], "reference_task": task_name}


def allowed_transitions(status: str) -> list[str]:
	return sorted(ALLOWED_TRANSITIONS.get(status or "open", frozenset()))


def normalize_priority_in(value: str | None) -> str:
	if not value:
		return "normal"
	v = value.strip().lower()
	if v == "medium":
		return "normal"
	return v


def _normalize_priority_out(value: str | None) -> str:
	return value or "normal"
'''

QUERY = '''# Copyright (c) 2026, Murugan and contributors
"""Paginated task list with keyset cursor (due_date, priority, modified, name)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.query_builder import Order
from frappe.query_builder.functions import Coalesce
from frappe.utils import get_datetime, getdate

from agriflow.task_engine.api.serializers import PRIORITY_RANK, to_task_summary

VALID_STATUSES = frozenset(
	{"open", "assigned", "in_progress", "blocked", "completed", "cancelled"}
)
VALID_PRIORITIES = frozenset({"low", "normal", "high", "urgent", "medium"})
LIST_FIELDS = [
	"name",
	"subject",
	"farmer_project",
	"farmer",
	"task_type",
	"status",
	"priority",
	"due_date",
	"assigned_officer",
	"assigned_to",
	"block",
	"stage_key",
	"doc_version",
	"modified",
	"client_id",
	"sla_due_at",
	"sla_started_at",
	"sla_breached_at",
]


def _priority_rank_expr(pt):
	"""CASE priority -> rank for ORDER BY DESC."""
	return (
		frappe.qb.terms.Case()
		.when(pt.priority == "urgent", 4)
		.when(pt.priority == "high", 3)
		.when(pt.priority == "normal", 2)
		.when(pt.priority == "medium", 2)
		.else_(1)
	)


def _normalize_due_before(payload: dict) -> str | None:
	return payload.get("due_before") or payload.get("due_date_lte")


def list_tasks(payload: dict) -> dict[str, Any]:
	limit = min(max(int(payload.get("limit") or 25), 1), 100)
	pt = frappe.qb.DocType("Project Task")
	pr = _priority_rank_expr(pt)

	q = (
		frappe.qb.from_(pt)
		.select(*[getattr(pt, f) for f in LIST_FIELDS])
		.where(pt.is_deleted == 0)
	)

	allowed = None
	from agriflow.api.v1.permissions import get_allowed_blocks

	allowed = get_allowed_blocks()
	if allowed is not None:
		q = q.where(pt.block.isin(list(allowed)))

	if payload.get("farmer_project"):
		q = q.where(pt.farmer_project == payload["farmer_project"])

	blocks = payload.get("block")
	if blocks:
		if isinstance(blocks, str):
			blocks = [blocks]
		q = q.where(pt.block.isin(blocks))

	statuses = payload.get("status")
	if statuses:
		if isinstance(statuses, str):
			statuses = [statuses]
		invalid = [s for s in statuses if s not in VALID_STATUSES]
		if invalid:
			frappe.throw(frappe._("Invalid status: {0}").format(", ".join(invalid)))
		q = q.where(pt.status.isin(statuses))

	priorities = payload.get("priority")
	if priorities:
		if isinstance(priorities, str):
			priorities = [priorities]
		norm = ["normal" if p == "medium" else p for p in priorities]
		q = q.where(pt.priority.isin(norm))

	assigned_to = payload.get("assigned_to")
	if assigned_to == "me":
		q = q.where(pt.assigned_to == frappe.session.user)
	elif assigned_to:
		q = q.where(pt.assigned_to == assigned_to)

	if payload.get("assigned_officer"):
		q = q.where(pt.assigned_officer == payload["assigned_officer"])

	due_before = _normalize_due_before(payload)
	if due_before:
		q = q.where(pt.due_date <= getdate(due_before))

	if payload.get("modified_since"):
		q = q.where(pt.modified >= get_datetime(payload["modified_since"]))

	cursor = payload.get("cursor")
	if cursor:
		cur = frappe.db.get_value(
			"Project Task",
			cursor,
			["name", "due_date", "priority", "modified"],
			as_dict=True,
		)
		if not cur:
			frappe.throw(frappe._("Invalid cursor"), exc=frappe.ValidationError)
		c_pr = PRIORITY_RANK.get(cur.priority or "normal", 2)
		c_mod = cur.modified
		c_due = cur.due_date
		c_name = cur.name
		# Rows strictly after cursor in sort order
		q = q.where(
			(pt.due_date > c_due)
			| ((pt.due_date == c_due) & (pr < c_pr))
			| ((pt.due_date == c_due) & (pr == c_pr) & (pt.modified < c_mod))
			| (
				(pt.due_date == c_due)
				& (pr == c_pr)
				& (pt.modified == c_mod)
				& (pt.name > c_name)
			)
		)

	q = (
		q.orderby(pt.due_date, order=Order.asc)
		.orderby(pr, order=Order.desc)
		.orderby(pt.modified, order=Order.desc)
		.orderby(pt.name, order=Order.asc)
		.limit(limit + 1)
	)

	rows = q.run(as_dict=True)
	has_more = len(rows) > limit
	if has_more:
		rows = rows[:limit]

	next_cursor = rows[-1].name if rows and has_more else None
	return {
		"items": [to_task_summary(r) for r in rows],
		"pagination": {"next_cursor": next_cursor, "has_more": has_more, "limit": limit},
		"generated_at": frappe.utils.now_datetime().isoformat(),
	}
'''

TASK_API = '''# Copyright (c) 2026, Murugan and contributors
"""Task API — API_CONTRACTS §16 (Phase 10b)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from agriflow.api.v1.errors import (
	SYNC_CONFLICT_LWW,
	VAL_INVALID,
	VAL_INVALID_CURSOR,
	VAL_REQUIRED_FIELD,
	conflict_from_stale,
	is_stale_doc_version,
)
from agriflow.api.v1.permissions import assert_task_access, assert_task_create, ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.task_engine.api.serializers import (
	allowed_transitions,
	assignment_history,
	normalize_priority_in,
	to_task_detail,
	timeline_preview,
)
from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.lifecycle import TaskLifecycleService
from agriflow.task_engine.services.query import list_tasks

VALID_TASK_TYPES = frozenset(
	{
		"field_visit",
		"document_collection",
		"verification",
		"approval",
		"installation",
		"follow_up",
	}
)


def _stale_response(exc: Exception, task_name: str, doc_version):
	if is_stale_doc_version(exc):
		return conflict_from_stale(task_name, doc_version, str(exc))
	return None


@frappe.whitelist()
def list(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		if payload.get("cursor") and not frappe.db.exists("Project Task", payload["cursor"]):
			return fail(VAL_INVALID_CURSOR, _("Invalid cursor"), http_status=400)
		return success(list_tasks(payload))
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		if "cursor" in str(exc).lower():
			return fail(VAL_INVALID_CURSOR, str(exc), http_status=400)
		return fail(VAL_INVALID, str(exc), http_status=400)


@frappe.whitelist()
def get(data=None):
	try:
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail(VAL_INVALID, _("name is required"), http_status=400)
		row = assert_task_access(name)
		return success(
			{
				"task": to_task_detail(row),
				"assignment_history": assignment_history(name),
				"timeline_preview": timeline_preview(name, row.farmer_project),
				"sla": {
					**to_task_detail(row)["sla"],
					"is_overdue": to_task_detail(row)["is_overdue"],
				},
				"allowed_transitions": allowed_transitions(row.status),
			}
		)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def create(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		for field in ("client_id", "subject", "farmer_project", "task_type", "due_date"):
			if not payload.get(field):
				return fail(VAL_REQUIRED_FIELD, _("{0} is required").format(field), http_status=400)
		if payload["task_type"] not in VALID_TASK_TYPES:
			return fail(VAL_INVALID, _("Invalid task_type"), http_status=400)
		assert_task_create(payload["farmer_project"])
		svc = TaskLifecycleService()
		doc = svc.create_task(
			subject=payload["subject"],
			farmer_project=payload["farmer_project"],
			task_type=payload["task_type"],
			due_date=payload["due_date"],
			priority=normalize_priority_in(payload.get("priority")),
			description=payload.get("description"),
			client_id=payload["client_id"],
			assigned_officer=payload.get("assigned_officer"),
			assigned_to=payload.get("assigned_to"),
			auto_assign=bool(payload.get("assigned_officer")),
		)
		if payload.get("assigned_officer") and not payload.get("assigned_to"):
			pass
		elif payload.get("assigned_to") and payload.get("assigned_officer"):
			TaskAssignmentService().assign(
				doc.name,
				payload["assigned_officer"],
				assigned_to=payload["assigned_to"],
				reason="initial",
			)
			doc.reload()
		return success({"task": to_task_detail(doc)})
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail(VAL_INVALID, str(exc), http_status=400)


@frappe.whitelist()
def update(data=None):
	try:
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail(VAL_INVALID, _("name is required"), http_status=400)
		if payload.get("doc_version") is None:
			return fail(VAL_REQUIRED_FIELD, _("doc_version is required"), http_status=400)
		assert_task_access(name)
		doc_version = int(payload["doc_version"])
		lifecycle = TaskLifecycleService()
		assign_svc = TaskAssignmentService()
		task = frappe.get_doc("Project Task", name)

		try:
			if payload.get("assigned_officer"):
				task = assign_svc.assign(
					name,
					payload["assigned_officer"],
					assigned_to=payload.get("assigned_to"),
					reason="reassignment",
				)
				doc_version = task.doc_version

			if payload.get("status"):
				task = lifecycle.transition_status(
					name,
					payload["status"],
					doc_version=doc_version,
					blocked_reason=payload.get("blocked_reason"),
					visit_outcome=payload.get("visit_outcome"),
				)
			elif payload.get("description") is not None:
				task = lifecycle.update_description(
					name, doc_version=doc_version, description=payload["description"]
				)
		except frappe.ValidationError as exc:
			stale = _stale_response(exc, name, doc_version)
			if stale:
				return stale
			return fail(VAL_INVALID, str(exc), http_status=400)

		task.reload()
		return success({"task": to_task_detail(task)})
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def complete(data=None):
	try:
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail(VAL_INVALID, _("name is required"), http_status=400)
		if payload.get("doc_version") is None:
			return fail(VAL_REQUIRED_FIELD, _("doc_version is required"), http_status=400)
		assert_task_access(name)
		doc_version = int(payload["doc_version"])
		try:
			task = TaskLifecycleService().complete(
				name,
				doc_version=doc_version,
				visit_outcome=payload.get("visit_outcome"),
				completed_on=payload.get("completed_on"),
			)
		except frappe.ValidationError as exc:
			stale = _stale_response(exc, name, doc_version)
			if stale:
				return stale
			return fail(VAL_INVALID, str(exc), http_status=400)
		return success({"task": to_task_detail(task)})
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
'''


if __name__ == "__main__":
    main()
