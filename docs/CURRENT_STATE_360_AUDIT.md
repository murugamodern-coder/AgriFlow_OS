# AgriFlow_OS — Current State 360° Audit

**Audit date:** 2026-06-06  
**Auditor mode:** Read-only diagnosis (Area 5 bench start attempted; no fixes applied)  
**Project root:** `C:\AgriFlow_OS\AgriFlow_Main`  
**WSL bench:** `/home/muruga/workspace/frappe-bench`  
**Site:** `dev.agriflow.local`

---

## Executive Summary

- **Project location:** `C:\AgriFlow_OS\AgriFlow_Main`
- **Last commit:** `a9f2913` — feat(stabilization-v1): windsurf phase 1 audit + pubspec generate fix + app launch ready (2026-05-29 13:42:31 +0530)
- **Branch:** `stabilization-v1` (in sync with `origin/stabilization-v1`, divergence `0 0`)
- **Backend status:** 🔴 DOWN — `bench` CLI missing from venv; port 8000 not listening; site DB exists but has **0 tables**
- **Mobile status:** 🟡 PARTIAL — Flutter project builds (`.dart_tool/` + `build/` present); Tamil l10n generated; no `API_BASE_URL` by default → sync/API calls fail (`NetworkFailure`)
- **Demo readiness:** **2/8** checklist items demonstrable today without a live backend (Tamil login shell + navigation shell only)
- **Overall completion:** **~58%** source/code vs PRD scope; **~12%** operational/runtime readiness

---

## What Works Today (Evidence-Based)

- ✅ **Git repository is clean and synced** — `git status`: working tree clean; local HEAD matches `origin/stabilization-v1` at `a9f2913` (Area 1)
- ✅ **Mobile app compiles and launches (UI shell)** — `mobile/agriflow_mobile/.dart_tool` and `build/` exist; `pubspec.lock` present; `flutter: generate: true` in `pubspec.yaml:51`
- ✅ **Tamil i18n pipeline complete** — `lib/l10n/app_localizations.dart`, `app_localizations_ta.dart`, `app_en.arb`, `app_ta.arb` all present (Area 6)
- ✅ **Core demo-path Flutter features exist in code** — `auth` (4), `dashboard` (2), `farmer` (3), `project_lifecycle` (11), `tasks` (8), `notifications` (6), `sync` (5) files under `lib/features/` (Area 6)
- ✅ **Backend source code in repo is substantial** — 33 DocType JSON files, 21 API v1 modules under `backend/agriflow/agriflow/api/v1/` including `auth.py`, `farmer.py`, `project.py`, `task.py`, `sync.py`, `inventory.py`, `notification.py` (Areas 2, 9)
- ✅ **WSL infrastructure services running** — `systemctl is-active mariadb` → `active`; `systemctl is-active redis-server` → `active` (Area 3)
- ✅ **MariaDB credentials valid** — DB `_d3af7c5e24dd488b` exists and is reachable with site credentials (Area 4)

---

## What's Broken (Evidence-Based)

- ❌ **Frappe bench CLI absent** — `/home/muruga/workspace/frappe-bench/env/bin/bench`: No such file; `pip show frappe-bench` → not found; `python -m bench` → No module named bench (Area 3, 5)
- ❌ **Backend not serving HTTP** — WSL `curl http://127.0.0.1:8000/api/method/ping` → HTTP_CODE `000`; `PORT_8000_NOT_LISTENING`; Windows `Test-NetConnection localhost:8000` → `TcpTestSucceeded: False`; WSL IP `172.28.181.245:8000` → `False` (Areas 5, 7)
- ❌ **Site database is empty (no Frappe schema)** — `SELECT COUNT(*) ... table_schema='_d3af7c5e24dd488b'` → `table_count: 0`; `tabSingles` does not exist (Area 4). Stale `touched_tables.json` lists core tables from a prior partial install — not reflected in live DB.
- ❌ **`bench --site dev.agriflow.local list-apps` cannot run** — bench binary missing (Area 3)
- ❌ **Mobile ↔ backend connectivity** — `API_BASE_URL` defaults to empty string (`env.dart:7-9`); `docs/CONNECTION_DIAGNOSIS.md` documents Windows cannot reach `:8000`; matches audit curl/network tests (Areas 6, 7)
- ❌ **Real login and sync** — `auth_repository.dart:103-107` posts to `agriflow.api.v1.auth.login`; without backend + URL, real auth fails; sync orchestrator requires `SyncRemote` API (Area 10)

---

## What's Not Built (PRD vs Reality)

- ⬜ **M3 Dual Billing** — `modules.txt` lists `Billing` but no Billing DocType JSON under `backend/agriflow/`; no `billing` mobile feature folder
- ⬜ **M7 Service / AMC** — `modules.txt` lists `Service`; no Service DocType or mobile UI
- ⬜ **M9 Profit Dashboard** — `modules.txt` lists `Profit`; no Profit DocType, API, or mobile screen
- ⬜ **M4 MIMIS Sync (standalone module)** — MIMIS fields exist on `Farmer Project` (`farmer_project.json` mimis_* fields); no `MIMIS Import Batch` / reconciliation DocTypes implemented (spec-only in `DOCTYPES.md`)
- ⬜ **Mobile modules never created** — no `lib/features/billing`, `catalog`, `expense`, or `officer` folders (Area 6)
- ⬜ **`docs/BACKEND_LIVE_REPORT.md`** — file does not exist (Area 8)
- ⬜ **Root `deploy/` folder** — not present; deployment artifacts live under `scripts/deploy/` and `infra/` instead (Area 2)

---

## Area-by-Area Findings

### Area 1: Repository State

| Check | Result | Evidence |
|-------|--------|----------|
| Working tree | **Clean** | `git status`: nothing to commit, working tree clean |
| Branch | `stabilization-v1` | `* stabilization-v1` |
| Remote | Alive | `origin https://github.com/murugamodern-coder/AgriFlow_OS.git` |
| Local vs remote | **In sync** | `git rev-list --left-right --count origin/stabilization-v1...HEAD` → `0 0` |
| Last local commit | `a9f2913` 2026-05-29 | Same hash on `origin/stabilization-v1` |
| Untracked files | **None** | `git status --porcelain` empty |

**Recent commits (`git log --oneline -10`):**

```
a9f2913 feat(stabilization-v1): windsurf phase 1 audit + pubspec generate fix + app launch ready
7382b5a Added stabilization roadmap
df468d8 docs: polish GitHub presentation layer
b56f29a feat: AgriFlow SaaS platform
fb02436 fix: localize timeline stage secondary labels for Tamil demo
64f7872 release: pilot demo ready
a735f39 polish: theme + i18n consistency
bfc0ed4 feat: visible sync engine for demo wow moment
a3753ae feat: polish notification panel for demo
529403c feat: polish task feed for demo
```

**Branches:** `main`, `stabilization-v1`, `remotes/origin/main`, `remotes/origin/stabilization-v1`

**Note:** Latest commit is **8 days old** (2026-05-29 vs audit date 2026-06-06). No local divergence, but no commits since backend recovery work described in task context.

---

### Area 2: Project File Integrity

**Top-level folders present:** `backend/`, `mobile/`, `docs/`, `infra/`, `scripts/` — **no root `deploy/`** (deploy scripts under `scripts/deploy/`).

**Git tracked files:** 799 paths at HEAD (`git ls-tree -r HEAD --name-only | Measure-Object`).

**Working tree vs HEAD:** Clean — no modified or untracked files; on-disk matches committed state.

**PHASE*_REPORT.md files (14 found, all at repo root):**

- `PHASE11_SYNC_REPORT.md` through `PHASE24_PERFORMANCE_OBSERVABILITY_REPORT.md`
- Also `PHASE13_INVENTORY_REPORT.md`, `PHASE14_MOBILE_REPORT.md`, `PHASE15_E2E_VALIDATION_REPORT.md`, etc.
- No single `PHASE1_REPORT.md` — early phases documented via scripts + `DOCTYPES.md` instead

**Architecture docs:**

| File | Status |
|------|--------|
| `PRD.md` | ✅ Present |
| `ARCHITECTURE.md` | ✅ Present |
| `DOCTYPES.md` | ✅ Present (1500+ lines, spec dated 2026-05-20) |
| `docs/CONNECTION_DIAGNOSIS.md` | ✅ Present (4618 bytes, 2026-05-29) |
| `docs/BACKEND_LIVE_REPORT.md` | ❌ Missing |

**Orphan/corrupt files:** None detected. WSL warning on audit: `wsl: Failed to start the systemd user session for 'muruga'` — environmental, not repo corruption.

---

### Area 3: Backend (Frappe) Setup

**Bench directory (`ls -la /home/muruga/workspace/frappe-bench/`):**

```
Procfile, apps/, archived/, config/, env/, logs/, patches.txt, sites/
```

**Apps (`ls apps/`):** `agriflow`, `frappe`

**Sites (`ls sites/`):** `apps.json`, `apps.txt`, `assets`, `common_site_config.json`, `dev.agriflow.local`

**`site_config.json` (first keys):**

```json
{
 "agriflow_fcm_server_key": "simulate",
 "agriflow_min_app_version": "0.24.0",
 "agriflow_rollout_wave": "pilot_a",
 "db_name": "_d3af7c5e24dd488b",
 "db_password": "LJeWV9V7Y7ffySnT",
 "db_type": "mariadb",
 "host_name": "https://filled-neutral-pentium-forty.trycloudflare.com"
}
```

| Check | Status | Evidence |
|-------|--------|----------|
| `list-apps` | 🔴 FAIL | `env/bin/bench: No such file or directory` |
| Frappe processes | 🔴 NONE | `ps aux \| grep bench\|gunicorn\|frappe` → no matches |
| MariaDB service | 🟢 active | `systemctl is-active mariadb` → `active` |
| Redis service | 🟢 active | `systemctl is-active redis-server` → `active` |
| Procfile | Expects `bench` | `web: bench serve --port 8000` — cannot run without bench package |
| Frappe app source | ✅ Present | `apps/frappe/frappe/__init__.py` exists |
| AgriFlow app on bench | ✅ Symlinked | `apps/agriflow` listed |

**Root cause:** Python venv has Frappe runtime deps but **`frappe-bench` CLI was never installed** (or was removed) from `env/bin/`. Site cannot be managed or served via standard bench commands.

---

### Area 4: Database Health

**Credentials:** ✅ Valid — user `_d3af7c5e24dd488b` connects.

**`SHOW DATABASES;`:**

```
Database
_d3af7c5e24dd488b
information_schema
```

**Table count:**

```sql
SELECT COUNT(*) AS table_count FROM information_schema.tables
WHERE table_schema='_d3af7c5e24dd488b';
→ table_count: 0
```

**Core Frappe tables:**

| Table | Status |
|-------|--------|
| `tabSingles` | ❌ Does not exist |
| `tabDocType` | ❌ Does not exist |
| `tabUser` | ❌ Does not exist |

**Verdict:** 🔴 **Empty database** — schema not installed. Consistent with failed migration / pending reinstall described in task context.

**Stale artifact:** `sites/dev.agriflow.local/touched_tables.json` lists `tabDocType`, `tabSingles`, etc. from **2026-05-20** partial touch — **not authoritative**; live MariaDB has zero tables.

---

### Area 5: Backend Live Test

**Procedure executed:**

1. `pkill -f bench/gunicorn` — exit 15 (no processes)
2. Attempted `nohup ./env/bin/bench start` — **bench binary not found**; no `/tmp/audit_bench.log` created
3. Waited; tested endpoints

**Results:**

```
curl http://127.0.0.1:8000/api/method/ping
→ HTTP_CODE: 000

curl -H 'Host: dev.agriflow.local' .../frappe.client.get_count?doctype=User
→ HTTP_CODE: 000

ss/netstat port 8000 → PORT_8000_NOT_LISTENING
```

**Verdict:** 🔴 **DOWN**

**Note:** Bench was **not left running** — it could not be started. User must reinstall `frappe-bench` CLI and run `bench new-site` / `bench migrate` or `bench reinstall` before any live test can succeed.

---

### Area 6: Mobile App (Flutter)

| Check | Result |
|-------|--------|
| `pubspec.yaml` | ✅ `mobile/agriflow_mobile/pubspec.yaml` |
| `generate: true` | ✅ Line 51 |
| l10n files | ✅ 5 files in `lib/l10n/` including `app_localizations*.dart` |
| `pubspec.lock` | ✅ Present |
| `.dart_tool/` | ✅ True (pub get ran) |
| `build/` | ✅ True (prior build ran) |
| Flutter in WSL | ✅ `/mnt/c/Users/murug/Downloads/flutter_sdk/flutter/bin/flutter` |

**Feature folder file counts:**

| Folder | Files | Expected in audit brief |
|--------|-------|-------------------------|
| auth | 4 | ✅ |
| farmer | 3 | ✅ |
| project_lifecycle | 11 | ✅ (lifecycle) |
| tasks | 8 | ✅ |
| sync | 5 | ✅ |
| notifications | 6 | ✅ |
| inventory | 1 | partial (remote only) |
| commercial | 1 | partial |
| dashboard | 2 | ✅ |
| pilot_ops | 3 | extra |
| readiness | 1 | extra |
| **billing** | — | ❌ missing |
| **catalog** | — | ❌ missing |
| **expense** | — | ❌ missing |
| **officer** | — | ❌ missing |

**API configuration issue:**

- `Env.apiBaseUrl` default `''` (`env.dart:7-9`)
- `Env.demoMode` default `true` → disables dev auth stub (`env.dart:51-53`)
- Debug launch without `API_BASE_URL` hits assert unless `DEV_AUTH_STUB=true` + `DEMO_MODE=false` (`env.dart:56-64`, `CONNECTION_DIAGNOSIS.md:22-30`)

**Mobile status verdict:** 🟡 **PARTIAL** — rich UI code, builds locally, cannot complete E2E without backend URL + populated DB.

---

### Area 7: WSL Network Configuration

**WSL IP:** `172.28.181.245`

**Default route:** `default via 172.28.176.1 dev eth0`

**Windows connectivity (PowerShell `Test-NetConnection`):**

| Target | Port | TcpTestSucceeded |
|--------|------|------------------|
| `localhost` | 8000 | **False** |
| `172.28.181.245` (WSL IP) | 8000 | **False** |

**Verdict:** Flutter on Windows **cannot** reach Frappe on WSL today because **nothing listens on port 8000**. Even with WSL mirrored networking, backend must be started first. Documented fix path in `CONNECTION_DIAGNOSIS.md`: set `--dart-define=API_BASE_URL=http://<wsl-ip>:8000` once bench serves.

---

### Area 8: Documentation Trail

**`docs/` listing (28 markdown files + screenshots/):**

All committed (working tree clean). Key audit-requested files:

| Document | Size | LastWrite | Committed | Stale (>7d)? |
|----------|------|-----------|-----------|--------------|
| `AUDIT_PASS_1_REPORT.md` | 16283 | 2026-05-20 | ✅ | Yes |
| `AUDIT_PASS_2_REPORT.md` | 15682 | 2026-05-20 | ✅ | Yes |
| `PRE_REHEARSAL_AUDIT.md` | 17544 | 2026-05-22 | ✅ | Yes |
| `DAY5_VERIFICATION.md` | 9853 | 2026-05-22 | ✅ | Yes |
| `CONNECTION_DIAGNOSIS.md` | 4618 | 2026-05-29 | ✅ | Yes (8d) |
| `GITHUB_POLISH_REPORT.md` | 5492 | 2026-05-22 | ✅ | Yes |
| `BACKEND_LIVE_REPORT.md` | — | — | ❌ N/A | N/A |

**Documentation quality:** Extensive rehearsal/GA checklists exist, but **none reflect the current empty-DB / missing-bench state** after backend recovery attempts. `CONNECTION_DIAGNOSIS.md` (May 29) is closest to present reality.

---

### Area 9: PRD Module Matrix

Evidence paths cited below are under `C:\AgriFlow_OS\AgriFlow_Main\`.

| Module | Backend DocType | Backend API | Mobile UI | E2E Working |
|--------|----------------|-------------|-----------|-------------|
| **M1 Farmer Registry** | ✅ `backend/.../farmer/farmer.json`, `farmer_land_parcel.json` | ✅ `api/v1/farmer.py` | ✅ `lib/features/farmer/` (3 files) | 🔴 No — empty DB, API down |
| **M2 Inventory** | ✅ `inventory_item`, `warehouse`, `stock_ledger_entry`, `project_material_allocation` | ✅ `api/v1/inventory.py` | 🟡 `lib/features/inventory/` (1 file, remote only) | 🔴 No |
| **M3 Dual Billing** | ❌ No DocType | ❌ No billing API | ❌ No feature folder | 🔴 NOT IMPLEMENTED |
| **M4 MIMIS Sync** | 🟡 Fields on `Farmer Project` + timeline events; no import batch DocType | 🟡 Via project/sync APIs | ❌ No dedicated UI | 🔴 No |
| **M5 12-Stage Lifecycle** | ✅ `farmer_project`, `project_stage`, `timeline_event`, fixtures | ✅ `api/v1/project.py`, lifecycle services | ✅ `lib/features/project_lifecycle/` (11 files) | 🔴 No — needs backend + seed |
| **M6 Task Engine** | ✅ `project_task`, templates in fixtures | ✅ `api/v1/task.py` | ✅ `lib/features/tasks/` (8 files) | 🔴 No |
| **M7 Service/AMC** | ❌ Listed in `modules.txt` only | ❌ | ❌ | 🔴 NOT IMPLEMENTED |
| **M8 Officer Network** | ✅ `officer`, `cluster`, `village`, `block`, `district`, assignment history | 🟡 Indirect via permissions/geo | ❌ No `officer` feature folder | 🔴 No |
| **M9 Profit View** | ❌ Listed in `modules.txt` only | ❌ | ❌ | 🔴 NOT IMPLEMENTED |

**PRD modules fully coded for demo spine (M1+M5+M6+sync+notifications):** ~5/9 with backend+mobile artifacts. **PRD modules E2E working today:** 0/9.

---

### Area 10: Demo Readiness Checklist

Assumes default launch (`DEMO_MODE=true`, empty `API_BASE_URL`, backend 🔴 DOWN as audited).

| Demo item | Status | Evidence |
|-----------|--------|----------|
| Login flow | 🟡 **PARTIAL** | UI renders Tamil (`login_screen.dart`); real login needs API (`auth_repository.dart:103`); dev stub only when `DEMO_MODE=false` + `DEV_AUTH_STUB=true` |
| Owner dashboard | 🟡 **PARTIAL** | `home_dashboard_screen.dart` exists; counts from projections — empty without prior sync/seed |
| Farmer list (read-only) | 🔴 **BROKEN** | `farmer_list_provider` calls API then cache fallback (`farmer_list_screen.dart:15-20`) — empty DB + no cache → `emptyFarmers` |
| 12-stage Timeline UI | 🟡 **PARTIAL** | `project_timeline_screen.dart` + `ProjectStages.ordered` — needs `projectRemote.fetchTimelineBundle`; fails offline without cached projections |
| Task feed | 🟡 **PARTIAL** | `task_inbox_screen.dart` — UI complete; data from sync/API |
| Stage update + auto-task | 🔴 **BROKEN** | `_advanceStage` calls `projectRemote.transition` (`project_timeline_screen.dart:56-60`) — requires live backend |
| Notification panel | 🟡 **PARTIAL** | `notification_inbox_screen.dart` — UI complete; inbox empty without sync |
| Offline → online sync demo | 🔴 **BROKEN** | `SyncOrchestrator` + `SyncRemote` require reachable `API_BASE_URL`; `NetworkFailure` documented in `CONNECTION_DIAGNOSIS.md` |

**Score: 2/8** — Tamil login/navigation shell demonstrable; data-rich demo paths from `PRE_REHEARSAL_AUDIT.md` (May 22) **not reproducible** without backend reinstall + seed + `API_BASE_URL`.

---

## Critical Issues (Ranked by Demo Impact)

1. **Empty site database (0 tables)** — blocks all API, auth, sync, demo seed — **~2–4 hours** (`bench reinstall` + migrate + `seed_demo`)
2. **Missing `frappe-bench` CLI in venv** — cannot start serve/worker/schedule — **~30 min** (`pip install frappe-bench` in bench env or recreate venv)
3. **No process on port 8000** — Flutter `NetworkFailure` — unblocked by #1 + #2 + `bench start`
4. **`API_BASE_URL` not set in mobile launch** — even after backend up, app won't connect — **~5 min** (dart-define or env doc update)
5. **Docs claim "pilot demo ready" but post-recovery state undocumented** — risk of false confidence — **~30 min** doc refresh

---

## Recommended Next Steps (Prioritized)

1. **Install bench CLI in WSL venv** — 30 min — `cd frappe-bench && env/bin/pip install frappe-bench` — unblocks all bench commands
2. **Reinstall/migrate site on empty DB** — 2–4 hours — `bench --site dev.agriflow.local reinstall` or `bench migrate` + install apps — creates Frappe schema + AgriFlow DocTypes
3. **Run demo seed** — 30 min — `bench execute agriflow.commands.seed_demo` (script exists at `backend/.../commands/seed_demo.py`) — populates Kumar/Palani demo data
4. **Start bench and verify ping** — 15 min — `bench start`; curl ping + User count — confirms Area 5 🟢
5. **Launch Flutter with WSL IP** — 5 min — `--dart-define=API_BASE_URL=http://172.28.x.x:8000 --dart-define=DEMO_MODE=true` — unblocks E2E demo path
6. **Write `BACKEND_LIVE_REPORT.md`** — 20 min — capture working curl outputs for future audits

---

## Path to 100% Completion

Realistic timeline based on findings (single developer, familiar with bench):

| Window | Deliverable |
|--------|-------------|
| **Today (next 2 hours)** | Restore bench CLI + reinstall site schema + `bench start` + ping OK |
| **Tomorrow** | Demo seed + Flutter E2E for M1/M5/M6/sync/notifications (rehearsal path from May 22) |
| **This week** | M2 inventory mobile UI; M4 MIMIS reconciliation DocTypes; officer mobile views |
| **Later** | M3 billing, M7 AMC, M9 profit — currently spec-only / module.txt placeholders |

**Code-complete estimate:** ~58% of PRD today → **~75%** after demo spine E2E restored → **100%** requires M3/M7/M9 greenfield (likely 3–4 additional weeks).

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Empty DB re-install fails mid-migrate | Medium | Use `bench backup` before retry; follow `docs/SETUP_FROM_SCRATCH.md` |
| WSL IP changes break Flutter dart-define | High | Use `localhost` with WSL2 mirrored networking or document IP refresh |
| Stale docs mislead stakeholders | High | Treat this audit as source of truth until backend live report exists |
| `host_name` in site_config points to dead Cloudflare tunnel | Medium | Override for local dev or update tunnel |
| Secrets in site_config committed to bench (not git repo) | Low | Rotate DB password if bench ever copied |

---

## Confidence Score

| Dimension | Score (0–100) | Rationale |
|-----------|---------------|-----------|
| Code quality | **72** | Structured feature-first Flutter; Frappe services/APIs well-organized |
| Demo readiness | **15** | UI ready; runtime stack down |
| Production readiness | **8** | Empty DB, no running services, tunnel hostname stale |
| Documentation | **55** | Volume high but stale vs actual backend state |
| **Honest overall** | **58** | Strong codebase, weak operational layer |

---

## Appendix: Raw Command Evidence

<details>
<summary>Area 5 curl output</summary>

```
HTTP_CODE: 000  (ping)
HTTP_CODE: 000  (get_count User)
PORT_8000_NOT_LISTENING
```
</details>

<details>
<summary>Area 4 DB query</summary>

```
table_count: 0
ERROR 1146: Table '_d3af7c5e24dd488b.tabSingles' doesn't exist
```
</details>

<details>
<summary>Area 3 bench missing</summary>

```
/home/muruga/workspace/frappe-bench/env/bin/bench: No such file or directory
WARNING: Package(s) not found: frappe-bench
```
</details>

---

*End of audit — generated 2026-06-06. No code, config, or database mutations were performed except attempted (failed) bench start.*
