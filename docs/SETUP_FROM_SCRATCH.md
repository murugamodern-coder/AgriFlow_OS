# AgriFlow OS — Setup from scratch (~30 min)

Walkthrough for a **new developer** with WSL2 (Ubuntu) + Windows Flutter SDK.

## Prerequisites

| Tool | Version |
|------|---------|
| WSL Ubuntu | 22.04+ |
| MariaDB + Redis | Via bench or Docker |
| Frappe bench | v15 with site `dev.agriflow.local` |
| Flutter | 3.24+ |
| Python | 3.10+ |

## 1. Clone repository

```bash
git clone <your-repo-url> AgriFlow_OS
cd AgriFlow_OS
```

## 2. Install backend on bench

```bash
# WSL
cd /mnt/c/.../AgriFlow_OS   # or clone inside ~/projects for faster I/O
sed -i 's/\r$//' scripts/install_backend_to_bench.sh
./scripts/install_backend_to_bench.sh

cd ~/workspace/frappe-bench
bench --site dev.agriflow.local migrate
bench --site dev.agriflow.local clear-cache
```

**First-time bench:** If `backend/agriflow` is empty, run phase scripts (6→16) per `IMPLEMENTATION_PLAN.md`, then `./scripts/copy_backend_to_repo.sh` to refresh the committed snapshot.

## 3. Seed demo data (optional)

```bash
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase15_seed_demo.execute
```

Demo login: `field.officer@agriflow.local` / `AgriFlow@2026` (see `docs/LOCAL_LIVE_DEMO.md`).

## 4. Start backend

```bash
cd ~/workspace/frappe-bench
bench start
# Verify: curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000
```

## 5. Mobile app

```powershell
cd mobile\agriflow_mobile
flutter pub get
flutter gen-l10n
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000 --dart-define=DEMO_MODE=true
```

For device/emulator pointing at WSL host, use your machine LAN IP or Cloudflare tunnel URL from `docs/LOCAL_LIVE_DEMO.md`.

## 6. Verify demo path

1. Login  
2. **Home** — role + project/task counts  
3. **Farmers** — list → tap farmer → **12-stage timeline**  
4. **Advance stage** (online) → **Tasks** tab → new tasks after sync  
5. **Notifications** — Tamil titles  
6. **Sync** — queue → sync now  

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `farmer.list` 404 | Run `demo_day1_api_extensions.py` + `bench clear-cache` |
| Empty farmers | Run seed + `sync now` on app |
| OneDrive rsync fails | Use `Copy-Item` from `\\wsl$\...` or clone repo outside OneDrive |
| CRLF on scripts | `sed -i 's/\r$//' scripts/*.sh` |

## What not to do

- Do not edit generated code only on bench without updating `backend/agriflow`.
- Do not commit `.env` files (see root `.gitignore`).
