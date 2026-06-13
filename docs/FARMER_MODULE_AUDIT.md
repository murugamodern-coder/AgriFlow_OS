# Farmer Module Audit Report

**Site:** `dev.agriflow.local`  
**Date:** 2026-06-07  
**Mode:** Read-only audit (no product code changes)  
**Scope:** Create, Edit, List, Search, Detail, Mobile APIs, Sync fields, Geography integrity

---

## Executive Summary

| Area | Status | Notes |
|------|--------|-------|
| Farmer Create (Desk + API) | ✅ Pass | Live insert tests succeeded |
| Farmer Edit (Desk) | ✅ Pass | Notes update persisted |
| Duplicate mobile | ✅ Pass | Warn-only; save allowed |
| Geography validation | ✅ Pass | Invalid village/block rejected |
| Mobile format validation | ✅ Pass | Non-10-digit rejected |
| API list/search/get/create | ✅ Pass | All live tests passed |
| Geography linkage (DB) | ✅ Pass | 4/4 farmers valid |
| Orphan farmers | ✅ Pass | No deleted farmers with active projects |
| Mobile UX completeness | 🟡 Partial | Create + list only; no edit/detail/search UI |
| Offline / sync integration | 🟡 Partial | Sync fields on DocType; Farmer not in delta sync |
| Permissions (field users) | 🟡 Risk | DocType perm = System Manager only |

**Live automated checks:** 15/15 PASS on bench (`agriflow.scripts.audit_farmer_module.run_audit`).

---

## 1. Farmer Create

### Desk (Frappe Form)

| Check | Result |
|-------|--------|
| Required fields enforced | ✅ `farmer_name`, `mobile`, `state`, `district`, `block`, `village` |
| Cascading geography | ✅ Client Script + `link_filters` on district/block/village |
| Autoname | ✅ `format:FR-{#####}` via `tabSeries` |
| Duplicate mobile | ✅ Orange `msgprint` warning; save continues |
| Invalid geography | ✅ Throws with explicit block/village mismatch message |

**Files:** `farmer.json`, `farmer.py`, `validation.py`, `farmer_cascading_geography.js`

**Operational risk (not logic bug):** `tabSeries` row lock from stale DB connections can hang save (`Lock wait timeout 1205`). See prior tabSeries audit.

### Mobile Create

| Check | Result |
|-------|--------|
| API `farmer.create` | ✅ Live test created FR-00062 |
| Geography cascade | ✅ State → district → block → village search |
| Payload | ✅ Sends link IDs (`593`, `5724`, etc.) |
| `created_via` | ✅ Set server-side to `mobile` |
| `client_id` | ⚠️ Not sent from mobile — no idempotent retry |
| Offline queue | ❌ Direct HTTP only; not in sync mutation queue |

**File:** `mobile/.../farmer_create_screen.dart`, `api/v1/farmer.py`

---

## 2. Farmer Edit

### Desk

| Check | Result |
|-------|--------|
| Save existing record | ✅ Pass (FR-00056 notes updated) |
| `doc_version` increment | ✅ Auto on each save |
| Deactivate with active project | ✅ Blocked by validation |
| Geography change | ✅ Re-validates full chain on save |

### Mobile

| Check | Result |
|-------|--------|
| Edit screen | ❌ **Not implemented** |
| `farmer.update` API | ❌ **Does not exist** |

---

## 3. Farmer List View

### Desk

| Check | Result |
|-------|--------|
| List loads | ✅ Standard Frappe list (System Manager) |
| `in_list_view` columns | ✅ farmer_name, mobile, district, block, village |
| Block scoping | ❌ No server-side block filter for Desk (API only) |

### Mobile

| Check | Result |
|-------|--------|
| List loads | ✅ `farmerListProvider` → API or offline projection fallback |
| FAB create | ✅ Routes to `/farmers/new` |
| Pull-to-refresh | ✅ Invalidates list + sync orchestrator |
| Tap row | ⚠️ Opens **project timeline**, not farmer profile |
| Search UI | ❌ **None** (API supports `search` param) |

**File:** `farmer_list_screen.dart`

---

## 4. Farmer Search

### Desk

| Check | Result |
|-------|--------|
| Global search / list filter | ✅ `search_fields`: farmer_name, mobile, aadhaar_last4, village |

### API (`farmer.list`)

| Check | Result |
|-------|--------|
| Search by farmer_name | ✅ Pass (live) |
| Search by mobile | ✅ Pass (live) |
| Search by ID (FR-xxxxx) | ✅ Supported in code |
| Pagination | ⚠️ Post-filters top `limit` rows by `modified desc` — may miss matches outside window |
| `has_more` / `cursor` | ⚠️ Always `false` / `null` |

### Mobile

| Check | Result |
|-------|--------|
| Search wired | ❌ Not used |

---

## 5. Farmer Detail View

### Desk

| Check | Result |
|-------|--------|
| Form view | ✅ Standard DocType form with all fields |
| Land parcels child table | ✅ Present; no custom validation in child controller |

### Mobile

| Check | Result |
|-------|--------|
| Dedicated detail screen | ❌ **None** |
| Profile snippet | ✅ Via project timeline header (`farmer.get` in `ProjectRemote`) |
| `FarmerRemote.get()` | ⚠️ Implemented but unused in farmer feature |

---

## 6. Mobile Farmer APIs

| Endpoint | Auth | Block scope | Live test |
|----------|------|-------------|-----------|
| `farmer.list` | JWT / session | ✅ | ✅ |
| `farmer.get` | JWT / session | ✅ | ✅ |
| `farmer.create` | JWT / session | ✅ | ✅ |
| `farmer.update` | — | — | ❌ Missing |
| `farmer.delete` | — | — | ❌ Missing |

**Permission note:** `doc.insert()` in API uses DocType permissions. Only **System Manager** has Farmer create in `farmer.json`. Field officers with JWT but without role will get **403 PERM_DENIED** unless permissions are expanded.

---

## 7. Farmer Mobile Sync Fields

| Field | DocType | Controller | API create | API get/list | Mobile sends |
|-------|---------|------------|------------|--------------|--------------|
| `client_id` | ✅ | Unique validate | ❌ not set | ❌ not returned | ❌ |
| `doc_version` | ✅ | Auto increment | default 1 | ✅ list/get | ❌ |
| `sync_status` | ✅ | — | `"synced"` | ❌ not returned | ❌ |
| `is_deleted` | ✅ | Soft delete side effect | filter only | filter only | ❌ |
| `created_via` | ✅ | — | `"mobile"` | ❌ not returned | ❌ |

**Sync engine:** Farmer is **not** a pull/push entity. Delta sync covers `timeline`, `task`, `farmer_project` only (`sync_engine/services/pull.py`).

---

## 8. Geography Linkage Integrity

**Live DB audit (4 active farmers):**

| Farmer | District | Block | Village | Chain |
|--------|----------|-------|---------|-------|
| FR-00001 | 593 | 5724 | VLG01 | ✅ |
| FR-00002 | 593 | 5724 | VLG01 | ✅ |
| FR-00055 | 593 | 5724 | 631737 | ✅ |
| FR-00056 | 593 | 5724 | 631737 | ✅ |

- No broken District/Block/Village links
- No orphan Farmer records with active Farmer Projects
- Invalid cross-district village (630559 on block 5724) correctly **rejected**

---

## Issues Found

| # | Issue | Severity | Area |
|---|-------|----------|------|
| 1 | No mobile farmer **edit** (no UI, no API) | **High** | Mobile |
| 2 | Farmer **not in sync engine** — create is online-only, no offline idempotency | **High** | Sync |
| 3 | **`client_id` never sent** on mobile create — retry can duplicate farmers | **High** | Mobile / API |
| 4 | DocType permissions = **System Manager only** — field JWT users may fail create | **High** | Permissions |
| 5 | API list **search scans only top N** by modified — misses older farmers | **Medium** | API |
| 6 | Mobile list has **no search UI** despite API support | **Medium** | Mobile |
| 7 | List row tap opens **project**, not farmer detail | **Medium** | Mobile UX |
| 8 | No dedicated **farmer detail screen** on mobile | **Medium** | Mobile |
| 9 | Duplicate mobile **warning invisible on mobile** (`msgprint` Desk-only) | **Medium** | Mobile / API |
| 10 | `farmer.get` omits `state`, `is_active`, sync metadata | **Medium** | API |
| 11 | Desk list has **no block scoping** (unlike API) | **Medium** | Desk |
| 12 | **`tabSeries` lock timeout** can hang Farmer create (operational) | **Medium** | Ops / DB |
| 13 | No list **pagination** (`has_more` always false) | **Low** | API |
| 14 | `FarmerRemote.get()` dead code in farmer feature | **Low** | Mobile |
| 15 | Officer link **unfiltered** by block/district | **Low** | Desk / API |
| 16 | Land parcel child table **no validation** | **Low** | Desk |
| 17 | Deep link `/farmers/new` not registered | **Low** | Mobile |

**Critical issues:** None in live functional tests. Geography and validation gates are working.

---

## Recommended Fixes (priority order)

### High

1. **Add Farmer DocType permissions** for field officer role (or use `ignore_permissions` with explicit block-scope checks in API only — document chosen model).
2. **Send `client_id` (UUID) from mobile create**; honor idempotent create in API if `client_id` already exists.
3. **Add `farmer.update` API** + mobile edit screen (or defer explicitly in product roadmap).
4. **Integrate Farmer into offline strategy** — either add to sync pull with `modified_since`, or queue creates in mutation log.

### Medium

5. **Mobile search bar** wired to `farmer.list?search=`.
6. **Mobile farmer detail route** (`/farmers/:name`) using `farmer.get`.
7. **Move API search to SQL** (`LIKE` on farmer_name/mobile) instead of post-filter on limited rows.
8. **Return duplicate-mobile warning** in API create response (e.g. `warnings: []`) for mobile snackbar.
9. **Expand `farmer.get`** to include `state`, `is_active`, `doc_version`, `created_via`.

### Low

10. Implement cursor pagination on `farmer.list`.
11. Filter `officer` link by block in Client Script + API validation.
12. Add land parcel validation (survey uniqueness per village, etc.) when business rules defined.
13. Resolve stale `tabSeries` locks proactively (kill stale connections / bench restart SOP).

---

## Test Evidence (Live — dev.agriflow.local)

```
Geography linkage integrity     PASS  (4 farmers)
Duplicate mobile save           PASS  (FR-00059 shared with FR-00056)
Invalid geography blocked       PASS  (630559 rejected for 5724)
Mobile format validation        PASS  (5-digit rejected)
Farmer edit                     PASS  (FR-00056 notes)
API search by farmer_name       PASS
API search by mobile            PASS
API get detail                  PASS  (FR-00056)
API create                      PASS  (FR-00062, cleaned up)
Orphan farmer records           PASS
Sync fields on DocType          PASS  (all 5 present)
```

---

## Key Files Reference

| Purpose | Path |
|---------|------|
| DocType | `backend/agriflow/agriflow/farmer_registry/doctype/farmer/farmer.json` |
| Controller | `backend/agriflow/agriflow/farmer_registry/doctype/farmer/farmer.py` |
| Validation | `backend/agriflow/agriflow/farmer_registry/utils/validation.py` |
| API | `backend/agriflow/agriflow/api/v1/farmer.py` |
| Permissions | `backend/agriflow/agriflow/api/v1/permissions.py` |
| Desk cascade script | `backend/agriflow/agriflow/farmer_registry/client_scripts/farmer_cascading_geography.js` |
| Mobile create | `mobile/agriflow_mobile/lib/features/farmer/presentation/farmer_create_screen.dart` |
| Mobile list | `mobile/agriflow_mobile/lib/features/farmer/presentation/farmer_list_screen.dart` |
| Mobile API client | `mobile/agriflow_mobile/lib/features/farmer/data/farmer_remote.dart` |
