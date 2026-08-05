# MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Closeout Contract: v1
- Kind: Developer Agent implementation task — re-derive the Markpoint
  domain's full canonical denominator from current code (not keyword
  search), verify `1x`'s real ownership, and single-source every
  implementation-ready Markpoint screen into the real product. Same lineage
  as the Wagle/Admin/Auth/Family single-source integration tasks above.

## Environment (measured, this session, continuation of the Auth/Family tasks)

- WSL2, no Docker. Node v26.2.0 / pnpm 10.32.1. Python 3.12.3,
  `backend/.venv`, uvicorn 0.34.0, native PostgreSQL 16 (`mc_festival`).
- Runtime: the same `./dev.sh` stack already running from the prior tasks
  this session, not restarted.
- Branch `dev-newmarkp`, HEAD unchanged at `97bc09d…` throughout (no commit
  performed by any task this session).
- `accounts`/`family_groups` measured empty (0 rows) at task start.

## Markpoint domain boundary (re-derived, not a keyword search)

`find frontend/src/screens/markpoint -maxdepth 1 -type d`: **6 pre-existing**
canonical Screen directories (`ExchangeConfirm`/`LevelUp`/`MissionDetail`/
`MissionReject`/`RewardExchange`/`RewardShop`), each cross-checked against
the 64-row Matrix by its own `Canonical_Screen_ID` (`2h`/`2c`/`1k`/`1s`/
`1l`/`2j`). `1c` (포인트 잔치, the domain's root screen) had **no** such
directory — its own Preview (`PointFestivalPreview`) was a static `ui-only`
page never extracted into the `screens/*` pattern, the same shape the Auth
task found for `1j`/`1j-1` and the Family task found for `1b`. Extracting
it this task brings the total to **7**.

**`1x` (주간 리포트) — investigated per this task's own instruction not to
classify by data content alone**: `grep`-confirmed zero real Product Entry,
Container, or navigation trigger exists anywhere in the frontend or backend
for it — only its own `/__wave6/1x` preview route and the static preview
file itself. Its content (points/missions/level badge) is genuinely
Markpoint-shaped *data*, but no domain (Markpoint, Family, Admin, or
otherwise) actually owns a real *screen/navigation/container* for it. Per
this task's own instruction to separate those four ownership axes rather
than collapse them, `1x` is counted in the Markpoint denominator by data
ownership (no other domain claims it either) but correctly deferred —
`DESIGN_DECISION_REQUIRED`, matching its own pre-existing Matrix
classification, not reopened or force-implemented.

**Markpoint denominator: 8** — `1c`, `1k`, `1l`, `1s`, `2c`, `2h`, `2j`,
`1x`.

## `1c` (포인트 잔치) — root screen, same pattern as Family Home

`/markpoint` (`platform/markpoint/MarkpointUser.tsx`) is a real, carefully-
reasoned 550-line page (its own docblock is explicit about never re-deriving
a balance or mission status client-side, and about keeping spendable
`current_balance` visually separate from EXP-input `lifetime_earned` — "a
child's level appearing to fall when they spend points" is a named,
deliberately-avoided defect class). The canonical `1c` Screen's frozen
visual (header/profile-card + week-picker + family cheer-message cards +
a single selected-day mission list + a one-row point-history summary)
overlaps only *part* of the real page's own structure (3 stat cards +
a full always-expanded weekly day-list + a full deductions list + 6 real
overlay flows for mission detail/reject, level-up, and 3 reward flows).

### Resolution: header + profile-card only, not a full replacement

Two real constraints, found by direct evidence before writing any layout
code, ruled out adopting the canonical Screen's own week-picker/cheer/
mission-list/history zones into the Product:

1. **No backend "family cheer message" capability exists anywhere** —
   confirmed by reading every Markpoint API client function. Rendering the
   frozen visual's own 2 example cheer messages in the real product would
   be fabricating user-authored content, not a numeric placeholder.
2. **A committed E2E spec already has a DOM contract on the real weekly
   list** — `tests/e2e/specs-mongle/03-target-ui.spec.ts` asserts
   `markpoint-weekly-days` is an `<ol>` with `> li` children (≥7, every
   cycle day always expanded, never a single selected day), a
   `[data-today="true"]` marker, and a `[data-testid^="submit-mission-"]`
   button per active mission. The canonical Screen's own week-picker is a
   single-selected-day picker — a structurally different contract. Reading
   this spec **before** touching the layout (not after breaking it) is
   what caught this.

Resolution: composed only the canonical Screen's header + profile-card
zones (`showWeeklySection={false}`, a new prop added to the Screen's own
contract precisely for this) into `MarkpointUser`'s ready state, real-data-
bound (level, progress, lifetime_earned/next_threshold, today_earned,
remaining_missions, current_balance, real `accountDisplayName`). The
existing real weekly day-list, deductions list, and all 6 overlay blocks
(mission detail, mission reject, level-up, reward shop, reward exchange,
exchange confirm) are **byte-identical to before** — confirmed by diff —
just no longer sitting under the old ad hoc header/3-card layout. The two
real header entry points the frozen visual had no slot for (보상 교환 /
리워드샵 buttons, plus the 레벨업 축하 trigger and 4 sub-stats the old
4-stat card carried) were relocated into their own small real row directly
below the canonical zone — same test-ids, same handlers, same behavior,
just repositioned.

The Preview (`/__wave6/1c`) renders the **full** canonical Screen (all
zones, its own fixture, `showWeeklySection` defaults `true`) — it remains
the single, complete, standalone reproduction of the frozen `1c` visual;
only the Product's own composition chooses to consume a subset of it.

### Real bug found and fixed during composition

While verifying real runtime rendering, the header's own logout button
rendered at 144×48px and squeezed the adjacent title/subtitle text into a
21px-wide column that wrapped one Korean character per line. Root-caused to
two compounding issues, both pre-existing in the original `PointFestival
Preview.module.css` (carried over verbatim during extraction, not
introduced by this task):

1. `font: 700 12px/normal inherit` is invalid CSS — the `font` shorthand's
   final component must be a real font-family value, and `inherit` is only
   valid as the *entire* shorthand's value, not one part of a mixed
   declaration. Browsers silently drop an invalid shorthand declaration
   entirely, so this rule never actually set a font-size at all.
2. With no font-size winning from this rule, an unrelated, pre-existing,
   **unscoped** `header button { ...; font-size: 24px; }` element selector
   from a *different* stylesheet elsewhere in this repository (CSS Modules
   only scopes class/id selectors, not bare element selectors, so such a
   rule leaks globally onto every `<header><button>` in the whole app) won
   uncontested.

Fixed with real longhand CSS properties (`font-family: inherit; font-size:
12px; font-weight: 700; line-height: normal;`) plus a strengthened
`.header .logout` selector (specificity 0,2,0, reliably beating the leaking
0,0,2 element selector regardless of source order) — both changes confined
to this task's own new `PointFestivalScreen.module.css`; no other
stylesheet in the repository was touched. This bug was latent and harmless
in the original, never-live-wired Preview (nobody had reason to pixel-check
a small header button on a page nothing consumed); it only became visible
and actively harmful once this task composed the Screen into a real,
tested product context.

## `1k`/`1l`/`1s`/`2c`/`2h`/`2j` — already real, re-confirmed not re-implemented

A grep across `MarkpointUser.tsx` for `screens/markpoint/*` imports found
all 6 already imported and rendered as real overlays, each with a docblock
comment already disclosing its own exact real-vs-static boundary. Direct
source read this task confirmed, not merely trusted:

- `1k` (미션 상세): title/reward/description/checklist real
  (`own_weekly_detail`); photo-evidence notice stays static copy — no
  file-storage abstraction exists anywhere in the backend (same
  infrastructure gate as `2v`/`2z`), disclosed, not fabricated.
- `1l`/`2j` (보상 교환/리워드샵): rewards/cost/availability real (reward
  catalog API), balance real.
- `1s` (미션 반려): reviewer/reason real (`own_weekly_detail`).
- `2c` (레벨업 축하): level/levelTitle real; `bonusPoints: 0` and the
  manual-only trigger (no automatic level-up event exists — no backend
  push support) are both disclosed, intentional absences — no level-up
  bonus mechanic exists anywhere in the Ledger/mission pipeline
  (grep-confirmed by a prior task, re-confirmed unchanged here), a real
  economy/business-rule decision out of this task's authority, not a
  wiring gap to close.
- `2h` (교환 확인): real redemption endpoint, real balance-after
  calculation, failure surfaces via `redeemError`, never silently closes.

None of these 6 were modified. `Product_Entry_Test`/`Responsive_Test`/
`Detached_Regression` are recorded `NOT_RE_EXECUTED` for these 6 in the
Matrix — confirmed unchanged by diff, not independently re-run this task.

## Files changed

- `frontend/src/screens/markpoint/PointFestival/**` (new): `types.ts`,
  `PointFestivalScreen.tsx`, `PointFestivalScreen.module.css` (zones minus
  the bottom dock, plus the two CSS fixes above), `pointFestival.fixture.ts`,
  `index.ts`.
- `frontend/src/pages/PointFestivalPreview/{index.tsx,
  PointFestivalPreview.module.css}` — rewritten to consume the extracted
  Screen (full, `showWeeklySection` default), dock kept preview-local.
- `frontend/src/platform/markpoint/MarkpointUser.tsx` — header/3-card zone
  replaced by the canonical Screen (`showWeeklySection={false}`); reward-
  entry buttons + level-up trigger + 4 sub-stats relocated into their own
  real row (same test-ids/handlers); weekly day-list, deductions list, and
  all 6 overlay blocks byte-identical to before.
- `engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv`
  — additive columns for the 8 Markpoint rows only, chained after the
  existing Wagle/Admin/Auth/Family columns.
- `agent-system/qa/COVERAGE_MAP.md` — one new row,
  `FE-W7-4-MARKPOINT-POINT-FESTIVAL-SINGLE-SOURCE-001`.
- `agent-system/active.md`, `agent-system/relay/current.md` — this task's
  own entries.
- This handoff and its QA evidence file.

## Database — additive-only, fully cleaned up

Same protocol as the Family task: `mc_festival`'s account/family tables
were empty at start; a disposable, INSERT-only synthetic Account +
FamilyGroup + FamilyMembership + owner role + active Markpoint subscription
+ credential was created for real-login verification (never the
repository's own blanket-delete `phase1_seed_synthetic.py`), then removed
via ID-scoped `DELETE`s in FK-safe order (including `AccountSession` rows
created by the login itself). Final independently re-queried counts: all
tables `0`. `git status --short backend/` confirmed clean throughout.

## Validation

- `pnpm run lint` — clean.
- `pnpm run build` (`tsc -b && vite build`) — clean.
- `git diff --check` — clean.
- `git status --short` — matches the file list above exactly.

## Runtime verification (executed)

- Real login (disposable synthetic account, active Markpoint subscription)
  → `/markpoint`: canonical header/profile rendered with real (honest
  zero-state) data; `markpoint-balance`/`markpoint-level`/`markpoint-
  remaining` test-ids present, exact-text-verified against the same
  contract `03-target-ui.spec.ts` asserts; reward-shop overlay opened
  correctly; canonical header's own real logout button cleared the session
  and navigated to `/`; 0 console/page errors.
- 3-viewport check (390×844/820×1180/1180×820) on both the real Product
  entry and the Preview: 0 horizontal overflow at any size.
- `/__wave6/1c` (Preview) independently re-checked: still renders the
  **full** canonical Screen (week-picker 7 days, 1 cheer-message section,
  3 missions) via its own fixture, unaffected by the Product's
  `showWeeklySection={false}` composition.

Not executed: the committed `03-target-ui.spec.ts`/`04-w75-data-wiring.
spec.ts` suites were not run end-to-end against the properly-seeded
`owner.a`/`admin.a`/`member.a` synthetic accounts (running the repository's
own seed script that provisions them requires a blanket `DELETE` this task
declined to run against the persistent dev DB — see Database section
above). Instead, this task verified by construction: the weekly day-list/
deductions/overlay JSX those specs depend on is **0-diff unchanged**
(confirmed via `git diff`), so their existing DOM contract is preserved by
not having been touched, not re-proven by a fresh run. The specific
test-ids those specs also assert on the *new* canonical zone
(`markpoint-balance`/`-level`/`-remaining`) were independently verified live
against real data this task, with exact-text matching where the spec
requires it. Flagged as a disclosed gap, not silently skipped.

## Independent QA

Not performed by this task (implementer does not self-award QA PASS, per
`agent-system/rules.md` Invariant 6).

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md

The four fields above are the documentation-synchronization obligations
only — narrower than Lifecycle `COMPLETED`, PM approval, graduation, or a
later independent verification pass's own separate verdict; see
`Verification` in `active.md`'s own entry for this task, deliberately left
at `DEVELOPER_SELF_CHECK_COMPLETE`/`INDEPENDENT_QA_PENDING`.

## Unverified / estimated values (explicit)

- The committed E2E suites (`03-target-ui.spec.ts`/`04-w75-data-wiring.
  spec.ts`) were not independently re-run this task, for the reason
  disclosed above (their own required seeded accounts are absent from this
  DB, and provisioning them via the repository's own script would require a
  blanket delete this task declined to perform against the persistent dev
  DB). Their DOM contract is preserved by non-modification, not re-proven
  by execution.
- `1k`/`1l`/`1s`/`2c`/`2h`/`2j`'s own runtime/responsive checks were not
  independently re-executed this task (recorded `NOT_RE_EXECUTED`, not
  `PASS`, in the Matrix) — their preservation claim rests on 0-diff
  confirmation, not a fresh live exercise of each overlay.

## Next Action

Awaiting PM review and a focused Independent QA pass — ideally including an
actual run of `03-target-ui.spec.ts`/`04-w75-data-wiring.spec.ts` in an
environment where the proper seeded synthetic accounts can be provisioned
without a blanket-delete risk (e.g. a genuinely isolated/disposable
database, as `tests/README.md` already specifies for other Markpoint test
runs). `1x` remains open pending a genuine PM/design decision on whether
and where a weekly-report feature should be surfaced — no new decision item
introduced by this task. W7.6 remains out of this task's scope, untouched.
No backend/migration/policy/KST-UTC/Auth/Family/Admin/Wagle change of any
kind. No commit/push/merge/rebase performed.
