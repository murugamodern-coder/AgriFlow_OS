# Audit Pass 2: Code Quality (Demo-Focused)

**Date:** 2026-05-20  
**Auditor mode:** Report only — no fixes applied  
**Scope:** Narrow 5-day pilot demo (7 features). Ignores billing, MIMIS Excel, AMC, officer commission.  
**Prior work:** [AUDIT_PASS_1_REPORT.md](./AUDIT_PASS_1_REPORT.md) (not repeated here)

---

## Overall Demo-Readiness Score: **48 / 100**

**Summary:** Backend code for lifecycle, tasks, sync, and notifications is **demo-capable on bench** if seeded and accessed via desk/API. The **Flutter app does not implement half of the demo script** (owner dashboard, farmer list, 12-stage hero timeline, stage update UI). What exists is a **solid ops slice** (login, event timeline, tasks, notifications, sync screen) but **not** the story you plan to tell in 5 days without **3–4 days of focused UI work**.

---

## Demo Scope vs Reality

| # | Demo feature | Mobile | Backend | Demo-ready? |
|---|--------------|--------|---------|-------------|
| 1 | Owner login + role-based dashboard | Login only; **no owner dashboard** | JWT + permissions manifest | **PARTIAL** |
| 2 | Farmer list (read-only) | **Missing** | Farmer DocType + data on bench | **NO** (mobile) |
| 3 | 12-stage Project Timeline (HERO) | **Event feed**, not 12 stages | `project.timeline` API returns `stage_history` + `workflow` | **NO** (mobile) |
| 4 | Task feed (today's work) | Task inbox (all cached tasks) | Project Task + templates | **PARTIAL** |
| 5 | Stage update + auto-tasks | **No UI**; sync **blocks** `farmer_project` ops | `transition()` + `generate_stage_tasks()` | **Desk/API only** |
| 6 | Notification panel | Inbox exists | Phase 12 engine | **PARTIAL** (raw i18n keys in UI) |
| 7 | Offline → online sync demo | Sync tab + queue | push/pull clean | **YES** (best demo surface) |

---

## 🚨 Demo Blockers (Fix in Day 1–2)

| Priority | file:line | What's wrong | Why it'll break demo |
|----------|-----------|--------------|----------------------|
| **P0** | `mobile/.../timeline_feed_screen.dart:85` | Hardcoded `final project = 'FP-2026-00007'` on timeline note FAB | Demo on any other seeded project fails silently or writes to wrong project |
| **P0** | *Missing screen* | No **12-stage stepper/timeline HERO** UI | Client expectation #3; current screen is generic event cards |
| **P0** | *Missing screen* | No **farmer list** (read-only) | Demo feature #2 absent |
| **P0** | *Missing screen* | No **owner role dashboard** (cards/filters by role) | Demo feature #1 is only a 4-tab shell + app title |
| **P0** | *Missing flow* | No mobile **stage transition** UI; `phase11_push.py:65-66` rejects `farmer_project` via sync | Demo feature #5 cannot be shown from app without new screen + online API call |
| **P0** | `mobile/.../notification_inbox_screen.dart:42` | `Text(item.titleI18nKey)` shows keys like `notification.task_due` | Notifications look broken / untranslated in Tamil demo |
| **P1** | `mobile/.../timeline_feed_screen.dart:80,92-93` | Hardcoded English: `'Note'`, `'Queue note'` | Violates Tamil-first demo; looks unfinished |
| **P1** | `mobile/.../sync_status_screen.dart:114,146` | English: `'Last request_id'`, `'Repair queue'` | Same |
| **P1** | `mobile/.../task_detail_screen.dart:152-161` | English: `'Materials'`, `'Consume 1'` | Same; inventory UI may confuse if not in demo script |
| **P1** | `mobile/.../dashboard_shell.dart:74-77` | Auto `context.push(onboarding)` on first launch | Derails demo flow unless disabled for demo build |
| **P1** | `mobile/.../login_screen.dart:62-68` | `loginDevStub` when `DEV_AUTH_STUB` enabled | Accidental tap → fake session, no real server story |

---

## ⚠️ Demo Risks (Should Fix in Day 3–4)

| Area | file:line / location | Risk |
|------|----------------------|------|
| Error UX | `timeline_feed_screen.dart:25`, `task_inbox_screen.dart:25`, etc. | `Text(e.toString())` — stack traces / English Dio errors, not Tamil `errorGeneric` |
| Loading UX | `shared/widgets/loading_view.dart` | Spinner only — audit asks for shimmer; lists feel empty on slow sync |
| Notifications list | `notification_inbox_screen.dart` | **No** `RefreshIndicator` (tasks/timeline have it) |
| Task "today" filter | `task_repository.dart` | No `due_date` / today filter — inbox shows all projections |
| Timeline data source | `timeline_repository.dart` | Uses Drift projections only — never calls `agriflow.api.v1.project.timeline` (which has `stage_history`) |
| Release dialog | `dashboard_shell.dart:52-55` | `Download APK` `onPressed: () {}` — dead button if readiness API fires |
| Debug menu | `dashboard_shell.dart:97-111` | Popup: Feedback + Onboarding — visible to all users |
| Auth errors | `login_screen.dart:73-76` | `auth.error.toString()` — not localized |
| Offline catch | `dashboard_shell.dart:70-72`, `sync_status_screen.dart:41` | Empty/silent catch — acceptable for launch but hides misconfiguration |
| `Navigator.pop` | `task_detail_screen.dart:71`, timeline sheet | Minor go_router inconsistency |
| Backend permissions | `phase7/8 *_bootstrap.py` `PERMS_SM` | Desk CRUD wide open; demo OK if API-only, risky if desk shown |
| Bench dependency | No `backend/` in repo | Demo machine must have run phase6–16 deploy scripts or bench diverges |

---

## 💡 Polish Opportunities (Nice to have)

- Wire `project.timeline` API into a dedicated **ProjectTimelineScreen** with 12 stage chips + history dates (backend already returns `stage_history`, `workflow.can_transition`).
- Add **role-aware home** using `PermissionManifest.roles` from `auth_session.dart` (Owner vs Field Staff destinations).
- Localize notification titles via `AppLocalizations` lookup from `titleI18nKey` or server `title` field.
- Replace hardcoded demo project with selected project from list or deep link query param.
- Filter tasks: `due_date <= today` and `status != completed`.
- Hide pilot/commercial surfaces (device health on sync tab, feedback menu) for demo build flag.
- Add shimmer placeholders in `LoadingView` for list screens.
- Remove or gate `task_detail` inventory "Consume 1" unless inventory is in demo script.

---

## ✅ What's Done Well

| Pattern | Evidence | Why it matters for demo |
|---------|----------|-------------------------|
| **Queue-only writes** | `mutation_queue.dart`, `task_repository.dart` comment L36 | Sync demo is honest — completes queue then push |
| **Sync orchestration** | `sync_orchestrator.dart` — phases, watermarks, repair | Sync tab can show queue → server visually |
| **Secure JWT storage** | `secure_token_store.dart`, `auth_repository.dart` | Real login demo without SharedPreferences leak |
| **AsyncValue on auth** | `auth_repository.dart` L16-41 | Login loading/error states structured |
| **StreamProvider + block scope** | `task_repository.dart`, `timeline_repository.dart` | Field officer scope respected from Hive permissions |
| **go_router navigation** | `app_router.dart`, task `context.push` | No ad-hoc route stacks in main flows |
| **Backend sequential lifecycle** | `phase8_project_bootstrap.py` lifecycle service L427-438 | Stage skip guard — demo transition on desk/API is trustworthy |
| **Auto-task generation** | `phase10_task_bootstrap.py` `generate_stage_tasks` wired into transition | Feature #5 works **server-side** after transition |
| **Rich project.timeline API** | `phase9b_api_bootstrap.py` L609-638 | Mobile can adopt without new backend work |
| **Sync push idempotency** | `phase11_push.py` — `find_prior`, batch buckets | Offline replay demo won't duplicate rows |
| **Design tokens** | `color_tokens.dart` + `agriflow_theme.dart` | Colors centralized (token file uses `Color(0xFF…)` — acceptable per project pattern) |
| **Offline banner** | `offline_banner.dart` + `dashboard_shell.dart` | Clear offline → online narrative |
| **No TODO/FIXME in feature widgets** | Grep `lib/features/` clean | Reduces demo-killer surprise |

---

## Backend Audit (Demo Features Only)

### Frappe DocTypes

| Check | Status | Notes |
|-------|--------|-------|
| Geography well-modeled? | ✅ | phase6 — District→Block→Cluster→Village, Officer Assignment History |
| Farmer PRD fields? | ⚠️ | Core identity/geo/land present; **Farmer Document** child, structured **tags** (vs `tags` Small Text) missing |
| Farmer Project 12-stage workflow? | ✅ | Custom service + fixtures; not Frappe Workflow doc |
| Project Task auto-creation? | ✅ | `generate_stage_tasks` on transition (phase10 patch) |
| Notification engine? | ✅ | phase12 bootstrap + fanout |
| Sync push/pull clean? | ✅ | Typed handlers, idempotency; explicit reject of project transition via sync |

### Python Quality (phase6–13 runtime modules in scripts)

| Check | Status | Notes |
|-------|--------|-------|
| Type hints | ✅ | `phase11_push.py`, APIs use `from __future__ import annotations` |
| No bare `except:` | ✅ | No matches in phase9–12 API/push/pull |
| `frappe.log_error` vs print | ⚠️ | Runtime services use logging; **bootstrap/verify scripts** use `print()` (not in user path) |
| Transactions for multi-step | ⚠️ | Frappe `doc.save()` per transition; push batch serial per project — acceptable |
| N+1 in list endpoints | ⚠️ | `phase11_pull.py` loops entities — watch large datasets; OK for 15-user demo |
| Hardcoded secrets | ✅ | None in phase6–13 scripts |

**Demo-critical backend gap:** Mobile cannot trigger `project.transition` through existing sync queue (`phase11_push.py:65-66`). Demo needs **online** API wrapper on mobile or desk transition before sync pull refreshes tasks.

---

## Mobile Audit (Demo Features Only)

### Architecture

| Check | Status |
|-------|--------|
| Feature folders auth / timeline / task / sync / notification | ⚠️ `project_lifecycle/` not `timeline/`; no `farmer/` |
| Riverpod (not setState in non-trivial) | ⚠️ `sync_status_screen`, `dashboard_shell`, `task_detail_screen`, pilot screens use **setState** |
| go_router (no Navigator.push) | ✅ Main routes; ⚠️ `Navigator.pop` in sheets/detail |
| freezed / json_serializable models | ❌ `equatable` + manual `fromPayload` only |
| AsyncValue for async states | ⚠️ Login yes; lists use `StreamProvider` + `.when` (good); sync screen uses manual state |

### Dart Quality

| Check | Status |
|-------|--------|
| Null safety / chained `!` | ✅ No abusive chains in demo paths |
| dispose() on controllers | ✅ `login_screen.dart` |
| const constructors | ⚠️ Mixed |
| Theme tokens (no hardcoded colors in widgets) | ✅ Widgets use theme; tokens file holds hex |
| Tamil via i18n | ❌ Multiple hardcoded English strings in demo paths (see blockers) |
| TODO / UnimplementedError in demo paths | ⚠️ `UnimplementedError` in providers until `bootstrap.dart` overrides — OK at runtime; **not** user-facing |
| `UnimplementedError` in user flows | ✅ None |

### Demo-Critical Behaviors

| Check | Status |
|-------|--------|
| Cold start <3s | ⚠️ Not measured; `bootstrap()` opens Hive + Drift + repair — risk on 2GB device |
| Timeline shows all 12 stages | ❌ Event list only |
| Stage transitions without errors | ❌ No mobile UI |
| Task list refreshes | ✅ Pull-to-refresh + sync |
| Notifications load | ⚠️ Yes, but **unlocalized keys** |
| Offline no crash | ✅ Empty catches + offline banner |
| Sync queue → server visual | ✅ **Best demo** — Sync tab |
| Errors Tamil-friendly | ❌ |
| Shimmer loading | ❌ `CircularProgressIndicator` only |
| Pull-to-refresh on lists | ⚠️ Tasks + timeline yes; notifications no |

---

## Demo-Killer Hunt (CRITICAL)

| Scan | Result |
|------|--------|
| TODO/FIXME/HACK in user-touch paths | ✅ None in `lib/features/` |
| `print` / `debugPrint` | ⚠️ `telemetry.dart:37`, `workmanager_registration.dart:32` — debug only |
| Hardcoded test data | 🚨 `FP-2026-00007`; dev stub `dev@agriflow.local` / `Dev Officer` |
| Empty catch | ⚠️ `sync_status_screen.dart:41`, `dashboard_shell.dart:65,70` |
| Unimplemented UI | 🚨 Missing screens (farmer, 12-stage, owner dash, stage update) |
| Commented UI with buttons | ⚠️ Dead APK download button |
| Debug menus | ⚠️ Feedback, onboarding, dev login stub, sync repair |

---

## Repo Hygiene Status

| Item | Rating | Finding |
|------|--------|---------|
| **backend/ commit status** | **CRITICAL** | No `backend/agriflow/` in monorepo. Source = `scripts/phase*_bootstrap.py` → WSL bench path. Reproducibility requires documented copy/migrate steps (partially in PHASE reports, not one `setup.sh`). |
| **Setup reproducibility** | **CRITICAL** | Not git-initialized in workspace; new developer cannot `git clone` + run in 30 min from README alone (README §7.2 still says apps “not yet present”). |
| **Documentation** | **CRITICAL** for onboarding; **OK** for ops | `docs/LOCAL_LIVE_DEMO.md` helps tunnel demo; README contradicts actual `mobile/` presence. |
| **.env in .gitignore** | **CRITICAL** | No root `.gitignore`; only `mobile/agriflow_mobile/.gitignore`. `infra/docker/.env.*.example` exists. |
| **Secrets in git history** | N/A | Repository not a git repo in current workspace — run `git init` + hygiene before sharing. |

---

## Top 10 Items for Demo Polish

Ranked by **demo impact**, not purity.

1. **Build 12-stage HERO screen** — consume `project.timeline` (`stage_history` + current stage); this is the client “wow” moment.  
2. **Remove hardcoded `FP-2026-00007`** — project picker or route param from farmer/project list.  
3. **Add read-only Farmer list screen** — pull from sync `farmer` entity or new list API + projection.  
4. **Owner / role dashboard landing** — show role, block scope, counts (projects/tasks due), navigation hubs.  
5. **Stage transition button** — online `project.transition` call + sync pull to refresh tasks (prove auto-task).  
6. **Fix notification titles** — map `titleI18nKey` to Tamil `AppLocalizations` or display server-rendered title.  
7. **i18n sweep on demo paths** — Note, Queue note, Repair queue, error messages, sync labels.  
8. **Demo build flags** — disable onboarding auto-route, dev stub, feedback menu, readiness APK dialog.  
9. **Today’s tasks filter** — `due_date` on inbox + empty state in Tamil.  
10. **Single-page demo runbook** — bench seed IDs, owner vs field login, tunnel URL, exact tap order (Sync tab last).

---

## Checklist Roll-up (Demo Scope)

| Section | Pass | Fail | Partial |
|---------|------|------|---------|
| Backend DocTypes (demo) | 4 | 0 | 2 |
| Backend Python quality | 4 | 0 | 3 |
| Mobile architecture | 2 | 3 | 4 |
| Mobile Dart quality | 4 | 4 | 3 |
| Demo behaviors | 2 | 6 | 4 |
| Demo-killer hunt | 2 | 4 | 4 |
| Repo hygiene | 0 | 4 | 1 |

---

## Honest 5-Day Recommendation

| Days | Focus |
|------|--------|
| **1–2** | Blockers: HERO timeline UI, farmer list, kill hardcoded project ID, notification i18n, demo build flags |
| **3** | Stage transition screen (online API) + prove new tasks appear after sync |
| **4** | Owner dashboard shell + Tamil error/loading polish |
| **5** | Rehearse: login → dashboard → farmer → project timeline → transition → tasks → notifications → offline queue → sync tab |

**Do not** spend demo prep on billing, MIMIS Excel, or inventory consume unless client explicitly asks.

---

*Generated by Audit Pass 2 — Code Quality (Demo-Focused). No code changes applied.*
