#!/usr/bin/env python3
import json
from pathlib import Path

fixtures = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/fixtures")
district = [
    {
        "doctype": "District",
        "name": "TVM",
        "district_code": "TVM",
        "district_name": "Tiruvannamalai",
        "state": "Tamil Nadu",
        "is_active": 1,
    }
]
blocks = []
for i in range(1, 13):
    code = f"BLK{i:02d}"
    blocks.append(
        {
            "doctype": "Block",
            "name": code,
            "block_code": code,
            "block_name": f"Block {i:02d}",
            "district": "TVM",
            "is_active": 1,
        }
    )
(fixtures / "district.json").write_text(json.dumps(district, indent=1) + "\n")
(fixtures / "block.json").write_text(json.dumps(blocks, indent=1) + "\n")
print("fixtures updated with name fields")
