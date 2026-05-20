#!/usr/bin/env python3
"""Fix broken doc_events block in agriflow hooks.py."""
from pathlib import Path

p = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow/hooks.py")
text = p.read_text(encoding="utf-8")

start = text.find("# after_migrate = [\"agriflow.project_lifecycle.install.seed_project_stages.after_migrate\"]")
if start == -1:
    start = text.find("doc_events = {\n# \t\"*\":")
end_marker = "# }\n\n# Scheduled Tasks"
end = text.find(end_marker, start)
if start != -1 and end != -1:
    text = (
        text[:start]
        + "# doc_events and after_migrate are configured in the Fixtures section below.\n\n"
        + text[end + len("# }\n\n") :]
    )

if 'after_migrate = ["agriflow.project_lifecycle.install.seed_project_stages.after_migrate"]' not in text:
    text = text.replace(
        "# Fixtures\n# --------\nfixtures = [",
        'after_migrate = ["agriflow.project_lifecycle.install.seed_project_stages.after_migrate"]\n\n# Fixtures\n# --------\nfixtures = [',
        1,
    )

p.write_text(text, encoding="utf-8")
print("hooks.py fixed")
