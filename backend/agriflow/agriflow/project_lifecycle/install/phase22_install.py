# Copyright (c) 2026, Murugan and contributors
"""Install Phase 22 GA DocTypes and refresh Support Ticket schema."""

from __future__ import annotations

import json
from pathlib import Path

import frappe


def _import_doctype(json_path: Path) -> str:
	from frappe.modules.import_file import import_file_by_path

	name = json.loads(json_path.read_text(encoding="utf-8"))["name"]
	import_file_by_path(str(json_path), force=True)
	frappe.db.commit()
	return f"updated:{name}" if frappe.db.exists("DocType", name) else f"imported:{name}"


def execute():
	base = Path(frappe.get_app_path("agriflow")) / "project_lifecycle" / "doctype"
	results = []
	for folder, fname in (
		("ga_release_signoff", "ga_release_signoff.json"),
		("support_ticket", "support_ticket.json"),
	):
		jp = base / folder / fname
		if not jp.exists():
			results.append(f"missing:{jp}")
			continue
		results.append(_import_doctype(jp))
	return {"ok": True, "doctypes": results}
