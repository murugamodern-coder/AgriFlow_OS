# Copyright (c) 2026, Murugan and contributors
"""Idempotent replay via immutable Sync Mutation Log."""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe.utils import now_datetime

LOG_FLAG = "agriflow_sync_mutation_log_write"


def find_prior(client_mutation_id: str) -> dict[str, Any] | None:
	if not client_mutation_id:
		return None
	row = frappe.db.get_value(
		"Sync Mutation Log",
		{"client_mutation_id": client_mutation_id},
		["name", "status", "response_json", "entity_name", "entity", "client_id"],
		as_dict=True,
	)
	if not row:
		return None
	resp = row.response_json
	if isinstance(resp, str):
		try:
			resp = json.loads(resp)
		except json.JSONDecodeError:
			resp = {"raw": resp}
	if not resp:
		resp = {
			"status": row.status,
			"entity": row.entity,
			"name": row.entity_name,
			"client_id": row.client_id,
		}
	return {
		"status": row.status,
		"entity": row.entity,
		"entity_name": row.entity_name,
		"client_id": row.client_id,
		"result": resp,
	}


def record(
	*,
	sync_session: str,
	client_mutation_id: str,
	entity: str,
	op_type: str,
	status: str,
	request_json: dict,
	response_json: dict,
	entity_name: str | None = None,
	client_id: str | None = None,
) -> str:
	existing = frappe.db.get_value(
		"Sync Mutation Log",
		{"client_mutation_id": client_mutation_id},
		"name",
	)
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Sync Mutation Log",
			"sync_session": sync_session,
			"client_mutation_id": client_mutation_id,
			"entity": entity,
			"op_type": op_type,
			"status": status,
			"entity_name": entity_name or "",
			"client_id": client_id or "",
			"request_json": request_json,
			"response_json": response_json,
			"processed_on": now_datetime(),
		}
	)
	frappe.flags[LOG_FLAG] = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags[LOG_FLAG] = False
	return doc.name
