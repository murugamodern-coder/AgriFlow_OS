# Copyright (c) 2026, Murugan and contributors
"""Copy Phase 15 scripts into bench agriflow app."""

from __future__ import annotations

import shutil
from pathlib import Path

BENCH_AGRIFLOW = Path.home() / "workspace" / "frappe-bench" / "apps" / "agriflow" / "agriflow"
REPO_SCRIPTS = Path(__file__).resolve().parent


def execute():
	copies = [
		(REPO_SCRIPTS / "phase15_auth_api.py", BENCH_AGRIFLOW / "api" / "v1" / "auth.py"),
	]
	installed = []
	for src, dest in copies:
		if not src.exists():
			raise FileNotFoundError(src)
		dest.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy2(src, dest)
		installed.append(str(dest.relative_to(BENCH_AGRIFLOW.parent.parent)))
	# install package hook for seed/verify
	lifecycle = BENCH_AGRIFLOW / "project_lifecycle" / "install"
	lifecycle.mkdir(parents=True, exist_ok=True)
	for name in ("phase15_seed_demo.py", "phase15_verify_e2e.py"):
		shutil.copy2(REPO_SCRIPTS / name, lifecycle / name)
		installed.append(str((lifecycle / name).relative_to(BENCH_AGRIFLOW.parent.parent)))
	return {"installed": installed, "ok": True}
