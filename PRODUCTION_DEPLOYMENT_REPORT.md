# Production Deployment Setup — AgriFlow Staging

**Status:** Deployment artifacts ready (operator-run on Ubuntu VPS)  
**Stack:** Phase 24 backend · Mobile 0.24.0 · Docker MariaDB/Redis/MinIO · nginx TLS

---

## 1. Deployment topology

```
                    Internet
                        │
                        ▼
              ┌─────────────────┐
              │  nginx :443 TLS  │  Let's Encrypt
              │  (Docker)        │
              └────────┬────────┘
                       │ proxy
                       ▼
              ┌─────────────────┐
              │ Frappe bench     │  host process :8000
              │ (agriflow app)   │  bench schedule
              └────────┬────────┘
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   MariaDB:3307   Redis:6380    MinIO:9000
   (Docker vol)   (Docker vol)  (Docker vol)
   127.0.0.1 only — not public
```

- **Public:** HTTPS `staging.<your-domain>` (ports 80/443)  
- **Private:** DB/Redis/MinIO bound to `127.0.0.1` on the VPS  
- **Mobile:** `API_BASE_URL=https://staging.<your-domain>`

---

## 2. Infrastructure sizing (recommended)

| Profile | vCPU | RAM | Disk | Notes |
|---------|------|-----|------|-------|
| **Staging / pilot** | 2 | 4 GB | 40 GB SSD | ~15 users, demo load |
| **Production** | 4 | 8 GB | 80 GB SSD | 12 blocks, growth headroom |

OS: **Ubuntu 22.04 LTS**. Region: closest to Tamil Nadu users (e.g. Chennai/Mumbai).

---

## 3. Security setup

| Control | Implementation |
|---------|----------------|
| Firewall | `ufw` — SSH, 80, 443 only (`infra/vps/setup_vps.sh`) |
| SSH | Key-only login; fail2ban sshd jail |
| Secrets | `generate_secrets.sh` — JWT in `.jwt_secret` (600) |
| TLS | Let's Encrypt via `certbot_vps.sh` |
| DB exposure | MariaDB/Redis/MinIO on localhost ports only |
| Headers | HSTS, nosniff, frame-options in nginx |

---

## 4. Backup strategy

- **Daily:** Docker MariaDB mysqldump → `/var/backups/agriflow/*.sql.gz` (14d retention)  
- **Weekly:** `bench --site <site> backup --with-files`  
- **Quarterly:** Restore drill per [docs/BACKUP_RESTORE_GUIDE.md](./docs/BACKUP_RESTORE_GUIDE.md)

---

## 5. Rollout approach

1. Provision VPS → `setup_vps.sh`  
2. Clone repo → `generate_secrets.sh`  
3. DNS A record → VPS IP  
4. `deploy_production_staging.sh` (Docker + backend)  
5. `certbot_vps.sh` (HTTPS)  
6. `bench start` + `bench schedule` (systemd)  
7. `build_staging_apk.sh` → distribute to pilot officers  
8. `validate_staging_deployment.sh`

---

## 6. Deployment commands & files

| Step | Command / file |
|------|----------------|
| VPS bootstrap | `sudo bash infra/vps/setup_vps.sh` |
| Secrets | `STAGING_DOMAIN=staging.yourdomain.com bash infra/scripts/generate_secrets.sh` |
| Infra up | `cd infra/docker && docker compose -f docker-compose.staging.yml --env-file .env.staging up -d` |
| Full deploy | `bash infra/scripts/deploy_production_staging.sh` |
| TLS | `bash infra/scripts/certbot_vps.sh` |
| Backend only | `bash scripts/production_deploy_backend.sh` |
| Mobile APK | `API_BASE_URL=https://staging... bash mobile/scripts/build_staging_apk.sh` |
| Validate | `bash infra/scripts/validate_staging_deployment.sh` |

**Key files:**

- `infra/docker/docker-compose.staging.yml`  
- `infra/docker/nginx/agriflow-staging-vps.conf`  
- `infra/docker/.env.staging.example`  
- `infra/scripts/*` · `infra/vps/setup_vps.sh`  
- `infra/config/production_scheduler_hooks.snippet`  

---

## 7. Public URLs (replace domain)

| Service | URL |
|---------|-----|
| **Staging app** | `https://staging.<your-domain>` |
| Observability | `https://staging.<your-domain>/observability_console` |
| Enterprise ops | `https://staging.<your-domain>/enterprise_ops_console` |
| GA ops | `https://staging.<your-domain>/ga_ops_console` |
| Pilot ops | `https://staging.<your-domain>/pilot_ops_dashboard` |
| API (Frappe) | `https://staging.<your-domain>/api/method/...` |

Optional: `api.<your-domain>` CNAME → same VPS if you want a separate hostname (same nginx `server_name`).

---

## 8. Infrastructure summary

- Docker Compose stack: MariaDB 11, Redis 7, MinIO, nginx  
- Persistent volumes: `mariadb_staging`, `redis_staging`, `minio_staging`  
- Bench on host connects via `127.0.0.1:3307` / `:6380`  
- Min app version: **0.24.0** (adaptive sync, observability)

---

## 9. Security checklist

- [ ] `.env.staging` not in git  
- [ ] JWT secret ≥ 32 bytes hex  
- [ ] Redis `requirepass` set  
- [ ] MinIO root password rotated  
- [ ] UFW enabled  
- [ ] fail2ban active  
- [ ] TLS cert valid (A+ preferred on SSL Labs)  
- [ ] Administrator password rotated from default  
- [ ] `agriflow_fcm_server_key` set for real push (or `simulate` for pilot-only)

---

## 10. Backup / restore guide

See [docs/BACKUP_RESTORE_GUIDE.md](./docs/BACKUP_RESTORE_GUIDE.md).

---

## 11. Production operations checklist

See [docs/PRODUCTION_OPERATIONS_CHECKLIST.md](./docs/PRODUCTION_OPERATIONS_CHECKLIST.md).

---

## 12. Validation (operator-run on VPS)

After deploy:

```bash
export STAGING_URL=https://staging.yourdomain.com
bash infra/scripts/validate_staging_deployment.sh
```

Checks: HTTPS, ops consoles, `phase24_verify_perf`, backup script, self-check API.

**Local WSL (pre-VPS):** infra stack + bench on `dev.agriflow.local` remains valid; public staging requires VPS + DNS + certbot.

---

## 13. Recommended production rollout plan

| Phase | Action |
|-------|--------|
| **Week 0** | Staging VPS live; 2–3 pilot officers; daily observability review |
| **Week 1–2** | Real FCM; fix SLA breaches; backup restore drill on staging |
| **Week 3** | Second customer site clone (enterprise onboarding pack) |
| **Week 4+** | Production VPS separate compose file `.env.prod`; GA signoff per release |

---

## 14. Mobile configuration

```bash
API_BASE_URL=https://staging.yourdomain.com \
APP_VERSION=0.24.0 \
bash mobile/scripts/build_staging_apk.sh
```

Validate: login → full sync on Wi‑Fi → airplane mode → task view → sync again → push (if FCM configured).

---

*AgriFlow OS — production deployment package. Operator executes on real VPS; URLs use your registered domain.*
