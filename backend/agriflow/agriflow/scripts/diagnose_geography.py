# Copyright (c) 2026, Murugan and contributors
"""Read-only geography duplicate / legacy vs LGD diagnostic."""

from __future__ import annotations

from collections import Counter

import frappe


def run_diagnosis() -> dict:
	"""Print and return diagnostic snapshot for geography cleanup."""
	lines: list[str] = []

	def log(msg: str = "") -> None:
		print(msg)
		lines.append(msg)

	districts = frappe.get_all(
		"District",
		fields=["name", "district_name", "state", "lgd_code"],
		order_by="district_name",
	)

	log("=== ALL DISTRICTS ===")
	log(f"{'name':10} | {'district_name':25} | {'lgd':6} | blocks | villages | farmers")
	log("-" * 80)
	district_rows = []
	for d in districts:
		block_count = frappe.db.count("Block", {"district": d.name})
		village_count = frappe.db.count("Village", {"district": d.name})
		farmer_count = frappe.db.count("Farmer", {"district": d.name})
		project_count = frappe.db.count("Farmer Project", {"district": d.name}) if frappe.db.table_exists(
			"tabFarmer Project"
		) else 0
		row = {
			**d,
			"blocks": block_count,
			"villages": village_count,
			"farmers": farmer_count,
			"projects": project_count,
		}
		district_rows.append(row)
		log(
			f"{d.name:10} | {(d.district_name or ''):25} | {(d.lgd_code or ''):6} | "
			f"{block_count:6} | {village_count:8} | {farmer_count:7}"
		)

	names_lower = [d.district_name.lower() for d in districts if d.district_name]
	dupes = [name for name, count in Counter(names_lower).items() if count > 1]
	log("")
	log(f"Total districts: {len(districts)}")
	log(f"Duplicate district names (case-insensitive): {dupes}")

	log("")
	log("=== TIRUVANNAMALAI VARIANTS ===")
	tvm_variants = frappe.db.sql(
		"""
		SELECT name, district_name, lgd_code, state
		FROM `tabDistrict`
		WHERE LOWER(district_name) LIKE %s
		ORDER BY name
		""",
		("%iruvannamalai%",),
		as_dict=True,
	)
	for v in tvm_variants:
		log(
			f"  {v.name} | {v.district_name} | lgd={v.lgd_code or 'N/A'} | "
			f"blocks={frappe.db.count('Block', {'district': v.name})} | "
			f"villages={frappe.db.count('Village', {'district': v.name})} | "
			f"farmers={frappe.db.count('Farmer', {'district': v.name})}"
		)

	log("")
	log("=== LEGACY DEMO BLOCKS (district=TVM) ===")
	demo_blocks = frappe.get_all(
		"Block",
		filters={"district": "TVM"},
		fields=["name", "block_name", "lgd_code", "district"],
		order_by="block_name",
	)
	log(f"Demo blocks ({len(demo_blocks)}):")
	for b in demo_blocks:
		farmers = frappe.db.count("Farmer", {"block": b.name})
		villages = frappe.db.count("Village", {"block": b.name})
		projects = frappe.db.count("Farmer Project", {"block": b.name}) if frappe.db.table_exists(
			"tabFarmer Project"
		) else 0
		log(f"  {b.name:8} | {b.block_name:20} | lgd={b.lgd_code or 'N/A'} | v={villages} f={farmers} p={projects}")

	log("")
	lgd_tvm = next((d.name for d in districts if (d.district_name or "").upper() == "TIRUVANNAMALAI"), None)
	if not lgd_tvm:
		lgd_tvm = "593"
	log(f"=== LGD TIRUVANNAMALAI BLOCKS (district={lgd_tvm}) ===")
	lgd_tvm_blocks = frappe.get_all(
		"Block",
		filters={"district": lgd_tvm},
		fields=["name", "block_name", "lgd_code"],
		order_by="block_name",
	)
	log(f"LGD Tiruvannamalai blocks ({len(lgd_tvm_blocks)}):")
	for b in lgd_tvm_blocks[:20]:
		villages = frappe.db.count("Village", {"block": b.name})
		log(f"  {b.name:8} | {b.block_name:20} | lgd={b.lgd_code or 'N/A'} | villages={villages}")
	if len(lgd_tvm_blocks) > 20:
		log(f"  ... and {len(lgd_tvm_blocks) - 20} more")

	log("")
	log("=== LEGACY VILLAGES (district=TVM) ===")
	legacy_villages = frappe.get_all(
		"Village",
		filters={"district": "TVM"},
		fields=["name", "village_name", "block", "cluster"],
	)
	for v in legacy_villages:
		log(f"  {v.name} | {v.village_name} | block={v.block} | cluster={v.cluster or 'N/A'}")

	log("")
	log("=== FARMERS ON LEGACY TVM ===")
	legacy_farmers = frappe.get_all(
		"Farmer",
		filters={"district": "TVM", "is_deleted": 0},
		fields=["name", "farmer_name", "block", "village", "cluster"],
	)
	for f in legacy_farmers:
		log(f"  {f.name} | {f.farmer_name} | block={f.block} | village={f.village}")

	log("")
	log("=== POLUR BLOCK NAME SEARCH ===")
	polur_blocks = frappe.db.sql(
		"""
		SELECT name, block_name, district
		FROM `tabBlock`
		WHERE LOWER(block_name) LIKE %s
		ORDER BY district, block_name
		""",
		("%polur%",),
		as_dict=True,
	)
	for b in polur_blocks:
		log(f"  {b.name} | {b.block_name} | district={b.district} | villages={frappe.db.count('Village', {'block': b.name})}")

	log("")
	log("=== GLOBAL COUNTS ===")
	log(f"Districts: {frappe.db.count('District')}")
	log(f"Blocks: {frappe.db.count('Block')}")
	log(f"Villages: {frappe.db.count('Village')}")
	log(f"Farmers: {frappe.db.count('Farmer', {'is_deleted': 0})}")

	log("")
	log("=== CROSS-REFERENCES TO LEGACY TVM/BLK ===")
	for dt, flt in [
		("Farmer Project", {"district": "TVM"}),
		("Farmer Project", {"block": "BLK01"}),
		("Project Task", {"block": "BLK01"}),
		("Cluster", {"block": "BLK01"}),
	]:
		if frappe.db.table_exists(f"tab{dt}"):
			count = frappe.db.count(dt, flt)
			log(f"  {dt} {flt}: {count}")

	return {
		"district_count": len(districts),
		"duplicate_names": dupes,
		"tvm_variants": tvm_variants,
		"demo_blocks": demo_blocks,
		"lgd_tvm_blocks_count": len(lgd_tvm_blocks),
		"legacy_farmers": legacy_farmers,
		"lines": lines,
	}


if __name__ == "__main__":
	run_diagnosis()
