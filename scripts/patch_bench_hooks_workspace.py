from pathlib import Path

p = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow/hooks.py")
text = p.read_text(encoding="utf-8")
needle = '    {"dt": "Project Stage"},\n'
insert = needle + '    {"dt": "Workspace", "filters": [["name", "in", ["Inventory"]]]},\n'
if insert not in text:
    if needle not in text:
        raise SystemExit("needle not found in hooks.py")
    p.write_text(text.replace(needle, insert, 1), encoding="utf-8")
    print("patched hooks.py")
else:
    print("hooks.py already patched")
