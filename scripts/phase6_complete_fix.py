#!/usr/bin/env python3
import json
from pathlib import Path

fixtures = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/fixtures")
blocks = [
    {
        "doctype": "Block",
        "block_code": f"BLK{i:02d}",
        "block_name": f"Block {i:02d}",
        "district": "TVM",
        "is_active": 1,
    }
    for i in range(1, 13)
]
(fixtures / "block.json").write_text(json.dumps(blocks, indent=1) + "\n")
print("wrote block.json")

hooks = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow/hooks.py")
content = hooks.read_text(encoding="utf-8")
content = content.replace('app_title = "yes"', 'app_title = "AgriFlow OS"')
if "fixtures = [" not in content:
    content = content.rstrip() + '''

# Fixtures
# --------
fixtures = [
    {"dt": "District"},
    {"dt": "Block"},
]

# Document Events
# ---------------
doc_events = {
    "Officer Assignment History": {
        "after_insert": "agriflow.officer_network.services.officer_assignment.on_assignment_change",
        "on_update": "agriflow.officer_network.services.officer_assignment.on_assignment_change",
    },
}
'''
hooks.write_text(content, encoding="utf-8")
print("updated hooks.py")
