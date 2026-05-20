# Phase 21 — Real Pilot Operations & Product Refinement

**Site:** `dev.agriflow.local` · **Mobile:** `agriflow_mobile` v0.21.0+1  
**Date:** 2026-05-20

---

## Pre-implementation

### 1. Operational pain points (audit)

| Pain point | Phase 21 response |
|------------|-------------------|
| No multi-customer onboarding view | `pilot.list_pilot_customers` + dashboard table |
| Readiness not scored for go-live | `deployment_readiness_score` (0–100) |
| Stale devices without workflow | `stale_device_followups` + `acknowledge_stale_followup` |
| Support SLA opaque | `support_response_metrics` |
| APK rollout visibility weak | `rollout_cadence_summary` |
| Admin console lacks search/filter | `/pilot_ops_dashboard` search + status filter |
| Offline banner too generic | Contextual banner (pending count, last sync) |
| Sync retry invisible to officers | Phase progress (`repair` → `push` → `pull` …) |
| Queue failed rows retry forever | Cap at 5, then `QUEUE_MAX_RETRIES` |
| FCM queue worker no retry | `send_fcm_with_retry` in queue processor |

### 2. Expected UX bottlenecks

- Officers unsure when offline vs slow network → dual banner states
- Conflict resolution unclear → numbered steps in conflict sheet
- Sync “spinning” with no phase → `LinearProgressIndicator` + phase label
- Task complete requires detail screen → inbox already has list **Complete** (retained)
- Dashboard reloads sync summary every build → `FutureProvider` cache + invalidate after sync

### 3. Pilot-support workflow

```
Field issue / feedback
  → Support Ticket (officer or admin)
  → pilot.track_pilot_issue [PILOT] tag
  → pilot.escalate_pilot_issue (optional sla_breach)
  → Operational Incident linked
  → Stale device: ops acknowledges via acknowledge_stale_followup
```

### 4. Rollout cadence strategy

| Wave | Min version | Cadence |
|------|-------------|---------|
| pilot_a | 0.21.0 | Weekly APK to field officers; ops reviews `rollout_cadence_summary` |
| pilot_b | T+1 week | Block users below min via readiness API (Phase 18) |
| GA | 0.21.x stable | Bi-weekly; telemetry archive policy |

Config: `bench --site <site> set-config agriflow_min_app_version 0.21.0`

### 5. Refinement priorities

1. Pilot visibility (dashboard + readiness score)  
2. Support metrics + escalation  
3. Field sync UX (offline, phases, conflicts)  
4. Reliability (retry jitter, queue cap, FCM retry)  
5. Multi-customer simulation for provisioning QA  

### 6. Tasks delivered

**Backend:** `api/v1/pilot.py`, `phase21_analytics.py`, `phase21_simulation.py`, `phase21_verify_pilot_ops.py`, `/pilot_ops_dashboard`  
**Mobile:** v0.21.0 — offline banner, sync phases, conflict steps, retry jitter, queue cap  
**Deploy:** `scripts/phase21_deploy_pilot.sh`

---

## Post-implementation validation

```bash
export AGRIFLOW_REPO=/mnt/c/Users/murug/OneDrive/Desktop/DOCUMENT/Projects/AgriFlow_OS
bash $AGRIFLOW_REPO/scripts/phase21_deploy_pilot.sh
```

**Result (2026-05-20):** `phase21_verify_pilot_ops` → **`ok: true`** (install21, phase20 regression, pilot dashboard, rollout, export, simulation, stale ack)

**Simulations:** `phase21_simulation.execute` — multi-customer onboarding + pilot issue drill

---

## 1. Pilot operations report

AgriFlow supports **real pilot execution** with multi-customer tracking, readiness scoring, stale-device follow-ups, and an ops dashboard. Phase 20 commercial APIs remain; Phase 21 adds pilot-specific orchestration.

**URLs:**
- `/pilot_ops_dashboard` — primary pilot ops UI
- `/commercial_ops_console` — SLA/commercial (Phase 20)

---

## 2. UX refinement summary

| Area | Change |
|------|--------|
| Offline | Banner shows pending count + last sync time |
| Degraded network | Separate hint when online but backlog > 5 |
| Sync | Phase label + progress bar during sync |
| Conflicts | 3-step guidance (en/ta) |
| Queue repair | i18n snackbar with reset/dedup counts |
| Retry | Exponential backoff + jitter |

---

## 3. Operational tooling summary

| Tool | API |
|------|-----|
| Pilot dashboard | `pilot.pilot_status_dashboard` |
| Customer list/filter | `pilot.list_pilot_customers` |
| Customer report | `pilot.customer_level_report` |
| Pilot audit export | `pilot.export_pilot_audit` |
| Rollout cadence | `pilot.rollout_cadence_summary` |
| Stale ack | `pilot.acknowledge_stale_followup` |

---

## 4. Reliability tuning summary

- Sync `RetryPolicy`: jitter on backoff delays  
- Queue repair: max 5 auto-heals, then `QUEUE_MAX_RETRIES`  
- FCM queue processor: uses `send_fcm_with_retry`  
- Long offline: existing 72h watermark full-pull (unchanged)  
- Telemetry heartbeat: unchanged (best-effort)

---

## 5. Support metrics overview

| Metric | Meaning |
|--------|---------|
| `open_tickets` | Active pilot support load |
| `avg_open_age_hours` | Responsiveness |
| `escalated` | High-touch cases |
| `resolved_last_days` | Throughput |
| `critical_open` | high/critical priority open |

Targets: first response 4h, resolution 48h (documented in API payload).

---

## 6. Remaining rollout risks

| Risk | Mitigation |
|------|------------|
| Real-device observations not automated | Weekly field review + pilot feedback DocType |
| Multi-site provisioning manual | `phase21_simulation` + onboarding templates |
| Flutter tests not run in CI here | Local `flutter test` before APK |
| Version compare string sort | Normalize semver in Phase 22 if needed |

---

## 7. Recommended production scaling strategy

1. **Week 1–2** — Single block pilot; daily `/pilot_ops_dashboard` review  
2. **Week 3–4** — Second customer site clone; `list_pilot_customers` tracks both  
3. **Month 2** — Enforce min version 0.21.0; weekly rollout cadence meeting  
4. **Month 3** — Assign ops owner for support metrics; archive telemetry > 90d  
5. **GA prep** — Readiness score ≥ 80 for 7 consecutive days before new block  

---

## Deploy

```bash
bash scripts/phase21_deploy_pilot.sh
```

**Demo:** `field.officer@agriflow.local` / `AgriFlow@2026`
