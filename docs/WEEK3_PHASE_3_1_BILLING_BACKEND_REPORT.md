# Week 3 Phase 3.1 — Billing Backend Foundation Report

## Status: 🟢 COMPLETE

## Phase Results
| Phase | Action | Status |
|-------|--------|--------|
| 1 | Audit existing setup | ✅ 0 invoices pre-ERPNext; 18 Items, 4 SIs post-setup |
| 2 | Custom Fields on Sales Invoice | ✅ 10 fields added |
| 3 | Billing API endpoints | ✅ 5 methods |
| 4 | Sample item catalog | ✅ 18 items seeded |
| 5 | API tests | ✅ All 4 flows tested |

## Phase 1 Audit (Before)
- **Sales Invoice / Customer / Item:** Not present — ERPNext was not installed on bench (Frappe + Agriflow only).
- **Agriflow billing doctypes:** `inventory_item`, `customer_onboarding` (custom inventory, not ERPNext billing).
- **ERPNext:** Installed during this phase (`version-15`) as required dependency for standard Sales Invoice.

## Phase 1 Audit (After)
| DocType | Count |
|---------|-------|
| Sales Invoice | 4 |
| Customer | 2 |
| Item | 18 |

## Custom Fields Added
1. agriflow_sale_mode (Cash & Carry / Project Sale / Service Invoice)
2. agriflow_farmer_project (Link)
3. agriflow_farmer (Link, fetched)
4. agriflow_walkin_customer_name (Data)
5. agriflow_walkin_mobile (Data)
6. agriflow_subsidy_amount (Currency)
7. agriflow_farmer_portion (Currency)
8. agriflow_payment_mode_extra (Select)
9. agriflow_whatsapp_status (Select, read-only)
10. agriflow_created_via (Select, read-only)

## API Endpoints Created
- `create_cash_carry_invoice` (POST)
- `create_project_invoice` (POST)
- `list_recent_invoices` (GET)
- `get_item_search` (GET)
- `get_or_create_walkin_customer` (utility)

## Test Results
- Cash & Carry invoice: Created `ACC-SINV-2026-00003`, total ₹1900 ✅
- Item search "Drip": 4 matching items ✅
- Project invoice for FP-2026-00007: subsidy ₹6000 + farmer ₹2500 ✅
- Recent invoices list: returns latest invoices ✅

## Sample Item Catalog
- 18 items across categories: drip, sprinkler, pipes, fittings, motor, filters, parts, fertilizer
- Price range: ₹4 (drippers) to ₹12,500 (open well motor)

## Bench Setup (One-time)
ERPNext + company bootstrap required on `dev.agriflow.local`:
1. `bench get-app erpnext --branch version-15`
2. Add `erpnext` to `sites/apps.txt`
3. `bench --site dev.agriflow.local install-app erpnext`
4. `bench --site dev.agriflow.local execute agriflow.install.bootstrap_billing_setup.run`
5. `bench --site dev.agriflow.local execute agriflow.scripts.seed_billing_items.run`

## Files Changed
- New: `backend/agriflow/agriflow/api/v1/billing.py`
- New: `backend/agriflow/agriflow/scripts/seed_billing_items.py`
- New: `backend/agriflow/agriflow/fixtures/custom_field.json`
- New: `backend/agriflow/agriflow/install/audit_billing_setup.py`
- New: `backend/agriflow/agriflow/install/bootstrap_billing_setup.py`
- New: `backend/agriflow/agriflow/install/test_billing_api.py`
- Modified: `backend/agriflow/agriflow/hooks.py` (`required_apps`, fixtures, commands)

## Next Phase Preview (3.2)
Mobile POS screen:
- Item scan/search
- Add to cart
- Live total
- Customer mobile entry
- Save + print
