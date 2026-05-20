# Local Live Demo (Cloudflare Tunnel / ngrok)

Expose **WSL bench** `http://127.0.0.1:8000` to the internet for customer demos — **no VPS**.

---

## Prerequisites

```bash
cd ~/workspace/frappe-bench
bench start          # keep this terminal open
# separate terminal:
bench schedule       # recommended for sync/jobs
```

Verify: `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000` → `200`

---

## 1. Cloudflare Tunnel (preferred)

```bash
export AGRIFLOW_REPO=/mnt/c/Users/.../AgriFlow_OS   # or your clone path
bash $AGRIFLOW_REPO/scripts/demo/start_cloudflare_tunnel.sh
bash $AGRIFLOW_REPO/scripts/demo/configure_demo_site.sh
bash $AGRIFLOW_REPO/scripts/demo/verify_local_demo.sh
```

Public URL is written to `/tmp/agriflow-tunnel/public_url.txt` and printed once (e.g. `https://xxxx.trycloudflare.com`).

**Note:** Quick tunnel URLs **change every run** and are not for production.

---

## 2. ngrok (fallback)

```bash
ngrok config add-authtoken <YOUR_TOKEN>   # one-time
bash scripts/demo/start_ngrok_tunnel.sh
bash scripts/demo/configure_demo_site.sh
```

Inspect: http://127.0.0.1:4040

---

## 3. Validation checklist

| Check | How |
|-------|-----|
| Local bench | http://127.0.0.1:8000 |
| Public HTTPS | URL from tunnel script |
| Login | Desktop browser → public URL |
| Ops consoles | `/observability_console`, `/pilot_ops_dashboard` |
| API | Mobile or `curl $URL/api/method/...` |
| Scheduler | `bench schedule` running |

```bash
bash scripts/demo/verify_local_demo.sh
```

---

## 4. Mobile testing

```bash
PUBLIC_URL=$(cat /tmp/agriflow-tunnel/public_url.txt)
cd mobile/agriflow_mobile
flutter build apk --debug \
  --dart-define=API_BASE_URL=$PUBLIC_URL \
  --dart-define=APP_VERSION=0.24.0 \
  --dart-define=PUSH_DEBUG_STUB=true
```

Or run on device via USB:

```bash
flutter run \
  --dart-define=API_BASE_URL=https://YOUR.trycloudflare.com \
  --dart-define=APP_VERSION=0.24.0
```

**Demo login:** `field.officer@agriflow.local` / `AgriFlow@2026` (if seeded)

Test: login → sync → airplane mode → open Tasks → sync again.

---

## 5. Security (demo-only)

| Risk | Mitigation |
|------|------------|
| Entire desk exposed | Tunnel only port **8000** — never expose MariaDB/Redis |
| Random public URL | Share only in demo; stop tunnel after |
| Dev data / weak passwords | Use demo site; rotate after |
| No SLA | Quick tunnels can drop; restart script |
| CSRF relaxed | `ignore_csrf` for demo — **revert after** |

**Do not expose:** Docker DB ports, Redis, bench file manager, or SSH via tunnel.

---

## 6. Shutdown

```bash
bash scripts/demo/stop_demo_tunnel.sh
```

Restore local-only config (optional):

```bash
cd ~/workspace/frappe-bench
bench --site dev.agriflow.local set-config host_name http://127.0.0.1:8000
bench --site dev.agriflow.local set-config ignore_csrf 0
```

---

## Current session example

If you started the tunnel in this session, your URL may be:

`https://filled-neutral-pentium-forty.trycloudflare.com`

(Re-run `start_cloudflare_tunnel.sh` for a new URL.)
