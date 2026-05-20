# Copyright (c) 2026, Murugan and contributors
"""Sync API — pull / push (API_CONTRACTS §8–9, §13)."""

from __future__ import annotations

import frappe
from frappe import _

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.sync_engine.services.pull import pull as run_pull
from agriflow.sync_engine.services.push import push as run_push
from agriflow.sync_engine.services.session import complete_session, open_session

SYNC_PARTIAL = "SYNC_PARTIAL_FAILURE"


@frappe.whitelist()
def pull(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		session = open_session(
			device_id=payload.get("device_id"),
			session_type="pull",
			watermarks_in=payload.get("modified_since") or {},
		)
		body = run_pull(payload)
		token = complete_session(
			session.name,
			watermarks_out=body.get("server_watermark"),
			summary={"entities": list((body.get("entities") or {}).keys())},
		)
		body["sync_token"] = token
		return success(body)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)


@frappe.whitelist()
def push(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		operations = payload.get("operations") or []
		if not operations:
			return fail("VAL_INVALID", _("operations required"), http_status=400)

		session = open_session(
			device_id=payload.get("device_id"),
			session_type="push",
		)
		outcome = run_push(session.name, operations)
		token = complete_session(
			session.name,
			summary=outcome.get("summary"),
		)
		data_out = {
			"sync_token": token,
			"results": outcome["results"],
			"summary": outcome["summary"],
		}
		if outcome.get("partial"):
			frappe.local.response["http_status_code"] = 207
			envelope = success(data_out)
			envelope["error"] = {
				"code": SYNC_PARTIAL,
				"message": _("Batch partially applied"),
				"details": outcome["summary"],
			}
			return envelope
		return success(data_out)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
