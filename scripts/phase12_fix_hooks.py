#!/usr/bin/env python3
from pathlib import Path

p = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow/hooks.py")
text = p.read_text(encoding="utf-8")
text = text.replace(
	'\t"agriflow.notification_engine.services.sla_alerts.scan_task_overdue_notifications",\n',
	"",
)
if "scan_task_overdue_notifications" not in text:
	text = text.rstrip() + """

scheduler_events = {
\t"daily": [
\t\t"agriflow.notification_engine.services.sla_alerts.scan_task_overdue_notifications",
\t],
}
"""
p.write_text(text, encoding="utf-8")
print("fixed", p)
