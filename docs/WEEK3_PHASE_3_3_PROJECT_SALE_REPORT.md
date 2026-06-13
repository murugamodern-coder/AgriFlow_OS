# Week 3 Phase 3.3 — Project Sale Flow Report

**Date:** 2026-06-12  
**Branch:** `stabilization-v1`  
**Status:** 🟢 COMPLETE (mobile); 🟡 PARTIAL (live backend verify — bench not running at audit time)

---

## Phase Results

| Phase | Status | Notes |
|-------|--------|-------|
| 1 Backend verify + project advance | 🟡 | `ping` returned HTTP 000 (bench not listening). Endpoint code confirmed in `billing.py`. User must run `bench start` + advance FP-2026-00007 to **Quotation Generated** before E2E. |
| 2 Repository extended | ✅ | `createProjectInvoice`, `getProjectDetails` via `ApiConfig.methodUrl` |
| 3 Domain models | ✅ | `ProjectSaleQuote` with 80/20 auto-split |
| 4 Provider | ✅ | `projectSaleCartProvider`, `projectDetailsProvider` |
| 5 Screen UI | ✅ | Search + cart + subsidy split + confirm sheet |
| 6 Navigation + Timeline button | ✅ | Route + `TimelineProjectSaleButton` on quotation stage |

---

## Files Created

| File | Purpose |
|------|---------|
| `lib/features/billing/domain/models/project_sale_models.dart` | `ProjectSaleQuote` model |
| `lib/features/billing/presentation/providers/project_sale_providers.dart` | Cart + project details providers |
| `lib/features/billing/presentation/screens/project_sale_screen.dart` | Full Project Sale UI |
| `lib/features/project_lifecycle/presentation/widgets/timeline_project_sale_button.dart` | Timeline CTA when stage = Quotation Generated |

## Files Modified

| File | Change |
|------|--------|
| `lib/features/billing/data/billing_repository.dart` | `createProjectInvoice`, `getProjectDetails` |
| `lib/features/billing/domain/models/billing_models.dart` | `InvoiceResult.fromProjectJson` (+ subsidy fields) |
| `lib/app/router/routes.dart` | `AppRoutes.projectSale(name)` |
| `lib/app/router/app_router.dart` | `/billing/project-sale/:projectName` route |
| `lib/features/project_lifecycle/presentation/project_timeline_screen.dart` | Timeline project sale button |
| `lib/l10n/app_en.arb` | 14 new billing strings |
| `lib/l10n/app_ta.arb` | Tamil equivalents |
| `lib/l10n/app_localizations*.dart` | Regenerated via `flutter gen-l10n` |

---

## Tamil ARB Strings Added

| Key | English | Tamil |
|-----|---------|-------|
| `projectSale` | Project Sale | திட்ட விற்பனை |
| `generateInvoice` | Generate invoice | பில் உருவாக்கு |
| `generateProjectInvoice` | Generate project invoice | திட்ட பில் உருவாக்கு |
| `govtSubsidy` | Govt subsidy (80%) | அரசு மானியம் (80%) |
| `farmerPortion` | Farmer portion (20%) | விவசாயி பங்கு (20%) |
| `subsidySplit` | Subsidy split | மானிய பிரிவு |
| `confirmGenerate` | Confirm & generate | உறுதிப்படுத்தி உருவாக்கு |

---

## flutter analyze

```
flutter analyze lib/features/billing lib/features/project_lifecycle/... lib/app/router/
→ No issues found!
```

---

## User E2E Test Flow

1. Start bench: `cd ~/workspace/frappe-bench && ./env/bin/bench start`
2. Advance test project (if needed):
   ```bash
   ./env/bin/bench --site dev.agriflow.local execute frappe.db.set_value \
     --kwargs '{"doctype":"Farmer Project","name":"FP-2026-00007","fieldname":"workflow_state","value":"Quotation Generated"}'
   ```
3. Run mobile:
   ```powershell
   cd mobile\agriflow_mobile
   flutter run -d windows --dart-define=API_BASE_URL=http://127.0.0.1:8000
   ```
4. Login → open FP-2026-00007 timeline → **Generate project invoice**
5. Add Drip Pipe × 10 + Dripper × 100 → total ₹8,900
6. Subsidy auto: ₹7,120 | Farmer: ₹1,780
7. Confirm & generate → success dialog with SI name
8. Verify backend:
   ```bash
   curl -s -H 'Host: dev.agriflow.local' \
     'http://127.0.0.1:8000/api/method/agriflow.api.v1.billing.list_recent_invoices?sale_mode=Project+Sale'
   ```

**Expected test invoice (from Phase 3.1 pattern):** subsidy ₹6,000 + farmer ₹2,500 on seeded quotation items — adjust cart to match your catalog rates.

---

## Design Decisions

- **No relative URLs:** All billing calls use `_config.methodUrl(...)` (Phase 3.2 pattern).
- **Project details:** Fetched via `agriflow.api.v1.project.timeline` (not guest `frappe.client.get`).
- **Subsidy split:** Auto 80/20 on cart change; editable in confirm sheet with validation.
- **Timeline gate:** Button visible when `currentState == 'Quotation Generated'` OR `currentStage == 'quotation_generated'`.
- **Cash & Carry unchanged:** Separate cart provider; no regression to POS flow.

---

## Next Phase Preview (3.4)

Thermal printer integration + PDF receipt share for both Cash & Carry and Project Sale success dialogs.
