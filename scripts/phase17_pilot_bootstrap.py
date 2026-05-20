# Copyright (c) 2026, Murugan and contributors
"""Pilot ops DocTypes — telemetry, feedback, operational logs."""

from __future__ import annotations

import json
from pathlib import Path

APP = Path(__file__).resolve().parents[1]  # scripts/ -> use when copied to bench


def field(fn, ft, label, **kw):
	row = {"fieldname": fn, "fieldtype": ft, "label": label}
	row.update(kw)
	return row


def doctype(name, fields, **meta):
	return {
		"doctype": "DocType",
		"name": name,
		"module": "Project Lifecycle",
		"custom": 1,
		"autoname": meta.get("autoname", "hash"),
		"engine": "InnoDB",
		"field_order": [f["fieldname"] for f in fields],
		"fields": fields,
		"permissions": [
			{
				"role": "System Manager",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 1,
				"export": 1,
				"report": 1,
			}
		],
		**{k: v for k, v in meta.items() if k not in ("autoname",)},
	}


def write(path: Path, content: str) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(content, encoding="utf-8")


def bootstrap_doctypes(bench_agriflow: Path) -> list[str]:
	"""Write DocType JSON into bench agriflow app. Call from install script with bench path."""
	base = bench_agriflow / "project_lifecycle" / "doctype"
	created = []

	telemetry_fields = [
		field("device_id", "Data", "Device ID", reqd=1, in_list_view=1),
		field("user", "Link", "User", options="User", reqd=1, in_list_view=1),
		field("app_version", "Data", "App Version", in_list_view=1),
		field("build_number", "Data", "Build Number"),
		field("platform", "Data", "Platform"),
		field("queue_pending", "Int", "Queue Pending", default="0"),
		field("queue_conflict", "Int", "Queue Conflicts", default="0"),
		field("queue_failed", "Int", "Queue Failed", default="0"),
		field("last_sync_at", "Datetime", "Last Sync At"),
		field("last_correlation_id", "Data", "Last Correlation ID"),
		field("reported_at", "Datetime", "Reported At", reqd=1, in_list_view=1),
		field("diagnostics_json", "JSON", "Diagnostics JSON"),
	]
	p = base / "pilot_device_telemetry"
	write(p / "pilot_device_telemetry.json", json.dumps(doctype("Pilot Device Telemetry", telemetry_fields, title_field="device_id"), indent=1) + "\n")
	write(p / "__init__.py", "")
	created.append("Pilot Device Telemetry")

	feedback_fields = [
		field("submitted_by", "Link", "Submitted By", options="User", reqd=1, in_list_view=1),
		field("device_id", "Data", "Device ID"),
		field("app_version", "Data", "App Version", in_list_view=1),
		field("category", "Select", "Category", options="sync\nux\ninventory\ntask\nnetwork\nother", reqd=1, in_list_view=1),
		field("severity", "Select", "Severity", options="low\nmedium\nhigh\ncritical", default="medium", in_list_view=1),
		field("body", "Text", "Feedback", reqd=1),
		field("farmer_project", "Link", "Farmer Project", options="Farmer Project"),
		field("workflow_status", "Select", "Status", options="new\nreviewed\nresolved", default="new", in_list_view=1),
		field("submitted_on", "Datetime", "Submitted On", reqd=1, in_list_view=1),
	]
	p = base / "pilot_operational_feedback"
	write(p / "pilot_operational_feedback.json", json.dumps(doctype("Pilot Operational Feedback", feedback_fields, title_field="submitted_by"), indent=1) + "\n")
	write(p / "__init__.py", "")
	created.append("Pilot Operational Feedback")

	log_fields = [
		field("event_type", "Data", "Event Type", reqd=1, in_list_view=1),
		field("source", "Data", "Source", in_list_view=1),
		field("device_id", "Data", "Device ID"),
		field("user", "Link", "User", options="User"),
		field("request_id", "Data", "Request ID"),
		field("correlation_id", "Data", "Correlation ID"),
		field("payload_json", "JSON", "Payload JSON"),
		field("recorded_on", "Datetime", "Recorded On", reqd=1, in_list_view=1),
	]
	p = base / "operational_log"
	write(p / "operational_log.json", json.dumps(doctype("Operational Log", log_fields, title_field="event_type"), indent=1) + "\n")
	write(p / "__init__.py", "")
	created.append("Operational Log")

	return created


if __name__ == "__main__":
	print(bootstrap_doctypes(Path("agriflow")))
