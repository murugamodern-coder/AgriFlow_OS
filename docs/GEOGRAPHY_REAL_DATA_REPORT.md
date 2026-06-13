# Geography Real Data Implementation Report

## Status: 🟢 COMPLETE

## Phase Results
| Phase | Goal | Result |
|-------|------|--------|
| 1 | LGD data downloaded | 3 CSVs, 18,833 data rows |
| 2 | DocType schema updated | `lgd_code` fields + `Geo State` + optional cluster/officer |
| 3 | Bulk import complete | 38 TN districts imported (+1 legacy TVM), 313 blocks, 18,482 villages |
| 4 | Cascading APIs created | 6 endpoints tested (Administrator session) |
| 5 | Mobile UI updated | Cascading dropdowns + village autocomplete |

## Phase 1: Data Source
- **Source used:** GitHub LGD mirror — [planemad/india-local-government-directory](https://github.com/planemad/india-local-government-directory)
- **CSVs in:** `scripts/geography_data/`
- **Prep script:** `scripts/geography_data/prepare_tn_csv.py`
- **States:** 1 (Tamil Nadu, LGD code 33)
- **Districts:** 38
- **Blocks:** 313 (LGD Sub-District / Taluk — village CSV parent key)
- **Villages:** 18,482 (UTF-8; Tamil local names when present)

> **Note:** LGD `4-village.csv` links villages to **Sub-District Code**, not Development Block Code. Sub-districts are imported as `Block` records so District → Block → Village cascading matches official village parent keys. Development blocks (`blocks.csv`, 388 rows) are documented in `DOWNLOAD_STEPS.md` as an alternate source.

## Phase 2: DocType Changes
- **`Geo State`** DocType added (named `Geo State` to avoid Frappe core `State` collision)
- **`District.lgd_code`** added; `state` → Link → Geo State
- **`Block.lgd_code`** added
- **`Village.lgd_code`** added; **`Village.cluster`** → optional
- **`Farmer.state`** → Link Geo State (required, default Tamil Nadu)
- **`Farmer.officer`** → Link Officer (optional)
- **`Farmer.cluster`** → optional, editable (no longer fetched read-only from village)

## Phase 3: Import Stats
- **Time taken:** ~72 seconds
- **Rows imported:** 38 districts, 313 blocks, 18,482 villages
- **Duplicates skipped:** 0 on re-run (existence check by PK / LGD code)
- **Live DB totals (incl. legacy demo):** Geo State 1 · District 39 · Block 325 · Village 18,483
- **Command:** `bench --site dev.agriflow.local execute agriflow.commands.import_geography.import_geography`

## Phase 4: API Endpoints
- `agriflow.api.v1.geography.get_states`
- `agriflow.api.v1.geography.get_districts?state=Tamil+Nadu`
- `agriflow.api.v1.geography.get_blocks?district=<district_code>`
- `agriflow.api.v1.geography.get_villages?block=<block_code>&search=<text>`
- `agriflow.api.v1.geography.get_clusters` (optional)
- `agriflow.api.v1.geography.get_officers` (optional)
- `agriflow.api.v1.farmer.create` (mobile save)
- All tested via bench console with Administrator ✅

## Phase 5: Mobile UI
- **File:** `mobile/agriflow_mobile/lib/features/farmer/presentation/farmer_create_screen.dart`
- **Route:** `/farmers/new` (FAB on farmer list)
- **Cascading dropdowns:** State → District → Block
- **Village:** `Autocomplete` search (min 2 chars)
- **Cluster, Officer:** Optional with grey helper text
- **Tamil labels:** ✅ via `app_ta.arb`
- **Analyze:** `flutter analyze lib/features/farmer` — clean (no errors)

## Sample User Journey (Working)
1. Open Farmers tab → tap **+** FAB
2. State defaults to **Tamil Nadu**
3. District dropdown loads **38** LGD districts (+ legacy TVM in DB)
4. Select **Tiruvannamalai (572)** → Block dropdown loads sub-districts for that district
5. Select block **Polur (5983)** → Village field becomes autocomplete
6. Type **Ala** → shows **Alagapuram**
7. Select village; skip Cluster and Officer
8. Enter name + 10-digit mobile → **Save** → Farmer created via `farmer.create` ✅

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| LGD portal not scripted | Used GitHub mirror + `prepare_tn_csv.py` |
| `blocks.csv` duplicate column headers | Sub-district parser for block names |
| Village CSV uses district code not state code | Filter by TN district codes + state column |
| Frappe core `State` name collision | Renamed DocType to **`Geo State`** |
| Bench app not symlinked to repo | `rsync` to `/home/muruga/workspace/frappe-bench/apps/agriflow` before migrate/import |

## Next Step
- Connect Windows Flutter app to WSL backend: `flutter run -d windows --dart-define=API_BASE_URL=http://<WSL_IP>:8000`
- Assign clusters/officers in Desk when admin ready
- Consider retiring legacy TVM/BLK01–12 demo geography fixtures after pilot cutover
