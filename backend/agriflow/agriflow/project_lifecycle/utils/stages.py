# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Project stage fixture loader (DB-backed, not hardcoded-only)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import frappe
from frappe import _

FIXTURES_DIR = Path(frappe.get_app_path("agriflow")) / "fixtures"


@lru_cache(maxsize=1)
def get_stage_map() -> dict[str, dict]:
	"""Return stage_key -> {sequence, label_i18n_key}."""
	rows = frappe.get_all(
		"Project Stage",
		filters={"is_active": 1},
		fields=["stage_key", "sequence", "label_i18n_key"],
		order_by="sequence asc",
	)
	if not rows:
		frappe.throw(_("Project Stage fixtures are not loaded. Run migrate."))
	return {r.stage_key: r for r in rows}


def get_stage_by_sequence(sequence: int) -> str | None:
	for key, row in get_stage_map().items():
		if row.sequence == sequence:
			return key
	return None


def get_next_stage_key(current_stage: str) -> str | None:
	current = get_stage_map().get(current_stage)
	if not current:
		return None
	return get_stage_by_sequence(current.sequence + 1)


def validate_stage_key(stage_key: str) -> None:
	if stage_key not in get_stage_map():
		frappe.throw(_("Invalid stage: {0}").format(stage_key))


@lru_cache(maxsize=1)
def get_role_matrix() -> dict[str, list[str]]:
	path = FIXTURES_DIR / "project_stage_role_matrix.json"
	if not path.exists():
		return {}
	with path.open(encoding="utf-8") as handle:
		return json.load(handle)


def user_may_transition_to(user: str, target_stage: str) -> bool:
	roles = set(frappe.get_roles(user))
	if roles & {"Administrator", "System Manager"}:
		return True
	allowed = get_role_matrix().get(target_stage) or []
	return bool(roles & set(allowed))
