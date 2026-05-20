# Backup & Restore Guide (Staging / Production)

## What is backed up

| Layer | Method | Schedule |
|-------|--------|----------|
| MariaDB (Docker) | `backup_daily.sh` → gzip SQL | Daily 02:00 |
| Frappe site + files | `bench --site <site> backup --with-files` | Weekly (cron) |
| MinIO | Volume snapshot / `mc mirror` (ops) | Weekly recommended |

Backups default to `/var/backups/agriflow` with **14-day** retention.

## Daily DB backup

```bash
bash infra/scripts/backup_daily.sh
```

## Manual bench backup

```bash
cd ~/workspace/frappe-bench
bench --site staging.example.com backup --with-files
```

## Restore validation (staging)

```bash
VALIDATE_RESTORE=1 bash scripts/backup_restore_validate.sh
```

## Full restore drill

1. Stop traffic: `docker compose ... stop nginx` or maintenance page  
2. Restore MariaDB dump:
   ```bash
   gunzip -c /var/backups/agriflow/mariadb_YYYYMMDD.sql.gz | \
     docker compose -f infra/docker/docker-compose.staging.yml exec -T mariadb \
     mariadb -uagriflow -p$MARIADB_PASSWORD agriflow_staging
   ```
3. Or restore bench archive:
   ```bash
   bench --site staging.example.com restore /path/to/backup.tar
   ```
4. `bench migrate` · `bench clear-cache`  
5. Run `infra/scripts/validate_staging_deployment.sh`  
6. Mobile smoke: login → sync → offline replay  

## Recovery drill automation

```bash
bench --site <site> execute agriflow.api.v1.observability.recovery_drill_automation
```
