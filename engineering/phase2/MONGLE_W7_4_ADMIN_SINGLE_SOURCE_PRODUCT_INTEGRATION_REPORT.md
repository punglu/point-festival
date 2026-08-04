# MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001 — Implementation Report

```text
Verdict: CONDITIONAL
```

`CONDITIONAL`: static validation (lint/typecheck/build/`git diff --check`/
`check_all.py`) is clean and every implementation-ready Admin screen with
no genuine blocker was implemented (5/8), but (a) no browser/E2E runtime
was available in this session — same disclosed gap as the prior Wagle
task, not re-litigated here — and (b) 3 screens (`2e`, `2i`, `2l`), all
carrying `READY_FOR_LEGACY_REPLACEMENT` in the Matrix, were found during
actual implementation to have a real structural conflict between their
frozen canonical mockup and materially richer, already-real Admin
functionality; forcing either would have violated this Task's own
"preserve existing behavior" / "don't replace real API with fixture/mock"
prohibitions, so they were deferred with precise evidence instead.

## 1. Baseline

```text
Worktree: /Users/mac/mac_Project/mongle_ui
Branch:   dev-newmarkp
HEAD (start): 0319940ad452105ed512029b8260b5159d2a4815 (unchanged through this task)
Existing dirty at start: this session's own prior Wagle task output only
  (MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001, already
  committed to no branch, still uncommitted working-tree changes) — no
  dirty state from any other task or session
Task-owned changes: see Section 9 (file list)
Commit/push/merge/rebase: none performed
```

## 2. Authority Readback

```text
Matrix:  engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv
Report:  engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_REPORT.md
QA/handoff: MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001 and its
  CONDITIONAL-CLOSEOUT-REMEDIATION-001 companion; the prior
  MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001 report/QA/handoff
  (for pattern precedent: `embedded` prop convention, additive Matrix
  columns, disclosed-gap style)
```

Admin target derivation method: filtered the current Matrix CSV (via
`csv.DictReader`) for rows whose any field mentions `AdminDashboard` or
`/admin`, case-insensitive — not a fixed ID list. This surfaced **10**
rows: `1m, 2a, 2e, 2i, 2l, 2m, 2o, 2t, 2x, 3b`.

## 3. Admin Target Set

| ID | Screen | Canonical Source | Implementation Readiness (write-once, preserved) | This Task Action |
| --- | --- | --- | --- | --- |
| `1m` | 미션 승인 | MissionApprovalPreview | `READY_FOR_LEGACY_REPLACEMENT` | **CREATE_MINIMAL_PRODUCT_CONTAINER** |
| `2a` | 사용자 관리 상세 | UserManagementDetailPreview | `READY_FOR_LEGACY_REPLACEMENT` | **CREATE_MINIMAL_PRODUCT_CONTAINER** |
| `2e` | 미션 관리 | MissionManagementPreview | `READY_FOR_LEGACY_REPLACEMENT` | **DEFER_CONFIRMED_BLOCKER** (newly discovered) |
| `2i` | 보호자 대시보드 | ParentDashboardPreview | `READY_FOR_LEGACY_REPLACEMENT` | **DEFER_CONFIRMED_BLOCKER** (newly discovered) |
| `2l` | 미션 생성 폼 | MissionCreateFormPreview | `READY_FOR_LEGACY_REPLACEMENT` | **DEFER_CONFIRMED_BLOCKER** (newly discovered) |
| `2m` | 미션 상세 폼 | MissionDetailFormPreview | `READY_FOR_WIRING` | **MERGE_CANONICAL_INTO_EXISTING_CONTAINER** |
| `2o` | 포인트 정책 편집 | PointPolicyEditorPreview | `INFRASTRUCTURE_PREREQUISITE_REQUIRED` | `DEFER_CONFIRMED_BLOCKER` (unchanged) |
| `2t` | 관리자 알림 발송 | AdminNotificationSendPreview | `ALREADY_COMPLETE` | `PRESERVE_AND_REGRESSION_TEST` |
| `2x` | 미션 통계 대시보드 | MissionStatisticsDashboardPreview | `READY_FOR_LEGACY_REPLACEMENT` | **MERGE_CANONICAL_INTO_EXISTING_CONTAINER** |
| `3b` | 미션 통계 필터 | MissionStatisticsFilterPreview | `READY_FOR_WIRING` | **ADAPT_EXISTING_LOGIC_TO_CANONICAL** |

```text
Admin canonical denominator:              10
ALREADY_COMPLETE:                         1  (2t)
READY_FOR_LEGACY_REPLACEMENT:             6  (1m, 2a, 2e, 2i, 2l, 2x)
READY_FOR_PARTIAL_INTEGRATION_COMPLETION: 0
READY_FOR_WIRING:                         2  (2m, 3b)
DESIGN_DECISION_REQUIRED:                 0  (per original Matrix; 3
                                              newly reclassified this
                                              session — see Section 6)
POLICY_DECISION_REQUIRED:                 0
INFRASTRUCTURE_PREREQUISITE_REQUIRED:     1  (2o)
NO_IMPLEMENTATION_REQUIRED:               0
Sum: 10 (matches denominator)

Implemented this Task:  5  (1m, 2a, 2m, 2x, 3b)
Deferred (pre-existing infra blocker, unchanged): 1  (2o)
Deferred (newly-discovered structural conflict):  3  (2e, 2i, 2l)
```

Every screen that was `READY_FOR_LEGACY_REPLACEMENT` / `READY_FOR_WIRING`
with **no real blocker found in code** was implemented (5/8 net of the 3
genuinely conflicted). No implementation-ready screen was left unprocessed
without a documented reason.

## 4. Implemented Screens

### `1m` — 미션 승인 (CREATE_MINIMAL_PRODUCT_CONTAINER)

```text
Previous consumer: none (no dedicated approval queue existed anywhere;
                    PendingMissionCard previewed the top 4 pending items
                    with zero actions, "전체 보기" only navigated away)
Final consumer:     DashboardView -> PendingMissionCard "전체 보기" ->
                    MissionApprovalScreen (embedded overlay)
Canonical source:   frontend/src/screens/admin/MissionApproval/
                    MissionApprovalScreen.tsx (new extraction, mirrors the
                    Wagle FamilyChat pattern: model+callbacks, embedded
                    prop suppresses the frozen preview's own duplicate
                    admin sidebar)
Preserved behavior: PendingMissionCard's own preview list/count badge
                    untouched; its "전체 보기" trigger's destination
                    changed from a page navigation to an actionable queue,
                    which is what the button's own label already promised
Real wiring:        approve/reject call useAdminData's existing
                    approveMission/rejectMission (already-used real
                    mutations, no new API); stat counts (승인 대기/오늘
                    승인/오늘 반려/지급 예정 포인트) computed from
                    already-loaded missions/players, no fabricated numbers
Tests:              lint/build/typecheck only this pass (Section 8)
Evidence:           frontend/src/screens/admin/MissionApproval/**,
                    frontend/src/pages/MissionApprovalPreview/index.tsx,
                    DashboardView.tsx, PendingMissionCard.tsx
```

### `2a` — 사용자 관리 상세 (CREATE_MINIMAL_PRODUCT_CONTAINER)

```text
Previous consumer: none (PlayerProfileCard already showed most real data
                    inline as a compact card; no expanded detail view)
Final consumer:     PlayerView -> PlayerProfileCard "상세보기" (new
                    button) -> UserManagementDetailScreen (embedded)
Canonical source:   frontend/src/screens/admin/UserManagementDetail/
                    UserManagementDetailScreen.tsx (new extraction)
Preserved behavior: PlayerProfileCard's existing PIN-change/photo-change/
                    lock-toggle/visibility-toggle/delete actions all
                    untouched, unchanged signatures
Real wiring:        completedMissionsLabel, lastActiveLabel, recentMissions
                    (top 5 by updated_at), roleLabel, isActive all real,
                    derived from already-loaded players/missions.
                    onToggleLock calls the same real adminApi.lockPlayer
                    path PlayerProfileCard already used
Disclosed gaps:     보유 포인트 / 누적 획득 / 교환 횟수 / 레벨 / 가입일 /
                    알림 / 보호자 승인 render as "—" — none of these
                    fields exist on the Admin `Player`/`Mission` API
                    response today (confirmed by direct type-file read,
                    not assumed); exposing them would require a Backend
                    DTO change, forbidden by this Task's own scope. Labels
                    and cell positions kept exactly as the frozen mockup
                    (visual baseline unchanged) — only the values are
                    honestly placeholder rather than fabricated numbers
Tests:              lint/build/typecheck only this pass
Evidence:           frontend/src/screens/admin/UserManagementDetail/**,
                    frontend/src/pages/UserManagementDetailPreview/index.tsx,
                    PlayerView.tsx, PlayerProfileCard.tsx
```

### `2m` — 미션 상세 폼 (MERGE_CANONICAL_INTO_EXISTING_CONTAINER)

```text
Previous consumer: ActiveMissionDetailModal (a real, working, but entirely
                    custom row-list component under a misleading code
                    comment claiming canonical 2m was "wired to a real
                    trigger here" -- direct code read showed it never
                    actually imported or rendered MissionDetailFormScreen
                    at all; that comment was inaccurate, corrected in
                    place)
Final consumer:     ActiveMissionDetailModal row click -> canonical
                    MissionDetailFormScreen (embedded)
Preserved behavior: The modal's own player-tab + date-grouped list
                    untouched; no existing behavior removed
Real wiring:        onDelete now calls the real adminApi.deleteMission
                    (this modal previously had no delete action at all,
                    a genuine capability addition, not a regression) then
                    reload() via a new onChanged prop
Disclosed gap:      onSave is a no-op close. The frozen contract's
                    `onSave?: () => void` carries no payload at all --
                    title/description/points/assignee render via
                    uncontrolled `defaultValue` inputs with no onChange --
                    so there is no field for a real save to write back,
                    matching this codebase's own established precedent for
                    other frozen-form gaps (2z/3f/3g/3k/3l all disclosed
                    identically rather than fabricating input wiring the
                    frozen visual doesn't support)
Evidence:           frontend/src/screens/admin/MissionDetailForm/**,
                    ActiveMissionDetailModal.tsx, DashboardView.tsx
```

### `2x` — 미션 통계 대시보드 (MERGE_CANONICAL_INTO_EXISTING_CONTAINER)

```text
Previous consumer: none (DashboardView's own stat cards/ranking already
                    covered this conceptually but no dedicated drill-in
                    existed)
Final consumer:     DashboardView -> "이번 주기 진행률" card detail panel
                    -> "미션 통계 대시보드 보기" -> canonical
                    MissionStatisticsDashboardScreen (embedded)
Real wiring:        completion/active reuse DashboardView's own already-
                    computed stats.cycleRate/stats.totalActiveMissions;
                    points is a real sum of completed-mission points
                    within the cycle range (from already-loaded
                    missions); members[] is real per-child-player
                    completion % within the cycle. No new statistics
                    engine was built -- every number is a reuse or a
                    one-line derivation of data DashboardView already had
                    loaded. "기간 필터" button reopens the existing 3b
                    filter overlay (shared state, not duplicated)
Evidence:           frontend/src/screens/admin/MissionStatisticsDashboard/**,
                    DashboardView.tsx
```

### `3b` — 미션 통계 필터 (ADAPT_EXISTING_LOGIC_TO_CANONICAL)

```text
Previous consumer: DashboardView already triggered this canonical overlay,
                    but onApply was a structural no-op (disclosed in the
                    Matrix's own Gap_Summary: "no dedicated filter state
                    exists")
Final consumer:     same trigger, now real
Real wiring:        가족 구성원 select is now a real, controlled <select>
                    bound to `MissionRanking`'s own existing player-filter
                    state, lifted from local to a shared controlled prop
                    (MissionRanking's real filtering behavior is
                    unchanged, just now also reachable from this overlay
                    instead of only its own inline PlayerTab). 미션 상태
                    (전체/완료/진행 중) converted from static, non-
                    interactive `<b>` labels to real toggle `<button>`s;
                    '진행 중' computes a real parallel ranking from
                    already-loaded active missions (a one-line reuse of
                    the same grouping logic useAdminData already applies
                    to completed missions -- not a new backend capability)
Disclosed gap:      기간 (period) select stays a single, disabled option
                    ("최근 30일") -- no real date-range API exists; this
                    was already true before this Task and remains true,
                    disclosed rather than silently dropped from the
                    layout
Evidence:           frontend/src/screens/admin/MissionStatisticsFilter/**,
                    DashboardView.tsx, MissionRanking.tsx
```

## 5. `2t` — Regression-reviewed, not modified

`AdminNotificationSendScreen` inside `NotificationView.tsx` was confirmed
still real and unchanged (`git diff --name-only` shows 0 changes to either
file). No action needed per Section 7's `PRESERVE_AND_REGRESSION_TEST`.

## 6. Newly-discovered blockers (`2e`, `2i`, `2l`)

All three were `READY_FOR_LEGACY_REPLACEMENT` in the Matrix — the original
audit's own `Recommended_Next_Action` for each was "verify against
AdminDashboard [View]," which this Task did, by direct code read (not
assumed). In all three cases, the real Admin container turned out to have
materially richer functionality than the frozen canonical mockup models,
and the frozen mockup's own callback contracts carry **no payload at all**
(`onCreate?: () => void`, uncontrolled `defaultValue` inputs) — the exact
same shape already disclosed elsewhere in this Matrix for other frozen
forms (2z, 3f/3g/3k/3l). A literal swap in any of these three cases would
either delete real, already-relied-upon capability or require redesigning
the frozen visual to add missing affordances (multi-select, a richer
dashboard layout) — both explicitly outside this Task's authority (Section
20: "PM Decision 임의 확정," "디자인 baseline 임의 변경" both forbidden).

```text
2e (미션 관리):
  Real MissionView already provides: WeeklyGrid (per-cell bulk approve),
  action bar (player+date filter, import, add, template management),
  ProposedMissionSection, and per-card approve/reject/edit/delete/undo via
  MissionCard/MissionCardEdit. Canonical mockup: a status-tab
  (전체/활성/완료) + search + edit/delete-only table, with no equivalent
  for any of the above. Currently completable without a decision: none —
  the table visual itself cannot host the real grid's richer per-mission
  actions without either omitting them (regression) or redesigning the
  frozen table row (baseline change). Blocked exactly at: reconciling
  which of MissionView's real capabilities the canonical table is meant
  to replace vs. keep alongside.
  Preserved: MissionView.tsx completely untouched.

2i (보호자 대시보드):
  Real DashboardView already provides 6 real sections (PlayerStatusCard,
  BalanceSection, RecentAlerts, PendingMissionCard, WeeklyActivityChart,
  MissionRanking) plus the 4 canonical overlays this Task wired (1m/2m/
  2x/3b). Canonical 2i mockup: a simpler 2-stat-card + 2-column
  activity/approval-feed layout — a strict visual subset of what
  DashboardView already renders. This is the identical shape already
  raised for 1b/1c/1d by `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001
  (REOPENED)` and left to PM, not resolved by this Task's own Wagle
  predecessor. Blocked exactly at: whether PM wants DashboardView's real,
  richer composition kept as the de facto single source for 2i's
  conceptual scope (my recommendation, given no functionality would need
  to be deleted), or the simpler frozen visual enforced instead.
  Preserved: no reduction to DashboardView; all of this Task's own
  additions to it (1m/2m/2x/3b wiring) are purely additive overlays.

2l (미션 생성 폼):
  Real NewMissionModal supports multi-player assignment (shared
  group_id for later bulk-delete), quick-point buttons, and
  today/tomorrow/custom date modes. Canonical MissionCreateFormScreen:
  single "담당 자녀" (one fixed option only), no date-mode, decorative
  "미션 유형" pills with no backend concept, `onCreate` no-arg. Blocked
  exactly at: real multi-assign/date-mode creation cannot flow through a
  contract with no field-carrying callback and no multi-select affordance
  without either deleting those real capabilities or adding new visible
  UI to the frozen mockup.
  Preserved: NewMissionModal.tsx completely untouched.
```

## 7. Common Components

```text
Extracted (new): MissionApproval, UserManagementDetail — both follow the
  established embedded-prop pattern (frozen preview's own decorative
  sidebar suppressed only in Product; Preview default unchanged)
Reused: none new — MissionDetailForm/MissionStatisticsDashboard/
  MissionStatisticsFilter already existed from a prior session; this Task
  widened their prop contracts (embedded, value/players, real onApply
  payload) rather than re-extracting them
Kept local: adapter functions (toFamilyChatMessages-equivalents:
  toMissionDetailFormModel, toDetailModel, approvalModel/statsDashboardModel
  useMemo blocks) — each has exactly one real consumer, no extraction
  warranted
Rejected extraction candidates: a shared "embedded modal overlay" wrapper
  was considered (DashboardModal.module.css's .overlay, PlayerView's
  .detailOverlay, and DashboardView's .overlay are near-duplicates) but
  NOT extracted this pass -- 3 near-identical `position:fixed` CSS rules
  is below this Task's own "2+ consumer, real duplication reduction" bar
  once weighed against the risk of touching 3 already-real modal stacking
  contexts for a purely cosmetic consolidation; left as a flagged future
  candidate, not silently deferred
```

## 8. Single-Source Validation

```text
Product -> canonical (5 screens): DashboardView/PlayerView import each
  Screen directly from screens/admin/**
Preview -> canonical (5 screens): each *Preview/index.tsx reduced to a
  model-only wrapper (2 of the 5 -- MissionApproval, UserManagementDetail
  -- were rewritten from raw duplicate markup this Task, mirroring the
  Wagle FamilyChatPreview precedent; the other 3 were already thin
  wrappers from a prior session)
Product -> Preview import: 0 (grep-verified across all 5 touched Preview
  pages: each imported only by App.tsx's own /__wave6/* route)
Duplicate legacy/canonical consumer: 0 for the 5 implemented screens (old
  duplicate markup + duplicate CSS module deleted in the same change for
  1m/2a, matching the Wagle 1d precedent)
Retired legacy source: frontend/src/pages/MissionApprovalPreview/
  MissionApprovalPreview.module.css and frontend/src/pages/
  UserManagementDetailPreview/UserManagementDetailPreview.module.css
  deleted (0 remaining references, confirmed via grep before deletion)
```

## 9. Behavior Regression (code-review basis; Section 11 discloses what
   was not runtime-executed)

```text
auth/permission:  untouched -- no AdminProtectedRoute/get_current_admin
                   path touched by any change in this Task
API:               only already-existing calls reused (adminApi.
                   deleteMission, adminApi.lockPlayer via the existing
                   handleToggleLock path, useAdminData's approveMission/
                   rejectMission/listParticipants-equivalent) -- 0 new
                   endpoints
state:             MissionRanking's player-filter state lifted from local
                   to controlled-with-local-fallback (verified: omitting
                   the new props preserves the exact old behavior, so any
                   other hypothetical consumer of MissionRanking is
                   unaffected -- grep confirms DashboardView is its only
                   consumer)
mutation:          approveMission/rejectMission/deleteMission/lockPlayer
                   all pre-existing, unchanged signatures
navigation:        PendingMissionCard's "전체 보기" no longer navigates to
                   /admin/missions -- intentional (Section 4), the
                   destination route itself (MissionView) is untouched and
                   still reachable via the sidebar
modal/overlay:     all 4 new/changed overlays (1m/2m/2x/3b) follow the
                   same position:fixed pattern already used by the
                   pre-existing showStatsFilter overlay; 0 z-index
                   collisions introduced (verified: all use the existing
                   .overlay/.detailOverlay classes at the same stacking
                   context depth as before)
```

## 10. Screen Tests

```text
component/unit: none exist for Admin views in this repository today (no
                 *.test.*/*.spec.* under frontend/src/pages/AdminDashboard/**)
                 -- none added this pass, same disclosed trade-off as the
                 prior Wagle task given the runtime-provisioning gap
route:           N/A -- none of the 5 implemented screens are dedicated
                 routes; all are modal/overlay entries within existing
                 Admin routes, verified via direct code read of each
                 trigger's render chain
focused E2E:     NOT EXECUTED this pass -- see Section 11
viewport results: NOT EXECUTED this pass -- see Section 11
```

## 11. Validation

```text
lint:              PASS (pnpm run lint, exit 0, 0 findings)
build:              PASS (pnpm run build = tsc -b && vite build; same
                   pre-existing >500kB chunk-size warning as the Wagle
                   task, unrelated to this Task's files)
tests:              NOT EXECUTED
detached preview:  statically reviewed only (see Section 8) -- 5 preview
                   pages read and confirmed still render correctly with
                   `embedded` defaulting to falsy, not runtime-executed
git diff --check:  PASS (clean; the Matrix CSV edit reused the LF-only
                   writer discipline established by the Wagle task, so no
                   CRLF/trailing-whitespace regression this time)
check_all.py:       report-only, exit 0; all WARNING lines pre-date this
                   Task (none reference MONGLE-W7-4-ADMIN-SINGLE-SOURCE-
                   PRODUCT-INTEGRATION-001)
```

Runtime/E2E was not executed for the identical, already-disclosed reason
as the prior Wagle task: no local `backend/.venv`, no local PostgreSQL,
and the fixed native-E2E resource ports were confirmed idle (not
contended) rather than attempted-and-blocked. Standing up a local
Postgres/Python environment from scratch remains judged out of a single
Developer session's reasonable scope without explicit operator
confirmation.

## 12. Documents

```text
Created: engineering/phase2/MONGLE_W7_4_ADMIN_SINGLE_SOURCE_PRODUCT_
  INTEGRATION_REPORT.md (this file)
Created: agent-system/qa/MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-
  INTEGRATION-001.md
Created: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-SINGLE-SOURCE-
  PRODUCT-INTEGRATION-001.md
Updated: engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_
  MATRIX.csv -- the same 12 additive columns the Wagle task introduced,
  now also populated for the 10 Admin rows (Wagle's 7 rows untouched by
  this edit). Primary_Classification/Confidence/Final_Classification/
  Final_Confidence/Implementation_Readiness (write-once) unmodified for
  all 64 rows, verified by CSV round-trip diff
Updated (minimal): agent-system/active.md, agent-system/relay/current.md
COVERAGE_MAP.md: NO_CHANGE_REQUIRED -- no test was executed or added by
  this Task, same reasoning as the Wagle task
```

## 13. State After Task

```text
Admin integration:            IN PROGRESS -> 5/8 implementation-ready
                               Admin screens now product-integrated (1m,
                               2a, 2m, 2x, 3b); 1 pre-existing infra
                               blocker unchanged (2o); 3 newly-discovered
                               structural conflicts deferred with evidence
                               (2e, 2i, 2l), none silently skipped
W7.4 overall integration:      IN PROGRESS (Wagle: implementation
                               complete, runtime pending. Admin: this
                               Task's own state above. Auth/Markpoint/
                               Family: untouched, per this Task's own
                               scope)
Wagle runtime verification:    PENDING (unchanged from the prior task --
                               not re-executed or re-assessed by this
                               Admin-scoped Task)
W7.5 overall:                   CONDITIONAL / HUMAN_GATE (unchanged)
W7.6:                           BLOCKED (unchanged)
```

## 14. Remaining Blockers

| Screen ID | Blocker type | Required decision/prerequisite | Preserved behavior |
| --- | --- | --- | --- |
| `2o` | INFRASTRUCTURE_PREREQUISITE_REQUIRED (pre-existing) | No policy API exists in the backend | `PointView.tsx` untouched |
| `2e` | DESIGN_DECISION_REQUIRED (newly discovered) | Reconcile canonical table-row contract vs. real WeeklyGrid/template/bulk-approve/undo capability set | `MissionView.tsx` untouched |
| `2i` | DESIGN_DECISION_REQUIRED (newly discovered) | Confirm whether DashboardView's real, richer composition stands as 2i's de facto single source, or the simpler frozen visual is enforced (same open question as 1b/1c/1d) | `DashboardView.tsx`'s pre-existing sections untouched (only additive overlays added) |
| `2l` | DESIGN_DECISION_REQUIRED (newly discovered) | Reconcile single-assignee/no-date-mode frozen contract vs. real multi-assign/quick-point/date-mode capability | `NewMissionModal.tsx` untouched |

## 15. Next Recommended Domain

```text
MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001 (or the domain the
next Matrix re-derivation actually shows the most implementation-ready,
blocker-free screens for -- Auth is a reasonable next guess given it
hasn't been scoped by either this or the Wagle task, but should be
re-verified against the Matrix at that Task's own start, not assumed here)
```

A close second recommendation: bring the newly-discovered `2e`/`2i`/`2l`
blockers to PM for the same kind of scope decision `MONGLE-W7-4-PRODUCT-
STRUCTURE-INTEGRATION-001 (REOPENED)` already owns for `1b`/`1c`/`1d` --
these may belong under that same reconciliation umbrella rather than a
fresh domain sweep.

## Allowed final declarations actually supported by this Task's evidence

```text
MONGLE_W7_4_ADMIN_SINGLE_SOURCE_PRODUCT_INTEGRATION_CONDITIONAL
ADMIN_IMPLEMENTATION_READY_SCREENS_PRODUCT_BOUND (5/8 net of 3 newly-
  discovered conflicts; 5/5 of the blocker-free set)
ADMIN_CANONICAL_SINGLE_SOURCE_PRESERVED (for the 5 implemented screens)
ADMIN_EXISTING_FUNCTIONAL_BEHAVIOR_PRESERVED (by code review; not
  runtime-confirmed; and specifically preserved BY DEFERRING rather than
  regressing for 2e/2i/2l)
W7_4_PRODUCT_INTEGRATION_REMAINS_IN_PROGRESS
W7_5_OVERALL_REMAINS_CONDITIONAL_HUMAN_GATE
W7_6_REMAINS_BLOCKED
```

Not declared, because not supported: `ADMIN_PRODUCT_ENTRY_VERIFIED` (no
runtime), `W7_4_ADMIN_INTEGRATION_COMPLETE` (3 screens genuinely
undecided, not merely unstarted).

No commit, push, merge, or rebase was performed by this task.
