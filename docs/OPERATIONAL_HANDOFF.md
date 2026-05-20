# Operational Handoff Guide (Pilot → Production)

## Roles

| Role | Responsibility |
|------|----------------|
| AgriFlow ops | `/ga_ops_console`, escalations, releases |
| Customer admin | User provisioning, block scope |
| Field lead | Device health, officer feedback |

## Handoff steps

1. **Pilot exit review** — `pilot.pilot_status_dashboard` + `ga.pilot_conversion` metrics  
2. **Readiness gate** — `ga.customer_readiness(onboarding_id=…)` must show `go_live_ready: true`  
3. **Go-live checklist** — [CUSTOMER_GO_LIVE_CHECKLIST.md](./CUSTOMER_GO_LIVE_CHECKLIST.md)  
4. **Training** — Officers complete mobile onboarding screen; ops reviews sync SLA for 7 days  
5. **Support** — Assign default `assigned_to` for Support Tickets; document escalation path  

## Weekly ops rhythm

- Monday: Review customer health table in GA console  
- Daily: Run escalations (`ga.run_ga_escalations`) or scheduler  
- Friday: Export `ga.export_ga_operations_summary` for customer success review  

## APIs

- Dashboard: `agriflow.api.v1.ga.ga_operations_dashboard`  
- Escalations: `agriflow.api.v1.ga.run_ga_escalations`  
- Incidents: `agriflow.api.v1.ga.incident_review_export`  
