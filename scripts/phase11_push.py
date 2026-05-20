# Copyright (c) 2026, Murugan and contributors
"""Batch sync push with idempotency and partial success."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import frappe
from frappe import _

from agriflow.sync_engine.services.handlers import task as task_handlers
from agriflow.sync_engine.services.handlers import timeline as timeline_handlers
from agriflow.sync_engine.services.idempotency import find_prior, record

SUCCESS = frozenset({"success", "skipped"})
TERMINAL_FAIL = frozenset({"failed", "conflict", "dependency_failed"})


def _project_key(op: dict) -> str | None:
	payload = op.get("payload") or {}
	return payload.get("farmer_project") or payload.get("name")


def _depends_met(op: dict, completed: dict[str, str]) -> bool:
	deps = op.get("depends_on") or []
	if not deps:
		return True
	for dep in deps:
		if completed.get(dep) not in SUCCESS:
			return False
	return True


def _process_one(op: dict) -> dict[str, Any]:
	client_mutation_id = op.get("client_mutation_id")
	if not client_mutation_id:
		frappe.throw(_("client_mutation_id is required"))

	prior = find_prior(client_mutation_id)
	if prior:
		out = prior["result"]
		out = dict(out)
		out["status"] = "skipped"
		out["replay"] = True
		return out

	entity = op.get("entity")
	op_type = op.get("op_type")

	if entity == "task":
		if op_type == "create":
			return task_handlers.handle_create(op)
		if op_type == "update":
			return task_handlers.handle_update(op)
		if op_type == "complete":
			return task_handlers.handle_complete(op)
		frappe.throw(_("Unsupported task op_type: {0}").format(op_type))

	if entity == "timeline":
		if op_type in ("note", "create"):
			return timeline_handlers.handle_note(op)
		frappe.throw(_("Unsupported timeline op_type: {0}").format(op_type))

	if entity == "farmer_project":
		frappe.throw(_("project.transition is not available via sync in Phase 11"))

	frappe.throw(_("Unsupported entity: {0}").format(entity))


def push(sync_session: str, operations: list[dict]) -> dict[str, Any]:
	"""Process batch; return results + summary."""
	results: list[dict[str, Any]] = []
	completed: dict[str, str] = {}
	summary = {"success": 0, "conflict": 0, "failed": 0, "skipped": 0, "dependency_failed": 0}

	# Group by farmer_project for serial execution within project
	buckets: dict[str, list[dict]] = defaultdict(list)
	global_ops: list[dict] = []
	for op in operations:
		pk = _project_key(op)
		if pk:
			buckets[pk].append(op)
		else:
			global_ops.append(op)

	ordered: list[dict] = []
	for pk in sorted(buckets.keys()):
		ordered.extend(buckets[pk])
	ordered.extend(global_ops)

	for op in ordered:
		cmid = op.get("client_mutation_id")
		entry = {
			"client_mutation_id": cmid,
			"entity": op.get("entity"),
			"op_type": op.get("op_type"),
		}
		try:
			if not _depends_met(op, completed):
				entry["status"] = "dependency_failed"
				entry["error"] = {"code": "SYNC_DEPENDENCY_FAILED", "message": "depends_on not satisfied"}
				summary["dependency_failed"] += 1
				results.append(entry)
				completed[cmid] = "dependency_failed"
				record(
					sync_session=sync_session,
					client_mutation_id=cmid,
					entity=op.get("entity") or "",
					op_type=op.get("op_type") or "",
					status="dependency_failed",
					request_json=op,
					response_json=entry,
				)
				continue

			out = _process_one(op)
			if out.get("replay"):
				entry.update(out)
				summary["skipped"] += 1
				completed[cmid] = "skipped"
				results.append(entry)
				continue
			status = out.get("status", "success")
			if status not in summary:
				status = "failed"
			entry.update(out)
			summary[status] = summary.get(status, 0) + 1
			completed[cmid] = status
			record(
				sync_session=sync_session,
				client_mutation_id=cmid,
				entity=op.get("entity") or "",
				op_type=op.get("op_type") or "",
				status=status,
				request_json=op,
				response_json=out,
				entity_name=out.get("name"),
				client_id=out.get("client_id") or op.get("client_id"),
			)
		except frappe.ValidationError as exc:
			entry["status"] = "failed"
			entry["error"] = {"code": "VAL_INVALID", "message": str(exc)}
			summary["failed"] += 1
			completed[cmid] = "failed"
			record(
				sync_session=sync_session,
				client_mutation_id=cmid,
				entity=op.get("entity") or "",
				op_type=op.get("op_type") or "",
				status="failed",
				request_json=op,
				response_json=entry,
			)
		except Exception as exc:
			frappe.log_error(frappe.get_traceback(), "sync.push")
			entry["status"] = "failed"
			entry["error"] = {"code": "SRV_INTERNAL", "message": str(exc)}
			summary["failed"] += 1
			completed[cmid] = "failed"
			record(
				sync_session=sync_session,
				client_mutation_id=cmid,
				entity=op.get("entity") or "",
				op_type=op.get("op_type") or "",
				status="failed",
				request_json=op,
				response_json=entry,
			)
		results.append(entry)

	partial = summary.get("conflict", 0) + summary.get("failed", 0) + summary.get("dependency_failed", 0) > 0
	return {"results": results, "summary": summary, "partial": partial}
