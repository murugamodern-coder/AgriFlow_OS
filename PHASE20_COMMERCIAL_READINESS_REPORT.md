# Phase 20 — Commercial Readiness & Operational Excellence

**Site:** `dev.agriflow.local` · **Mobile:** `agriflow_mobile` v0.20.0+1  
**Date:** 2026-05-20

---

## 1. Pre-implementation — commercial readiness gaps

| Gap (post Phase 19) | Phase 20 |
|---------------------|----------|
| No SLA/trend dashboards | `commercial.sla_dashboard` + analytics module |
| No customer onboarding record | **Customer Onboarding** wizard APIs |
| No support ticket linkage | **Support Ticket** + `create_support_ticket` / `escalate_incident` |
| Limited exports | `export_operational_summary` (JSON/CSV) |
| Conflict UX terse | i18n `conflictExplanation` |
| No device health score | `device_health_scores` + mobile Sync tab |
| Queue failed stuck | Queue repair resets `failed` → `pending` (≤5 retries) |
| FCM no retry | `send_fcm_with_retry` (Phase 20 patch) |

---

## 2. Onboarding workflow design

```
Admin starts onboarding (customer_name, role_template)
    → Customer Onboarding DocType (steps_json: `{"items": [step…]}`)
    → For each step: site_config, roles, demo_seed, verify, users, APK, training
    → status = ready → customer go-live
```

**Automation:** `phase20_demo_customer.execute` · `phase20_deploy_commercial.sh`  
**Checklist:** [docs/COMMERCIAL_ONBOARDING_CHECKLIST.md](./docs/COMMERCIAL_ONBOARDING_CHECKLIST.md)

---

## 3. SLA metric strategy

| Metric | Source | Target |
|--------|--------|--------|
| Push success rate | Push Delivery Log 7d | ≥ 95% |
| Avg device health | Telemetry scoring | ≥ 70 |
| Stale devices | No heartbeat 48h | 0 |
| Sync failure rate | Mutation log 7d | &lt; 10% days |
| Queue backlog | Telemetry 24h | pending ≤ 10 |

---

## 4. Support / escalation flow

```
Officer feedback / alert
    → Operational Incident (auto, Phase 19)
    → commercial.create_support_ticket (optional link)
    → escalate_incident → severity high + ticket
    → Resolved → ticket + incident closed
```

---

## 5. Reporting architecture

| Report | API |
|--------|-----|
| SLA dashboard | `commercial.sla_dashboard` |
| Ops console | `commercial.operations_console` |
| Pilot health | `commercial.pilot_health_report` |
| Sync SLA | `commercial.sync_sla_report` |
| Inventory movement | `commercial.inventory_movement_summary` |
| Export | `commercial.export_operational_summary` |

No OLAP — SQL aggregates + JSON export for customer ops reviews.

---

## 6. Tasks delivered

### Backend
- `api/v1/commercial.py`
- `phase20_analytics.py`
- `phase20_customer_onboarding.py`
- `phase20_demo_customer.py`
- DocTypes: Customer Onboarding, Support Ticket
- `/commercial_ops_console`

### Mobile v0.20.0
- Conflict explanation (i18n)
- Device health on Sync Status
- Queue auto-heal for failed rows

### Docs
- COMMERCIAL_ONBOARDING_CHECKLIST

---

## 7. Validation (bench)

```bash
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase20_verify_commercial.execute
```

**Result (2026-05-20):** `ok: true` — install20, phase19 regression, demo customer, onboarding wizard (3 steps), SLA dashboard, ops console, pilot report, support ticket, officer device health, operational export.

**Fixes applied during validation:**
- Onboarding `steps_json` wrapped as `{"items": [...]}` (Frappe JSON fields reject bare lists)
- `device_health_scores` SQL: qualified `t1.device_id` (ambiguous column)

---

## 8. Commercial readiness report

AgriFlow supports **commercial pilot onboarding** with admin console, SLA metrics, support tickets, exports, and improved field UX. Ready for first paying customer pilot with ops runbook.

---

## 9. SLA / reporting overview

- **Sync trends:** daily success/fail/skipped counts (14d)
- **Queue trends:** daily pending/conflict sums from telemetry
- **Push:** 7d success rate
- **Inventory:** utilization rate when allocations exist
- **Officers:** sync sessions + feedback counts

---

## 10. Customer onboarding flow

1. Sales/provisioning creates site + TLS  
2. `start_onboarding` → track steps in desk  
3. `phase20_demo_customer` for demo data  
4. Distribute APK 0.20.0  
5. Field training + `/commercial_ops_console` handoff  

---

## 11. Support tooling summary

- Support Ticket DocType
- Escalation API links incident → ticket
- Pilot feedback (Phase 17) retained
- Auto incidents (Phase 19) retained

---

## 12. Operational dashboard summary

**URL:** `/commercial_ops_console`  
**API:** `commercial.operations_console` = live dashboard + SLA block

KPI cards: push success, avg health, stale devices, open incidents, queue pending.

---

## 13. Reporting / export examples

```bash
# JSON export via API (Administrator session)
commercial.export_operational_summary?format=json

# Pilot health one-pager
commercial.pilot_health_report
```

CSV export sets `frappe.response` download filename `agriflow_ops_<site>.csv`.

---

## 14. Remaining scaling risks

| Risk | Mitigation |
|------|------------|
| Multi-tenant not native | One site per customer (Frappe pattern) |
| Analytics load on large telemetry | Archive telemetry &gt; 90d |
| Field Staff role on all sites | Role template in onboarding |
| Inventory utilization needs allocations | Graceful empty state |

---

## 15. Recommended rollout strategy

1. **Customer 1** — Full onboarding wizard + 2-week pilot with daily SLA review  
2. **Template** — Clone site config + demo seed scripts per region  
3. **Scale** — Dedicated ops analyst for `/commercial_ops_console`  
4. **Commercial GA** — Min version enforcement + support SOP SLA tiers  

---

## 16. Deploy

```bash
bash scripts/phase20_deploy_commercial.sh
```

**Console:** `https://<site>/commercial_ops_console`
