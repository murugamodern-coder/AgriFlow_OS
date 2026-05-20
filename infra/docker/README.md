# AgriFlow Docker deployment

## Topology (Phase 16 foundation)

```
[Mobile] ──HTTPS──► [nginx] ──► [Frappe bench :8000 on host or container]
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
        MariaDB       Redis        MinIO
```

| Service | Role |
|---------|------|
| **MariaDB** | Frappe primary DB |
| **Redis** | Cache, sessions, job queue |
| **MinIO** | Attachments (S3 API) |
| **nginx** | TLS termination, reverse proxy to bench |

Frappe/bench is **not** containerized in this foundation — run `bench start` on the host (WSL) or add an erpnext image later.

## Public VPS staging (Production Deployment Setup)

1. `sudo bash infra/vps/setup_vps.sh`
2. `STAGING_DOMAIN=staging.yourdomain.com bash infra/scripts/generate_secrets.sh`
3. `bash infra/scripts/deploy_production_staging.sh`
4. DNS + `bash infra/scripts/certbot_vps.sh`
5. `bash infra/scripts/validate_staging_deployment.sh`

See [PRODUCTION_DEPLOYMENT_REPORT.md](../../PRODUCTION_DEPLOYMENT_REPORT.md).

## Dev vs prod vs staging (Phase 18)

| File | Use |
|------|-----|
| `docker-compose.dev.yml` | Local MariaDB/Redis/MinIO ports exposed |
| `docker-compose.staging.yml` | Staging volumes + HTTPS nginx (ports 8081/8443) |
| `docker-compose.prod.yml` | Restart policies, passwords required, nginx front door |
| `.env.dev.example` | Dev secrets template |
| `.env.staging.example` | Staging secrets template |
| `.env.prod.example` | Prod secrets template |
| `nginx/agriflow-staging.conf` | TLS + HSTS (place certs in `nginx/certs/`) |

## Site configuration (bench)

```bash
bench --site dev.agriflow.local set-config agriflow_auth_mode jwt
bench --site dev.agriflow.local set-config agriflow_jwt_secret "$(openssl rand -hex 32)"
```

## Phase 16 API tracing headers

| Header | Purpose |
|--------|---------|
| `X-Request-Id` | Per HTTP request (client or server generated) |
| `X-Sync-Correlation-Id` | Groups push/pull/notification refresh in one mobile sync |

Response envelope includes `request_id`; sync APIs add `sync_correlation_id`.
