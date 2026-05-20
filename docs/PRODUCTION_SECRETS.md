# Production secrets handling (Phase 18)

| Secret | Storage | Never |
|--------|---------|-------|
| `agriflow_jwt_secret` | `bench --site <site> set-config` | In git |
| MariaDB passwords | `.env.prod` on host only | In repo |
| Redis password | `.env.prod` | Committed |
| MinIO keys | `.env.prod` | Logs |
| FCM server key | Site config `agriflow_fcm_server_key` | Mobile APK |
| Sentry DSN | `--dart-define=SENTRY_DSN` at build | Hardcoded in source |

## Rotation

1. JWT: set new secret, force re-login (short access token limits blast radius).
2. DB: restore from backup to new credentials during maintenance window.
3. FCM: rotate in Firebase console, update site config.

## Staging vs production

- Separate `.env.staging` / `.env.prod` and Docker volume names.
- Separate bench sites: `staging.agriflow.local` vs production hostname.
- Separate `agriflow_jwt_secret` per site.
