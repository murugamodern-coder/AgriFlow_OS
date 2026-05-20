# Copyright (c) 2026, Murugan and contributors
"""Phase 24 performance & observability verification."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import observability as obs_api
from agriflow.project_lifecycle.install.phase23_verify_enterprise import execute as p23
from agriflow.project_lifecycle.install.phase24_benchmark import execute as benchmark
from agriflow.project_lifecycle.install.phase24_install import execute as install24


def execute():
	errors = []
	out = {"ok": False, "errors": errors}

	out["install24"] = install24()
	out["phase23"] = p23()
	if not out["phase23"].get("ok"):
		errors.append("phase23 regression")

	frappe.set_user("Administrator")
	out["benchmark"] = benchmark()
	out["benchmark_pass"] = out["benchmark"].get("pass")

	dash = obs_api.ops_metrics_dashboard()
	out["metrics_dashboard_ok"] = dash.get("ok")
	lat = obs_api.dashboard_latency()
	out["latency_ok"] = lat.get("ok")
	if lat.get("ok"):
		out["latency_ms"] = (lat.get("data") or {})

	out["rollup_ok"] = obs_api.refresh_telemetry_rollup().get("ok")
	out["queue_ok"] = obs_api.queue_throughput_metrics().get("ok")
	out["cost_ok"] = obs_api.infrastructure_cost_summary().get("ok")
	out["self_check_ok"] = obs_api.operational_self_check_api().get("ok")
	out["recovery_ok"] = obs_api.recovery_drill_automation().get("ok")
	out["retention_dry"] = obs_api.run_batched_retention().get("ok")

	out["ok"] = len(errors) == 0
	out["errors"] = errors
	return out
