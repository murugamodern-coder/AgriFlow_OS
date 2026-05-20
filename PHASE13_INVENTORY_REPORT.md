# Phase 13 — Inventory & Material Logistics Verification Report

**Site:** `dev.agriflow.local` · **Bench:** `~/workspace/frappe-bench`  
**Verified:** 2026-05-20 · **Script:** `agriflow.project_lifecycle.install.phase13_verify_inventory.execute`  
**Result:** `ok: true`, `errors: []`

---

## 1. Inventory verification report

| Check | Result |
|-------|--------|
| DocTypes: Inventory Item, Warehouse, Stock Ledger Entry, Project Material Allocation | Pass |
| No mutable Stock Entry header | Pass (not implemented) |
| Warehouses `WH-CENTRAL-01`, `WH-CENTRAL-02` seeded | Pass |
| `inward` → derived on-hand | Pass |
| `reserve` → available ↓, reserved ↑ | Pass |
| `consume` (partial) → on-hand ↓, reserved ↓ | Pass |
| Negative stock blocked (`outward` when insufficient) | Pass |
| Transfer = outward + inward (savepoint atomic) | Pass |
| Ledger idempotent `client_id` replay | Pass |
| Ledger immutability (save blocked) | Pass |
| Timeline `material_*` emit | Off (`EMIT_TIMELINE_MATERIAL = False`) |
| Stage gate (sequence ≥ 9) | Pass (verify bumps dev project when needed) |

**Commands**

```bash
cd ~/workspace/frappe-bench
bench --site dev.agriflow.local migrate
bench --site dev.agriflow.local clear-cache
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase13_seed_inventory.execute
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase13_verify_inventory.execute
```

**Sample verify output**

```json
{
  "on_hand_after_inward": 295.0,
  "ledger_replay_count": 1,
  "allocation": "PMA-2026-00054",
  "available_after_reserve": 235.0,
  "reserved_after_reserve": 60.0,
  "consume_status": "partially_consumed",
  "on_hand_after_consume": 285.0,
  "reserved_after_consume": 50.0,
  "negative_stock_blocked": true,
  "transfer_ledgers": ["jhhpp4ubhv", "jhhv6ruip4"],
  "wh2_on_hand_delta": 5.0,
  "ledger_immutable": true,
  "ok": true
}
```

---

## 2. Sample ledger flows

### A. Receipt (inward)

```json
{
  "movement_type": "inward",
  "warehouse": "WH-CENTRAL-01",
  "inventory_item": "ITEM-DRIP-001",
  "qty": 100,
  "batch_no": "BATCH-001",
  "client_id": "uuid-inward-001"
}
```

→ `Stock Ledger Entry` `movement_type=inward`, `qty=100`.

### B. Reserve for project

```json
{
  "farmer_project": "FP-2026-00007",
  "warehouse": "WH-CENTRAL-01",
  "inventory_item": "ITEM-DRIP-001",
  "qty": 30,
  "batch_no": "BATCH-001",
  "client_id": "uuid-reserve-001"
}
```

→ `Project Material Allocation` + ledger `reserve`.

### C. Consume (installation)

```json
{
  "allocation": "PMA-2026-00054",
  "qty": 10,
  "doc_version": 1,
  "batch_no": "BATCH-001",
  "client_id": "uuid-consume-001"
}
```

→ ledger `consume`; allocation `partially_consumed`.

### D. Transfer (atomic)

```json
{
  "from_warehouse": "WH-CENTRAL-01",
  "to_warehouse": "WH-CENTRAL-02",
  "inventory_item": "ITEM-DRIP-001",
  "qty": 5,
  "client_id": "uuid-transfer-001"
}
```

→ ledgers `outward` (WH1) + `inward` (WH2) in one savepoint.

### E. Adjust

```json
{
  "movement_type": "adjust",
  "adjustment_sign": "+",
  "warehouse": "WH-CENTRAL-01",
  "inventory_item": "ITEM-DRIP-001",
  "qty": 2,
  "client_id": "uuid-adjust-001"
}
```

---

## 3. Reservation proof

- `allocation_reserve` creates **PMA** + ledger `reserve`.
- **Available** = on_hand − reserved (e.g. after +100 inward and reserve 30: available 70 on clean ledger).
- Verify run: `reserved_after_reserve: 60` (cumulative test data), `available_after_reserve: 235` consistent with `on_hand − reserved`.

---

## 4. Consumption proof

- `allocation_consume` requires matching `doc_version`.
- Posts ledger `consume` (reduces on-hand and reserved pool).
- Verify: `consume_status: partially_consumed`, `on_hand_after_consume` reduced by 10, `reserved_after_consume` reduced by 10.

---

## 5. Derived-stock proof

`StockProjectionService` (SQL only — no qty on masters):

| Helper | Formula |
|--------|---------|
| `get_on_hand` | inward − outward − consume ± adjust |
| `get_reserved` | reserve − release − consume |
| `get_available` | on_hand − reserved |

`inventory.stock_on_hand` API returns all three for mobile.

---

## 6. Mobile integration notes

| Topic | Guidance |
|-------|----------|
| Masters | `inventory.items`, `inventory.warehouses` → Hive (server-wins) |
| Stock check | `inventory.stock_on_hand` before reserve/issue |
| Movements | `inventory.movement_post` (inward/outward/adjust) |
| Project material | `allocation.reserve` / `consume` / `release` |
| Transfer | `inventory.transfer_post` |
| Sync | `client_id` + `client_mutation_id` on writes; **no** `sync.pull` inventory entity yet |
| Stage UX | Block reserve/consume until project stage ≥ 9 |
| Serial items | One `serial_no` per ledger row, `qty=1` |
| Batch items | `batch_no` required when `has_batch_no` |

**Legacy alias:** `inventory.stock_entry.create` → `movement_post`.

---

## 7. Scalability notes

| Area | Approach |
|------|----------|
| Truth | Append-only `Stock Ledger Entry` |
| Indexes | `(warehouse, inventory_item, posting_datetime)`, `client_id`, allocation link |
| Projection | Aggregating SQL; optional snapshot table later |
| Transfer | MariaDB savepoint — both legs or neither |
| Scope | Block on ledger + User Permission |
| Low stock | `list_low_stock()` foundation + reorder_level on item |

---

## 8. Transfer atomicity proof

- `transfer()` wraps outward + inward in `frappe.db.savepoint(...)`.
- On failure, `rollback(save_point=...)` — no orphan inward without outward.
- Verify: `transfer_ledgers` has two names; `wh2_on_hand_delta: 5`.

---

## 9. Ledger immutability proof

- Controller rejects update/delete on `Stock Ledger Entry`.
- Verify: `doc.save()` after mutating `qty` → exception; `ledger_immutable: true`.
- Corrections: new row with `compensates_ledger` (foundation field).

---

## 10. Replay / idempotency proof

- `client_id` on each ledger post; `find_ledger_by_client_id` returns existing name.
- Verify: second post with same inward `client_id` → `ledger_replay_count: 1`.
- PMA reserve: `client_id` on allocation prevents duplicate PMA.

---

## Implementation map

```
apps/agriflow/agriflow/
  inventory/
    doctype/{inventory_item,warehouse,stock_ledger_entry,project_material_allocation}/
    services/{validation,idempotency,projection,ledger,movement,reservation,consumption,timeline_hook}.py
    api/serializers.py
  api/v1/inventory.py
  project_lifecycle/install/phase13_{seed,verify}_inventory.py
fixtures/
  warehouse.json
  inventory_item.json
```

Windows mirrors: `AgriFlow_OS/scripts/phase13_*.py`

**APIs**

| Method | Purpose |
|--------|---------|
| `inventory.items` | Item master |
| `inventory.warehouses` | Warehouse list |
| `inventory.stock_on_hand` | Derived qty |
| `inventory.ledger_list` | Read-only history |
| `inventory.movement_post` | inward / outward / adjust |
| `inventory.transfer_post` | Atomic transfer |
| `inventory.allocation.reserve` | Reservation |
| `inventory.allocation.consume` | Consumption |
| `inventory.allocation.release` | Release |
| `inventory.allocation.list` | By project |
| `inventory.stock_entry_create` | Legacy alias |

---

## Out of scope (confirmed)

- Procurement / accounting GL  
- ERPNext Stock module  
- Auto-reorder AI  
- `sync.pull` inventory entity  
