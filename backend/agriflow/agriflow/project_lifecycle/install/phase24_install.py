# Copyright (c) 2026, Murugan and contributors
"""Phase 24 install — indexes + cache config."""

from __future__ import annotations

from agriflow.project_lifecycle.install.phase24_cache_tuning import apply_recommended_site_config
from agriflow.project_lifecycle.install.phase24_indexes import ensure_performance_indexes


def execute():
	return {
		"ok": True,
		"indexes": ensure_performance_indexes(),
		"cache": apply_recommended_site_config(),
	}
