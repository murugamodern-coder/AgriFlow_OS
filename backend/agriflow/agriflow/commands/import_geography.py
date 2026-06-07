# Copyright (c) 2026, Murugan and contributors
"""Bulk import Tamil Nadu geography from LGD CSV files."""

from __future__ import annotations

import csv
from pathlib import Path

import click
import frappe

DEFAULT_DATA_DIR = "/mnt/c/AgriFlow_OS/AgriFlow_Main/scripts/geography_data"
STATE_NAME = "Tamil Nadu"


def _ensure_state() -> None:
	if not frappe.db.exists("Geo State", STATE_NAME):
		frappe.get_doc(
			{
				"doctype": "Geo State",
				"state_name": STATE_NAME,
				"lgd_code": "33",
				"country": "India",
				"is_active": 1,
			}
		).insert(ignore_permissions=True)
	click.echo(f"State: {STATE_NAME}")


def _legacy_district_state_fixup() -> None:
	for row in frappe.get_all("District", fields=["name"]):
		frappe.db.set_value("District", row.name, "state", STATE_NAME)


def import_geography(data_dir: str | None = None) -> None:
	"""Import real Tamil Nadu geography from LGD CSVs."""
	data_path = Path(data_dir or DEFAULT_DATA_DIR)
	if not data_path.exists():
		raise click.ClickException(f"Data directory not found: {data_path}")

	_ensure_state()
	_legacy_district_state_fixup()

	district_file = data_path / "tn_districts.csv"
	block_file = data_path / "tn_blocks.csv"
	village_file = data_path / "tn_villages.csv"
	for path in (district_file, block_file, village_file):
		if not path.exists():
			raise click.ClickException(f"Missing CSV: {path}")

	district_count = 0
	with district_file.open(encoding="utf-8") as handle:
		for row in csv.DictReader(handle):
			code = row["district_code"].strip()
			if frappe.db.exists("District", code):
				continue
			frappe.get_doc(
				{
					"doctype": "District",
					"district_code": code,
					"district_name": row["district_name"].strip(),
					"lgd_code": row.get("lgd_code", "").strip(),
					"state": STATE_NAME,
					"is_active": 1,
				}
			).insert(ignore_permissions=True)
			district_count += 1
	frappe.db.commit()
	click.echo(f"Districts imported: {district_count}")

	block_count = 0
	with block_file.open(encoding="utf-8") as handle:
		for row in csv.DictReader(handle):
			code = row["block_code"].strip()
			if frappe.db.exists("Block", code):
				continue
			frappe.get_doc(
				{
					"doctype": "Block",
					"block_code": code,
					"block_name": row["block_name"].strip(),
					"lgd_code": row.get("lgd_code", "").strip(),
					"district": row["district_code"].strip(),
					"is_active": 1,
				}
			).insert(ignore_permissions=True)
			block_count += 1
			if block_count % 100 == 0:
				frappe.db.commit()
	frappe.db.commit()
	click.echo(f"Blocks imported: {block_count}")

	village_count = 0
	with village_file.open(encoding="utf-8") as handle:
		for row in csv.DictReader(handle):
			code = row["village_code"].strip()
			if frappe.db.exists("Village", code):
				continue
			frappe.get_doc(
				{
					"doctype": "Village",
					"village_code": code,
					"village_name": row["village_name"].strip(),
					"lgd_code": row.get("lgd_code", "").strip(),
					"pincode": row.get("pincode", "").strip(),
					"block": row["block_code"].strip(),
					"is_active": 1,
				}
			).insert(ignore_permissions=True)
			village_count += 1
			if village_count % 500 == 0:
				frappe.db.commit()
				click.echo(f"  ... {village_count} villages")
	frappe.db.commit()
	click.echo(f"Villages imported: {village_count}")
	click.echo("Geography import complete")


def report_counts() -> None:
	for dt in ("Geo State", "District", "Block", "Village"):
		click.echo(f"{dt}: {frappe.db.count(dt)}")


@click.command("import-geography")
@click.option("--data-dir", default=DEFAULT_DATA_DIR, show_default=True)
def import_geography_command(data_dir: str) -> None:
	import_geography(data_dir=data_dir)


commands = [import_geography_command]
