# GA Production Rollout Checklist

Use before each production release wave.

## Pre-release

- [ ] `ga.run_backup_verification` passes on staging
- [ ] `phase22_verify_ga` → `ok: true` on staging site
- [ ] Staging smoke: login, sync, tasks, inventory queue
- [ ] `ga.request_upgrade_approval_api` created and approved
- [ ] Rollback checklist reviewed ([rollback section](#rollback))

## Release

- [ ] Deploy backend (`phase22_deploy_ga.sh`)
- [ ] `bench migrate` on production site
- [ ] Set `agriflow_min_app_version` to target (e.g. `0.22.0`)
- [ ] Distribute APK to field officers
- [ ] `ga.deploy_release_api` marks signoff as `released`

## Post-release (24h)

- [ ] Review `/ga_ops_console` — no queue/push anomalies
- [ ] `ga.run_ga_escalations` or scheduler
- [ ] Support workload within SLA targets
- [ ] Customer health scores ≥ 60 (amber) for all active customers

## Rollback

- [ ] Stop APK rollout
- [ ] `ga.rollback_release_api` with notes
- [ ] Restore backup if data corruption (`bench restore`)
- [ ] Revert `agriflow_min_app_version`
- [ ] Customer notification + incident postmortem
