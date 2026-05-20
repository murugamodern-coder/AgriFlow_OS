# AgriFlow OS — UI Tokens & Design System

**Version:** 1.0  
**Status:** Phase 1 specification (documentation only)  
**Last updated:** 2026-05-20  

**Platform:** Flutter 3.24 · Material 3  
**Related documents:** [PRD.md](./PRD.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · [DOCTYPES.md](./DOCTYPES.md) · [API_CONTRACTS.md](./API_CONTRACTS.md) · [.cursorrules](./.cursorrules)

---

## Document purpose

This document is the **single source of truth** for visual design tokens, component standards, and UX patterns for AgriFlow OS mobile (primary) and desk (secondary). Implementation must reference tokens from `lib/core/design_tokens/` — **never hardcode colors, spacing, or Tamil strings in widgets**.

**Design north star:** A calm, timeline-first operational app for Tamil Nadu field staff — not an ERP.

---

## Table of contents

1. [Design philosophy](#1-design-philosophy)  
2. [Brand identity](#2-brand-identity)  
3. [Color system](#3-color-system)  
4. [Semantic color tokens](#4-semantic-color-tokens)  
5. [Typography system](#5-typography-system)  
6. [Tamil font strategy](#6-tamil-font-strategy)  
7. [Spacing scale](#7-spacing-scale)  
8. [Radius scale](#8-radius-scale)  
9. [Elevation system](#9-elevation-system)  
10. [Iconography guidelines](#10-iconography-guidelines)  
11. [Component sizing standards](#11-component-sizing-standards)  
12. [Button system](#12-button-system)  
13. [Input field system](#13-input-field-system)  
14. [Card system](#14-card-system)  
15. [Timeline UI tokens](#15-timeline-ui-tokens)  
16. [Status chip tokens](#16-status-chip-tokens)  
17. [Stage color mapping](#17-stage-color-mapping)  
18. [Navigation patterns](#18-navigation-patterns)  
19. [Bottom navigation standards](#19-bottom-navigation-standards)  
20. [List item standards](#20-list-item-standards)  
21. [Table/grid standards](#21-tablegrid-standards)  
22. [Form UX standards](#22-form-ux-standards)  
23. [Empty states](#23-empty-states)  
24. [Loading states](#24-loading-states)  
25. [Error states](#25-error-states)  
26. [Offline sync indicators](#26-offline-sync-indicators)  
27. [Notification/toast system](#27-notificationtoast-system)  
28. [Dialog patterns](#28-dialog-patterns)  
29. [Accessibility guidelines](#29-accessibility-guidelines)  
30. [Dark mode strategy](#30-dark-mode-strategy)  
31. [Responsive breakpoints](#31-responsive-breakpoints)  
32. [Animation guidelines](#32-animation-guidelines)  
33. [Design invariants](#33-design-invariants)  

---

## Token naming conventions

| Layer | Pattern | Example |
|-------|---------|---------|
| **Primitive** | `{palette}{shade}` | `green700`, `slate50` |
| **Semantic** | `{role}{variant}` | `colorPrimary`, `colorSurfaceVariant` |
| **Component** | `{component}{part}{state}` | `buttonFilledContainer`, `timelineNodeActive` |
| **Stage** | `stage{Key}{part}` | `stageFieldSurveyAccent` |
| **Spacing** | `space{scale}` | `space16` |
| **Radius** | `radius{scale}` | `radius12` |
| **Typography** | `text{role}` | `textTitleLarge` |

**Rules**

- Semantic tokens map to primitives — widgets use **semantic only**.  
- Token keys in code: `camelCase` matching Flutter `ThemeExtension` fields.  
- JSON asset (optional): `assets/design_tokens/tokens.json` mirrors this document.  
- All user-visible copy: **i18n ARB keys** — tokens never embed Tamil/English strings.

---

## 1. Design philosophy

### 1.1 Principles

| Principle | UX implication |
|-----------|----------------|
| **Timeline-first** | Project timeline occupies ≥50% of primary screen vertical space |
| **Offline-first** | Sync status always visible in app chrome; never hide queue depth |
| **Tamil-first** | Default locale `ta`; typography tuned for Tamil script density |
| **Mobile-first** | Touch targets ≥44dp; single-column layouts; bottom-weighted actions |
| **Workflow-first** | Next stage action is the primary CTA — not buried in menus |
| **Calm enterprise** | Muted neutrals + restrained green primary; no alarmist reds except errors |
| **Field reality** | High contrast for outdoor/sunlight; large tap areas; minimal typing |

### 1.2 Influences (PRD §13)

| Reference | Borrow |
|-----------|--------|
| **Linear** | Clean timeline, subtle borders, focused hierarchy |
| **Notion** | Card-based content, breathing room |
| **Khatabook** | Simple lists, money clarity (profit/expense) |
| **PhonePe** | Bold primary actions, trust through consistency |

### 1.3 Anti-patterns (forbidden)

- ERP multi-tab forms, dense data grids as primary views  
- Desktop-style menu bars, hover-dependent UI  
- More than one primary CTA per screen  
- Stage progress hidden behind modals  
- Gray-on-gray body text outdoors  
- Hardcoded `#047857` in widgets (use tokens)  
- Hardcoded Tamil strings in Dart

---

## 2. Brand identity

### 2.1 Product personality

**AgriFlow OS** — *operational memory* for agriculture businesses: trustworthy, orderly, human-scale (15 users, 12 blocks), not “enterprise bloat.”

### 2.2 Logo and mark (guidelines)

| Asset | Usage |
|-------|--------|
| Primary mark | Green leaf + flow line on `colorSurface` |
| Clear space | Minimum `space24` on all sides |
| Minimum size | 32×32 dp digital |
| On photos | Use white knock-out with subtle shadow |

*Asset files live outside this doc in `assets/brand/` when produced.*

### 2.3 Voice and tone (i18n)

- Short, imperative CTAs: “தொடரவும்” / “Continue” — via ARB, not tokens  
- Avoid jargon; prefer “அடுத்த படி” (next step) over internal stage keys in UI  
- Error messages: explain what to do next, not error codes

---

## 3. Color system

### 3.1 Brand primitives (PRD §14)

| Token | Hex | Role |
|-------|-----|------|
| `primitivePrimary` | `#047857` | Emerald 700 — brand, primary actions |
| `primitivePrimaryLight` | `#10B981` | Emerald 500 — highlights |
| `primitivePrimaryDark` | `#065F46` | Emerald 800 — pressed states |
| `primitiveAccent` | `#4F46E5` | Indigo 600 — links, secondary emphasis |
| `primitiveAccentLight` | `#818CF8` | Indigo 400 — badges |
| `primitiveBackground` | `#F8FAFC` | Slate 50 — app background |

### 3.2 Neutral palette (Material 3 slate)

| Token | Hex | Use |
|-------|-----|-----|
| `neutral0` | `#FFFFFF` | Cards, sheets |
| `neutral50` | `#F8FAFC` | Background |
| `neutral100` | `#F1F5F9` | Subtle fill |
| `neutral200` | `#E2E8F0` | Borders, dividers |
| `neutral400` | `#94A3B8` | Placeholder, disabled |
| `neutral600` | `#475569` | Secondary text |
| `neutral800` | `#1E293B` | Primary text |
| `neutral900` | `#0F172A` | Headlines |

### 3.3 Functional palette

| Token | Hex | Use |
|-------|-----|-----|
| `functionalSuccess` | `#059669` | Completed, synced |
| `functionalWarning` | `#D97706` | Pending, due soon |
| `functionalError` | `#DC2626` | Errors, failed sync |
| `functionalInfo` | `#0284C7` | Informational toasts |

**Outdoor contrast rule:** Body text on `colorSurface` must meet **WCAG AA (4.5:1)** — use `neutral800` minimum, not `neutral400`, for readable Tamil labels in sunlight.

---

## 4. Semantic color tokens

Map primitives to Material 3 roles (light theme — Phase 1 default).

| Semantic token | Maps to | Usage |
|----------------|---------|--------|
| `colorPrimary` | `primitivePrimary` | FAB, key buttons, active nav |
| `colorOnPrimary` | `#FFFFFF` | Text/icons on primary |
| `colorPrimaryContainer` | `#D1FAE5` | Soft green backgrounds |
| `colorOnPrimaryContainer` | `#065F46` | Text on primary container |
| `colorSecondary` | `primitiveAccent` | Secondary buttons, links |
| `colorOnSecondary` | `#FFFFFF` | On secondary |
| `colorSecondaryContainer` | `#E0E7FF` | Accent chips |
| `colorOnSecondaryContainer` | `#3730A3` | On accent container |
| `colorSurface` | `neutral0` | Cards, sheets |
| `colorOnSurface` | `neutral800` | Body text |
| `colorSurfaceVariant` | `neutral100` | Input fills, list stripes |
| `colorOnSurfaceVariant` | `neutral600` | Captions, metadata |
| `colorBackground` | `primitiveBackground` | Scaffold |
| `colorOnBackground` | `neutral900` | Screen titles |
| `colorOutline` | `neutral200` | Borders |
| `colorOutlineVariant` | `neutral100` | Subtle dividers |
| `colorError` | `functionalError` | Errors |
| `colorOnError` | `#FFFFFF` | On error buttons |
| `colorErrorContainer` | `#FEE2E2` | Error banners |
| `colorOnErrorContainer` | `#991B1B` | Error text |

### 4.1 Semantic usage examples

| UI element | Token |
|------------|-------|
| App scaffold | `colorBackground` |
| Project timeline card | `colorSurface` + `elevation1` |
| Primary CTA “Advance stage” | `colorPrimary` / `colorOnPrimary` |
| Secondary “Add note” | `colorSecondaryContainer` / `colorOnSecondaryContainer` |
| Disabled field | `colorOnSurfaceVariant` @ 38% opacity |
| Sync error banner | `colorErrorContainer` / `colorOnErrorContainer` |
| Profit positive figure | `functionalSuccess` (not primary green) |

---

## 5. Typography system

### 5.1 Font families

| Role | Family | Weights |
|------|--------|---------|
| **Latin UI** | Inter | 400, 500, 600 |
| **Latin display** | Poppins | 500, 600, 700 |
| **Tamil** | Noto Sans Tamil | 400, 500, 600, 700 |

### 5.2 Type scale (Material 3 aligned)

| Token | Family | Size (sp) | Weight | Line height | Letter spacing |
|-------|--------|-----------|--------|-------------|----------------|
| `textDisplayLarge` | Poppins | 32 | 600 | 40 | -0.5 |
| `textDisplayMedium` | Poppins | 28 | 600 | 36 | 0 |
| `textHeadlineLarge` | Poppins | 24 | 600 | 32 | 0 |
| `textHeadlineMedium` | Poppins | 20 | 600 | 28 | 0 |
| `textTitleLarge` | Inter | 18 | 600 | 26 | 0 |
| `textTitleMedium` | Inter | 16 | 600 | 24 | 0.15 |
| `textTitleSmall` | Inter | 14 | 600 | 20 | 0.1 |
| `textBodyLarge` | Inter / Noto | 16 | 400 | 24 | 0.15 |
| `textBodyMedium` | Inter / Noto | 14 | 400 | 20 | 0.25 |
| `textBodySmall` | Inter / Noto | 12 | 400 | 16 | 0.4 |
| `textLabelLarge` | Inter | 14 | 500 | 20 | 0.1 |
| `textLabelMedium` | Inter | 12 | 500 | 16 | 0.5 |
| `textLabelSmall` | Inter | 11 | 500 | 16 | 0.5 |

**Tamil rule:** When locale is `ta`, apply **Noto Sans Tamil** to all `textBody*` and `textTitle*`; keep Poppins for numeric-only displays if needed.

### 5.3 Typography hierarchy (screens)

| Level | Token | Example usage |
|-------|-------|---------------|
| Screen title | `textHeadlineMedium` | “திட்டம் FP-2026-00124” |
| Section | `textTitleLarge` | “படிநிலை வரலாறு” (Timeline) |
| Card title | `textTitleMedium` | Farmer name on list |
| Body | `textBodyLarge` | Task description, notes |
| Meta | `textBodySmall` + `colorOnSurfaceVariant` | Modified time, block name |
| CTA label | `textLabelLarge` | Button text |
| Chip | `textLabelMedium` | Stage chip, status |

### 5.4 Numeric and currency

| Token | Style |
|-------|--------|
| `textMoneyLarge` | Inter 20/600 tabular figures |
| `textMoneyMedium` | Inter 16/600 tabular figures |

Use tabular lining for expense and subsidy amounts (Khatabook clarity).

---

## 6. Tamil font strategy

### 6.1 Locale-driven font resolution

```
if (locale == ta) {
  body/title → Noto Sans Tamil
} else {
  body/title → Inter
}
headlines → Poppins (Latin) or Noto Sans Tamil 600 (ta)
```

### 6.2 Readability rules

| Rule | Value |
|------|-------|
| Minimum body size (Tamil) | **16 sp** (`textBodyLarge`) — never 12 sp for primary labels |
| Line height | ≥1.5× font size for Tamil body |
| Mixed Tamil + English | Single family per span where possible; avoid font switching mid-word |
| Truncation | Ellipsize end; max 2 lines for list titles; full name on detail |
| Stage labels | Use i18n `project.stage.*` — allow 2 lines on chips |

### 6.3 Testing checklist

- Long Tamil village names in list rows  
- Stage names at 12 sp minimum on chips (`textLabelMedium` + Noto)  
- Outdoor glare: contrast check on `colorBackground` and `colorSurface`

---

## 7. Spacing scale

Base unit: **4 dp**. Token = multiple of 4.

| Token | dp | Typical use |
|-------|-----|-------------|
| `space0` | 0 | — |
| `space2` | 2 | Hairline gaps |
| `space4` | 4 | Icon-text gap |
| `space8` | 8 | Chip padding, dense inline |
| `space12` | 12 | Card inner compact |
| `space16` | 16 | Standard padding, list item vertical |
| `space20` | 20 | Section gap small |
| `space24` | 24 | Card padding, screen horizontal margin |
| `space32` | 32 | Section gap large |
| `space40` | 40 | Timeline node spacing |
| `space48` | 48 | Bottom nav clearance |
| `space56` | 56 | FAB offset above nav |
| `space64` | 64 | Hero / empty state |

### 7.1 Spacing examples

```
Screen horizontal padding:     space24 (24 dp)
Timeline card padding:         space16
Between timeline entries:      space24
List item vertical padding:    space16
Form field vertical gap:       space20
Section title to content:      space12
Bottom sheet safe padding:     space24 + system inset
```

**Mobile screen side margins:** `space24` minimum; `space16` only inside cards.

---

## 8. Radius scale

| Token | dp | Use |
|-------|-----|-----|
| `radiusNone` | 0 | Tables (rare) |
| `radius4` | 4 | Chips, small badges |
| `radius8` | 8 | Inputs, small buttons |
| `radius12` | 12 | Cards, list tiles (default) |
| `radius16` | 16 | Bottom sheets, modals |
| `radius24` | 24 | Large hero cards |
| `radiusFull` | 999 | Pills, FAB, avatars |

**Default card:** `radius12`. **Timeline node:** circular `radiusFull`.

---

## 9. Elevation system

Material 3 tonal elevation preferred over heavy shadows outdoors.

| Token | Shadow / tonal | Use |
|-------|----------------|-----|
| `elevation0` | None | Flat lists on background |
| `elevation1` | 1 dp / surface +1 tone | Standard cards |
| `elevation2` | 2 dp | FAB, sticky header |
| `elevation3` | 4 dp | Bottom sheet, dialogs |
| `elevation4` | 8 dp | Modal, urgent overlay |

**Outdoor preference:** Rely on `colorSurface` vs `colorBackground` contrast before increasing shadow.

---

## 10. Iconography guidelines

| Property | Standard |
|----------|----------|
| Library | Material Symbols (rounded variant) |
| Default size | 24 dp |
| Nav icons | 24 dp |
| List leading | 24 dp in `colorOnSurfaceVariant` |
| Active | `colorPrimary` |
| Touch padding | Icon button **48×48 dp** hit area |

| Context | Icon semantics |
|---------|----------------|
| Timeline complete | `check_circle` — `functionalSuccess` |
| Timeline current | `radio_button_checked` — `colorPrimary` |
| Timeline future | `radio_button_unchecked` — `neutral400` |
| Sync pending | `cloud_upload` — `functionalWarning` |
| Sync error | `cloud_off` — `functionalError` |
| Task visit | `location_on` |
| Farmer | `person` |
| Project | `assignment` |

Avoid decorative icons; every icon must have a semantic meaning.

---

## 11. Component sizing standards

| Element | Min size | Preferred |
|---------|----------|-----------|
| Touch target | **44×44 dp** | **48×48 dp** |
| List row height | 56 dp | 64 dp (with subtitle) |
| Input height | 48 dp | 56 dp (Tamil labels) |
| Primary button height | 48 dp | 52 dp |
| Bottom nav bar | 56 dp + safe area | — |
| Timeline row min | 72 dp | 88 dp (2-line Tamil) |
| FAB | 56 dp | — |
| Avatar / officer | 40 dp | 48 dp |

---

## 12. Button system

### 12.1 Variants

| Variant | Token prefix | Use |
|---------|--------------|-----|
| **Filled** | `buttonFilled` | Primary stage action (one per screen) |
| **Filled tonal** | `buttonFilledTonal` | Secondary confirm |
| **Outlined** | `buttonOutlined` | Cancel, alternative |
| **Text** | `buttonText` | Tertiary, inline |
| **Destructive filled** | `buttonDanger` | Cancel project (Owner only) |

### 12.2 Specs

| Property | Filled | Outlined | Text |
|----------|--------|----------|------|
| Min height | 48 dp | 48 dp | 44 dp |
| Horizontal padding | `space24` | `space24` | `space12` |
| Radius | `radius8` | `radius8` | `radius8` |
| Label | `textLabelLarge` | `textLabelLarge` | `textLabelLarge` |
| Disabled opacity | 38% | 38% | 38% |

### 12.3 Placement

- Primary CTA: **sticky bottom** above nav (safe area), full-width with `space24` margin  
- Never stack more than 2 buttons vertically; use tonal + text for secondary  
- Stage transition: label from i18n `action.advance_to_{stage}`

---

## 13. Input field system

### 13.1 Style

Material 3 **outlined** fields (better sunlight edge definition than filled alone).

| Token | Value |
|-------|-------|
| `inputHeight` | 56 dp |
| `inputRadius` | `radius8` |
| `inputBorder` | `colorOutline` 1 dp |
| `inputBorderFocused` | `colorPrimary` 2 dp |
| `inputFill` | `colorSurface` |
| `inputLabel` | `textBodySmall` → `textLabelLarge` when focused |
| `inputError` | `colorError` border + `textBodySmall` error text |

### 13.2 Field UX (see §22)

- One primary input per “step sheet”  
- Mobile: numeric keyboard for mobile, phone, acres, amount  
- Tamil labels above field (not placeholder-only)  
- Voice input: Phase 2 — reserve trailing icon space

---

## 14. Card system

| Card type | Token | Spec |
|-----------|-------|------|
| **Standard** | `cardStandard` | `colorSurface`, `radius12`, `elevation1`, padding `space16` |
| **Timeline** | `cardTimeline` | `cardStandard` + left rail gutter `space40` |
| **List tile** | `cardList` | `radius12`, no elevation; border `colorOutline` 1 dp optional |
| **Highlight** | `cardHighlight` | `colorPrimaryContainer` border left 4 dp `colorPrimary` |
| **Sync alert** | `cardSync` | `colorErrorContainer` or warning container |

**Avoid:** nested cards more than 1 level deep.

---

## 15. Timeline UI tokens

Timeline is the **dominant visual** on Farmer Project detail.

### 15.1 Layout tokens

| Token | Value |
|-------|-------|
| `timelineRailWidth` | 24 dp |
| `timelineNodeSize` | 20 dp (24 dp current stage) |
| `timelineRailColor` | `colorOutline` |
| `timelineRailActive` | `colorPrimary` |
| `timelineEntryGap` | `space24` |
| `timelineCardMaxWidth` | full width − `space48` |
| `timelineMinScreenRatio` | 50% viewport height |

### 15.2 Node states

| State | Node | Connector |
|-------|------|-----------|
| Completed | Filled `colorPrimary` + check icon `colorOnPrimary` | Solid `colorPrimary` |
| Current | Ring 3 dp `colorPrimary`, inner fill `colorPrimaryContainer` | Solid to node; dashed below |
| Future | `neutral400` outline | Dashed `neutral200` |
| Correction | `functionalWarning` + `warning` icon | Dotted `functionalWarning` |

### 15.3 Entry content

| Slot | Typography |
|------|------------|
| Stage name | `textTitleMedium` |
| Date/time | `textBodySmall` + `colorOnSurfaceVariant` |
| Actor | `textBodySmall` |
| Notes | `textBodyMedium`, max 3 lines expand |
| Attachment | Chip + icon 32 dp thumb |

### 15.4 Next action panel (below timeline)

| Token | Value |
|-------|-------|
| `nextActionPanelBackground` | `colorPrimaryContainer` |
| `nextActionPanelRadius` | `radius12` |
| `nextActionPanelPadding` | `space16` |
| CTA | `buttonFilled` full width |

Shows `workflow.next_stage` from API (i18n label).

---

## 16. Status chip tokens

### 16.1 Project status

| Status | Background | Text/icon |
|--------|------------|-----------|
| `active` | `colorPrimaryContainer` | `colorOnPrimaryContainer` |
| `on_hold` | `#FEF3C7` | `#92400E` |
| `completed` | `#D1FAE5` | `#065F46` |
| `cancelled` | `colorErrorContainer` | `colorOnErrorContainer` |

### 16.2 Task status

| Status | Variant |
|--------|---------|
| `open` | Outlined chip `colorOutline` |
| `in_progress` | Tonal `colorSecondaryContainer` |
| `completed` | Tonal success container |
| `cancelled` | Muted `neutral100` |

### 16.3 Chip dimensions

| Token | Value |
|-------|-------|
| `chipHeight` | 28 dp (32 dp Tamil 2-line) |
| `chipPaddingH` | `space12` |
| `chipRadius` | `radiusFull` |
| `chipIconSize` | 16 dp |

---

## 17. Stage color mapping

Stages use **muted accent dots** on timeline — not 12 loud colors (avoids carnival UI). Stage identity = label (i18n) + sequence number.

### 17.1 Stage accent tokens (dot / left border)

| stage_key | Accent token | Hex (accent dot) |
|-----------|--------------|------------------|
| `lead_captured` | `stageLeadCaptured` | `#64748B` |
| `eligibility_check` | `stageEligibilityCheck` | `#6366F1` |
| `documents_collected` | `stageDocumentsCollected` | `#8B5CF6` |
| `mimis_registered` | `stageMimisRegistered` | `#0891B2` |
| `field_survey` | `stageFieldSurvey` | `#059669` |
| `quotation_generated` | `stageQuotationGenerated` | `#0D9488` |
| `pre_inspection_approval` | `stagePreInspection` | `#D97706` |
| `work_order_received` | `stageWorkOrder` | `#CA8A04` |
| `material_dispatched` | `stageMaterialDispatched` | `#EA580C` |
| `installation_done` | `stageInstallationDone` | `#047857` |
| `post_inspection_approval` | `stagePostInspection` | `#D97706` |
| `subsidy_released` | `stageSubsidyReleased` | `#065F46` |

### 17.2 Stage visualization guidance

| Rule | Guidance |
|------|----------|
| Current stage chip | Full chip with `textLabelMedium` + accent left bar 3 dp |
| Completed stages | Muted text; accent dot only |
| Future stages | `colorOnSurfaceVariant` text |
| Progress bar (optional) | Segmented 12 — filled `colorPrimary` up to `stage_sequence` |
| Never | 12 different button colors per stage |

**Grouping (visual hierarchy)**

| Group | Stages | UI hint |
|-------|--------|---------|
| Intake | 1–3 | Neutral accents |
| Govt / MIMIS | 4 | Cyan accent |
| Field / quote | 5–6 | Green-teal |
| Approvals | 7, 11 | Amber |
| Execution | 8–10 | Orange → primary green |
| Closure | 12 | Dark green |

---

## 18. Navigation patterns

### 18.1 Architecture (go_router)

| Pattern | Use |
|---------|-----|
| **Shell route** | Role-based bottom nav container |
| **Stack push** | Detail screens (farmer, project) |
| **Modal sheet** | Quick capture, filters |
| **Full screen** | Camera / document scan |

### 18.2 Primary destinations by role

| Role | Primary tabs |
|------|----------------|
| Field Staff | Projects, Tasks, Farmers, Sync |
| Office Staff | Projects, Farmers, Tasks, More |
| Store Keeper | Stock, Projects (stage 9), Sync |
| Installer | Projects (install), Tasks |
| Service Tech | Service, Tasks |
| Office Manager | Projects, Reports, MIMIS, More |
| Owner | Dashboard, Projects, Reports, More |

### 18.3 Deep links

- `/projects/:id/timeline` — default project landing  
- `/tasks/:id` — task detail  
- `/farmers/:id` — farmer profile  

---

## 19. Bottom navigation standards

| Token | Value |
|-------|-------|
| `bottomNavHeight` | 56 dp + `SafeArea` |
| `bottomNavBackground` | `colorSurface` |
| `bottomNavElevation` | `elevation2` |
| `bottomNavActive` | `colorPrimary` |
| `bottomNavInactive` | `neutral400` |
| `bottomNavLabel` | `textLabelSmall` |
| Max items | **4** (+ “More” hub if needed) |

**Rules**

- Labels always visible (not icon-only) for Tamil clarity  
- Badge on Sync tab: pending queue count (`functionalWarning` if >0, `functionalError` if failed)

---

## 20. List item standards

### 20.1 Project list row

```
[leading stage dot]  [title: farmer + village]     [trailing chevron]
                     [subtitle: stage label + date]
                     [meta: block · officer]
```

| Token | Value |
|-------|-------|
| Row min height | 72 dp |
| Leading dot | 12 dp stage accent |
| Title | `textTitleMedium` |
| Subtitle | `textBodyMedium` |
| Meta | `textBodySmall` + `colorOnSurfaceVariant` |
| Divider | `colorOutlineVariant` inset `space72` |

### 20.2 Task list row

- Priority indicator: 4 dp left bar (`functionalError` urgent, `functionalWarning` high)  
- Due date: red only if overdue, else `colorOnSurfaceVariant`

### 20.3 Farmer list row

- Avatar circle 40 dp `colorPrimaryContainer` + initial  
- Mobile masked: `98XX XXX210` in list (privacy)

---

## 21. Table/grid standards

**Mobile:** Avoid tables as primary UI. Use lists.

| Context | Pattern |
|---------|---------|
| Owner profit summary | Horizontal scroll cards, not wide grid |
| MIMIS reconciliation (desk) | Table allowed; sticky header; row height 48 dp min |
| Inventory (Store Keeper) | 2-column card grid on tablet; list on phone |

| Token | Value |
|-------|-------|
| `tableHeaderBackground` | `neutral100` |
| `tableRowHeight` | 48 dp |
| `tableCellPadding` | `space12` |

---

## 22. Form UX standards

### 22.1 Principles

| Rule | Implementation |
|------|----------------|
| One thing per sheet | Bottom sheet wizard; ≤5 fields per step |
| Progressive disclosure | Advanced fields behind “More details” |
| Save offline | Primary button enqueues — label “சேமி” / `action.save` (i18n) |
| No multi-tab forms | Use steps with progress dots |
| Defaults | Pre-fill block/cluster from user JWT |

### 22.2 Step sheet

| Token | Value |
|-------|-------|
| Sheet radius | `radius16` top |
| Step indicator height | 4 dp bar `colorPrimary` |
| Field gap | `space20` |
| Keyboard action | `next` / `done` per field |

### 22.3 High-friction fields

| Field | UX |
|-------|-----|
| Mobile | OTP-style optional Phase 2; 10 digit pad |
| Survey number | Uppercase alphanumeric |
| Amount | Currency prefix ₹ + tabular figures |
| Photo | Camera full-screen; preview before attach |

---

## 23. Empty states

| Token | Value |
|-------|-------|
| `emptyIllustrationSize` | 120 dp |
| `emptyTitle` | `textTitleLarge` |
| `emptyBody` | `textBodyMedium` + `colorOnSurfaceVariant` |
| `emptyAction` | `buttonFilled` optional |

| Context | Message direction (i18n keys) |
|---------|-------------------------------|
| No projects | `empty.projects.title` + filter hint |
| No tasks | `empty.tasks.title` |
| Offline never synced | `empty.sync.first_pull` |
| Search no results | `empty.search` |

Center vertically in content area; min `space64` padding.

---

## 24. Loading states

| Type | Pattern |
|------|---------|
| Screen first load | Skeleton timeline + 3 list rows |
| Pull refresh | M3 `RefreshIndicator` `colorPrimary` |
| Button action | Inline 20 dp spinner `colorOnPrimary` |
| Background sync | Subtle linear progress under app bar 2 dp `colorPrimary` |
| MIMIS batch | Determinate progress + `textBodySmall` row count |

**Skeleton tokens:** `skeletonBase` = `neutral100`, `skeletonShimmer` = `neutral200`.

---

## 25. Error states

| Level | UI |
|-------|-----|
| Field validation | Inline below input `colorError` |
| Form submit | Banner `cardSync` style |
| Screen | Illustration + `textTitleMedium` + retry `buttonFilled` |
| Sync conflict | Bottom sheet explaining refresh (i18n `error.sync.stale_transition`) |

| Token | Value |
|-------|-------|
| `errorIconSize` | 48 dp |
| `errorTitle` | `textTitleLarge` |
| `errorBody` | `textBodyMedium` |

Never show raw `error.code` to field staff — log only.

---

## 26. Offline sync indicators

**Mandatory visibility** (ARCHITECTURE invariant).

### 26.1 App bar sync chip

| State | Icon | Color | Label (i18n) |
|-------|------|-------|--------------|
| Synced | `cloud_done` | `functionalSuccess` | `sync.status.synced` |
| Pending | `cloud_upload` | `functionalWarning` | `sync.status.pending` + count |
| Syncing | animated `sync` | `colorPrimary` | `sync.status.syncing` |
| Offline | `cloud_off` | `neutral600` | `sync.status.offline` |
| Error | `cloud_off` | `functionalError` | `sync.status.error` |

| Token | Value |
|-------|-------|
| `syncChipHeight` | 32 dp |
| `syncChipRadius` | `radiusFull` |
| `syncChipPadding` | `space8` horizontal |

### 26.2 Sync detail sheet

- Queue depth, last push/pull time, per-entity failure with “Retry”  
- Tap app bar chip to open

### 26.3 Row-level pending

- Dim opacity 0.7 + small `cloud_upload` icon for unsynced local rows

---

## 27. Notification/toast system

| Type | Background | Duration |
|------|------------|----------|
| Success | `functionalSuccess` / white text | 3 s |
| Info | `functionalInfo` | 4 s |
| Warning | `functionalWarning` | 5 s |
| Error | `functionalError` | Sticky until dismiss |

| Token | Value |
|-------|-------|
| `snackBarRadius` | `radius8` |
| `snackBarMargin` | `space16` |
| `snackBarAction` | `textLabelLarge` underline |

Use SnackBar / MaterialBanner — not custom overlays blocking timeline.

---

## 28. Dialog patterns

| Pattern | Use |
|---------|--------|
| **Alert** | Destructive confirm (cancel project) |
| **Confirm** | Stage transition confirm |
| **Bottom sheet** | Filters, quick add, sync detail |
| **Full screen** | Rare — document viewer |

| Token | Value |
|-------|-------|
| `dialogRadius` | `radius16` |
| `dialogPadding` | `space24` |
| `dialogTitle` | `textHeadlineSmall` |
| `dialogBody` | `textBodyLarge` |

Stage transition dialog shows **from → to** stage labels (i18n) + optional notes field.

---

## 29. Accessibility guidelines

| Requirement | Standard |
|-------------|----------|
| Touch target | ≥ **44×44 dp** (prefer 48) |
| Contrast | WCAG AA minimum; AAA for Tamil meta in sunlight |
| Screen reader | Semantics labels on timeline nodes (“Stage 5 of 12, Field Survey, completed”) |
| Motion | Respect `reduce motion` — disable timeline animations |
| Font scaling | Support up to 1.3× without layout break; timeline may scroll |
| Color alone | Never sole indicator of status — use icon + text |
| Focus order | Timeline top → next action → tasks → metadata |

---

## 30. Dark mode strategy

| Phase | Scope |
|-------|-------|
| **Phase 1** | Light theme only (field sunlight priority) |
| **Phase 2** | Dark theme via paired semantic tokens |

### 30.1 Dark token pairs (reserved)

| Light | Dark (reserved) |
|-------|-----------------|
| `colorBackground` `#F8FAFC` | `#0F172A` |
| `colorSurface` `#FFFFFF` | `#1E293B` |
| `colorOnSurface` `#1E293B` | `#F1F5F9` |
| `colorPrimary` `#047857` | `#10B981` |

Document dark tokens in JSON when implemented; do not half-implement in Phase 1.

---

## 31. Responsive breakpoints

Mobile-first; tablet secondary (Owner desk review).

| Breakpoint | Width | Layout |
|------------|-------|--------|
| `compact` | < 600 dp | Single column, bottom nav |
| `medium` | 600–840 dp | Optional 2-column detail (timeline + tasks side) |
| `expanded` | > 840 dp | Navigation rail + content (tablet) |

| Token | Value |
|-------|-------|
| `contentMaxWidth` | 600 dp centered on expanded |
| `timelineSidePanelWidth` | 320 dp on `medium+` |

---

## 32. Animation guidelines

| Motion | Duration | Curve |
|--------|----------|-------|
| Screen push | 300 ms | `easeOutCubic` |
| Bottom sheet | 250 ms | `easeOut` |
| Timeline node complete | 400 ms | `easeInOut` (respect reduce motion) |
| Chip status change | 200 ms | `easeIn` |
| Sync icon rotate | 1000 ms loop | linear (only while syncing) |

**Avoid:** parallax, bounce, celebratory confetti (not Khatabook/PhonePe payment success — this is ops software).

---

## 33. Design invariants

| # | Invariant |
|---|-----------|
| 1 | **No hardcoded colors** in widgets — semantic tokens only |
| 2 | **No hardcoded Tamil/English** — i18n ARB only |
| 3 | **Timeline visually dominant** on project detail (≥50% content) |
| 4 | **Sync status always visible** in app chrome |
| 5 | **Touch targets ≥ 44 dp** |
| 6 | **One primary filled button** per screen |
| 7 | **Tamil body ≥ 16 sp** Noto Sans Tamil |
| 8 | **No ERP multi-tab forms** |
| 9 | **Outdoor-readable contrast** for text and stage chips |
| 10 | **Stage colors muted** — accent dots, not rainbow UI |
| 11 | **Material 3** components as base |
| 12 | **Role-based nav** — no cluttering all tabs for every user |

---

## Appendix A — Token file structure (implementation reference)

When implementing (not in Phase 1 doc scope):

```
lib/core/design_tokens/
  app_colors.dart          # semantic colors
  app_typography.dart      # TextTheme extension
  app_spacing.dart         # space*
  app_radius.dart
  app_elevation.dart
  app_component_themes.dart
  stage_tokens.dart        # stage accent map
assets/design_tokens/
  tokens.json              # optional mirror of this doc
```

---

## Appendix B — Role dashboard visual hierarchy

| Role | Home screen focus |
|------|-------------------|
| Field Staff | Active projects by block → overdue tasks |
| Office Staff | Document-pending stages → farmer search |
| Store Keeper | Stock alerts → projects at material_dispatched |
| Owner | Profit snapshot cards → block-wise stage funnel |

Use `textHeadlineMedium` for greeting, `cardHighlight` for KPIs, standard list for drill-down.

---

## Appendix C — Change control

| Change | Update |
|--------|--------|
| New stage | §17 mapping + i18n + fixture |
| Brand color change | PRD §14 + this doc + regenerate tokens |
| New component variant | This doc + `app_component_themes.dart` |

---

*End of UI_TOKENS.md*
