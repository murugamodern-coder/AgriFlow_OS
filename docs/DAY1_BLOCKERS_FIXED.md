# Day 1 — Demo blockers fixed (Pass 2)

**Date:** 2026-05-20  
**Commits:** `fix: demo blockers from pass 2 audit` · `chore: commit generated backend app for reproducibility`

---

## Blockers fixed

| # | Blocker | Fix | Verify |
|---|---------|-----|--------|
| P0 | Hardcoded `FP-2026-00007` on timeline note | `selectedProjectProvider` + note sheet requires selected project; FAB hidden without selection | Manual: open project from farmer list, add note |
| P0 | No 12-stage HERO UI | `ProjectTimelineScreen` — 12 steps, history dates, advance button via `project.timeline` / `project.transition` | Manual: Farmers → project → see all stages |
| P0 | No farmer list | `FarmerListScreen` + `farmer.list` API (fallback: project cache) | Manual: Farmers tab after sync |
| P0 | No owner dashboard | `HomeDashboardScreen` — role, blocks, project/task counts | Manual: Home tab after login |
| P0 | No stage transition in app | `ProjectRemote.transition()` online API | Manual: Advance stage → sync → Tasks |
| P0 | Notification raw i18n keys | `AgriFlowI18n.notificationTitle()` | Manual: Notifications tab |
| P1 | English timeline note strings | `timelineNoteLabel`, `timelineNoteQueue` in en/ta ARB | Code review |
| P1 | English sync strings | `syncLastRequestId`, `syncRepairQueue` | Code review |
| P1 | English task detail materials | `taskMaterialsTitle`, `taskConsumeOne` | Code review |
| P1 | Auto onboarding on launch | Skipped when `Env.demoMode` (default `true`) | `test/config/demo_mode_test.dart` |
| P1 | Dev login stub in demo | Hidden when `demoMode` | `demo_mode_test.dart` |

---

## Backend / repo hygiene

| Item | Status |
|------|--------|
| `backend/agriflow/` committed | Done (~full bench app snapshot via WSL copy) |
| `agriflow.api.v1.farmer.list` | `backend/agriflow/agriflow/api/v1/farmer.py` |
| `agriflow.api.v1.project.transition` | Present in `project.py` |
| Root `.gitignore` | Added |
| `docs/SETUP_FROM_SCRATCH.md` | Added |
| `scripts/install_backend_to_bench.sh` | Bench ← repo sync |
| `scripts/copy_backend_to_repo.sh` | Repo ← bench snapshot |

---

## Still concerns (not blockers — Pass 2 Risks/Polish)

- **Error messages** still generic / not always Tamil on all screens (`errorGeneric` only on some paths).
- **No shimmer** loading — spinners only.
- **Task “today” filter** not implemented.
- **Notifications** — no pull-to-refresh.
- **Cold start &lt;3s** not benchmarked on 2GB device.
- **DocType permissions** still System-Manager-heavy on desk; API layer enforces block scope.
- **Flutter tests** — `demo_mode_test` + `agriflow_i18n_test` added; full `flutter test` not run in CI here (Flutter not on Windows PATH in agent shell).
- **OneDrive** — rsync to `/mnt/c` can fail; use `Copy-Item \\wsl$\...` or clone outside OneDrive for team.
- **README** partially updated; full rewrite of §7.2 still recommended.
- **Git push** — user must `git init` / remote push manually if repo was not initialized.

---

## Demo rehearsal order

1. Login (owner or field officer)  
2. Home → sync  
3. Farmers → pick farmer → timeline HERO  
4. Advance stage → Sync  
5. Tasks → complete one  
6. Notifications  
7. Sync tab (queue demo)

---

## Key new files (mobile)

- `lib/features/dashboard/presentation/home_dashboard_screen.dart`
- `lib/features/farmer/presentation/farmer_list_screen.dart`
- `lib/features/project_lifecycle/presentation/project_timeline_screen.dart`
- `lib/features/project_lifecycle/data/project_remote.dart`
- `lib/core/i18n/agriflow_i18n.dart`
- `lib/core/demo/demo_selection.dart`
