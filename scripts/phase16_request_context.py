# Copyright (c) 2026, Murugan and contributors
"""API request tracing — structured request_id + sync_correlation_id (Phase 16)."""

from __future__ import annotations

import frappe


def bind_request_context() -> None:
	"""Call from before_request hook."""
	headers = getattr(frappe.local, "request", None) and frappe.local.request.headers or {}
	req_id = headers.get("X-Request-Id") or headers.get("X-Request-ID")
	if not req_id:
		req_id = frappe.generate_hash(length=12)
	frappe.flags.request_id = req_id
	frappe.flags.sync_correlation_id = (
		headers.get("X-Sync-Correlation-Id")
		or headers.get("X-Sync-Correlation-ID")
		or req_id
	)


def get_request_id() -> str:
	return frappe.flags.get("request_id") or frappe.generate_hash(length=12)


def get_sync_correlation_id() -> str:
	return frappe.flags.get("sync_correlation_id") or get_request_id()
