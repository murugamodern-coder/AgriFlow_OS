#!/usr/bin/env python3
"""Download LGD mirror CSVs and emit Tamil Nadu geography files for AgriFlow import.

Source: planemad/india-local-government-directory (LGD mirror, state_code 33 = TN)
Outputs:
  tn_districts.csv  — district_code, district_name, lgd_code
  tn_blocks.csv     — block_code, block_name, lgd_code, district_code
  tn_villages.csv   — village_code, village_name, lgd_code, pincode, block_code

Note: LGD villages attach to Sub-District (Taluk). We import sub-districts as Block
records so the cascade District → Block → Village matches official village parent keys.
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen

BASE = "https://raw.githubusercontent.com/planemad/india-local-government-directory/master/administrative"
VILLAGE_ZIP = f"{BASE}/4-village.csv.zip"
TN_STATE = "33"
OUT_DIR = Path(__file__).resolve().parent


def fetch_text(url: str) -> str:
	with urlopen(url, timeout=120) as resp:
		return resp.read().decode("utf-8-sig")


def fetch_bytes(url: str) -> bytes:
	with urlopen(url, timeout=300) as resp:
		return resp.read()


def read_csv(text: str) -> list[dict[str, str]]:
	reader = csv.DictReader(io.StringIO(text))
	rows: list[dict[str, str]] = []
	for row in reader:
		normalized = {(k or "").strip().lower().replace(" ", "_"): (v or "").strip() for k, v in row.items()}
		rows.append(normalized)
	return rows


def pick(row: dict[str, str], *keys: str) -> str:
	for key in keys:
		norm = key.strip().lower().replace(" ", "_")
		if norm in row and row[norm]:
			return row[norm]
	return ""


def read_subdistrict_blocks(text: str) -> list[dict[str, str]]:
	"""Sub-district rows become Block records (village CSV parent key)."""
	reader = csv.reader(io.StringIO(text))
	next(reader, None)
	rows: list[dict[str, str]] = []
	for row in reader:
		if len(row) < 8 or row[1].strip() != TN_STATE:
			continue
		rows.append(
			{
				"district_code": row[3].strip(),
				"district_name": row[4].strip() if len(row) > 4 else "",
				"block_code": row[5].strip(),
				"block_name": row[7].strip(),
			}
		)
	return rows


def read_villages_csv(zbytes: bytes, district_codes: set[str]) -> list[dict[str, str]]:
	with zipfile.ZipFile(io.BytesIO(zbytes)) as zf:
		inner = next(n for n in zf.namelist() if n.endswith(".csv"))
		text = zf.read(inner).decode("utf-8-sig")
	reader = csv.reader(io.StringIO(text))
	next(reader, None)
	rows: list[dict[str, str]] = []
	for row in reader:
		if len(row) < 8:
			continue
		state_code = row[12].strip() if len(row) > 12 else ""
		district_code = row[1].strip()
		if state_code != TN_STATE and district_code not in district_codes:
			continue
		name_en = row[7].strip() if len(row) > 7 else ""
		name_local = row[8].strip() if len(row) > 8 else ""
		name = name_local or name_en
		rows.append(
			{
				"village_code": row[5].strip(),
				"village_name": name,
				"lgd_code": row[5].strip(),
				"pincode": "",
				"block_code": row[3].strip(),
			}
		)
	return rows


def main() -> int:
	print("Downloading LGD administrative CSVs…")
	district_rows = [r for r in read_csv(fetch_text(f"{BASE}/2-district.csv")) if pick(r, "state_code") == TN_STATE]
	block_rows = read_subdistrict_blocks(fetch_text(f"{BASE}/3-subdistrict.csv"))

	print("Downloading village zip (all-India, filtering TN)…")
	district_code_by_lgd: dict[str, str] = {}
	districts_out: list[dict[str, str]] = []
	for row in district_rows:
		lgd = pick(row, "district_code", "lgd_code")
		name = pick(row, "district_name", "district_name_english", "name")
		code = lgd
		district_code_by_lgd[lgd] = code
		districts_out.append({"district_code": code, "district_name": name, "lgd_code": lgd})

	district_codes = set(district_code_by_lgd.keys())

	blocks_out: list[dict[str, str]] = []
	block_code_by_lgd: dict[str, str] = {}
	for row in block_rows:
		lgd = row["block_code"]
		name = row["block_name"]
		district_code = district_code_by_lgd.get(row["district_code"], row["district_code"])
		code = lgd
		block_code_by_lgd[lgd] = code
		blocks_out.append(
			{
				"block_code": code,
				"block_name": name,
				"lgd_code": lgd,
				"district_code": district_code,
			}
		)

	village_rows = read_villages_csv(fetch_bytes(VILLAGE_ZIP), district_codes)
	villages_out: list[dict[str, str]] = []
	for row in village_rows:
		block_code = block_code_by_lgd.get(row["block_code"], row["block_code"])
		villages_out.append(
			{
				"village_code": row["village_code"],
				"village_name": row["village_name"],
				"lgd_code": row["lgd_code"],
				"pincode": row.get("pincode", ""),
				"block_code": block_code,
			}
		)

	def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
		with path.open("w", newline="", encoding="utf-8") as f:
			writer = csv.DictWriter(f, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows(rows)

	write_csv(OUT_DIR / "tn_districts.csv", ["district_code", "district_name", "lgd_code"], districts_out)
	write_csv(
		OUT_DIR / "tn_blocks.csv",
		["block_code", "block_name", "lgd_code", "district_code"],
		blocks_out,
	)
	write_csv(
		OUT_DIR / "tn_villages.csv",
		["village_code", "village_name", "lgd_code", "pincode", "block_code"],
		villages_out,
	)

	print(f"Districts: {len(districts_out)}")
	print(f"Blocks: {len(blocks_out)}")
	print(f"Villages: {len(villages_out)}")
	if blocks_out:
		print(f"Sample block: {blocks_out[0]}")
	if villages_out:
		print(f"Sample village: {villages_out[0]}")
		tamil = next((v for v in villages_out if any(ord(c) > 127 for c in v["village_name"])), None)
		if tamil:
			print(f"Tamil sample: {tamil['village_name']}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
