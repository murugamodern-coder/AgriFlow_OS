# Production Operations Checklist (Staging → Production)

## Daily

- [ ] `/observability_console` — latency cards green (< 2s bundle)
- [ ] Error log count < 50 / 24h (`operational_self_check_api`)
- [ ] Support tickets reviewed (`/ga_ops_console`)

## Weekly

- [ ] `phase23_automation` / daily cron escalations reviewed
- [ ] Backup files present in `/var/backups/agriflow`
- [ ] `phase24_retention_batch` / weekly retention log
- [ ] APK version vs `agriflow_min_app_version`

## Per release

- [ ] `production_deploy_backend.sh` + `phase24_verify_perf` OK
- [ ] GA Release Signoff approved
- [ ] `certbot renew --dry-run`
- [ ] Mobile `build_staging_apk.sh` with correct `API_BASE_URL`
- [ ] Pilot users notified

## Consoles (Administrator)

| Console | Path |
|---------|------|
| Observability | `/observability_console` |
| Enterprise | `/enterprise_ops_console` |
| GA | `/ga_ops_console` |
| Pilot | `/pilot_ops_dashboard` |

## Processes

```bash
bench start          # web + socketio
bench schedule       # background jobs (must run in prod)
```

Prefer **systemd** units for `bench start` and `bench schedule` on VPS.
