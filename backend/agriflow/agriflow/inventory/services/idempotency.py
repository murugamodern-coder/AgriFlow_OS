# Copyright (c) 2026, Murugan and contributors
"""Ledger idempotency via client_id."""

from __future__ import annotations

import frappe


def find_ledger_by_client_id(client_id: str | None) -> str | None:
	if not client_id:
		return None
	return frappe.db.get_value("Stock Ledger Entry", {"client_id": client_id}, "name")
