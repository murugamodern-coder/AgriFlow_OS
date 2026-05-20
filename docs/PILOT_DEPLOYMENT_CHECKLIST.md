# Pilot deployment checklist (Phase 17)

Use this checklist before each controlled pilot block deployment.

## Environment

- [ ] Staging site URL and TLS certificate valid
- [ ] `agriflow_auth_mode=jwt` and `agriflow_jwt_secret` set on site
- [ ] Redis available for refresh rotation (production/staging)
- [ ] Demo/pilot users created with correct block scope
- [ ] Phase 17 DocTypes installed (`phase17_install.execute`)
- [ ] `phase17_verify_pilot.execute` returns `ok: true`

## Mobile build

- [ ] `APP_VERSION` / `API_BASE_URL` dart-defines set for release APK
- [ ] `DEV_AUTH_STUB` disabled in release
- [ ] Unique `DEVICE_ID` per pilot handset (or auto UUID)
- [ ] Officers completed in-app onboarding once

## Operational monitoring

- [ ] Pilot dashboard reachable: `/pilot_dashboard` (System Manager)
- [ ] `pilot_ops.dashboard` reviewed daily during pilot week
- [ ] Inventory reconcile (`inventory_health`) — zero mismatches target
- [ ] Sync failure rate under agreed threshold (see PHASE17 report)

## Field validation scenarios

- [ ] Weak / intermittent network (2G/3G toggle)
- [ ] Long offline period (4+ hours) then sync
- [ ] Repeated task retries / replay
- [ ] Inventory shortage consume attempt
- [ ] Two officers, same block, concurrent sync
- [ ] Device restart with pending queue
- [ ] Stale app version flagged in `app_versions` matrix
- [ ] App upgrade with queued mutations (upgrade after offline work)

## Sign-off

| Role | Name | Date |
|------|------|------|
| Field lead | | |
| Tech lead | | |
| Ops / admin | | |
