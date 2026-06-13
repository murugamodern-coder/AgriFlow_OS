#!/usr/bin/env bash
set -euo pipefail

REPO="/mnt/c/AgriFlow_OS/AgriFlow_Main/backend/agriflow"
BENCH="/home/muruga/workspace/frappe-bench/apps/agriflow"

mkdir -p "${BENCH}/agriflow/inventory/install"
mkdir -p "${BENCH}/fixtures"

cp "${REPO}/agriflow/inventory/workspace_data.py" "${BENCH}/agriflow/inventory/workspace_data.py"
cp "${REPO}/agriflow/inventory/install/repair_inventory_workspace.py" "${BENCH}/agriflow/inventory/install/repair_inventory_workspace.py"
touch "${BENCH}/agriflow/inventory/install/__init__.py"
cp "${REPO}/fixtures/workspace_inventory.json" "${BENCH}/fixtures/workspace_inventory.json"

if ! grep -q '"Workspace"' "${BENCH}/agriflow/hooks.py"; then
	python3 <<'PY'
from pathlib import Path
p = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow/hooks.py")
text = p.read_text(encoding="utf-8")
needle = '    {"dt": "Project Stage"},\n'
insert = needle + '    {"dt": "Workspace", "filters": [["name", "in", ["Inventory"]]]},\n'
if insert not in text:
    text = text.replace(needle, insert, 1)
    p.write_text(text, encoding="utf-8")
    print("patched hooks.py")
else:
    print("hooks.py already has Workspace fixture")
PY
fi

echo "=== bench files ==="
ls -la "${BENCH}/agriflow/inventory/workspace_data.py"
ls -la "${BENCH}/agriflow/inventory/install/repair_inventory_workspace.py"
ls -la "${BENCH}/fixtures/workspace_inventory.json"
