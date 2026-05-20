#!/usr/bin/env python3
"""Day 1 demo — add farmer.list and project.transition to bench agriflow API."""
from __future__ import annotations

from pathlib import Path

BENCH_APP = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
REPO_APP = Path(__file__).resolve().parents[1] / "backend" / "agriflow" / "agriflow"

FARMER_PY = '''# Copyright (c) 2026, Murugan and contributors
"""Farmer API — list for mobile demo (read-only)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from agriflow.api.v1.permissions import assert_block_scope, ensure_authenticated, get_allowed_blocks
from agriflow.api.v1.response import fail, parse_data, success


def _iso(dt) -> str | None:
	if not dt:
		return None
	return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


@frappe.whitelist()
def list(data=None):
	"""agriflow.api.v1.farmer.list — scoped farmer search."""
	try:
		ensure_authenticated()
		payload = parse_data(data)
		limit = min(max(int(payload.get("limit", 50)), 1), 100)
		filters: dict[str, Any] = {"is_deleted": 0, "is_active": 1}
		if payload.get("block"):
			filters["block"] = payload["block"]
		if payload.get("village"):
			filters["village"] = payload["village"]
		search = (payload.get("search") or "").strip()
		allowed = get_allowed_blocks()
		if allowed is not None:
			filters["block"] = ("in", list(allowed))
		rows = frappe.get_all(
			"Farmer",
			filters=filters,
			fields=[
				"name",
				"farmer_name",
				"mobile",
				"block",
				"village",
				"district",
				"cluster",
				"doc_version",
				"modified",
			],
			order_by="modified desc",
			limit_page_length=limit,
		)
		if search:
			needle = search.lower()
			rows = [
				r
				for r in rows
				if needle in (r.farmer_name or "").lower()
				or needle in (r.mobile or "").lower()
				or needle in (r.name or "").lower()
			]
		for row in rows:
			row["modified"] = _iso(row.modified)
			if row.block:
				assert_block_scope(row.block)
		return success({"items": rows, "has_more": False, "cursor": None})
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
'''

TRANSITION_APPEND = '''

@frappe.whitelist()
def transition(data=None):
	"""agriflow.api.v1.project.transition — sequential stage advance."""
	try:
		ensure_authenticated()
		payload = parse_data(data)
		name = payload.get("name")
		target_stage = payload.get("target_stage")
		doc_version = payload.get("doc_version")
		if not name or not target_stage:
			return fail("VAL_INVALID", _("name and target_stage are required"), http_status=400)
		if doc_version is None:
			return fail("VAL_INVALID", _("doc_version is required"), http_status=400)

		assert_project_access(name)
		from agriflow.project_lifecycle.services.lifecycle import ProjectLifecycleService

		result = ProjectLifecycleService().transition(
			project_name=name,
			target_stage=target_stage,
			notes=payload.get("notes"),
			doc_version=int(doc_version),
			client_id=payload.get("client_id"),
		)
		return success(result)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
'''


def write(path: Path, content: str) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(content, encoding="utf-8")
	print(f"  wrote {path}")


def patch_project_py(app_root: Path) -> None:
	project_py = app_root / "api" / "v1" / "project.py"
	if not project_py.exists():
		raise SystemExit(f"missing {project_py}")
	text = project_py.read_text(encoding="utf-8")
	if "def transition(data=None):" in text:
		print("  project.transition already present")
		return
	if "from agriflow.project_lifecycle.utils.stages import get_next_stage_key, get_stage_map" in text:
		text = text.replace(
			"from agriflow.project_lifecycle.utils.stages import get_next_stage_key, get_stage_map",
			"from agriflow.project_lifecycle.services.lifecycle import ProjectLifecycleService\n"
			"from agriflow.project_lifecycle.utils.stages import get_next_stage_key, get_stage_map",
		)
	write(project_py, text.rstrip() + TRANSITION_APPEND + "\n")


def main() -> None:
	for label, root in (("bench", BENCH_APP), ("repo", REPO_APP)):
		if not root.exists():
			print(f"skip {label}: {root} missing")
			continue
		write(root / "api" / "v1" / "farmer.py", FARMER_PY)
		write(root / "api" / "v1" / "__init__.py", "")
		patch_project_py(root)
	print("Done. Run: bench --site dev.agriflow.local clear-cache")


if __name__ == "__main__":
	main()
