# Rollout governance (Phase 19)

## Waves

| Wave | Config | Audience | Gate |
|------|--------|----------|------|
| `pilot_a` | `agriflow_rollout_wave=pilot_a` | 5–10 devices, 1 block | `phase19_verify_rollout` ok |
| `pilot_b` | `pilot_b` | 30 officers | Zero critical incidents 7d |
| `production` | `production` | Block-by-block | Min version enforced |

```bash
bench --site <site> set-config agriflow_rollout_wave pilot_a
bench --site <site> set-config agriflow_min_app_version "0.19.0"
```

## Version governance

- Only **two** active APK versions in field at once.
- Raise `agriflow_min_app_version` only after 80% devices on previous target (check `app_versions` in live dashboard).

## Change control

1. Deploy backend → `phase19_deploy_rollout.sh`
2. Run verify + concurrent pilot scripts
3. Publish APK with new `APP_VERSION`
4. Monitor `/ops_live_dashboard` for 48h

## Rollback

See [ROLLBACK_CHECKLIST.md](./ROLLBACK_CHECKLIST.md).
