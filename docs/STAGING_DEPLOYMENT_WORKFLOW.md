# Staging deployment workflow (updated — Production Deployment Setup)

> **Full guide:** [PRODUCTION_DEPLOYMENT_REPORT.md](../PRODUCTION_DEPLOYMENT_REPORT.md)

## Quick path (Ubuntu VPS)

```bash
# 1. VPS bootstrap
sudo bash infra/vps/setup_vps.sh

# 2. Clone repo, set domain
export STAGING_DOMAIN=staging.yourdomain.com
export AGRIFLOW_REPO=/opt/agriflow
cd $AGRIFLOW_REPO

# 3. Secrets + stack + backend
bash infra/scripts/generate_secrets.sh
bash infra/scripts/deploy_production_staging.sh

# 4. DNS → VPS, then TLS
bash infra/scripts/certbot_vps.sh

# 5. Run bench (use systemd in production)
cd ~/workspace/frappe-bench
bench start
bench schedule

# 6. Validate
bash infra/scripts/validate_staging_deployment.sh
```

## Local WSL (pre-VPS)

```bash
export AGRIFLOW_REPO=/mnt/c/Users/.../AgriFlow_OS
bash scripts/production_deploy_backend.sh   # FRAPPE_SITE=dev.agriflow.local
cd infra/docker && cp .env.staging.example .env.staging
# edit passwords, then:
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d
```

## Mobile staging APK

```bash
API_BASE_URL=https://staging.yourdomain.com bash mobile/scripts/build_staging_apk.sh
```

## Smoke verification

```bash
bench --site $FRAPPE_SITE execute agriflow.project_lifecycle.install.phase24_verify_perf.execute
```

## Rollback

See [ROLLBACK_CHECKLIST.md](./ROLLBACK_CHECKLIST.md) and GA rollback APIs.
