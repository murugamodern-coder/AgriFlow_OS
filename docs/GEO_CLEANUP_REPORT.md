# Geography Cleanup — Final Report

**Site:** `dev.agriflow.local`  
**Date:** 2026-06-07  
**Branch:** `stabilization-v1`  
**Strategy:** A (LGD-first) — merge TVM demo into LGD `593`, delete orphan demo blocks

---

## Executive Summary

Live migration **Phase 3c + 3d** completed in a single transaction:

- **195** field updates (farmers, projects, tasks, notifications, stock ledger, material allocations, timeline events, demo village/cluster)
- **13** deletes: legacy blocks `BLK01`, `BLK03`; orphan blocks `BLK02`, `BLK04`–`BLK12`; orphan district `TVM`
- **0** errors; all 10 orphan block deletions passed live safety checks (0 remaining references)

Geography is now **LGD-only** with no duplicate Tiruvannamalai district and no generic demo blocks.

---

## Final Clean Counts

| Metric | Target | Actual | Status |
|--------|-------:|-------:|--------|
| Districts | 38 | **38** | ✅ |
| Tiruvannamalai variants | 1 (LGD 593) | **1** (`593`) | ✅ |
| Blocks | 313 | **313** | ✅ |
| Villages | 18,483 | **18,483** | ✅ |
| Farmers (active) | 2 | **2** | ✅ |
| Orphan district TVM | deleted | **deleted** | ✅ |
| Orphan demo blocks BLK01–BLK12 | deleted | **12 deleted** | ✅ |

**Note on Tiruvannamalai village count:** District `593` shows **1,126** villages (1,125 LGD + demo `VLG01` reparented to Polur block `5724`). Polur block `5724` has **107** villages (106 LGD + `VLG01`).

---

## Migration Actions

### Phase 3c — Reference migration

| Action | Detail |
|--------|--------|
| District | `TVM` → `593` on all linked records |
| Block merge | `BLK01` (Block 01) → `5724` (Polur) |
| Block merge | `BLK03` (Chetpet) → `6617` (LGD Chetpet) |
| Demo village | `VLG01` reparented to district `593`, block `5724` (kept as demo village) |
| Demo cluster | `CLU01` reparented to district `593`, block `5724` |

### Phase 3d — Orphan block deletion

Each block verified for **0 references** in: Farmer, Farmer Project, Project Task, Notification, Stock Ledger Entry, Project Material Allocation, Timeline Event, Village, Cluster, Officer Assignment History.

| Block ID | Legacy name | Reason | Result |
|----------|-------------|--------|--------|
| BLK01 | Block 01 | Merged into Polur `5724` | Deleted |
| BLK02 | Block 02 | Generic placeholder, no LGD code | Deleted |
| BLK03 | Chetpet | Merged into LGD `6617` | Deleted |
| BLK04 | Block 04 | Generic placeholder, no LGD code | Deleted |
| BLK05 | Block 05 | Generic placeholder, no LGD code | Deleted |
| BLK06 | Block 06 | Generic placeholder, no LGD code | Deleted |
| BLK07 | Block 07 | Generic placeholder, no LGD code | Deleted |
| BLK08 | Block 08 | Generic placeholder, no LGD code | Deleted |
| BLK09 | Block 09 | Generic placeholder, no LGD code | Deleted |
| BLK10 | Block 10 | Generic placeholder, no LGD code | Deleted |
| BLK11 | Block 11 | Generic placeholder, no LGD code | Deleted |
| BLK12 | Block 12 | Generic placeholder, no LGD code | Deleted |
| TVM | Tiruvannamalai | Orphan legacy district | Deleted |

---

## Farmers After Migration

| Farmer | District | Block | Village |
|--------|----------|-------|---------|
| FR-00001 | `593` (TIRUVANNAMALAI) | `5724` (Polur) | VLG01 |
| FR-00002 | `593` (TIRUVANNAMALAI) | `5724` (Polur) | VLG01 |

---

## Phase 4 — Re-diagnosis

Post-migration `diagnose_geography.run_diagnosis` confirms:

- **38** districts, **0** duplicate district names
- **Single** Tiruvannamalai: `593 | TIRUVANNAMALAI | lgd=593 | blocks=12 | villages=1126 | farmers=2`
- **0** legacy demo blocks under `TVM`
- **0** farmers on legacy `TVM`
- **0** cross-references to `TVM` / `BLK01`
- **313** blocks, **18,483** villages globally

LGD Tiruvannamalai blocks (12): Arani, Chengam, Chetpet, Cheyyar, Jamunamarathoor, Kalasapakkam, Kilpennathur, **Polur**, THANDRAMPET, Tiruvannamalai, Vandavasi, Vembakkam.

---

## Phase 5 — API Tests

Run via `bench execute agriflow.scripts.test_geography_api.run_api_tests` as Administrator.

| Test | Expected | Result |
|------|----------|--------|
| `get_districts` count | 38 | **38** ✅ |
| Single Tiruvannamalai | `name=593`, `district_name=TIRUVANNAMALAI` | **✅** |
| `get_blocks?district=593` | 12 LGD blocks incl. Polur, Chetpet | **12** ✅ |
| `get_villages?block=5724` | LGD Polur villages | **107 in DB**; API returns up to **100** per request (limit cap) ✅ |
| `get_villages?block=5724&search=Ven` | Matching villages | **2** (Palvathuvendran, Venmani) ✅ |

### `get_districts` — Tiruvannamalai entry (full API response excerpt)

```json
{
  "ok": true,
  "data": {
    "items": [
      { "name": "610", "district_name": "Ariyalur", "lgd_code": "610" },
      { "name": "730", "district_name": "CHENGALPATTU", "lgd_code": "730" },
      { "name": "568", "district_name": "CHENNAI", "lgd_code": "568" },
      { "name": "569", "district_name": "COIMBATORE", "lgd_code": "569" },
      { "name": "570", "district_name": "CUDDALORE", "lgd_code": "570" },
      { "name": "571", "district_name": "DHARMAPURI", "lgd_code": "571" },
      { "name": "572", "district_name": "DINDIGUL", "lgd_code": "572" },
      { "name": "573", "district_name": "ERODE", "lgd_code": "573" },
      { "name": "729", "district_name": "KALLAKURICHI", "lgd_code": "729" },
      { "name": "574", "district_name": "KANCHIPURAM", "lgd_code": "574" },
      { "name": "575", "district_name": "KANNIYAKUMARI", "lgd_code": "575" },
      { "name": "576", "district_name": "KARUR", "lgd_code": "576" },
      { "name": "577", "district_name": "KRISHNAGIRI", "lgd_code": "577" },
      { "name": "578", "district_name": "MADURAI", "lgd_code": "578" },
      { "name": "735", "district_name": "Mayiladuthurai", "lgd_code": "735" },
      { "name": "579", "district_name": "NAGAPATTINAM", "lgd_code": "579" },
      { "name": "580", "district_name": "NAMAKKAL", "lgd_code": "580" },
      { "name": "581", "district_name": "PERAMBALUR", "lgd_code": "581" },
      { "name": "582", "district_name": "PUDUKKOTTAI", "lgd_code": "582" },
      { "name": "583", "district_name": "RAMANATHAPURAM", "lgd_code": "583" },
      { "name": "731", "district_name": "Ranipet", "lgd_code": "731" },
      { "name": "584", "district_name": "SALEM", "lgd_code": "584" },
      { "name": "585", "district_name": "SIVAGANGA", "lgd_code": "585" },
      { "name": "733", "district_name": "TENKASI", "lgd_code": "733" },
      { "name": "586", "district_name": "THANJAVUR", "lgd_code": "586" },
      { "name": "587", "district_name": "THE NILGIRIS", "lgd_code": "587" },
      { "name": "588", "district_name": "THENI", "lgd_code": "588" },
      { "name": "589", "district_name": "THIRUVALLUR", "lgd_code": "589" },
      { "name": "590", "district_name": "THIRUVARUR", "lgd_code": "590" },
      { "name": "591", "district_name": "TIRUCHIRAPPALLI", "lgd_code": "591" },
      { "name": "592", "district_name": "TIRUNELVELI", "lgd_code": "592" },
      { "name": "732", "district_name": "Tirupathur", "lgd_code": "732" },
      { "name": "634", "district_name": "TIRUPPUR", "lgd_code": "634" },
      { "name": "593", "district_name": "TIRUVANNAMALAI", "lgd_code": "593" },
      { "name": "594", "district_name": "TUTICORIN", "lgd_code": "594" },
      { "name": "595", "district_name": "VELLORE", "lgd_code": "595" },
      { "name": "596", "district_name": "VILLUPURAM", "lgd_code": "596" },
      { "name": "597", "district_name": "VIRUDHUNAGAR", "lgd_code": "597" }
    ]
  },
  "error": null
}
```

### `get_blocks?district=593` — sample

Polur: `{ "name": "5724", "block_name": "Polur", "lgd_code": "5724" }`  
Chetpet: `{ "name": "6617", "block_name": "Chetpet", "lgd_code": "6617" }`  
Total items: **12**

### `get_villages?block=5724&search=Ven`

```json
{
  "ok": true,
  "data": {
    "items": [
      { "name": "631695", "village_name": "Palvathuvendran", "lgd_code": "631695", "pincode": "" },
      { "name": "631737", "village_name": "Venmani", "lgd_code": "631737", "pincode": "" }
    ]
  }
}
```

---

## Scripts Added

| Script | Purpose |
|--------|---------|
| `agriflow/scripts/migrate_legacy_geography.py` | Phase 3c/3d migration (dry-run + live) |
| `agriflow/scripts/diagnose_geography.py` | Read-only duplicate/legacy diagnostic |
| `agriflow/scripts/test_geography_api.py` | Post-cleanup API verification |

**Bench commands:**

```bash
# Dry-run
bench --site dev.agriflow.local execute agriflow.scripts.migrate_legacy_geography.run

# Live (already executed)
bench --site dev.agriflow.local execute agriflow.scripts.migrate_legacy_geography.run_live

# Re-diagnose
bench --site dev.agriflow.local execute agriflow.scripts.diagnose_geography.run_diagnosis

# API tests
bench --site dev.agriflow.local execute agriflow.scripts.test_geography_api.run_api_tests
```

> **Bench sync:** Copy repo scripts to bench before execute — app is not symlinked:
> `rsync -a .../backend/agriflow/agriflow/scripts/ ~/workspace/frappe-bench/apps/agriflow/agriflow/scripts/`

---

## Mobile Cascading Test

From Windows, point the Flutter app at the WSL bench API:

```powershell
cd C:\AgriFlow_OS\AgriFlow_Main\mobile\agriflow_mobile
flutter run -d windows --dart-define=API_BASE_URL=http://172.28.181.245:8000
```

**Verify in app:**

1. State → Tamil Nadu → District dropdown shows **one** Tiruvannamalai (not two).
2. Select Tiruvannamalai → Block list shows **Polur**, **Chetpet**, Arani, etc. (12 LGD blocks).
3. Select Polur → Village search returns real LGD villages (e.g. search “Ven”).
4. Existing farmers FR-00001 / FR-00002 show district **593**, block **Polur (5724)**.

---

## Related Docs

- Pre-cleanup diagnosis: [GEO_CLEANUP_DIAGNOSIS.md](./GEO_CLEANUP_DIAGNOSIS.md)
- Original LGD import report: [GEOGRAPHY_REAL_DATA_REPORT.md](./GEOGRAPHY_REAL_DATA_REPORT.md)
