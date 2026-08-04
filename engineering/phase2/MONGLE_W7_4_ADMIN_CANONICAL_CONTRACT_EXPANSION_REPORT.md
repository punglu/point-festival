# MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001 — Implementation Report

```text
Verdict: CONDITIONAL
```

`CONDITIONAL`: all three PM-approved screens (`2e`, `2i`, `2l`) were fully
implemented — every real feature named in the prior task's deferral
(WeeklyGrid/templates/bulk-approval for `2e`; the 6 real dashboard
sections for `2i`; multi-assignee/quick-point/date-mode for `2l`) is now
represented in an expanded canonical contract and product-integrated,
with zero deletion of existing real functionality. Static validation
(lint/typecheck/build/`git diff --check`/`check_all.py`) is fully clean.
`CONDITIONAL` rather than `PASS` only because no browser/E2E runtime was
available in this session — the same disclosed gap carried by both prior
tasks in this lineage (Wagle, Admin Wave 1), not a new or larger gap.

## 1. Baseline

```text
Worktree: /Users/mac/mac_Project/mongle_ui
Branch:   dev-newmarkp
HEAD (start): 0319940ad452105ed512029b8260b5159d2a4815 (unchanged through this task)
Existing dirty at start: prior lineage output only (MONGLE-W7-4-WAGLE-
  SINGLE-SOURCE-PRODUCT-INTEGRATION-001 and MONGLE-W7-4-ADMIN-SINGLE-
  SOURCE-PRODUCT-INTEGRATION-001's own uncommitted changes, both this
  session's own prior work, neither reverted or restored)
Task-owned changes: see Section 9 (file list)
Commit/push/merge/rebase: none performed
```

## 2. PM Decision

```text
Affected screens: 2e, 2i, 2l
Option chosen:     Option 1 -- expand the canonical Screens' data/input/
                    behavior contract to fully absorb existing real
                    product functionality, without deleting anything or
                    keeping legacy/custom screens as a permanent parallel
                    consumer.
```

This report treats that decision as settled and does not re-litigate it.

## 3. Authority Readback

```text
Matrix:  engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv
Prior task: MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001 --
  its own report Section 6 ("newly-discovered blockers") is this task's
  starting point; its own deferral evidence (exact file names, exact
  contract mismatches) was independently re-verified by direct source
  read this session, not assumed still accurate.
Frontend Development Guide: engineering/FRONTEND_GUIDE.md -- consulted
  for placement (screen-local before feature-local before shared),
  colocation, and "judge a split by concerns/cohesion/real reuse, not
  line count."
```

## 4. Screen `2e` — 미션 관리

```text
Existing features (re-verified this session by direct source read):
  WeeklyGrid.tsx: real player x weekday matrix, self-fetching
    (/api/admin/weekly-summary), per-cell click-to-select, inline
    per-cell "전체 승인" bulk-approve button
  ProposedMissionSection.tsx: child-proposed missions, own card grid,
    real approve/reject
  MissionCard.tsx / MissionCardEdit.tsx: per-mission status-conditional
    actions (approve/reject/edit/edit-template/delete/undo) and inline
    edit form
  Action bar: player filter select, date input, import-from-history
    button, template-manager button (TemplateManager/TemplateModal/
    ImportMissionModal, all separate real modals)
  Standalone bulk-approve button (selectedPlayer + pending mission exists)

Previous contract gap: the canonical `2e` mockup was a single flat table
  (전체/활성/완료 tabs, search, edit/delete-only rows) with no
  representation at all for the weekly grid, templates, proposed-mission
  approval, or bulk approval -- a literal swap would have deleted all of
  the above.

Expanded contract: `MissionManagementModel` (stats/playerOptions/
  selectedPlayerId/selectedDate/filterStatus/searchQuery/rows/
  canBulkApprove/loading) + `MissionManagementProps` adds two composition
  slots (`weekGridSlot`, `proposedSlot`) for the two already-real,
  already-styled components (`WeeklyGrid`, `ProposedMissionSection`) that
  this Screen deliberately does NOT reimplement -- doing so would
  duplicate real business logic a Canonical Screen must never own (Section
  6.1's own "직접 fetch 금지" already rules out `WeeklyGrid`'s self-fetch
  living inside the Screen). The mission-row list uses a new,
  Screen-local `AdminDataGrid` component (this task's one common-component
  extraction) for its grid chrome, with each row's actual content supplied
  by the Product Container as `MissionCard`/`MissionCardEdit` -- identical
  to the slot strategy, just per-row instead of per-section.

Final product consumer: `MissionView.tsx` (Product Container). Renders
  `MissionManagementScreen` with `weekGridSlot={<WeeklyGrid .../>}` and
  `proposedSlot={<ProposedMissionSection .../>}`, both byte-identical to
  their pre-existing invocations.

Preserved behavior: 100% of the features listed above, confirmed via
  `git diff --name-only` showing 0 changes to `WeeklyGrid.tsx`,
  `MissionCard.tsx`, `MissionCardEdit.tsx`, or `ProposedMissionSection.tsx`.
  `TemplateManager`/`TemplateModal`/`ImportMissionModal` also unchanged,
  now triggered via the canonical Screen's `onOpenTemplates`/`onOpenImport`
  callbacks instead of directly-rendered buttons in the old ad hoc JSX.

Newly real (not required by PM, added because it was free and safe): the
  frozen mockup's own 전체/활성/완료 status tabs and 미션 검색 input --
  previously decorative in the mockup and absent entirely from the real
  product -- are now real, pure client-side filters over the
  already-loaded `regularMissions` array. Zero new API calls, zero risk to
  any mutation path. The 3 stat cards (전체 미션/진행 중/승인 대기) also
  now show real computed counts instead of the frozen fixture's static
  values.

Data grid: per the review direction to apply a real data grid to the
  grid area, `AdminDataGrid` (Screen-local, `screens/admin/
  MissionManagement/components/AdminDataGrid/`) provides the mission
  list's structural chrome (loading/empty state, responsive table-vs-
  card-grid layout) -- assembled by reference to this codebase's own
  existing `CardDetailTable`'s `<table>`+`data-label` mobile-responsive
  convention (see Section 8), not invented from scratch, and consumed
  with `renderRow` (card-grid mode) so `MissionCard`/`MissionCardEdit`'s
  real per-status logic renders unmodified inside it.

Tests: lint/typecheck/build only this pass -- see Section 10.
```

## 5. Screen `2i` — 보호자 대시보드

```text
Existing features (re-verified this session): DashboardView.tsx already
  composes 6 real, independently complex sections in this exact order:
  1. PlayerStatusCard   -- real player roster + today's mission/point summary
  2. BalanceSection      -- real per-child point-balance comparison chart
  3. RecentAlerts        -- real notification feed
  4. PendingMissionCard  -- real pending-approval preview (wired to the
                            real 1m approval queue by the prior task)
  5. WeeklyActivityChart -- real weekly completion chart
  6. MissionRanking      -- real completed-mission ranking, wired to the
                            real 3b filter overlay by the prior task
  Plus: header, real cycle banner, 4 real stat cards with click-to-expand
  detail panel (CardDetailTable + 2m/2x drill-in triggers), and the 4
  canonical overlays (1m/2m/2x/3b) the prior task already wired.

Previous contract gap: the canonical `2i` mockup modeled only a 2-column
  "오늘의 가족 활동"/"승인 대기" feed layout with 4 differently-labeled
  stat cards -- a strict visual subset that cannot represent 6 real
  sections plus 4 already-real overlay integrations without deleting them.

Expanded canonical composition: `ParentDashboardModel` types the simple,
  low-risk-to-reimplement parts for real (`title`, `cycleLabel`,
  `statCards: ParentDashboardStatCard[]`, `selectedStatCard`).
  `ParentDashboardProps` adds 6 named ReactNode slots
  (`playerStatusSlot`/`balanceSlot`/`alertsSlot`/`pendingMissionSlot`/
  `weeklyActivitySlot`/`rankingSlot`) plus `detailPanelSlot` and
  `overlaysSlot`. Per Section 8's own explicit guidance ("실제 구조가
  다르면 현재 코드를 따른다" / "children/slot 계약" is one of the four
  listed acceptable strategies), this is not a fallback to avoid
  reimplementation -- it is the charter's own named strategy for exactly
  this shape of real-vs-mockup mismatch, matching the same "real page
  richer than frozen mockup" pattern `MONGLE-W7-4-PRODUCT-STRUCTURE-
  INTEGRATION-001 (REOPENED)` already carries open for `1b`/`1c`/`1d`.

Final product consumer: `DashboardView.tsx`. Renders `ParentDashboardScreen`
  as its outer shell; each of the 6 sections and the overlay layer pass
  through as slots, each byte-identical to its pre-existing JSX.

Preserved behavior: `git diff --name-only` confirms 0 changes to
  `PlayerStatusCard.tsx`, `BalanceSection.tsx`, `RecentAlerts.tsx`,
  `WeeklyActivityChart.tsx`. `PendingMissionCard.tsx` and
  `MissionRanking.tsx` keep the exact prop contracts the prior task
  (`MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001`) already gave
  them, unmodified again by this task. All 4 canonical overlays (1m/2m/2x/
  3b) and `ActiveMissionDetailModal` render inside `overlaysSlot`,
  unchanged from the prior task's own wiring.

Tests: lint/typecheck/build only this pass -- see Section 10.
```

## 6. Screen `2l` — 미션 생성 폼

```text
Existing features (re-verified this session, from NewMissionModal.tsx):
  multi-player assignment (chip toggle group + "모두"), a shared group_id
  across the fan-out for later bulk-delete, quick-point buttons
  (POINT_QUICK_VALUES), today/tomorrow/custom date modes (real
  getLocalToday/shiftDay resolution), Promise.all real submission.

Previous contract gap: `MissionCreateFormModel` had `assignees: string`
  (one fixed pre-formatted name, not a real option list), no point-quick-
  select, no date mode, and `onCreate?: () => void` carried no payload at
  all -- structurally incapable of carrying a real multi-assignee/date-
  mode submission.

Expanded contract: `MissionCreateFormModel` gained
  `assignees: MissionCreateFormAssignee[]`, `selectedAssigneeIds: number[]`,
  `quickPointOptions: number[]`, `dateMode`, `todayLabel`/`tomorrowLabel`,
  `customDate`, `submitting`, `canSubmit`, `validationMessage`.
  `onCreate` now takes a typed `MissionCreateFormSubmitPayload`
  (`assigneeIds`/`title`/`description`/`point`/`dateMode`/`customDate`).
  The visual grammar (sidebar/content/columns/preview card, purple palette,
  radius, spacing) is unchanged -- the multi-select chips and quick-point/
  date-mode buttons reuse the same visual language as the frozen `.pills`/
  `.toggle` elements already in this Screen, not a new design system.

Final product consumer: `NewMissionModal.tsx`. `AdminModal` keeps owning
  the real overlay/title/close/Escape chrome it always did; its body now
  renders `MissionCreateFormScreen(embedded)`. The real multi-assignee
  fan-out (`Promise.all`, shared `group_id` when 2+ assignees) stays in
  the Container, driven by the single typed payload the canonical Screen
  emits on submit -- the canonical Screen still never calls the API.

Disclosed adapter decisions (not silent redesign):
  - `description` has no separate field in the real `Mission` schema
    (only free-text `text`). Rather than becoming a decorative no-op, it
    is folded into the submitted `text` when non-empty
    (`"{title} - {description}"`) -- a real use of the schema's existing
    free-text field, not a fabricated capability.
  - The frozen mockup's own "반복 주기" select (a single static "매일"
    option, never wired to anything, and this create flow has no
    recurrence concept -- recurrence is handled entirely by the separate
    Template system reachable from `2e`'s own "반복미션 관리" button) was
    removed. This is disclosed as a deliberate accuracy correction, not
    a redesign: keeping a static, always-non-functional control that
    implies false recurrence capability alongside three newly-real
    controls in the same form was judged a correctness risk worth fixing
    while already touching this exact form.
  - "미션 유형" pills, "인증 사진 필수" toggle, "보호자 승인 필요" toggle
    all remain exactly as pre-existing decorative elements -- unchanged,
    not wired, not removed (none of the three PM-approved feature bundles
    for `2l` name them).

Tests: lint/typecheck/build only this pass -- see Section 10.
```

## 7. Common Components

```text
Extracted: AdminDataGrid (frontend/src/screens/admin/MissionManagement/
  components/AdminDataGrid/) -- table-mode (columns) or card-grid mode
  (renderRow), following this codebase's own existing detailTable +
  data-label mobile-responsive convention (CardDetailTable.tsx), not
  invented from scratch, per this task's own direction to reference and
  assemble from existing components. Placed Screen-local (not Admin-
  feature-local or global shared) because it currently has exactly one
  real consumer (2e's mission row list) -- per the Frontend Development
  Guide's own placement table ("local-first; promote only after a second
  actual consumer") and Section 9's own priority order (Screen-local
  first).
Reused: WeeklyGrid, ProposedMissionSection, MissionCard, MissionCardEdit,
  PlayerStatusCard, BalanceSection, RecentAlerts, WeeklyActivityChart,
  PendingMissionCard, MissionRanking, TemplateManager, TemplateModal,
  ImportMissionModal -- all composed via slots/renderRow, none modified.
Kept local: `toDetailModel`-equivalent adapters (the `model`/`dashboardModel`
  `useMemo` blocks in MissionView.tsx/DashboardView.tsx) -- each has
  exactly one real consumer.
Rejected extraction candidates: a shared "embedded overlay" wrapper (the
  near-identical `position:fixed` CSS rule duplicated across
  DashboardModal.module.css's `.overlay`, PlayerView's `.detailOverlay`,
  DashboardView's `.overlay`) was flagged again (first flagged by the
  prior task) but still not extracted -- below the "real duplication
  reduction" bar once weighed against the risk of touching 3 already-real
  modal stacking contexts for a purely cosmetic consolidation, and out of
  this task's own PM-approved scope (2e/2i/2l only).
```

## 8. AdminDataGrid design rationale (assembly, not invention)

Per this task's own direction ("기존 컴포넌트가 없다면 기존 컴포넌트
참조해서 조립"), `AdminDataGrid` was assembled from two already-real
patterns already present in this codebase rather than designed from a
blank slate:

```text
Table mode CSS:  copies CardDetailTable.module.css's own <table> +
  data-label mobile-responsive convention (thead hidden below 640px,
  td::before renders attr(data-label)) verbatim in structure, not
  literally shared (CSS Modules stay page/screen-colocated per the
  Frontend Development Guide), so the visual language matches without a
  cross-module CSS dependency.
Card-grid mode:  auto-fill minmax(280px,1fr) grid, matching the same
  responsive pattern PlayerView.module.css's `.grid` already established
  for player cards.
```

Only the card-grid mode is actually consumed this task (`2e`'s mission
list, via `renderRow`); table mode exists in the component's own contract
for the next real consumer that needs strict tabular columns, but is not
exercised by any file this task touches -- built because it cost nothing
extra as part of the same small component, not spec-padding.

## 9. Single-Source Validation

```text
Product -> canonical (3 screens): MissionView/DashboardView/
  NewMissionModal import MissionManagementScreen/ParentDashboardScreen/
  MissionCreateFormScreen directly
Preview -> canonical (3 screens): MissionManagementPreview/
  ParentDashboardPreview/MissionCreateFormPreview each render the
  canonical Screen with fixture data (+ placeholder slot content for 2i,
  since its 6 real sections are legitimately absent from a Detached
  Preview -- same precedent as 2e's weekGridSlot being omitted, an
  optional prop the Screen already handles as absent)
Product -> Preview import: 0 (grep-verified across all 3 touched Preview
  pages)
Duplicate legacy/canonical consumer: 0 -- the old ad hoc JSX inside
  MissionManagementPreview/ParentDashboardPreview and the old
  MissionCreateFormScreen's single-select/no-payload contract were all
  replaced in the same change, not left as a second copy
Retired legacy source: frontend/src/pages/MissionManagementPreview/
  MissionManagementPreview.module.css and frontend/src/pages/
  ParentDashboardPreview/ParentDashboardPreview.module.css deleted (0
  remaining references, confirmed via grep before deletion).
  frontend/src/pages/AdminDashboard/views/MissionView/MissionView.module.css
  and .../components/NewMissionModal.module.css also deleted -- both
  became fully unused once their own top-level markup moved into the
  canonical Screen/slots (confirmed via grep: 0 references anywhere,
  before deletion)
```

## 10. Validation

```text
lint:              PASS (pnpm run lint, exit 0, 0 findings)
build:              PASS (pnpm run build = tsc -b && vite build; same
                   pre-existing >500kB chunk-size warning as both prior
                   tasks, unrelated to this task's files)
tests:              NOT EXECUTED
detached preview:  statically reviewed only (Section 9)
git diff --check:  PASS (clean on first attempt; the Matrix CSV script
                   reused `lineterminator='\n'` from the start, matching
                   the fix the Wagle task had to apply after the fact)
check_all.py:       report-only, exit 0; all WARNING lines pre-date this
                   task (verified: none reference this Task ID or its
                   files)
Regression-safety grep: git diff --name-only confirms 0 changes to
                   WeeklyGrid.tsx, MissionCard.tsx, MissionCardEdit.tsx,
                   ProposedMissionSection.tsx, PlayerStatusCard.tsx,
                   BalanceSection.tsx, RecentAlerts.tsx,
                   WeeklyActivityChart.tsx -- every real, already-tested
                   component this task composes via slot/renderRow was
                   independently confirmed untouched, not merely assumed
```

Runtime/E2E was not executed for the identical, already-disclosed reason
carried through this entire task lineage: no local `backend/.venv`, no
local PostgreSQL available in this session.

## 11. Documents

```text
Created: engineering/phase2/MONGLE_W7_4_ADMIN_CANONICAL_CONTRACT_
  EXPANSION_REPORT.md (this file)
Created: agent-system/qa/MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001.md
Created: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-CANONICAL-
  CONTRACT-EXPANSION-001.md
Updated: engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_
  MATRIX.csv -- 12 new additive columns (W7_4_Expansion_Task ..
  Expansion_Evidence), populated for the 3 expanded rows only. All 12
  columns the prior Admin task added (W7_4_Implementation_Task ..
  Implementation_Evidence, including its own DEFERRED verdict for 2e/2i/
  2l) are preserved byte-unchanged, per this task's own explicit
  instruction not to overwrite the prior task's record -- this expansion
  chains from it rather than replacing it. All write-once historical
  columns (Primary_Classification .. Implementation_Readiness) verified
  unmodified for all 64 rows via a Python csv round-trip diff.
Updated (minimal): agent-system/active.md, agent-system/relay/current.md
COVERAGE_MAP.md: NO_CHANGE_REQUIRED -- no test was executed or added by
  this task
```

## 12. State After Task

```text
2e: IMPLEMENTED (product-integrated, single-source, all real functionality preserved)
2i: IMPLEMENTED (product-integrated, single-source, all 6 real sections preserved)
2l: IMPLEMENTED (product-integrated, single-source, real multi-assign/
    quick-point/date-mode creation flow)
Admin integration:            IN PROGRESS -> the 3 screens this task's own
                               PM Decision covers are now fully resolved
                               (0 remaining Admin blockers of this kind);
                               2o remains its own separate, genuine
                               infrastructure blocker (no policy API
                               exists), unchanged, out of this task's scope
W7.4 overall integration:      IN PROGRESS (Auth/Markpoint/Family
                               untouched, per this task's own scope)
W7.5 overall:                   CONDITIONAL / HUMAN_GATE (unchanged)
W7.6:                           BLOCKED (unchanged)
```

## 13. Next Recommended Domain

```text
MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001 (or the domain the
next Matrix re-derivation actually shows the most implementation-ready,
blocker-free screens for -- an unverified guess, not confirmed here)
```

A close second: focused runtime/E2E re-verification across this entire
W7.4 lineage (Wagle + Admin Wave 1 + this expansion) once a Postgres/
backend runtime is available in-session -- three consecutive `CONDITIONAL`
verdicts for the identical disclosed reason is now the single largest gap
between this lineage's own developer self-check and an actual PASS.

## Allowed final declarations actually supported by this task's evidence

```text
MONGLE_W7_4_ADMIN_CANONICAL_CONTRACT_EXPANSION_CONDITIONAL
ADMIN_2E_EXISTING_FEATURES_CANONICALLY_INTEGRATED
ADMIN_2I_SIX_SECTION_DASHBOARD_CANONICALLY_INTEGRATED
ADMIN_2L_FULL_CREATION_FLOW_CANONICALLY_INTEGRATED
ADMIN_EXISTING_PRODUCT_BEHAVIOR_PRESERVED
ADMIN_CANONICAL_SINGLE_SOURCE_PRESERVED
W7_4_PRODUCT_INTEGRATION_REMAINS_IN_PROGRESS
W7_5_OVERALL_REMAINS_CONDITIONAL_HUMAN_GATE
W7_6_REMAINS_BLOCKED
```

Not declared: `MONGLE_W7_4_ADMIN_CANONICAL_CONTRACT_EXPANSION_PASS` --
withheld solely because runtime/E2E verification remains pending, exactly
as `PASS` was withheld from the two prior tasks in this lineage for the
same reason.

No commit, push, merge, or rebase was performed by this task.
