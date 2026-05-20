# Copyright (c) 2026, Murugan and contributors
"""Live ops dashboard + rollout governance APIs."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import success
from agriflow.api.v1 import push as push_api
from agriflow.api.v1 import readiness as readiness_api
from agriflow.api.v1.pilot_ops import _app_version_matrix, _officer_activity, _queue_backlog_metrics, _sync_health_window
from agriflow.project_lifecycle.install.phase16_inventory_reconcile import execute as inventory_reconcile
from agriflow.project_lifecycle.install.phase19_ops_alerts import execute as run_alerts


def _admin_only():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)


@frappe.whitelist(allow_guest=False)
def live_dashboard():
	"""Consolidated live ops view for production control room."""
	_admin_only()
	open_incidents = frappe.get_all(
		"Operational Incident",
		filters={"status": ("in", ("open", "investigating"))},
		fields=["name", "incident_type", "severity", "summary", "recorded_on"],
		order_by="recorded_on desc",
		limit=20,
	) if frappe.db.exists("DocType", "Operational Incident") else []

	return success(
		{
			"generated_at": str(now_datetime()),
			"site": frappe.local.site,
			"rollout_wave": frappe.conf.get("agriflow_rollout_wave") or "pilot_a",
			"sync_health": _sync_health_window(),
			"queue_backlog": _queue_backlog_metrics(),
			"inventory": inventory_reconcile(),
			"push_metrics": push_api.delivery_metrics().get("data"),
			"app_versions": _app_version_matrix(),
			"officer_activity": _officer_activity(),
			"open_incidents": open_incidents,
			"queue_alerts": readiness_api.queue_alerts().get("data"),
		}
	)


@frappe.whitelist(allow_guest=False)
def run_alert_checks():
	_admin_only()
	return success(run_alerts())


@frappe.whitelist(allow_guest=False)
def rollout_status():
	"""Rollout governance — wave, min version, allowed blocks."""
	_admin_only()
	return success(
		{
			"wave": frappe.conf.get("agriflow_rollout_wave") or "pilot_a",
			"min_app_version": frappe.conf.get("agriflow_min_app_version") or "0.18.0",
			"apk_url": frappe.conf.get("agriflow_apk_url") or "",
			"production_hostname": frappe.conf.get("agriflow_production_hostname") or "",
			"fcm_mode": (frappe.conf.get("agriflow_fcm_server_key") or "off")[:20],
		}
	)


@frappe.whitelist(allow_guest=False)
def background_sync_ack(data=None):
	"""Mobile headless worker — ack sync attempt (telemetry)."""
	ensure_authenticated()
	from agriflow.api.v1.response import parse_data

	payload = parse_data(data)
	frappe.get_doc(
		{
			"doctype": "Operational Log",
			"event_type": "headless_sync",
			"source": "mobile",
			"device_id": payload.get("device_id") or "",
			"user": frappe.session.user,
			"payload_json": payload,
			"recorded_on": now_datetime(),
		}
	).insert(ignore_permissions=True)
	return success({"ack": True})
