# Connection Diagnosis

## Phase 1 Summary

The mobile app is failing sync because it has no reachable Frappe backend URL at runtime.

## Mobile API Configuration

- `API_BASE_URL` is read from Dart compile-time defines in `mobile/agriflow_mobile/lib/core/config/env.dart`.
- Default value is an empty string: `String.fromEnvironment('API_BASE_URL', defaultValue: '')`.
- `ApiConfig.fromEnv()` trims trailing slashes and stores the value as `ApiConfig.baseUrl`.
- `ApiConfig.methodUrl(methodPath)` builds Frappe method URLs as:

```text
{API_BASE_URL}/api/method/{methodPath}
```

- `bootstrap()` creates `ApiConfig.fromEnv()`, then passes it to `createDio(...)`, `ApiClient`, `SyncRemote`, auth, notifications, inventory, and pilot telemetry.

## Current API_BASE_URL Value

The last known successful Windows debug launch used only:

```bash
--dart-define=DEMO_MODE=false --dart-define=DEV_AUTH_STUB=true
```

No `API_BASE_URL` was supplied, so the effective `Env.apiBaseUrl` is empty.

In debug mode this does not crash when `DEV_AUTH_STUB=true`, but real sync/API calls cannot reach the backend because generated method URLs are not backed by a valid server base URL.

## Backend API Contract

The backend exposes Frappe whitelisted methods under:

```text
/api/method/agriflow.api.v1.{area}.{action}
```

Examples confirmed in code:

- `agriflow.api.v1.auth.login`
- `agriflow.api.v1.auth.refresh`
- `agriflow.api.v1.sync.pull`
- `agriflow.api.v1.sync.push`

The architecture contract also documents:

```text
https://{site}/api/method/agriflow.api.{version}.{area}.{action}
```

## Backend Reachability Tests

### Windows localhost

Command:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/method/ping
```

Result:

```text
Unable to connect to the remote server
```

Conclusion: Frappe is not reachable from Windows at `127.0.0.1:8000`.

### WSL state

Command:

```powershell
wsl -l -v
```

Result:

```text
docker-desktop    Stopped    2
Ubuntu            Stopped    2
```

Conclusion: the Ubuntu WSL environment expected to run Frappe bench is currently stopped, so bench is not running.

### WSL process check

Command:

```powershell
wsl sh -lc "ps aux | grep -E 'bench|frappe|gunicorn|redis|mariadb' | grep -v grep || true"
```

Result: no matching process output.

Conclusion: no visible bench/frappe process is running.

### WSL IP

Command:

```powershell
wsl hostname -i
```

Result:

```text
127.0.1.1
```

Conclusion: because Ubuntu is stopped/not initialized for bench networking, this did not provide a usable WSL2 LAN IP such as `172.x.x.x`.

### Cloudflare tunnel

Command:

```powershell
Resolve-DnsName filled-neutral-pentium-forty.trycloudflare.com
```

Result:

```text
DNS name does not exist
```

Conclusion: the provided Cloudflare tunnel hostname is no longer active/resolvable.

## Backend Actual URL

No active backend URL is currently available.

Expected local Frappe URL after starting bench:

```text
http://127.0.0.1:8000
```

Expected API ping endpoint:

```text
http://127.0.0.1:8000/api/method/ping
```

If WSL2 localhost forwarding does not work, use the active Ubuntu WSL IP after starting WSL/bench:

```bash
hostname -I
```

Then use:

```text
http://<WSL_IP>:8000
```

## Recommended Fix

Option C would be best for a live demo only if a fresh Cloudflare tunnel URL is running. The provided tunnel URL is currently dead, so it cannot be used as-is.

Recommended immediate path:

1. Start WSL Ubuntu.
2. Start Frappe bench in WSL:

```bash
cd ~/workspace/frappe-bench
bench start
```

3. Verify from WSL:

```bash
curl http://127.0.0.1:8000/api/method/ping
```

4. Verify from Windows:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/method/ping -UseBasicParsing
```

5. If Windows localhost works, run Flutter with:

```bash
flutter run -d windows --dart-define=API_BASE_URL=http://127.0.0.1:8000 --dart-define=DEMO_MODE=false --dart-define=DEV_AUTH_STUB=true
```

6. If Windows localhost does not work, get WSL IP:

```bash
hostname -I
```

Then run Flutter with:

```bash
flutter run -d windows --dart-define=API_BASE_URL=http://<WSL_IP>:8000 --dart-define=DEMO_MODE=false --dart-define=DEV_AUTH_STUB=true
```

For demo stability, after bench is confirmed working, create a fresh Cloudflare tunnel and use that URL as `API_BASE_URL`.

## Phase 1 Verdict

FAIL: Backend connection cannot be fixed yet because no backend is currently running/reachable and the provided Cloudflare tunnel DNS no longer exists.

Stop condition reached per task rules: Phase 2 should not proceed until bench is started or a new working Cloudflare tunnel URL is provided.
