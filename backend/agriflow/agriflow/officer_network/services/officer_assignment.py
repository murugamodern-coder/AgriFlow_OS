# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Officer assignment validation and officer current_cluster sync."""

from __future__ import annotations

import frappe
from frappe import _


def validate_assignment(doc) -> None:
	if doc.valid_from and doc.valid_to and doc.valid_to < doc.valid_from:
		frappe.throw(_("Valid To cannot be before Valid From"))

	if not doc.cluster:
		return

	# One active officer per cluster at a time.
	if not doc.valid_to:
		overlap = frappe.db.exists(
			"Officer Assignment History",
			{
				"cluster": doc.cluster,
				"valid_to": ("is", "not set"),
				"name": ("!=", doc.name or ""),
			},
		)
		if overlap:
			frappe.throw(_("Cluster already has an active officer assignment"))


def on_assignment_change(doc, method=None) -> None:
	"""Sync Officer.current_cluster from active assignment."""
	if not doc.officer:
		return

	active_cluster = frappe.db.get_value(
		"Officer Assignment History",
		{"officer": doc.officer, "valid_to": ("is", "not set")},
		"cluster",
	)
	frappe.db.set_value("Officer", doc.officer, "current_cluster", active_cluster, update_modified=False)
