# Copyright (c) 2026, Murugan and contributors
"""Migrate legacy TVM / BLKxx demo geography to LGD district 593."""

from __future__ import annotations

from dataclasses import dataclass, field

import click
import frappe

LEGACY_DISTRICT = "TVM"
LGD_DISTRICT = "593"
LINK_OPTIONS = {"District", "Block", "Village", "Cluster"}
LEGACY_BLOCK_PREFIX = "BLK"
# Demo farmers sit on BLK01 — Polur is the intended LGD block when name is generic.
BLK01_POLUR_FALLBACK = "5724"
CHETPET_LGD = "6617"
ORPHAN_BLOCK_DELETE_IDS = (
	"BLK02",
	"BLK04",
	"BLK05",
	"BLK06",
	"BLK07",
	"BLK08",
	"BLK09",
	"BLK10",
	"BLK11",
	"BLK12",
)
PRIORITY_DOCTYPES = (
	"Farmer",
	"Farmer Project",
	"Project Task",
	"Village",
	"Block",
	"Cluster",
	"Officer Assignment History",
	"Notification",
	"Warehouse",
	"Stock Ledger Entry",
	"Project Material Allocation",
	"Timeline Event",
)
SAFETY_REF_DOCTYPES = PRIORITY_DOCTYPES


@dataclass
class PlannedChange:
	doctype: str
	name: str
	fieldname: str
	old_value: str
	new_value: str
	reason: str = ""


@dataclass
class MigrationPlan:
	block_map: dict[str, dict] = field(default_factory=dict)
	changes: list[PlannedChange] = field(default_factory=list)
	deletes: list[tuple[str, str, str]] = field(default_factory=list)
	errors: list[str] = field(default_factory=list)
	warnings: list[str] = field(default_factory=list)

	def log(self, msg: str) -> None:
		print(msg)


def _normalize_name(value: str | None) -> str:
	return (value or "").strip().lower()


def _lgd_blocks_by_name() -> dict[str, str]:
	rows = frappe.get_all(
		"Block",
		filters={"district": LGD_DISTRICT},
		fields=["name", "block_name"],
	)
	by_name: dict[str, str] = {}
	for row in rows:
		key = _normalize_name(row.block_name)
		if key:
			by_name[key] = row.name
	return by_name


def _find_lgd_block_by_name(legacy_block_name: str, lgd_by_name: dict[str, str]) -> str | None:
	key = _normalize_name(legacy_block_name)
	if not key:
		return None
	if key in lgd_by_name:
		return lgd_by_name[key]
	for lgd_name, lgd_id in lgd_by_name.items():
		if key in lgd_name or lgd_name in key:
			return lgd_id
	return None


def _build_block_mapping(plan: MigrationPlan) -> dict[str, dict]:
	lgd_by_name = _lgd_blocks_by_name()
	legacy_blocks = frappe.get_all(
		"Block",
		filters={"district": LEGACY_DISTRICT},
		fields=["name", "block_name"],
		order_by="name",
	)
	mapping: dict[str, dict] = {}

	for lb in legacy_blocks:
		legacy_id = lb.name
		match_id = _find_lgd_block_by_name(lb.block_name, lgd_by_name)

		if not match_id and legacy_id == "BLK01":
			match_id = BLK01_POLUR_FALLBACK
			plan.warnings.append(
				f"{legacy_id} block_name='{lb.block_name}' → fallback Polur ({BLK01_POLUR_FALLBACK})"
			)

		if not match_id and "chetpet" in _normalize_name(lb.block_name):
			match_id = CHETPET_LGD

		action = "merge" if match_id else "delete_orphan"
		if not match_id:
			plan.warnings.append(
				f"{legacy_id} block_name='{lb.block_name}' — orphan placeholder; delete after ref check"
			)

		mapping[legacy_id] = {
			"legacy_name": lb.block_name,
			"lgd_block": match_id,
			"action": action,
		}
		plan.log(
			f"  Block map: {legacy_id} ({lb.block_name}) → "
			f"{match_id or 'DELETE after safety check'} [{action}]"
		)

	if not mapping.get("BLK01", {}).get("lgd_block"):
		plan.errors.append("BLK01 has no LGD target — cannot migrate demo farmers")

	return mapping


def _get_link_fields() -> list[tuple[str, str, str]]:
	"""Return (doctype, fieldname, options) for geography Link fields in agriflow."""
	modules = frappe.get_all("Module Def", filters={"app_name": "agriflow"}, pluck="name")
	doctypes = frappe.get_all(
		"DocType",
		filters={"module": ["in", modules]} if modules else {"name": ("!=", "")},
		pluck="name",
		limit_page_length=500,
	)
	doctypes = list(dict.fromkeys([*doctypes, *PRIORITY_DOCTYPES]))
	seen: set[tuple[str, str]] = set()
	link_fields: list[tuple[str, str, str]] = []
	for dt in doctypes:
		if not frappe.db.table_exists(f"tab{dt}"):
			continue
		try:
			meta = frappe.get_meta(dt, cached=True)
		except Exception:
			continue
		for df in meta.fields:
			if df.fieldtype == "Link" and df.options in LINK_OPTIONS:
				key = (dt, df.fieldname)
				if key not in seen:
					seen.add(key)
					link_fields.append((dt, df.fieldname, df.options))
	if not link_fields:
		link_fields = [
			("Farmer", "district", "District"),
			("Farmer", "block", "Block"),
			("Farmer", "village", "Village"),
			("Farmer", "cluster", "Cluster"),
			("Farmer Project", "district", "District"),
			("Farmer Project", "block", "Block"),
			("Farmer Project", "village", "Village"),
			("Farmer Project", "cluster", "Cluster"),
			("Project Task", "district", "District"),
			("Project Task", "block", "Block"),
			("Project Task", "cluster", "Cluster"),
			("Village", "district", "District"),
			("Village", "block", "Block"),
			("Village", "cluster", "Cluster"),
			("Block", "district", "District"),
			("Cluster", "district", "District"),
			("Cluster", "block", "Block"),
			("Officer Assignment History", "district", "District"),
			("Officer Assignment History", "block", "Block"),
			("Officer Assignment History", "cluster", "Cluster"),
			("Notification", "district", "District"),
			("Notification", "block", "Block"),
			("Warehouse", "district", "District"),
			("Warehouse", "block", "Block"),
			("Stock Ledger Entry", "block", "Block"),
			("Project Material Allocation", "block", "Block"),
			("Timeline Event", "district", "District"),
			("Timeline Event", "block", "Block"),
		]
	return link_fields


def _iter_link_fields():
	for row in _get_link_fields():
		yield row


def _count_refs(doctype: str, fieldname: str, value: str) -> int:
	if not value or not frappe.db.table_exists(f"tab{doctype}"):
		return 0
	return frappe.db.count(doctype, {fieldname: value})


def _append_change(plan: MigrationPlan, change: PlannedChange) -> None:
	key = (change.doctype, change.name, change.fieldname, change.new_value)
	existing = {(c.doctype, c.name, c.fieldname, c.new_value) for c in plan.changes}
	if key in existing:
		return
	plan.changes.append(change)
	plan.log(f"  UPDATE {change.doctype} {change.name}.{change.fieldname}: {change.old_value} → {change.new_value}")


def _scan_reference_updates(plan: MigrationPlan, block_map: dict[str, dict]) -> None:
	value_map: dict[str, dict[str, str]] = {
		"District": {LEGACY_DISTRICT: LGD_DISTRICT},
		"Block": {},
		"Village": {},
		"Cluster": {},
	}
	for legacy_id, info in block_map.items():
		if info["lgd_block"]:
			value_map["Block"][legacy_id] = info["lgd_block"]

	plan.log("")
	plan.log("=== SCAN LINK REFERENCES ===")
	link_fields = _get_link_fields()
	plan.log(f"  Geography link fields to scan: {len(link_fields)}")
	for dt, fieldname, options in link_fields:
		old_values = value_map.get(options, {})
		for old_val, new_val in old_values.items():
			if old_val == new_val:
				continue
			names = frappe.get_all(
				dt,
				filters={fieldname: old_val},
				pluck="name",
				limit_page_length=500,
			)
			for name in names:
				_append_change(
					plan,
					PlannedChange(
						doctype=dt,
						name=name,
						fieldname=fieldname,
						old_value=old_val,
						new_value=new_val,
						reason=f"{options} migration",
					),
				)


def _effective_refs(link_option: str, old_value: str, plan: MigrationPlan) -> int:
	link_fields = [(dt, fn, opt) for dt, fn, opt in _iter_link_fields() if opt == link_option]
	total = sum(_count_refs(dt, fn, old_value) for dt, fn, _ in link_fields)
	for change in plan.changes:
		for dt, fn, _ in link_fields:
			if change.doctype == dt and change.fieldname == fn and change.old_value == old_value:
				total = max(0, total - 1)
	return total


def _plan_village_vlg01(plan: MigrationPlan, target_block: str) -> None:
	if not frappe.db.exists("Village", "VLG01"):
		return
	current_district = frappe.db.get_value("Village", "VLG01", "district")
	current_block = frappe.db.get_value("Village", "VLG01", "block")
	if current_district != LGD_DISTRICT:
		_append_change(
			plan,
			PlannedChange(
				"Village",
				"VLG01",
				"district",
				current_district,
				LGD_DISTRICT,
				"reparent demo village to LGD district",
			),
		)
	if current_block != target_block:
		_append_change(
			plan,
			PlannedChange(
				"Village",
				"VLG01",
				"block",
				current_block,
				target_block,
				"reparent demo village to LGD Polur block",
			),
		)
	plan.log(f"  Village VLG01: district→{LGD_DISTRICT}, block→{target_block} (keep VLG01)")


def _live_block_ref_count(block_id: str) -> int:
	total = 0
	details: list[str] = []
	for dt in SAFETY_REF_DOCTYPES:
		if not frappe.db.table_exists(f"tab{dt}"):
			continue
		for _dt, fieldname, options in _get_link_fields():
			if _dt != dt or options != "Block":
				continue
			count = _count_refs(dt, fieldname, block_id)
			if count:
				details.append(f"{dt}.{fieldname}={count}")
				total += count
	return total


def _plan_delete_orphan_blocks(plan: MigrationPlan, block_map: dict[str, dict]) -> None:
	plan.log("")
	plan.log("=== PHASE 3d: ORPHAN BLOCK DELETION (planned) ===")
	for legacy_id in ORPHAN_BLOCK_DELETE_IDS:
		info = block_map.get(legacy_id)
		if not info or info.get("action") != "delete_orphan":
			continue
		ref_count = _effective_refs("Block", legacy_id, plan)
		if ref_count == 0:
			plan.deletes.append(
				("Block", legacy_id, f"orphan placeholder '{info['legacy_name']}' — no LGD code")
			)
			plan.log(f"  DELETE orphan block {legacy_id} ({info['legacy_name']})")
		else:
			plan.warnings.append(
				f"SKIP delete {legacy_id} — {ref_count} block reference(s) remain after migration plan"
			)


def _delete_orphan_blocks_live(plan: MigrationPlan, block_map: dict[str, dict]) -> None:
	plan.log("")
	plan.log("=== PHASE 3d: ORPHAN BLOCK DELETION (live safety check) ===")
	for legacy_id in ORPHAN_BLOCK_DELETE_IDS:
		if not frappe.db.exists("Block", legacy_id):
			continue
		ref_count = _live_block_ref_count(legacy_id)
		if ref_count > 0:
			msg = f"SKIP delete {legacy_id} — {ref_count} live block reference(s) remain"
			plan.warnings.append(msg)
			plan.log(f"  ⚠️  {msg}")
			continue
		name = block_map.get(legacy_id, {}).get("legacy_name", legacy_id)
		frappe.delete_doc("Block", legacy_id, force=True, ignore_permissions=True)
		plan.log(f"  Deleted orphan block {legacy_id} ({name})")


def _plan_delete_legacy_blocks(plan: MigrationPlan, block_map: dict[str, dict]) -> None:
	for legacy_id, info in block_map.items():
		if info["action"] != "merge" or not info["lgd_block"]:
			continue
		ref_count = _effective_refs("Block", legacy_id, plan)
		if ref_count == 0:
			plan.deletes.append(("Block", legacy_id, f"merged into {info['lgd_block']}"))
			plan.log(f"  DELETE legacy block {legacy_id} (merged → {info['lgd_block']})")
		else:
			plan.warnings.append(f"Cannot delete {legacy_id} — still {ref_count} block refs after plan")


def _plan_delete_tvm(plan: MigrationPlan) -> None:
	ref_count = _effective_refs("District", LEGACY_DISTRICT, plan)
	if ref_count == 0 and frappe.db.exists("District", LEGACY_DISTRICT):
		plan.deletes.append(("District", LEGACY_DISTRICT, "orphan after migration"))
		plan.log(f"  DELETE orphan district {LEGACY_DISTRICT}")
	elif ref_count:
		plan.warnings.append(f"Cannot delete {LEGACY_DISTRICT} — {ref_count} district refs remain after plan")


def _validate_farmer_count(plan: MigrationPlan) -> None:
	affected_farmers = {
		c.name
		for c in plan.changes
		if c.doctype == "Farmer" and c.fieldname in ("district", "block", "village")
	}
	if len(affected_farmers) > 2:
		plan.errors.append(f"Unexpected farmer count affected: {len(affected_farmers)} — STOP")
	elif len(affected_farmers) < 2:
		plan.warnings.append(
			f"Only {len(affected_farmers)} farmer(s) in migration plan — expected 2 demo farmers"
		)


def build_plan() -> MigrationPlan:
	plan = MigrationPlan()
	plan.log("=== MIGRATION PLAN (Strategy A) ===")
	plan.log(f"Legacy district: {LEGACY_DISTRICT} → LGD: {LGD_DISTRICT}")
	plan.log("")
	plan.log("=== BLOCK NAME MAPPING ===")

	block_map = _build_block_mapping(plan)
	plan.block_map = block_map

	if plan.errors:
		return plan

	_scan_reference_updates(plan, block_map)
	blk01_target = block_map.get("BLK01", {}).get("lgd_block") or BLK01_POLUR_FALLBACK
	_plan_village_vlg01(plan, blk01_target)
	_plan_delete_legacy_blocks(plan, block_map)
	_plan_delete_orphan_blocks(plan, block_map)
	_plan_delete_tvm(plan)
	_validate_farmer_count(plan)

	plan.log("")
	plan.log("=== SUMMARY ===")
	plan.log(f"  Planned field updates: {len(plan.changes)}")
	plan.log(f"  Planned deletes: {len(plan.deletes)}")
	plan.log(f"  Warnings: {len(plan.warnings)}")
	plan.log(f"  Errors: {len(plan.errors)}")
	for w in plan.warnings:
		plan.log(f"  ⚠️  {w}")
	for e in plan.errors:
		plan.log(f"  ❌ {e}")

	return plan


def _apply_change(change: PlannedChange) -> None:
	frappe.db.set_value(change.doctype, change.name, change.fieldname, change.new_value, update_modified=False)


def _apply_plan(plan: MigrationPlan) -> None:
	try:
		seen: set[tuple[str, str, str]] = set()
		for change in plan.changes:
			key = (change.doctype, change.name, change.fieldname)
			if key in seen:
				continue
			seen.add(key)
			_apply_change(change)

		for dt, name, reason in plan.deletes:
			if dt != "Block":
				continue
			if name in ORPHAN_BLOCK_DELETE_IDS:
				continue
			if frappe.db.exists(dt, name):
				frappe.delete_doc(dt, name, force=True, ignore_permissions=True)
				print(f"Deleted {dt} {name} ({reason})")

		_delete_orphan_blocks_live(plan, plan.block_map)

		for dt, name, reason in plan.deletes:
			if dt == "District" and frappe.db.exists(dt, name):
				frappe.delete_doc(dt, name, force=True, ignore_permissions=True)
				print(f"Deleted {dt} {name} ({reason})")

		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
		raise


def run(dry_run: bool = True) -> dict:
	"""Execute or preview legacy geography migration."""
	plan = build_plan()
	result = {
		"dry_run": dry_run,
		"errors": plan.errors,
		"warnings": plan.warnings,
		"changes": len(plan.changes),
		"deletes": len(plan.deletes),
		"block_map": plan.block_map,
	}

	if plan.errors:
		print("")
		print("ABORT — fix errors before running live migration.")
		return result

	if dry_run:
		print("")
		print("DRY-RUN complete — no database changes made.")
		return result

	print("")
	print("Applying live migration…")
	_apply_plan(plan)
	print("Live migration committed.")
	return result


def run_live() -> dict:
	"""Convenience entrypoint: bench execute agriflow.scripts.migrate_legacy_geography.run_live"""
	return run(dry_run=False)


@click.command("migrate-legacy-geography")
@click.option("--dry-run/--live", default=True, show_default=True)
def migrate_legacy_geography_command(dry_run: bool) -> None:
	run(dry_run=dry_run)


commands = [migrate_legacy_geography_command]
