# AgriFlow OS — Pilot Demo Dress Rehearsal (Day 5)

**Target duration:** 10–12 minutes  
**Login:** `field.officer@agriflow.local` / `AgriFlow@2026`  
**District:** Tiruvannamalai demo seed

---

## Pre-demo setup (30 min before)

1. Fresh bench or reset site:
   ```bash
   bench --site dev.agriflow.local execute agriflow.commands.seed_demo
   ```
2. Phone: uninstall old APK or `flutter run --release` with `DEMO_MODE=true`
3. Wi‑Fi on for first login + one full sync
4. Charge device ≥80%; disable battery saver
5. Optional: second phone hotspot as backup internet

---

## Demo script (~11 min)

| Min | Action | Wow moment |
|-----|--------|------------|
| 0:00 | Login → Home | Tamil UI, role line |
| 0:30 | Farmers → **Kumar M.** → Timeline | 12-stage HERO, VIP, blocker, #1284 |
| 3:00 | Back → **Tasks** | Overdue / Today / Upcoming sections |
| 4:30 | Swipe complete one task (optional offline first) | Haptic + toast |
| 5:30 | **Notifications** | Red/amber/orange alerts, grouped by date |
| 7:00 | **Sync** tab → enable **Simulate offline** | App bar shows offline + pending |
| 8:00 | Complete another task → **Demo: go online & sync** | Flying cloud animation + “ஒத்திசைவு முடிந்தது ✓” |
| 9:30 | App bar **All synced** state | Client sees “nothing forgotten” |
| 10:30 | Q&A buffer | — |

---

## Rehearsal checklist (×3 runs)

- [ ] Run 1 — timed: _____ min
- [ ] Run 2 — timed: _____ min
- [ ] Run 3 — timed: _____ min
- [ ] Record screen on phone; watch for jank / wrong locale
- [ ] All toasts in Tamil
- [ ] No English leak on hero paths

---

## Backup plans

### Wi‑Fi fails

- Enable **Simulate offline** before demo; queue 2–3 actions
- Narrate: “Field staff keeps working; sync catches up when tower returns”
- Use phone hotspot; avoid guest Wi‑Fi with captive portal
- Pre-sync on LTE before entering venue

### App crashes

- Force-close → reopen (session restored from Hive)
- Fallback: screenshots/video from last rehearsal
- Secondary device with same build installed

### Backend down

- Mobile still shows cached farmers/tasks (offline projections)
- Show sync queue on Sync tab
- Do not tap “Force sync” repeatedly (explain server maintenance)

### Login fails

- Confirm bench running: `bench start`
- Re-run seed; verify user exists
- Dev fallback only if `DEV_AUTH_STUB` build (not demo APK)

---

## Post-rehearsal fixes log

| Run | Issue | Fix |
|-----|-------|-----|
| 1 | | |
| 2 | | |
| 3 | | |

---

## Release tag

After 3 clean rehearsals:

```bash
git tag -a pilot-demo-2026-05 -m "Pilot demo ready"
```

Commit message: `release: pilot demo ready`
