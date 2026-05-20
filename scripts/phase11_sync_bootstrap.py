#!/usr/bin/env python3
"""Phase 11 — Sync Engine foundation bootstrap."""
from __future__ import annotations

import json
from pathlib import Path

APP = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
FIXTURES = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/fixtures")
MODULE = "Sync Engine"
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


def doctype(name, fields, *, autoname, title_field="", track_changes=0):
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
        "sort_field": "modified",
        "sort_order": "DESC",
        "track_changes": track_changes,
        "title_field": title_field,
    }


def write_doctypes() -> None:
    ss_fields = [
        field("sync_token", "Data", "Sync Token", reqd=0, unique=1, in_list_view=1),
        field("device_id", "Data", "Device ID", in_list_view=1),
        field("user", "Link", "User", options="User", reqd=1, in_list_view=1),
        field("session_type", "Select", "Session Type", options="pull\npush\ncombined", reqd=1),
        field("started_on", "Datetime", "Started On", reqd=1),
        field("completed_on", "Datetime", "Completed On"),
        field("watermarks_in", "JSON", "Watermarks In"),
        field("watermarks_out", "JSON", "Watermarks Out"),
        field("summary", "JSON", "Summary"),
    ]
    base = APP / "sync_engine" / "doctype" / "sync_session"
    write(base / "__init__.py", "")
    write(base / "sync_session.json", json.dumps(doctype("Sync Session", ss_fields, autoname="format:SS-{YYYY}-{#####}", title_field="sync_token"), indent=1) + "\n")
    write(
        base / "sync_session.py",
        '''# Copyright (c) 2026
import frappe
from frappe.model.document import Document


class SyncSession(Document):
\tdef before_insert(self):
\t\tif not self.sync_token and self.name:
\t\t\tself.sync_token = self.name
''',
    )

    log_fields = [
        field("sync_session", "Link", "Sync Session", options="Sync Session", reqd=1, in_list_view=1),
        field("client_mutation_id", "Data", "Client Mutation ID", reqd=1, unique=1, length=36, in_list_view=1, search_index=1),
        field("entity", "Select", "Entity", options="task\ntimeline\nfarmer_project", reqd=1, in_list_view=1),
        field("op_type", "Select", "Op Type", options="create\nupdate\ncomplete\nnote", reqd=1),
        field("status", "Select", "Status", options="success\nconflict\nfailed\nskipped\ndependency_failed", reqd=1, in_list_view=1),
        field("entity_name", "Data", "Entity Name", in_list_view=1),
        field("client_id", "Data", "Client ID", length=36),
        field("request_json", "JSON", "Request JSON"),
        field("response_json", "JSON", "Response JSON"),
        field("processed_on", "Datetime", "Processed On", reqd=1, in_list_view=1),
    ]
    base = APP / "sync_engine" / "doctype" / "sync_mutation_log"
    write(base / "__init__.py", "")
    write(base / "sync_mutation_log.json", json.dumps(doctype("Sync Mutation Log", log_fields, autoname="hash", title_field="client_mutation_id", track_changes=0), indent=1) + "\n")
    write(
        base / "sync_mutation_log.py",
        '''# Copyright (c) 2026
import frappe
from frappe import _
from frappe.model.document import Document

LOG_FLAG = "agriflow_sync_mutation_log_write"


class SyncMutationLog(Document):
\tdef validate(self):
\t\tif not frappe.flags.get(LOG_FLAG) and not self.is_new():
\t\t\tfrappe.throw(_("Sync mutation logs are immutable"))

\tdef on_trash(self):
\t\tif frappe.session.user != "Administrator":
\t\t\tfrappe.throw(_("Sync mutation logs cannot be deleted"))
''',
    )


def patch_modules_txt() -> None:
    path = APP / "modules.txt"
    text = path.read_text(encoding="utf-8")
    if "Sync Engine" not in text:
        text = text.rstrip() + "\nSync Engine\n"
        path.write_text(text, encoding="utf-8")
        print("  patched modules.txt")


def main() -> None:
    print("Phase 11 sync bootstrap")
    write(APP / "sync_engine" / "__init__.py", "")
    write_doctypes()
    patch_modules_txt()

    # Services — written from companion files
    root = Path(__file__).resolve().parent
    for rel, dest in [
        ("phase11_session.py", APP / "sync_engine/services/session.py"),
        ("phase11_idempotency.py", APP / "sync_engine/services/idempotency.py"),
        ("phase11_pull.py", APP / "sync_engine/services/pull.py"),
        ("phase11_push.py", APP / "sync_engine/services/push.py"),
        ("phase11_handlers_task.py", APP / "sync_engine/services/handlers/task.py"),
        ("phase11_handlers_timeline.py", APP / "sync_engine/services/handlers/timeline.py"),
        ("phase11_handlers___init__.py", APP / "sync_engine/services/handlers/__init__.py"),
        ("phase11_serializers.py", APP / "sync_engine/api/serializers.py"),
        ("phase11_sync_api.py", APP / "api/v1/sync.py"),
    ]:
        src = root / rel
        if src.exists():
            write(dest, src.read_text(encoding="utf-8"))
        else:
            print(f"  MISSING {rel}")

    write(APP / "sync_engine/services/__init__.py", "")
    write(APP / "sync_engine/services/handlers/__init__.py", "")
    write(APP / "sync_engine/api/__init__.py", "")

    vsrc = root / "phase11_verify_sync.py"
    if vsrc.exists():
        write(APP / "project_lifecycle/install/phase11_verify_sync.py", vsrc.read_text(encoding="utf-8"))

    print("Done. bench migrate && bench clear-cache && phase11_verify_sync.execute")


if __name__ == "__main__":
    main()
