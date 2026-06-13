# Cascading Filter Fix Report

## Status: 🟢 FIXED

## Bug Summary

- Block dropdown showed all **313** TN blocks (should be **12** for Tiruvannamalai district `593`)
- Village dropdown showed all **18,483** villages (should be **107** for Polur block `5724`, incl. demo `VLG01`)
- Save failed: *"Village must belong to the selected Block"* when user picked village `630559` (Polur in Ranipet district `731`) while block was `5724` (Polur in Tiruvannamalai)

**Name collision example:** Village `630559` "Polur" → block `5715`, district `731`. Block `5724` "Polur" → district `593`. Same name, different hierarchy — filters are mandatory.

## Root Cause

- Farmer DocType Link fields (`district`, `block`, `village`) had **no `link_filters`**
- **No Client Script** enforcing `frm.set_query()` on parent field change
- Backend validation existed but only caught errors **after** bad selection (no UX filter)

## Fix Applied

| Phase | Action | Status |
|-------|--------|--------|
| 1 | `farmer.json` link_filters (`eval:doc.*` syntax) | ✅ |
| 2 | Client Script **"Farmer Cascading Geography"** (Desk form) | ✅ |
| 3 | Backend `validate_geography_chain` — clearer error messages | ✅ |
| 4 | Mobile cascading state reset on district change | ✅ |

### Phase 1 — DocType link_filters

```json
district → [["District","state","=","eval:doc.state"]]
block    → [["Block","district","=","eval:doc.district"]]
village  → [["Village","block","=","eval:doc.block"]]
```

> Note: Frappe requires `eval:doc.fieldname` — plain `"district"` is treated as a literal string and does **not** work.

### Phase 2 — Client Script

File: `farmer_registry/client_scripts/farmer_cascading_geography.js`  
Installed to DB as **Farmer Cascading Geography** via `after_migrate` hook.

Behavior:
- Clears child fields when parent changes (district → block/village, block → village)
- Sets `frm.set_query()` filters on district, block, village, cluster

### Phase 3 — Backend validation

`validate_geography_chain()` in `farmer_registry/utils/validation.py` (already called from `Farmer.validate()`):

```
Village '630559' does not belong to Block '5724'. It belongs to Block '5715'.
```

### Phase 4 — Mobile

`farmer_create_screen.dart`: district change now clears block, village, and blocks list in the same `setState` before reloading blocks.

## Test Results

| Test | Pre-Fix | Post-Fix |
|------|---------|----------|
| Block count after district `593` select | 313 ❌ | **12** ✅ |
| Village count after block `5724` select | 18,483 ❌ | **107** (DB) / **100** (API page cap) ✅ |
| Backend validation on bad hierarchy | Threw generic msg | **Throws with block IDs** ✅ |
| Client Script installed | None ❌ | **Enabled on Farmer Form** ✅ |
| link_filters on DocType | None ❌ | **All 3 fields set** ✅ |

## Files Changed

- `backend/agriflow/agriflow/farmer_registry/doctype/farmer/farmer.json`
- `backend/agriflow/agriflow/farmer_registry/utils/validation.py`
- `backend/agriflow/agriflow/farmer_registry/client_scripts/farmer_cascading_geography.js`
- `backend/agriflow/agriflow/farmer_registry/install/farmer_cascading_client_script.py`
- `backend/agriflow/agriflow/farmer_registry/install/apply_farmer_link_filters.py`
- `backend/agriflow/agriflow/hooks.py` (after_migrate hooks)
- `backend/agriflow/agriflow/scripts/verify_cascading_filters.py`
- `mobile/agriflow_mobile/lib/features/farmer/presentation/farmer_create_screen.dart`

## API Tests (Final)

```bash
# Blocks for Tiruvannamalai (593) — expect 12
bench --site dev.agriflow.local execute agriflow.scripts.verify_cascading_filters.run_verification
```

**Output (2026-06-07):**

```json
{
  "link_filters": {
    "district": "[[\"District\",\"state\",\"=\",\"eval:doc.state\"]]",
    "block": "[[\"Block\",\"district\",\"=\",\"eval:doc.district\"]]",
    "village": "[[\"Village\",\"block\",\"=\",\"eval:doc.block\"]]"
  },
  "client_script": { "enabled": 1, "dt": "Farmer", "view": "Form" },
  "db_block_count_593": 12,
  "db_village_count_5724": 107,
  "api_block_count_593": 12,
  "api_village_count_5724": 100,
  "bad_hierarchy_rejected": true,
  "bad_hierarchy_message": "Village '630559' does not belong to Block '5724'. It belongs to Block '5715'."
}
```

## User Verification Steps

### Frappe Desk (Web UI)

1. Hard refresh: **Ctrl+Shift+R** on `http://127.0.0.1:8000/app/farmer/new`
2. State: **Tamil Nadu**
3. District: **TIRUVANNAMALAI (593)** → Block field should list **12** blocks only (Polur, Chetpet, Arani, …)
4. Block: **Polur (5724)** → Village field should list **~107** villages (not 18,483)
5. Search village **Ven** → Venmani, Palvathuvendran
6. Save → **Success** ✅

### Mobile (Windows)

```powershell
cd C:\AgriFlow_OS\AgriFlow_Main\mobile\agriflow_mobile
flutter pub get
flutter run -d windows --dart-define=API_BASE_URL=http://172.28.181.245:8000
```

Same flow: TN → Tiruvannamalai → Polur → Venmani → Save.

## Deploy Notes

Bench app is not symlinked — rsync before migrate:

```bash
rsync -a .../backend/agriflow/agriflow/farmer_registry/ ~/workspace/frappe-bench/apps/agriflow/agriflow/farmer_registry/
rsync -a .../hooks.py ~/workspace/frappe-bench/apps/agriflow/agriflow/hooks.py
bench --site dev.agriflow.local migrate
bench --site dev.agriflow.local clear-cache
```

If full `migrate` hangs on metadata lock, run:

```bash
bench --site dev.agriflow.local execute agriflow.farmer_registry.install.apply_farmer_link_filters.apply_farmer_link_filters
bench --site dev.agriflow.local execute agriflow.farmer_registry.install.farmer_cascading_client_script.ensure_farmer_cascading_client_script
bench --site dev.agriflow.local clear-cache
```
