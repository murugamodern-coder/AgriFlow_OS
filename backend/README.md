# AgriFlow Frappe backend (committed app)

This directory is a **snapshot of the `agriflow` Frappe custom app** from the development bench.

## Layout

```
backend/agriflow/          ← Frappe app root (maps to `apps/agriflow` on bench)
  agriflow/                ← Python package
    api/v1/
    project_lifecycle/
    ...
  fixtures/
  hooks.py (via agriflow/hooks.py)
```

## Do not edit only on bench

1. Change code here (or in `scripts/` generators).
2. Sync to bench: `scripts/install_backend_to_bench.sh` (WSL).
3. Run `bench migrate` and `bench clear-cache`.

## Refresh snapshot from bench

```bash
# WSL — preferred when repo is on /mnt/c (OneDrive may block rsync)
./scripts/copy_backend_to_repo.sh
# Or Windows PowerShell:
# Copy-Item -Recurse \\wsl$\Ubuntu\home\muruga\workspace\frappe-bench\apps\agriflow backend\agriflow -Force
```

## Demo APIs (Day 1)

- `agriflow.api.v1.farmer.list` — read-only farmer list
- `agriflow.api.v1.project.transition` — stage advance (online; not via sync.push)

Applied by `scripts/demo_day1_api_extensions.py`.
