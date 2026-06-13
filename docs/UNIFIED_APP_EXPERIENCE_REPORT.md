# Unified App Experience Report

**Date:** 2026-06-12  
**Branch:** `stabilization-v1`  
**Status:** 🟢 COMPLETE

---

## Architecture Clarification

| Surface | Audience | Purpose |
|---------|----------|---------|
| **Frappe Desk** (`127.0.0.1:8000` in browser) | Developers / system admins only | DocType editing, bench config, ERPNext back-office |
| **Flutter Mobile App** (`agriflow_mobile`) | All end users (Owner, Office, Field, Installers, etc.) | Single product UI — login, dashboards, field workflows |
| **Frappe HTML ops consoles** (`/pilot_dashboard`, etc.) | Internal ops / pilot support | Not shown to customers in demo |

All surfaces share the **same Frappe site and database**. End users should only see the Flutter app.

---

## Phase 1 Audit Summary

### Feature folders (`lib/features/`)

| Feature | Role-aware UI before | Role checks |
|---------|---------------------|-------------|
| `auth/` | Login + permissions manifest | Roles stored at login, not used for routing |
| `dashboard/` | Generic welcome + 3 hardcoded role labels | Checked `'Owner'`, `'Office Manager'`, `'Field Staff'` — **wrong** vs backend names |
| `billing/` | None | Open to all logged-in users |
| `farmer/` | None | Block scope via sync projections |
| `project_lifecycle/` | Workflow `allowed_role` on server | Not used in dashboard |
| `tasks/` | None | Block-filtered via projections |
| `notifications/`, `sync/`, `pilot_ops/`, etc. | None | Same shell for all roles |

**Root UX bug:** Backend returns roles like `Agriflow Owner`, `Agriflow Field Staff` (from `frappe.get_roles()`), but the old dashboard checked short names (`Owner`, `Field Staff`). Every user saw the same generic layout.

**Role API:** No new backend endpoint required. Roles arrive in `agriflow.api.v1.auth.login` → `permissions.roles` and are cached in Hive with the session.

---

## Phase 2 — Role Detection

**File:** `lib/core/auth/user_role_provider.dart`

- `AgriflowRole` enum maps all 8 Agriflow roles + `unknown`
- Handles full backend names (`Agriflow Owner`) and legacy short aliases (`Field Staff`, dev stub)
- `UserSession.fromAuthSession()` derives from existing `AuthSession` / `PermissionManifest`
- `userSessionProvider` — sync `Provider` (no extra HTTP; uses login manifest)
- `primaryRole` priority: Owner → Office Manager → Field Staff → Installer Lead → Installer → Service Tech → Store Keeper → Office Staff

---

## Phase 3–5 — Role-Based Dashboards

**Router entry:** `/home` → `RoleBasedHome` (inside `DashboardShell` bottom nav)

| Role | Widget | Distinct UX |
|------|--------|-------------|
| Agriflow Owner | `OwnerDashboard` | 4 KPI cards, 6 quick actions, notifications link |
| Agriflow Office Manager | `OfficeManagerDashboard` | Approvals list, team notifications, POS + reports grid |
| Agriflow Office Staff | `OfficeStaffDashboard` | Data-entry buttons (new farmer, list, POS, sync) |
| Agriflow Field Staff | `FieldStaffDashboard` | Prominent open-task card, 4 large field buttons |
| Installer Lead / Installer | `InstallerDashboard` | Installation queue summary, tasks + projects; lead sees team notifications |
| Agriflow Service Technician | `ServiceTechDashboard` | Service visit card, tasks + sync |
| Agriflow Store Keeper | `StoreKeeperDashboard` | Inventory messaging, sync + POS |
| Unknown / unmapped | `GenericDashboard` | Legacy stats + farmers + sync |

Shared widgets: `lib/features/dashboard/presentation/widgets/dashboard_widgets.dart`  
Stats provider: `lib/features/dashboard/presentation/dashboard_stats.dart`

Responsive: KPI rows and action grids adapt to narrow Windows widths via `LayoutBuilder` / `MediaQuery`.

---

## Phase 6 — Router Update

**Modified:** `lib/app/router/app_router.dart`

```dart
// BEFORE
builder: (context, state) => const HomeDashboardScreen(),

// AFTER
builder: (context, state) => const RoleBasedHome(),
```

`home_dashboard_screen.dart` kept as typedef alias → `RoleBasedHome` for backward compatibility.

---

## How Demo Should Be Conducted (UPDATED)

1. “Sir, இது AgriFlow OS application” — open **Flutter app only**
2. Login as **Owner** (`Agriflow Owner` role) → full KPI + quick actions dashboard
3. Show farmers, timeline, Cash & Carry POS from owner home
4. Logout → login as **Field Staff** → simpler task-focused home
5. **Do not open Frappe Desk** unless asked about admin / DocType setup

Demo credentials: see `docs/LOCAL_LIVE_DEMO.md` / `docs/SETUP_FROM_SCRATCH.md`

```powershell
flutter run -d windows `
  --dart-define=API_BASE_URL=http://127.0.0.1:8000 `
  --dart-define=DEMO_MODE=false
```

---

## What Users See

- **One app icon, one login** — role chosen by backend assignment
- **Owner:** broad operational overview + all shortcuts
- **Field Staff:** tasks first, minimal distractions
- **Office roles:** billing / data entry / approvals as appropriate
- **Frappe Desk:** invisible to end users

---

## Files Created / Modified

### New
- `mobile/agriflow_mobile/lib/core/auth/user_role_provider.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/role_based_home.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/owner_dashboard.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/field_staff_dashboard.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/office_manager_dashboard.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/office_staff_dashboard.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/installer_dashboard.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/service_tech_dashboard.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/store_keeper_dashboard.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/generic_dashboard.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/dashboard_stats.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/widgets/dashboard_widgets.dart`
- `docs/UNIFIED_APP_EXPERIENCE_REPORT.md`

### Modified
- `mobile/agriflow_mobile/lib/app/router/app_router.dart`
- `mobile/agriflow_mobile/lib/features/dashboard/presentation/home_dashboard_screen.dart` (alias)

---

## Verification

```powershell
cd mobile\agriflow_mobile
flutter analyze lib/core/auth lib/features/dashboard lib/app/router/app_router.dart
```

Expected: **0 errors** on changed paths.

---

## Follow-ups (optional)

- Hide bottom-nav tabs per role (e.g. Store Keeper → Sync tab only)
- Owner KPI “Active Farmers” — wire to live API / projection count
- Tamil strings for new dashboard section titles (`Quick Actions`, role-specific subtitles)
- Redirect `/app` on Frappe site to a “Use mobile app” landing page for confused users
