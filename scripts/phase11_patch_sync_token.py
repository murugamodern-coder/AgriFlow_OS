#!/usr/bin/env python3
"""Patch Sync Session sync_token field (reqd=0) in bench."""
import json
from pathlib import Path

p = Path(__file__).resolve().parents[1]
# When run from WSL copy, path is under bench
for base in [
	Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow"),
	Path(__file__).resolve().parent.parent / "apps" / "agriflow" / "agriflow",
]:
	j = base / "sync_engine" / "doctype" / "sync_session" / "sync_session.json"
	if j.exists():
		d = json.loads(j.read_text())
		for f in d.get("fields", []):
			if f.get("fieldname") == "sync_token":
				f["reqd"] = 0
				break
		j.write_text(json.dumps(d, indent=1) + "\n")
		print("patched", j)
		break
else:
	raise SystemExit("sync_session.json not found")
