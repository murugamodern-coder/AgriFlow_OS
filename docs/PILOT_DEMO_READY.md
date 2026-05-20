# Pilot Demo Ready — AgriFlow OS

**Tag:** `pilot-demo-2026-05`  
**Week 1 deliverable:** Days 1–5 complete

## Included

- Hero **12-stage timeline** (Kumar M. / Project #1284)
- Hero **task feed** (overdue / today / upcoming)
- **Notifications** with urgency tones
- **Visible sync** (app bar, flying animation, simulate offline)
- **Tiruvannamalai seed** (`bench execute agriflow.commands.seed_demo`)
- Tamil-first UI (~98% on demo paths) — see [I18N_COVERAGE.md](./I18N_COVERAGE.md)
- Dress rehearsal guide — [DEMO_REHEARSAL.md](./DEMO_REHEARSAL.md)

## Quick start

```bash
# Backend
bench --site dev.agriflow.local execute agriflow.commands.seed_demo

# Mobile
cd mobile/agriflow_mobile
flutter pub get && flutter gen-l10n
flutter run --dart-define=DEMO_MODE=true
```

Login: `field.officer@agriflow.local` / `AgriFlow@2026`
