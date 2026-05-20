# Copyright (c) 2026, Murugan and contributors
"""Production readiness APIs — release check, queue alerts, sync failure rollup."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.project_lifecycle.install.phase16_inventory_reconcile import execute as inventory_reconcile
from agriflow.api.v1.pilot_ops import _queue_backlog_metrics, _sync_health_window


@frappe.whitelist(allow_guest=False)
def app_release_check(data=None):
	"""Mobile — compare APP_VERSION to site min version and APK URL."""
	ensure_authenticated()
	payload = parse_data(data)
	client_version = (payload.get("app_version") or "0.0.0").strip()
	min_version = frappe.conf.get("agriflow_min_app_version") or "0.17.0"
	apk_url = frappe.conf.get("agriflow_apk_url") or ""

	def _parse(v: str) -> tuple:
		parts = []
		for p in v.split("."):
			try:
				parts.append(int(p))
			except ValueError:
				parts.append(0)
		return tuple(parts)

	update_required = _parse(client_version) < _parse(min_version)
	return success(
		{
			"client_version": client_version,
			"min_version": min_version,
			"update_required": update_required,
			"apk_url": apk_url,
		}
	)


@frappe.whitelist(allow_guest=False)
def queue_alerts():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)
	backlog = _queue_backlog_metrics()
	alerts = []
	if backlog.get("total_pending", 0) > 10:
		alerts.append({"code": "QUEUE_BACKLOG_HIGH", "pending": backlog["total_pending"]})
	if backlog.get("total_conflicts", 0) > 0:
		alerts.append({"code": "QUEUE_CONFLICTS", "conflicts": backlog["total_conflicts"]})
	return success({"alerts": alerts, "backlog": backlog})


@frappe.whitelist(allow_guest=False)
def sync_failure_categories():
	"""Roll up mutation failures by error pattern (7d)."""
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)
	since = add_days(now_datetime(), -7)
	rows = frappe.db.sql(
		"""
		SELECT status, entity, COUNT(*) AS cnt
		FROM `tabSync Mutation Log`
		WHERE processed_on >= %(since)s
		  AND status IN ('failed', 'conflict', 'dependency_failed')
		GROUP BY status, entity
		ORDER BY cnt DESC
		""",
		{"since": since},
		as_dict=True,
	)
	return success(
		{
			"sync_health": _sync_health_window(),
			"failure_breakdown": rows,
		}
	)


@frappe.whitelist(allow_guest=False)
def production_dashboard():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)
	from agriflow.api.v1 import push as push_api

	push_metrics = push_api.delivery_metrics()

	return success(
		{
			"generated_at": str(now_datetime()),
			"sync_health": _sync_health_window(),
			"queue_backlog": _queue_backlog_metrics(),
			"inventory": inventory_reconcile(),
			"push_metrics": push_metrics.get("data"),
			"site": frappe.local.site,
			"jwt_mode": frappe.conf.get("agriflow_auth_mode"),
		}
	)
