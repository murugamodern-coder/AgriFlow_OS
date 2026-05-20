# Deployment rollback checklist

## Backend

- [ ] Note current git commit / file copies on bench
- [ ] Restore previous `api/v1/push.py`, `api/v1/ops.py` from backup
- [ ] `bench --site <site> migrate` (if DocType rollback needed, restore DB backup)
- [ ] Lower `agriflow_min_app_version` if APK rollback issued
- [ ] Verify `bench --site <site> execute agriflow.project_lifecycle.install.phase18_verify_production.execute`

## Mobile

- [ ] Distribute previous APK URL via `agriflow_apk_url`
- [ ] Officers reinstall or sideload previous build
- [ ] Confirm queues drain on old version (SQLite compatible)

## Infrastructure

- [ ] Revert nginx config to previous upstream
- [ ] Restore TLS cert if domain change failed
- [ ] Redis: flush only if session corruption confirmed

## Data

- [ ] If corruption: `bench --site <site> restore <backup-path>`
- [ ] Document incident in Operational Incident

## Sign-off

| Role | Date |
|------|------|
| Ops lead | |
| Tech lead | |
