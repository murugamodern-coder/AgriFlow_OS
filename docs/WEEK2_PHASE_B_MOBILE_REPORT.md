# Week 2 Phase B — Mobile UI Polish Report

## Status: 🟢 COMPLETE

## Phase Results

| Phase | Action | Status |
|-------|--------|--------|
| 1 | Workflow API endpoints created | ✅ `get_available_actions`, `apply_workflow_action` |
| 2 | Tamil ARB strings added | ✅ Action labels, confirm dialog, progress strings (EN + TA) |
| 3 | Domain models created | ✅ `WorkflowState`, `WorkflowAction`, `WorkflowStatus` |
| 4 | Repository + Provider | ✅ `WorkflowRepository` + Riverpod `projectWorkflowProvider` |
| 5 | Timeline stage row polished | ✅ `WorkflowTimelineStageRow` — 12 stages, completed/current/future |
| 6 | Header progress card | ✅ `TimelineWorkflowProgressCard` — "Stage X / 12" + linear progress |

## API Test Results (bench execute as Administrator)

**`get_available_actions(FP-2026-00007)`**

- `ok: true`
- `current_state`: Lead Captured → after apply: Eligibility Check
- `actions`: `[{action: "Verify Eligibility", next_state: "Eligibility Check", allowed_role: "Agriflow Office Manager"}]`
- `all_stages`: 12 entries with Tamil labels + colors

**`apply_workflow_action(action="Verify Eligibility")`**

- `ok: true`
- `new_state`: Eligibility Check
- `new_stage`: eligibility_check
- `new_sequence`: 2
- Bridge invoked `ProjectLifecycleService.transition()` (timeline + stage history updated)

## Mobile Architecture

```
ProjectTimelineScreen
├── TimelineHeaderCard (farmer context — unchanged)
├── TimelineWorkflowProgressCard ← projectWorkflowProvider
├── WorkflowTimelineStageRow × 12 ← all_stages from API
├── TimelineWorkflowActions ← apply via workflow API + invalidate providers
└── TimelineActionsBar (call / WhatsApp / note — unchanged)
```

- Uses **AgriFlow API envelope** (`ApiClient.postMethod`) — not raw Dio GET
- Manual Riverpod providers (matches existing codebase; no `riverpod_annotation`)
- On successful transition: invalidates `projectWorkflowProvider` + `projectTimelineDetailProvider`, runs sync

## Files Changed

| Path | Change |
|------|--------|
| `backend/agriflow/agriflow/api/v1/workflow.py` | **New** — workflow read + apply endpoints |
| `mobile/.../domain/models/workflow_state.dart` | **New** |
| `mobile/.../data/workflow_repository.dart` | **New** |
| `mobile/.../presentation/providers/workflow_provider.dart` | **New** |
| `mobile/.../presentation/workflow_ui_helpers.dart` | **New** — colors + i18n mappers |
| `mobile/.../widgets/workflow_timeline_stage_row.dart` | **New** |
| `mobile/.../widgets/timeline_workflow_actions.dart` | **New** |
| `mobile/.../widgets/timeline_workflow_progress_card.dart` | **New** |
| `mobile/.../presentation/project_timeline_screen.dart` | Wired workflow UI; removed legacy `advanceStage` button |
| `mobile/agriflow_mobile/lib/l10n/app_ta.arb` | Tamil action + progress strings |
| `mobile/agriflow_mobile/lib/l10n/app_en.arb` | English counterparts |

## flutter analyze

```
flutter analyze lib/features/project_lifecycle
→ 0 errors (3 pre-existing warnings in unrelated files)
```

Full-project analyze still reports legacy test-file issues outside this scope.

## User Verification Required (Mobile)

On Windows:

```powershell
cd C:\AgriFlow_OS\AgriFlow_Main\mobile\agriflow_mobile
flutter pub get
flutter gen-l10n
flutter run -d windows --dart-define=API_BASE_URL=http://172.28.181.245:8000
```

Then:

1. Login
2. Open farmer project **FP-2026-00007** (currently **Eligibility Check**, sequence 2)
3. Timeline screen should show:
   - Progress card: **2 / 12** + Tamil stage label
   - 12 vertical stages (1 ✓, 2 current, 3–12 dimmed)
   - Action button: **ஆவணங்கள் சேகரிக்க** (Collect Documents) if user has Agriflow Office Staff role
4. Tap action → Tamil confirmation modal
5. Confirm → state advances → timeline refreshes

**Note:** Workflow actions are role-gated. Field officers need matching Agriflow roles on their Frappe user, or test as Administrator.

## Issues

- Smoke test advanced FP-2026-00007 to **Eligibility Check** (matches demo scenario in task spec).
- `get_available_actions` uses Frappe `get_transitions()` — correct permission/self-approval handling vs manual role loop.

## Next Steps (Phase C preview)

- Offline queue for workflow transitions (`client_mutation_id`)
- Push notification on stage change
- Role-based action visibility in mobile permissions manifest
