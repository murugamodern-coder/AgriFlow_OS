# Copyright (c) 2026, Murugan and contributors
"""API envelope with request + sync correlation IDs (Phase 16)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.request_context import get_request_id, get_sync_correlation_id


def success(data: Any, *, include_sync_meta: bool = False) -> dict[str, Any]:
	out = {
		"ok": True,
		"data": data,
		"error": None,
		"server_time": now_datetime().isoformat(),
		"request_id": get_request_id(),
	}
	if include_sync_meta:
		out["sync_correlation_id"] = get_sync_correlation_id()
	return out


def fail(
	code: str,
	message: str,
	*,
	http_status: int = 400,
	details: dict | None = None,
	include_sync_meta: bool = False,
) -> dict[str, Any]:
	frappe.local.response["http_status_code"] = http_status
	out = {
		"ok": False,
		"data": None,
		"error": {"code": code, "message": message, "details": details or {}},
		"server_time": now_datetime().isoformat(),
		"request_id": get_request_id(),
	}
	if include_sync_meta:
		out["sync_correlation_id"] = get_sync_correlation_id()
	return out


def parse_data(data: Any) -> dict:
	if data is None:
		return {}
	if isinstance(data, str):
		import json

		return json.loads(data) if data else {}
	if isinstance(data, dict):
		return data
	return {}
