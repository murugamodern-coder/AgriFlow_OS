# Copyright (c) 2026, Murugan and contributors
"""Patch timeline.py task emit client_id length."""

from pathlib import Path

PATH = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow/project_lifecycle/services/timeline.py")
text = PATH.read_text(encoding="utf-8")

helper = '''

def _task_timeline_client_id(task, suffix: str) -> str | None:
\t"""Timeline client_id max 36 chars — use task name hash when needed."""
\tbase = (task.client_id or task.name or "")[:32]
\tif not base:
\t\treturn None
\tkey = f"{base}-{suffix}"
\treturn key if len(key) <= 36 else base[: max(0, 36 - len(suffix) - 1)] + "-" + suffix
'''

if "_task_timeline_client_id" not in text:
    anchor = "\ndef get_timeline_service"
    text = text.replace(anchor, helper + anchor)

text = text.replace(
    'client_id=f"{task.client_id}-created" if task.client_id else None,',
    'client_id=_task_timeline_client_id(task, "created"),',
)

PATH.write_text(text, encoding="utf-8")
print("patched timeline.py")
