# Copyright (c) 2026, Murugan and contributors
"""Farmer Project API — timeline read endpoints (API_CONTRACTS §15)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import now_datetime

from agriflow.api.v1.permissions import assert_farmer_timeline_access, assert_project_access, ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.services.queue import open_tasks_for_project
from agriflow.project_lifecycle.services.lifecycle import ProjectLifecycleService
from agriflow.project_lifecycle.utils.stages import get_next_stage_key, get_stage_map

MIMIS_GATE_APPROVED = frozenset({"approved", "waived"})


def _iso(dt) -> str | None:
	if not dt:
		return None
	return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def _project_summary(project: dict) -> dict[str, Any]:
	return {
		"name": project.name,
		"farmer": project.farmer,
		"current_stage": project.current_stage,
		"stage_sequence": project.stage_sequence,
		"status": project.status,
		"doc_version": project.doc_version,
		"block": project.block,
		"cluster": project.cluster,
		"village": project.village,
		"officer": project.officer,
		"modified": _iso(project.modified),
	}


def _slim_stage_history(project_name: str) -> list[dict[str, Any]]:
	rows = frappe.get_all(
		"Project Stage History",
		filters={"parent": project_name},
		fields=[
			"name",
			"from_stage",
			"to_stage",
			"from_sequence",
			"to_sequence",
			"transitioned_on",
			"transitioned_by",
			"notes",
			"is_correction",
		],
		order_by="to_sequence asc",
	)
	for row in rows:
		row["transitioned_on"] = _iso(row.transitioned_on)
		row["attachment_file_id"] = None
	return rows


def _workflow_meta(project: dict) -> dict[str, Any]:
	blocking: list[str] = []
	next_stage = get_next_stage_key(project.current_stage)
	can_transition = False

	if project.status != "active":
		blocking.append(_("Project status is {0}").format(project.status))
	elif not next_stage:
		blocking.append(_("No further stages"))
	else:
		can_transition = True
		if next_stage == "mimis_registered" and (project.mimis_gate_status or "pending") not in MIMIS_GATE_APPROVED:
			can_transition = False
			blocking.append(_("MIMIS gate not approved"))

	stage_map = get_stage_map()
	i18n_key = None
	if next_stage and next_stage in stage_map:
		i18n_key = stage_map[next_stage].label_i18n_key

	return {
		"next_stage": next_stage,
		"next_stage_i18n_key": i18n_key,
		"can_transition": can_transition,
		"allowed_roles": [],
		"blocking_reasons": [str(b) for b in blocking],
	}


@frappe.whitelist()
def timeline(data=None):
	"""agriflow.api.v1.project.timeline — project screen feed."""
	try:
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail("VAL_INVALID", _("name is required"))

		project = assert_project_access(name)
		timeline_svc = get_timeline_service()
		feed = timeline_svc.query(
			farmer_project=name,
			event_types=payload.get("event_types"),
			limit=payload.get("limit", 25),
			cursor=payload.get("cursor"),
			order="desc",
		)

		return success(
			{
				"project": _project_summary(project),
				"timeline": {
					"items": feed["items"],
					"next_cursor": feed["next_cursor"],
					"has_more": feed["has_more"],
					"generated_at": now_datetime().isoformat(),
				},
				"stage_history": _slim_stage_history(name),
				"open_tasks": open_tasks_for_project(name),
				"workflow": _workflow_meta(project),
			}
		)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)


@frappe.whitelist()
def timeline_since(data=None):
	"""agriflow.api.v1.project.timeline_since — delta timeline for sync replay."""
	try:
		payload = parse_data(data)
		project = payload.get("project")
		farmer = payload.get("farmer")
		since = payload.get("since")

		if not project and not farmer:
			return fail("VAL_INVALID", _("project or farmer is required"))
		if not since:
			return fail("VAL_INVALID", _("since is required"))

		if project:
			assert_project_access(project)
		if farmer:
			assert_farmer_timeline_access(farmer)

		timeline_svc = get_timeline_service()
		feed = timeline_svc.query(
			farmer_project=project,
			farmer=farmer,
			event_types=payload.get("event_types"),
			since=since,
			since_exclusive=True,
			limit=payload.get("limit", 50),
			cursor=payload.get("cursor"),
			order="asc",
		)

		return success(
			{
				"items": feed["items"],
				"next_cursor": feed["next_cursor"],
				"has_more": feed["has_more"],
				"generated_at": now_datetime().isoformat(),
				"since": since,
				"deleted": [],
			}
		)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)

@frappe.whitelist()
def transition(data=None):
	"""agriflow.api.v1.project.transition — sequential stage advance."""
	try:
		ensure_authenticated()
		payload = parse_data(data)
		name = payload.get("name")
		target_stage = payload.get("target_stage")
		doc_version = payload.get("doc_version")
		if not name or not target_stage:
			return fail("VAL_INVALID", _("name and target_stage are required"), http_status=400)
		if doc_version is None:
			return fail("VAL_INVALID", _("doc_version is required"), http_status=400)

		assert_project_access(name)
		from agriflow.project_lifecycle.services.lifecycle import ProjectLifecycleService

		result = ProjectLifecycleService().transition(
			project_name=name,
			target_stage=target_stage,
			notes=payload.get("notes"),
			doc_version=int(doc_version),
			client_id=payload.get("client_id"),
		)
		return success(result)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)

