#!/usr/bin/env python3
"""Phase 12 — Notification Engine bootstrap."""
from __future__ import annotations

import json
from pathlib import Path

APP = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
MODULE = "Notification Engine"
NOTIFICATION_TYPES = (
	"task_assigned\ntask_reassigned\ntask_completed\ntask_overdue\n"
	"project_stage_changed\nmanual_note\nsystem_alert"
)
DELIVERY_STATUSES = "delivered\nskipped_preference\nskipped_duplicate\nskipped_no_recipient"
PERMS_SM = [
	{
		"role": "System Manager",
		"read": 1,
		"write": 1,
		"create": 1,
		"delete": 0,
		"export": 1,
		"print": 1,
		"email": 1,
		"report": 1,
		"share": 1,
	}
]
SCRIPTS = Path(__file__).resolve().parent


def write(path: Path, content: str) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(content, encoding="utf-8")
	print(f"  wrote {path.relative_to(APP.parent)}")


def field(fn, ft, label, **kw) -> dict:
	f = {
		"fieldname": fn,
		"fieldtype": ft,
		"label": label,
		"reqd": kw.get("reqd", 0),
		"read_only": kw.get("read_only", 0),
		"in_list_view": kw.get("in_list_view", 0),
		"in_standard_filter": kw.get("in_standard_filter", 0),
		"search_index": kw.get("search_index", 0),
		"unique": kw.get("unique", 0),
	}
	for k in ("options", "default", "length"):
		if k in kw and kw[k] is not None:
			f[k] = kw[k]
	return f


def doctype(name, fields, *, autoname, title_field="", track_changes=0, sort_field="modified"):
	return {
		"actions": [],
		"allow_rename": 0,
		"autoname": autoname,
		"creation": "2026-05-20 00:00:00.000000",
		"doctype": "DocType",
		"engine": "InnoDB",
		"field_order": [f["fieldname"] for f in fields],
		"fields": fields,
		"module": MODULE,
		"name": name,
		"owner": "Administrator",
		"permissions": PERMS_SM,
		"sort_field": sort_field,
		"sort_order": "DESC",
		"track_changes": track_changes,
		"title_field": title_field,
	}


def write_doctypes() -> None:
	ntf_fields = [
		field("delivery_key", "Data", "Delivery Key", reqd=1, unique=1, length=64, search_index=1),
		field("recipient", "Link", "Recipient", options="User", reqd=1, in_list_view=1, in_standard_filter=1),
		field(
			"notification_type",
			"Select",
			"Notification Type",
			options=NOTIFICATION_TYPES,
			reqd=1,
			in_list_view=1,
			in_standard_filter=1,
		),
		field("title_i18n_key", "Data", "Title i18n Key", reqd=1),
		field("body_preview", "Data", "Body Preview", length=140),
		field("payload_json", "JSON", "Payload"),
		field("farmer_project", "Link", "Farmer Project", options="Farmer Project", reqd=1, in_list_view=1),
		field("farmer", "Link", "Farmer", options="Farmer", reqd=1),
		field("block", "Link", "Block", options="Block", in_standard_filter=1),
		field("district", "Link", "District", options="District"),
		field("timeline_event", "Link", "Timeline Event", options="Timeline Event"),
		field("source_doctype", "Data", "Source DocType"),
		field("source_name", "Data", "Source Name"),
		field("priority", "Select", "Priority", options="low\nnormal\nhigh", default="normal"),
		field("created_on", "Datetime", "Created On", reqd=1, in_list_view=1),
		field("read_on", "Datetime", "Read On"),
		field("is_deleted", "Check", "Is Deleted", default="0"),
	]
	base = APP / "notification_engine" / "doctype" / "notification"
	write(base / "__init__.py", "")
	write(
		base / "notification.json",
		json.dumps(
			doctype(
				"Notification",
				ntf_fields,
				autoname="hash",
				title_field="notification_type",
				sort_field="created_on",
			),
			indent=1,
		)
		+ "\n",
	)
	write(
		base / "notification.py",
		'''# Copyright (c) 2026
import frappe
from frappe import _
from frappe.model.document import Document

from agriflow.notification_engine.services.delivery import MUTABLE_FIELDS, NOTIFICATION_FLAG


class Notification(Document):
	def validate(self):
		if self.is_new():
			return
		if frappe.flags.get(NOTIFICATION_FLAG):
			return
		for df in self.meta.fields:
			fn = df.fieldname
			if fn in MUTABLE_FIELDS:
				continue
			if self.has_value_changed(fn):
				frappe.throw(_("Notification content is immutable"))
''',
	)

	pref_fields = [
		field("user", "Link", "User", options="User", reqd=1, unique=1),
		field("preferences_json", "JSON", "Preferences JSON"),
	]
	pbase = APP / "notification_engine" / "doctype" / "notification_preference"
	write(pbase / "__init__.py", "")
	write(
		pbase / "notification_preference.json",
		json.dumps(doctype("Notification Preference", pref_fields, autoname="hash", title_field="user"), indent=1)
		+ "\n",
	)
	write(
		pbase / "notification_preference.py",
		"# Copyright (c) 2026\nimport frappe\nfrom frappe.model.document import Document\n\nclass NotificationPreference(Document):\n\tpass\n",
	)

	log_fields = [
		field("delivery_key", "Data", "Delivery Key", reqd=1, unique=1, length=64, search_index=1),
		field("timeline_event", "Link", "Timeline Event", options="Timeline Event", in_list_view=1),
		field("notification", "Link", "Notification", options="Notification"),
		field("recipient", "Link", "Recipient", options="User", in_list_view=1),
		field(
			"notification_type",
			"Select",
			"Notification Type",
			options=NOTIFICATION_TYPES,
			reqd=1,
			in_list_view=1,
		),
		field("status", "Select", "Status", options=DELIVERY_STATUSES, reqd=1, in_list_view=1),
		field("processed_on", "Datetime", "Processed On", reqd=1, read_only=1),
	]
	lbase = APP / "notification_engine" / "doctype" / "notification_delivery_log"
	write(lbase / "__init__.py", "")
	write(
		lbase / "notification_delivery_log.json",
		json.dumps(
			doctype(
				"Notification Delivery Log",
				log_fields,
				autoname="hash",
				title_field="delivery_key",
				sort_field="processed_on",
			),
			indent=1,
		)
		+ "\n",
	)
	write(
		lbase / "notification_delivery_log.py",
		'''# Copyright (c) 2026
import frappe
from frappe import _
from frappe.model.document import Document

from agriflow.notification_engine.services.delivery import DELIVERY_LOG_FLAG


class NotificationDeliveryLog(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw(_("Notification Delivery Log is append-only"))

	def on_update(self):
		if not frappe.flags.get(DELIVERY_LOG_FLAG):
			frappe.throw(_("Notification Delivery Log is immutable"))
''',
	)


def copy_services() -> None:
	dest = APP / "notification_engine"
	for sub in ("", "services", "api"):
		(dest / sub).mkdir(parents=True, exist_ok=True)
	write(dest / "__init__.py", "")
	write(dest / "services" / "__init__.py", "")
	write(dest / "api" / "__init__.py", "")
	mapping = {
		"phase12_i18n_keys.py": dest / "services" / "i18n_keys.py",
		"phase12_recipients.py": dest / "services" / "recipients.py",
		"phase12_preferences.py": dest / "services" / "preferences.py",
		"phase12_delivery.py": dest / "services" / "delivery.py",
		"phase12_fanout.py": dest / "services" / "fanout.py",
		"phase12_unread.py": dest / "services" / "unread.py",
		"phase12_sla_alerts.py": dest / "services" / "sla_alerts.py",
		"phase12_serializers.py": dest / "api" / "serializers.py",
		"phase12_notification_api.py": APP / "api" / "v1" / "notification.py",
	}
	for src, dst in mapping.items():
		write(dst, (SCRIPTS / src).read_text(encoding="utf-8"))


def patch_modules_txt() -> None:
	path = APP / "modules.txt"
	lines = path.read_text(encoding="utf-8").strip().splitlines()
	if MODULE not in lines:
		lines.append(MODULE)
		path.write_text("\n".join(lines) + "\n", encoding="utf-8")
		print(f"  updated modules.txt (+{MODULE})")


def patch_timeline() -> None:
	path = APP / "project_lifecycle" / "services" / "timeline.py"
	text = path.read_text(encoding="utf-8")
	if "deliver_for_timeline_event" in text:
		print("  timeline.py already patched")
		return
	old = "\t\tfrappe.flags[TIMELINE_FLAG] = True\n\t\ttry:\n\t\t\tdoc.insert(ignore_permissions=True)\n\t\tfinally:\n\t\t\tfrappe.flags[TIMELINE_FLAG] = False\n\t\treturn doc.name"
	new = """\t\tfrappe.flags[TIMELINE_FLAG] = True
\t\ttry:
\t\t\tdoc.insert(ignore_permissions=True)
\t\tfinally:
\t\t\tfrappe.flags[TIMELINE_FLAG] = False
\t\tevent_id = doc.name
\t\ttry:
\t\t\tfrom agriflow.notification_engine.services.fanout import deliver_for_timeline_event

\t\t\tdeliver_for_timeline_event(event_id)
\t\texcept Exception:
\t\t\tfrappe.log_error(frappe.get_traceback(), "notification.fanout")
\t\treturn event_id"""
	if old not in text:
		raise SystemExit("timeline.py insert block not found")
	text = text.replace(old, new, 1)
	# idempotent return path
	old2 = "\t\t\tif existing:\n\t\t\t\treturn existing"
	new2 = """\t\t\tif existing:
\t\t\t\ttry:
\t\t\t\t\tfrom agriflow.notification_engine.services.fanout import deliver_for_timeline_event

\t\t\t\t\tdeliver_for_timeline_event(existing)
\t\t\t\texcept Exception:
\t\t\t\t\tfrappe.log_error(frappe.get_traceback(), "notification.fanout")
\t\t\t\treturn existing"""
	if old2 in text:
		text = text.replace(old2, new2, 1)
	path.write_text(text, encoding="utf-8")
	print("  patched timeline.py fanout hook")


def patch_hooks() -> None:
	path = APP / "hooks.py"
	text = path.read_text(encoding="utf-8")
	if "scan_task_overdue_notifications" in text and "scheduler_events = {" in text:
		print("  hooks.py already has scheduler")
		return
	text = text.replace(
		'\t"agriflow.notification_engine.services.sla_alerts.scan_task_overdue_notifications",\n',
		"",
	)
	block = """

scheduler_events = {
\t"daily": [
\t\t"agriflow.notification_engine.services.sla_alerts.scan_task_overdue_notifications",
\t],
}
"""
	text = text.rstrip() + block + "\n"
	path.write_text(text, encoding="utf-8")
	print("  patched hooks.py scheduler")


def main() -> None:
	print("Phase 12 Notification Engine bootstrap")
	write_doctypes()
	copy_services()
	patch_modules_txt()
	patch_timeline()
	patch_hooks()
	print("Done. Run: bench migrate && bench clear-cache")


if __name__ == "__main__":
	main()
