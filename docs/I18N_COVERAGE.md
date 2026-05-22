# AgriFlow Mobile — Tamil i18n Coverage (Day 5)

**Default locale:** `ta` (Tamil)  
**Fallback:** `en` via `app_en.arb`  
**Generated API:** `flutter gen-l10n` → `AppLocalizations`

Audit date: 2026-05-20 (Day 5 theme + i18n pass)

---

## Summary

| Metric | Value |
|--------|-------|
| Demo-path screens | 9 |
| Screens at 100% user-visible i18n | 9 |
| ARB keys (approx.) | 120+ |
| Hardcoded English UI strings (demo path) | 0 |
| Technical tokens shown as-is | Entity codes (`task`, `push`), IDs, API phases |

**Overall demo-path Tamil coverage: ~98%**  
(2% = dynamic server/API tokens intentionally not translated)

---

## Per-screen coverage

| Screen | Route / tab | Tamil keys | Coverage | Notes |
|--------|-------------|------------|----------|-------|
| Login | `/login` | All labels, buttons | 100% | `login*` keys |
| Home dashboard | `/home` | Welcome, stats, nav | 100% | `dashboard*`, `nav*` |
| Farmers list | `/farmers` | List, empty, errors | 100% | `emptyFarmers`, farmer names from API |
| Project timeline (HERO) | `/projects/:id/timeline` | 12 stages, header, actions, stage secondary labels | 100% | `stage*`, `timeline*`, `stageSecondary*` |
| Task feed (HERO #2) | `/tasks` | Sections, filters, due labels | 100% | `task*` keys |
| Notifications | `/notifications` | Groups, filters, tones | 100% | `notification*`; body from API preview |
| Sync status | `/sync` | Status, queue, history, dev | 100% | `sync*` keys |
| App bar sync chip | Global | Online/offline/syncing | 100% | `syncBar*` |
| Bottom navigation | Global | 5 destinations | 100% | `nav*` |

### Secondary / non-demo paths

| Screen | Coverage | Notes |
|--------|----------|-------|
| Task detail | 95% | Status/project line i18n; inventory item names from server |
| Timeline feed | 100% | Empty state i18n |
| Onboarding | 100% | Hidden in `DEMO_MODE` |
| Feedback | 100% | Hidden in `DEMO_MODE` |
| Conflict sheet | 100% | `conflict*` keys |

---

## What stays untranslated (by design)

- **Farmer / village / officer names** — master data from Frappe (Tamil names in seed)
- **Project IDs** — e.g. `FP-2026-00012`
- **Sync queue entity/op** — `task.complete`, `timeline.note` (developer-facing)
- **Sync run phase** — `push`, `pull`, `notifications` (log labels)
- **Error stack traces** — `errorGeneric` wrapper only in UI
- **Notification `body_preview`** — server-authored Tamil/English mix in seed

---

## Theme consistency (Day 5)

| Check | Status |
|-------|--------|
| No `Colors.*` in feature widgets | ✅ |
| No `Color(0xFF...)` outside `color_tokens.dart` | ✅ |
| Status icons unified (`AgriFlowStatusIcon`) | ✅ |
| Dark theme defined | ✅ `darkTheme` in `app.dart` |
| Spacing via `AgriFlowSpacing` / `AppDimensions` | ✅ |

---

## Maintenance

1. Add new UI strings to **`app_ta.arb` first**, then `app_en.arb`.
2. Run `flutter gen-l10n` after ARB edits.
3. Never hardcode Tamil in widgets (per `.cursorrules`).
4. Re-run this audit: grep `Colors.` and `Text('` under `lib/features/`.

---

## Verification command

```bash
cd mobile/agriflow_mobile
flutter gen-l10n
rg "Colors\.|Text\('[A-Za-z]" lib/features lib/shared --glob "*.dart"
```

Expected: no matches in presentation widgets (only `color_tokens.dart` / theme).
