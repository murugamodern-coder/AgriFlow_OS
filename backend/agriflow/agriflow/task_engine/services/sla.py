# Copyright (c) 2026, Murugan and contributors
"""SLA timestamp helpers — clock starts at in_progress only."""

from __future__ import annotations

from datetime import datetime, time

import frappe
from frappe.utils import get_datetime, now_datetime


def sla_due_at_from_date(due_date) -> datetime | None:
	if not due_date:
		return None
	date_val = get_datetime(due_date).date()
	# End of due_date in server TZ (IST on bench)
	return datetime.combine(date_val, time(23, 59, 59))


def apply_sla_fields(doc, old_status: str | None = None) -> None:
	"""Recompute SLA fields on task document before save."""
	doc.sla_due_at = sla_due_at_from_date(doc.due_date)
	new_status = doc.status or "open"
	old_status = old_status or doc.get_doc_before_save().status if doc.get_doc_before_save() else None

	if new_status == "in_progress" and not doc.sla_started_at:
		doc.sla_started_at = doc.started_on or now_datetime()
	if old_status != "in_progress" and new_status == "in_progress" and not doc.started_on:
		doc.started_on = doc.sla_started_at or now_datetime()

	if new_status in ("completed", "cancelled"):
		return

	if doc.sla_due_at and now_datetime() > get_datetime(doc.sla_due_at) and not doc.sla_breached_at:
		doc.sla_breached_at = now_datetime()


def is_overdue(doc) -> bool:
	if doc.status in ("completed", "cancelled"):
		return False
	if not doc.due_date:
		return False
	return get_datetime(doc.due_date).date() < get_datetime(now_datetime()).date()
