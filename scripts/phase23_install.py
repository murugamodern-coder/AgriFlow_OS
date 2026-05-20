# Copyright (c) 2026, Murugan and contributors
"""Install Phase 23 enterprise DocTypes."""

from __future__ import annotations

import json
from pathlib import Path

import frappe


def _import_doctype(json_path: Path) -> str:
	from frappe.modules.import_file import import_file_by_path

	name = json.loads(json_path.read_text(encoding="utf-8"))["name"]
	import_file_by_path(str(json_path), force=True)
	frappe.db.commit()
	return f"updated:{name}"


def execute():
	base = Path(frappe.get_app_path("agriflow")) / "project_lifecycle" / "doctype"
	jp = base / "tenant_ops_record" / "tenant_ops_record.json"
	if not jp.exists():
		return {"ok": False, "error": f"missing {jp}"}
	result = _import_doctype(jp)
	return {"ok": True, "doctypes": [result]}
