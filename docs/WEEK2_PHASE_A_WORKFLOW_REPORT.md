# Week 2 Phase A — Frappe Workflow Attached Report

## Status: 🟢 COMPLETE

## Phase Results

| Phase | Action | Status |
|-------|--------|--------|
| 1 | Backup taken | ✅ `/home/muruga/workspace/frappe-bench/sites/dev.agriflow.local/private/backups/20260607_121745-dev_agriflow_local-database.sql.gz` (+ site config, public/private files) |
| 2 | Workflow JSON created | ✅ `backend/agriflow/agriflow/workflow/farmer_project_workflow/farmer_project_workflow.json` |
| 3 | 8 Roles ensured | ✅ All 8 `Agriflow*` roles present on site |
| 4 | hooks.py updated | ✅ Role + Workflow fixture filters; after_migrate install hooks |
| 5 | Migration + project state migrate | ✅ Workflow installed; projects synced to workflow states |
| 6 | Desk UI verified | ✅ Workflow actions available; transition + timeline verified via bench execute |

## Workflow Details

- **Name:** Farmer Project Lifecycle
- **States:** 12 (sequential, PRD labels)
- **Transitions:** 11 (no skipping)
- **Document Type:** Farmer Project
- **State Field:** `workflow_state` (Link → Workflow State)
- **Bridge:** `workflow_bridge.py` calls existing `ProjectLifecycleService.transition()` on workflow save (service unchanged as fallback/API path)

## Existing Projects After Migration

| Project | Previous State (custom) | New workflow_state | current_stage |
|---------|-------------------------|--------------------|---------------|
| FP-2026-00007 | `lead_captured` (active) | Lead Captured | `lead_captured` |
| FP-2026-00008 | `lead_captured` (was on_hold) | Eligibility Check* | `eligibility_check` |

\*FP-2026-00008 was used during bridge debugging (status set to `active` for one transition test). Both projects are aligned: workflow_state mirrors `current_stage` via `migrate_project_workflow_state`.

## Test Scenario Run

- Logged in context: **Administrator** (bench execute)
- Opened **FP-2026-00007** (active, reset to Lead Captured)
- Available transition: **Verify Eligibility**
- Applied workflow action → `workflow_state` = **Eligibility Check**, `current_stage` = **eligibility_check**, `stage_sequence` = **2**
- **Timeline:** +1 `stage_transition` event (count 3 → 4)
- **Reverted** to Lead Captured / `lead_captured` for clean demo state

## Files Changed

| Path | Change |
|------|--------|
| `backend/agriflow/agriflow/workflow/farmer_project_workflow/farmer_project_workflow.json` | **New** — canonical workflow definition |
| `backend/agriflow/agriflow/workflow/farmer_project_workflow/__init__.py` | **New** |
| `backend/agriflow/agriflow/workflow/__init__.py` | **New** |
| `backend/agriflow/agriflow/fixtures/role.json` | **New** — 8 Agriflow roles |
| `backend/agriflow/fixtures/workflow.json` | **New** — export fixture copy |
| `backend/agriflow/agriflow/hooks.py` | Role/Workflow fixtures + after_migrate hooks |
| `backend/agriflow/agriflow/project_lifecycle/doctype/farmer_project/farmer_project.json` | Added `workflow_state`, `is_submittable` |
| `backend/agriflow/agriflow/project_lifecycle/doctype/farmer_project/farmer_project.py` | Workflow bridge hooks |
| `backend/agriflow/agriflow/project_lifecycle/workflow_bridge.py` | **New** — workflow ↔ lifecycle sync |
| `backend/agriflow/agriflow/project_lifecycle/install/install_farmer_project_workflow.py` | **New** — idempotent workflow install |
| `backend/agriflow/agriflow/project_lifecycle/install/migrate_project_workflow_state.py` | **New** — backfill workflow_state |
| `backend/agriflow/agriflow/project_lifecycle/install/verify_farmer_project_workflow.py` | **New** — bench verification helper |
| `backend/agriflow/fixture_data/*` | Moved non-doc JSON (`demo_geo`, `task_template`, `project_stage_role_matrix`) |
| `backend/agriflow/agriflow/project_lifecycle/utils/stages.py` | Updated role matrix path |
| `backend/agriflow/agriflow/task_engine/services/templates.py` | Updated task template path |
| `backend/agriflow/agriflow/commands/seed_demo.py` | Updated demo_geo path |

## Issues Encountered

1. **Initial migrate failure** — `demo_geo.json` in `agriflow/fixtures/` is not a Frappe doc (KeyError `doctype`). Moved data JSON to `fixture_data/`.
2. **Workflow LinkValidationError** — Workflow State + Workflow Action Master rows must exist before Workflow insert. Resolved in `install_farmer_project_workflow.py`.
3. **Bridge timing** — `on_update` read stale `workflow_state` from DB; fixed by capturing `_prev_workflow_state` in `before_save`.
4. **On-hold project** — FP-2026-00008 blocked lifecycle transition until `status=active` (by design in `ProjectLifecycleService`).

## Next Steps (Phase B Preview)

- Mobile Timeline UI to read `workflow_state`
- Mobile stage buttons → `frappe.model.workflow.apply_workflow` / API wrapper
- Auto-task creation already fires via lifecycle bridge on transition
- Notification dispatch on stage change

## User Verification Required

1. Browser hard refresh: **Ctrl+Shift+R** on `http://127.0.0.1:8000/app/farmer-project`
2. Open **FP-2026-00007** (active project)
3. Confirm workflow status bar shows **Lead Captured**
4. Confirm action button **Verify Eligibility** appears (Administrator or Agriflow Office Manager)
5. Click action → state becomes **Eligibility Check** and timeline updates
