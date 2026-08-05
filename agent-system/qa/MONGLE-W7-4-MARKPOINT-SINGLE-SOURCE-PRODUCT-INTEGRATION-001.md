# QA Evidence — MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Role: Developer self-check (implementer). **Not** Independent QA.
- Full narrative, `1c`/`1x` reasoning, and the CSS-bug root cause: see this
  task's own handoff,
  `agent-system/handoffs/active/MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md`.
  This file records the concrete evidence only.

## Baseline

- Branch: `dev-newmarkp`
- HEAD at start: `97bc09ddf1bd3c3002b969f89c089bd3d423e04a` (unchanged
  throughout — same as the prior Auth/Family tasks this session)
- `accounts`/`family_groups` tables: 0 rows, confirmed by `psql` before any
  seeding

## Static checks

| Check | Command | Result |
|---|---|---|
| Lint | `pnpm run lint` | PASS |
| Typecheck + build | `pnpm run build` (`tsc -b && vite build`) | PASS |
| Diff whitespace | `git diff --check` | PASS |
| Diff scope | `git status --short` | Matches declared file list exactly |

## Database seeding/cleanup (additive-only, verified)

```
CREATED account_id=3 family_group_id=3 membership_id=3
(active Markpoint ServiceSubscription granted)
```

Removed via ID-scoped DELETEs (never blanket) in FK-safe order
(MembershipRoleAssignment → ServiceSubscription → AccountCredential →
AccountSession → FamilyMembership → FamilyGroup → Account). Final
independently re-queried counts: `accounts=0 families=0`.
`git status --short backend/` confirmed clean before, during, and after.

## Runtime checks — `1c` (포인트 잔치)

Login: real `/login` (Account-model), disposable seed account with an
active Markpoint subscription.

| Check | Result |
|---|---|
| `/markpoint` renders canonical `1c` (`[data-canonical-screen-id="1c"]` count) | `1` |
| `markpoint-balance` test-id present, value | `0` (real, honest zero for a fresh account) |
| `markpoint-level` test-id present | `Lv.1` |
| `markpoint-remaining` test-id present, value | `0` |
| Reward-shop button visible + overlay opens | `true` / overlay count `1` |
| Reward-exchange button visible | `true` |
| Canonical header's own logout button → real logout | URL → `/`, `sessionStorage.accessToken` cleared |
| Console/page errors | `0` |

### CSS bug found, root-caused, and fixed during this verification

1. First render: logout button measured `144.67×48px`; sibling title/
   subtitle `div` measured `21.33px` wide, text wrapped one character per
   line.
2. `document.styleSheets` inspection found 4 different unscoped
   `header button {...}` element-selector rules from other stylesheets in
   the repository, one of them setting `font-size: 24px`, all matching this
   canonical `<header><button>` (CSS Modules does not scope bare element
   selectors).
3. The Screen's own `.logout` rule's `font: 700 12px/normal inherit`
   shorthand was confirmed, via `rule.cssText` inspection, to have been
   dropped entirely by the browser (invalid: `inherit` cannot be one
   component of a mixed `font` shorthand) — so nothing in the Screen's own
   CSS was actually contesting the leaking `font-size: 24px`.
4. Fix 1 (selector specificity): `.logout` → `.header .logout` (0,2,0),
   applied — re-measured, **still** 144×48 (the real cause was #3, not
   specificity alone, since the leaking rule was winning on an
   uncontested property, not a specificity fight).
5. Fix 2 (valid longhand properties): `font-family: inherit; font-size:
   12px; font-weight: 700; line-height: normal;` replacing the invalid
   shorthand. Re-measured: logout button `87×33px`, title/subtitle `div`
   `78.9×93px` — both re-confirmed via a second Playwright run, screenshot
   inspected, visually correct.

### Responsive (Product + Preview)

| Surface | Viewport | Horizontal overflow |
|---|---|---|
| `/markpoint` (Product) | 390×844 | `false` |
| `/markpoint` (Product) | 820×1180 | `false` |
| `/markpoint` (Product) | 1180×820 | `false` |
| `/__wave6/1c` (Preview) | 390×844 | `false` |
| `/__wave6/1c` (Preview) | 820×1180 | `false` |
| `/__wave6/1c` (Preview) | 1180×820 | `false` |

### Detached Preview regression

`/__wave6/1c` at all 3 viewports: canonical marker count `1`, week-picker 7
day buttons, 1 cheer-message section, 3 mission rows — the **full**
canonical Screen renders via its own fixture, confirming the Product's
`showWeeklySection={false}` composition did not affect the Preview's own
complete rendering.

## `1x` ownership re-derivation

```
grep -rln "WeeklyReport|주간.*리포트|weekly.*report" frontend/src --include=*.tsx --include=*.ts
→ App.tsx (its own /__wave6/1x route registration only)
→ pages/WeeklyReportPreview/index.tsx (the stub itself)

grep -rn "weekly.report|WeeklyReport" backend/app/
→ no matches
```

Zero real Product Entry, Container, or navigation trigger exists anywhere
for `1x`, in either the frontend or backend. Recorded `DEFERRED_CONFIRMED_
BLOCKER` (`DESIGN_DECISION_REQUIRED`), counted in the Markpoint denominator
by data ownership since no other domain claims it either.

## `1k`/`1l`/`1s`/`2c`/`2h`/`2j` fixture-usage audit

```
grep -n "Fixture|fixture" platform/markpoint/MarkpointUser.tsx
```

Confirmed: fixtures used only for (a) genuinely static, disclosed,
non-real-data copy (`missionDetailFixture.photoNotice`/`.submitNotice`,
`missionRejectFixture.missionIcon`) and (b) load-before-ready fallback only
(`rewardShopFixture`/`rewardExchangeFixture` spread with real `balance`/
`rewards` values taking priority via `??`/ternary once loaded) — the same
established fixture-fallback-before-load pattern already used throughout
this codebase (Family/Profile pages), never a fallback that persists after
real data is available. No new fixture leakage found; none of these 6
files were modified this task.

## Known gaps (disclosed)

- `03-target-ui.spec.ts`/`04-w75-data-wiring.spec.ts` were not independently
  re-run end-to-end — their own required seeded accounts
  (`owner.a`/`admin.a`/`member.a`) are not present in this DB, and
  provisioning them requires the repository's own `phase1_seed_synthetic.py`,
  which performs a blanket `DELETE` across `Account`/`FamilyGroup`/
  `WagleRoom`/`MarkpointMission`/etc. — declined against the persistent dev
  DB per this task's own DB-safety constraints. The DOM contract those
  specs depend on (the real weekly day-list) is preserved by 0-diff
  non-modification, confirmed via `git diff`, not by a fresh spec run.
- `1k`/`1l`/`1s`/`2c`/`2h`/`2j` were not independently re-exercised live
  this task (no mission/reward data was seeded for that level of testing);
  their preservation rests on the 0-diff confirmation plus the pre-existing
  disclosed comments already in their own source, re-read and re-confirmed
  this task.

## Final Declaration

- Verification: `DEVELOPER_SELF_CHECK_COMPLETE` / `INDEPENDENT_QA_PENDING`.
- Not a self-declared Independent QA PASS.
- No product/backend/migration/seed/policy/KST-UTC/Auth/Family/Admin/Wagle
  change of any kind. No commit/push/merge/rebase performed.
