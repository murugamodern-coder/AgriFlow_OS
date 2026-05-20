# Pilot support SOP (Phase 19)

## Daily cadence (ops lead)

| Time | Action |
|------|--------|
| 09:00 | Open `/ops_live_dashboard` — review queue, sync rate, incidents |
| 12:00 | Run `ops.run_alert_checks` if not on scheduler |
| 17:00 | Triage open **Operational Incident** rows |

## Officer escalation tiers

| Tier | Symptom | Response |
|------|---------|----------|
| L1 | Sync pending, offline banner | Officer: Sync tab → Repair queue → Wi‑Fi sync |
| L2 | Conflict on task | Refresh from server; re-apply change |
| L3 | Inventory mismatch alert | Store keeper + block lead; pause consume |
| L4 | App crash loop | Collect version + device_id; APK reinstall |

## Telemetry review

- **Queue backlog** &gt; 10 → L2 ops within 4h
- **Sync failure rate** &gt; 15% → engineering same day
- **Push failures** &gt; 3/day → check FCM key + token registry

## Incident logging

Automated via `phase19_ops_alerts.execute`. Manual incidents: create **Operational Incident** in desk.

## Communication

- Field lead WhatsApp group for L1–L2
- Engineering channel for L3–L4 with `request_id` / `correlation_id` from Sync Status screen
