# Geography Cleanup — Phase 1 Diagnosis

**Site:** `dev.agriflow.local`  
**Date:** 2026-06-06  
**Mode:** Read-only (no DB changes)

## Executive Summary

| Finding | Detail |
|---------|--------|
| **Duplicate districts** | **1 pair only** — `593` (LGD) vs `TVM` (legacy demo) |
| **Total districts** | 39 (38 LGD + 1 legacy) |
| **Root cause** | LGD import keyed by `district_code` (593); demo used `TVM` — no merge on import |
| **Business data at risk** | 2 farmers, 1 village, 1 cluster, 12 legacy blocks — all on `TVM` |
| **LGD Tiruvannamalai (593)** | **Fully populated** — 12 blocks, 1,125 villages (not empty) |

> **Correction vs initial report:** LGD district `593` already has blocks and villages. The duplicate appears in mobile/API because **both `593` and `TVM` show as “Tiruvannamalai”** (different casing).

---

## Global Counts (Before Cleanup)

| Entity | Count |
|--------|------:|
| Districts | 39 |
| Blocks | 325 |
| Villages | 18,483 |
| Farmers (active) | 2 |
| Geo States | 1 |

**Expected after cleanup:** 38 districts · 313 blocks · ~18,483 villages (unchanged village count; 12 orphan demo blocks removed)

---

## All Districts Snapshot

Only the Tiruvannamalai row is duplicated; all other 37 LGD districts are unique.

| name | district_name | lgd_code | blocks | villages | farmers |
|------|---------------|----------|-------:|---------:|--------:|
| 593 | TIRUVANNAMALAI | 593 | 12 | 1,125 | 0 |
| **TVM** | **Tiruvannamalai** | *(empty)* | 12 | 1 | **2** |
| *(others)* | *(37 LGD districts)* | *(set)* | … | … | 0 |

**Case-insensitive duplicate names:** `['tiruvannamalai']`

---

## Tiruvannamalai Variants (Detail)

### LGD official — `593`
- **PK / name:** `593`
- **Display:** `TIRUVANNAMALAI`
- **lgd_code:** `593`
- **Blocks (12):** Arani, Chengam, Chetpet, Cheyyar, Jamunamarathoor, Kalasapakkam, Kilpennathur, **Polur (5724)**, THANDRAMPET, Tiruvannamalai, Vandavasi, Vembakkam
- **Villages:** 1,125 (LGD sub-district hierarchy)
- **Farmers:** 0

### Legacy demo — `TVM`
- **PK / name:** `TVM`
- **Display:** `Tiruvannamalai`
- **lgd_code:** *(none)*
- **Blocks (12):** `BLK01`–`BLK12` (generic names “Block 01” … “Block 12”; `BLK03` = Chetpet)
- **Villages:** 1 (`VLG01` — Sample Village 01)
- **Farmers:** 2 (`FR-00001` Ravi Kumar, `FR-00002` Lakshmi Devi)
- **Cluster:** `CLU01` on `BLK01`

---

## Legacy Demo Blocks (`district=TVM`)

| Block PK | block_name | villages | farmers | notes |
|----------|------------|----------|---------|-------|
| BLK01 | Block 01 | 1 | 2 | **Active demo data** |
| BLK02–BLK12 | Block 02–12 | 0 | 0 | Orphan placeholders |
| BLK03 | Chetpet | 0 | 0 | Name matches LGD `6617` Chetpet |

**Important:** Legacy blocks do **not** use LGD names (Polur, Arani, etc.). They use generic `BLK01` codes from fixtures — so name-based block merge is only reliable for **Chetpet** (`BLK03` → `6617`).

---

## LGD Polur Test

| Block PK | block_name | district | villages |
|----------|------------|----------|---------:|
| 5724 | Polur | 593 | 106 |

Legacy farmers are on `BLK01`, not `5724`. Cascading to Polur villages requires **re-pointing farmers** to LGD block `5724` (or another LGD block).

---

## Cross-References to Preserve

| DocType | Legacy refs | Action needed |
|---------|-------------|---------------|
| Farmer (2) | `district=TVM`, `block=BLK01`, `village=VLG01`, `cluster=CLU01` | Re-point to `593` / LGD block |
| Village (1) | `VLG01` on `BLK01` / `TVM` | Re-point to `593` + LGD block |
| Cluster (1) | `CLU01` on `BLK01` / `TVM` | Re-point to `593` + LGD block |
| Farmer Project (~2) | Likely same chain as farmers | Update district/block/village |
| Project Task | Check block scope | Update if references `BLK01` |

---

## Phase 2 — Recommended Strategy

### ✅ Strategy A: LGD-First (Recommended)

**Keep:** LGD district `593` and all LGD blocks/villages  
**Migrate:** All legacy refs from `TVM` / `BLKxx` → LGD keys  
**Delete:** Orphan `TVM` district + 12 legacy blocks after refs cleared  

#### Rationale
- Preserves LGD codes for all 38 districts (future-proof)
- Only one duplicate pair — no widespread collision
- Strategy B would break LGD PK scheme (`610`, `593`, …) for no gain

#### Proposed migration steps (Phase 3)

1. **Set LGD target:** `lgd_tvm = "593"`, default demo block **`5724` (Polur)** for `BLK01` farmers
2. **Farmers:** `district: TVM → 593`, `block: BLK01 → 5724` (keep `VLG01` or attach to first Polur LGD village — prefer keep demo village on Polur block)
3. **Village `VLG01`:** `district → 593`, `block → 5724`
4. **Cluster `CLU01`:** `district → 593`, `block → 5724`
5. **Farmer Project / Project Task:** update any `district=TVM` or `block=BLK*` fields
6. **Delete legacy blocks** `BLK01`–`BLK12` (after zero refs)
7. **Delete district `TVM`** (after zero refs)
8. **Optional:** Set `593.district_name` display to title case for UX — *defer* (API can sort by name; mobile shows one entry)

#### Dry-run
Migration script will support `--dry-run` before live execute.

#### Expected after state

| Metric | Before | After (expected) |
|--------|-------:|-----------------:|
| Districts | 39 | 38 |
| Tiruvannamalai variants | 2 | 1 (`593`) |
| Blocks | 325 | 313 |
| Farmers on TVM | 2 | 0 |
| Farmers on 593 | 0 | 2 |

---

## Strategy B (Not Recommended)

Keep `TVM` naming, delete LGD `593`, re-key 1,125 villages — **high risk, large blast radius**. Rejected.

---

## Diagnostic Command

```bash
wsl -d Ubuntu -- bash -c "cd /home/muruga/workspace/frappe-bench && \
  ./env/bin/bench --site dev.agriflow.local execute agriflow.scripts.diagnose_geography.run_diagnosis"
```

Script: `backend/agriflow/agriflow/scripts/diagnose_geography.py`

---

## Approval Required

**Proceed with Strategy A (LGD-First, migrate legacy refs)?**  
Reply **`yes`** to run Phase 3 migration (`migrate_legacy_geography.py` with dry-run first), or **`no`** to adjust strategy.
