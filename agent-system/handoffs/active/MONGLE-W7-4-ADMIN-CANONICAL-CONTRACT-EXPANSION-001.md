# Handoff — MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001

- Task ID: MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001

## Origin

Opened directly by PM as the resolution task for the 3 screens
(`2e`, `2i`, `2l`) `MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001`
deferred after discovering their frozen canonical mockups could not carry
the real product's own richer functionality. PM's explicit decision:
Option 1 -- expand the canonical contracts to absorb the real
functionality losslessly, rather than deleting real features or keeping
legacy/custom screens permanently parallel. PM also directed: if no
existing common component fits a need, assemble one by referencing
existing components; apply a real data grid to the grid area(s).

## Scope 1 — `2e` (미션 관리)

Re-verified the prior task's deferral evidence by direct source read of
`MissionView.tsx`, `WeeklyGrid.tsx`, `MissionCard.tsx`, `MissionCardEdit.tsx`,
`ProposedMissionSection.tsx`, `NewMissionModal.tsx`,
`TemplateManager.tsx`/`TemplateModal.tsx`/`ImportMissionModal.tsx`. New
`screens/admin/MissionManagement/` canonical Screen: typed
`stats`/`playerOptions`/`selectedPlayerId`/`selectedDate`/`filterStatus`/
`searchQuery`/`rows`/`canBulkApprove`/`loading`, plus two composition
slots (`weekGridSlot`, `proposedSlot`) for the two already-real,
already-styled sub-components this Screen deliberately does not
reimplement. New Screen-local `AdminDataGrid` common component (this
task's one extraction, assembled from this codebase's own existing
`CardDetailTable` table convention and `PlayerView`'s card-grid
convention) supplies the mission-row list's grid chrome; each row's
actual content stays `MissionCard`/`MissionCardEdit`, composed via
`renderRow`. `MissionView.tsx` rewritten as the Product Container: builds
the model, wires real `approveMission`/`rejectMission`/`deleteMission`/
`updateMission`/`undoComplete`/`createMission` (all pre-existing,
unchanged), and adds a genuinely new but zero-risk capability -- real
client-side status-filter/search over already-loaded missions (the frozen
mockup's own previously-decorative controls). `MissionManagementPreview`
rewritten to consume the canonical Screen; its old duplicate CSS module
deleted.

## Scope 2 — `2i` (보호자 대시보드)

Re-verified `DashboardView.tsx`'s own 6 real sections
(`PlayerStatusCard`/`BalanceSection`/`RecentAlerts`/`PendingMissionCard`/
`WeeklyActivityChart`/`MissionRanking`) plus the 4 canonical overlays
(1m/2m/2x/3b) the prior task already wired there. New
`screens/admin/ParentDashboard/` canonical Screen types the
low-risk-to-reimplement parts for real (`title`/`cycleLabel`/
`statCards`/`selectedStatCard`) and composes the 6 real sections plus a
detail panel and the overlay layer as named `ReactNode` slots -- the
charter's own explicitly-listed "children/slot 계약" strategy for exactly
this "real structure differs from frozen mockup" shape, the same shape
already open for `1b`/`1c`/`1d` under
`MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)` (cross-
referenced there). `DashboardView.tsx` rewritten to render
`ParentDashboardScreen` as its outer shell; every section/overlay passes
through as a slot, byte-identical to its prior JSX.
`ParentDashboardPreview` rewritten to consume the canonical Screen with
its own fixture plus two illustrative placeholder slots; old duplicate
CSS module deleted.

## Scope 3 — `2l` (미션 생성 폼)

Re-verified `NewMissionModal.tsx`'s real multi-assignee/quick-point/
date-mode/group_id-fan-out logic. Expanded `screens/admin/
MissionCreateForm/`'s existing (pre-this-session) canonical Screen: typed
multi-select `assignees`/`selectedAssigneeIds`, `quickPointOptions`,
`dateMode`/`todayLabel`/`tomorrowLabel`/`customDate`, `submitting`,
`canSubmit`, `validationMessage`; `onCreate` now carries a full typed
`MissionCreateFormSubmitPayload` instead of taking no arguments.
`NewMissionModal.tsx` rewritten as the Product Container: `AdminModal`
keeps its real chrome, body now renders `MissionCreateFormScreen(embedded)`;
the real `Promise.all` multi-assignee fan-out with shared `group_id`
orchestration is unchanged, now driven by the canonical Screen's single
typed payload. `description` (no real backend field) folded into the
submitted free-text `text` rather than left as a decorative no-op. The
frozen mockup's own always-non-functional "반복 주기" select (implying
false recurrence capability) was removed as a disclosed accuracy
correction, not a redesign -- the other decorative elements (미션 유형/
인증 사진 필수/보호자 승인 필요) were left exactly as they were.

## Scope 4 — Mid-task correction (self-caught)

An initial `2e` design typed the proposed-mission list directly into the
canonical model and reimplemented its card rendering inline, which would
have silently orphaned the real `ProposedMissionSection.tsx` component --
a near-miss against this task's own "기존 기능 손실 0" requirement.
Caught by a self-run `grep -rl "ProposedMissionSection"` before writing
this handoff (it returned only the component's own file, meaning nothing
imported it anymore). Corrected to a `proposedSlot` composition prop,
matching the `weekGridSlot` precedent already in the same file. Disclosed
in the QA evidence rather than silently smoothed over.

## Scope 5 — Matrix update (additive only, chained)

12 new columns (`W7_4_Expansion_Task` .. `Expansion_Evidence`) appended
for the 3 rows only. Per this task's own explicit instruction not to
overwrite the prior task's record, the 12 columns
`MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001` already wrote
for these same 3 rows (including its own `DEFERRED` verdict) are
preserved byte-unchanged -- this task's own result chains alongside it,
not over it. Verified via a Python `csv` round-trip diff across all 64
rows.

## Scope 6 — Validation

`pnpm run lint` PASS (0 findings), `pnpm run build` PASS (one pre-existing
chunk-size warning, unrelated), `git diff --check` clean on first attempt,
`check_all.py` report-only exit 0 with 0 new warnings attributable to this
task's lineage. Regression-safety `git diff --name-only` confirms zero
changes to every already-real component this task composes via slot/
renderRow (`WeeklyGrid.tsx`, `MissionCard.tsx`, `MissionCardEdit.tsx`,
`ProposedMissionSection.tsx`, `PlayerStatusCard.tsx`, `BalanceSection.tsx`,
`RecentAlerts.tsx`, `WeeklyActivityChart.tsx`). E2E/browser runtime **not
executed** -- same disclosed reason carried through this entire task
lineage (no local `backend/.venv`, no local PostgreSQL).

## Baseline integrity

```text
product code modified by this task:   frontend/src/screens/admin/
  MissionManagement/** (new, incl. Screen-local AdminDataGrid),
  frontend/src/screens/admin/ParentDashboard/** (new),
  frontend/src/screens/admin/MissionCreateForm/** (expanded, pre-existing
  files from an earlier session); frontend/src/pages/AdminDashboard/views/
  MissionView/MissionView.tsx (rewritten) + .module.css (deleted, unused);
  .../MissionView/components/NewMissionModal.tsx (rewritten) + .module.css
  (deleted, unused); frontend/src/pages/AdminDashboard/views/DashboardView/
  DashboardView.tsx (rewritten); frontend/src/pages/
  {MissionManagementPreview,ParentDashboardPreview}/index.tsx (rewritten,
  duplicate CSS modules deleted)
test code modified by this task:      0
migration/seed code modified:         0
backend code modified:                0
other Admin sub-domains touched:      0 (PointView/NotificationView/
  FeedbackView/ConfigView untouched, confirmed via diff)
other product domains touched:        0 (Auth/Markpoint/Family/Wagle
  untouched)
other worktree/repository touched:    0
real already-tested components touched: 0 (WeeklyGrid/MissionCard/
  MissionCardEdit/ProposedMissionSection/PlayerStatusCard/BalanceSection/
  RecentAlerts/WeeklyActivityChart all confirmed unchanged via diff)
governance/audit docs modified:       engineering/phase2/MONGLE_W7_4_LIVE_
  CONSUMER_INTEGRATION_AUDIT_MATRIX.csv (additive columns only), this
  handoff, its own QA evidence, the new implementation report, active.md,
  relay/current.md
git diff --check:                     clean
existing pre-session dirty state:     this session's own prior lineage
  output only (Wagle + Admin Wave 1 tasks' uncommitted changes), untouched
  by this task
commit/push/merge/rebase:             none performed
```

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: NO_CHANGE_REQUIRED
- COVERAGE MAP Reason: no test was executed or added by this task
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001.md

`CLOSEOUT GATE: PASS` means only that this task's own 4 documentation
obligations are synchronized -- it does NOT mean this task's own
substantive verdict is `PASS` (it is `CONDITIONAL`; see the report), and
it does NOT mean Admin integration overall is complete (`2o` remains its
own separate infra blocker), W7.5 overall is `PASS`, or W7.6 is unblocked.
W7.5 overall remains `CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`.

## Not independently measured / estimates disclosed

- No independent QA has yet reviewed this implementation.
- No live browser runtime session was run by this task.
- `AdminDataGrid`'s table-mode is implemented but has no real consumer in
  this task's own change set -- only its card-grid mode is exercised.

No commit, push, merge, or rebase was performed by this task.
