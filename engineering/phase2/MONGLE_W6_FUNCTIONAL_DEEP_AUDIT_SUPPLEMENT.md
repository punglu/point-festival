# MONGLE_W6_FUNCTIONAL_DEEP_AUDIT_SUPPLEMENT

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 13. Read-only supplement to 6.0B's `NOT_VERIFIED`
items (`FUNCTIONAL_CONTRACT_MATRIX.md`, `SCREEN_COMPONENT_GAP_MATRIX_V2.md`). No product code modified —
confirmed via `git status --short`/`git diff --stat` scoped to `frontend/src` and `tests/` (empty both,
re-checked after this reading pass).

## A. UserDashboard (`/dashboard`, maps to A3 Markpoint / `1c` 포인트잔치)

Full read: `frontend/src/pages/UserDashboard/hooks/useDashboard.ts` (282 lines).

- **Hook structure**: single `useDashboard()` hook, 8 `useEffect` blocks, all API-triggered effects use
  `AbortController` with cleanup (`return () => controller.abort()`) — confirms CLAUDE.md's own
  "AbortController cleanup 필수" rule is followed here, not just documented.
- **Data flow**: `selectedDate` + `player` drive the primary day-data load
  (`missions`/`cheers`/`feedbacks`/`deductions`/`dailyPoint`); a separate cycle-summary load keys off
  `pointCycle` (loaded once from `app_configs`, defaults `'weekly'` on failure); total-earned reloads
  whenever `dailyPoint` changes (points-just-changed signal, not a poll).
- **Mutation**: `requestApproval`, `proposeMission`, `sendFeedback`, `sendReply` — each is a direct
  `dashboardApi` call followed by `refreshData()` (no optimistic update, no AbortController on these —
  correctly so, since they're user-initiated single-shot actions, matching CLAUDE.md's stated exception
  ("폼 제출 API 호출에도 signal 전달 필수" applies to *forms*; these are already-committed mutations, not
  form submits under race risk from re-renders).
- **Derived state**: `myProposals`/`activeMissions`/`totalDeducted`/`totalAllocated`/`pendingPoints` are
  computed inline every render (not memoized) — a Wave 6.1 concern only if profiling shows it matters,
  not a correctness issue.
- **Loading/error**: single boolean `loading`; errors are `console.error`-only, no user-facing error UI
  state distinguishable from "still loading" — **confirmed gap**, `NOT_VERIFIED` in 6.0B is now
  `CONFIRMED_GAP`: this hook has no error-state contract for the tablet Screen Spec to preserve, meaning
  a tablet A3 error-zone would be new UI, not a preserved one.
- **Responsive dependency**: zero. Nothing in this hook reads `window.innerWidth`/`matchMedia` — layout
  entirely delegated to CSS, which is exactly what Section 2's "same component, breakpoint-only CSS
  adaptation" principle requires and confirms this hook needs **zero changes** for a tablet A3 build.
- **Functions the tablet visual reconstruction must preserve**: date navigation (`quickDate`), the 3-tab
  UI state (`missions`/`proposal`/`feedback`), the ranking nav toggle (`activeNav`), and the
  config-driven sender list (`senders`, with a hardcoded 2-parent fallback) — the tablet `1c` screen's
  "가족 응원 메시지" zone (Delta Matrix) must bind to this same `senders`/cheer data shape, not invent a
  new one.

## B. AdminDashboard / PointView (maps to A5 Admin Point / `1e` 관리자 포인트 관리)

Full read: `frontend/src/pages/AdminDashboard/hooks/useAdminData.ts` (129 lines), `useCycle.ts` (40
lines, not fully excerpted here — confirmed it's the same cycle-range utility 6.0AB's
`P-HOTFIX-CYCLE-INTEGRITY-001` pattern in CLAUDE.md describes), `useAdminAuth.ts` (21 lines).

- **Hook structure**: `useAdminData()` composes `useCycle()` + `useAdminToast()`, single
  `loadDashboardData(signal)` callback loading players/missions/notifications in parallel, then a
  per-player `Promise.all` for cycle-ranged daily points (N+1 request pattern — **confirmed**, not
  previously measured in 6.0B: for P players this issues 1 + P requests per load, a real but currently
  non-blocking scale concern, not relevant to Wave 6.1 visual work).
- **Mutation with dialog**: `approveMission`/`rejectMission` — real API calls
  (`adminApi.updateMissionStatus`), toast feedback, triggers `reload()`. This **confirms** 6.0B's
  headline claim ("A5 already exceeds its own approved-source depiction with working edit/delete
  dialogs") at the hook level, not just the component level.
- **Filter/permission**: no client-side permission branching visible in this hook (RBAC is enforced
  route-level via `AdminProtectedRoute`/`get_current_admin`, per CLAUDE.md §12 — this hook trusts the
  route guard, does not re-check role).
- **Table state**: `stats` (derived counts/rates) and `missionRanking` (top-8 completed-mission text
  grouped by player) are both computed inline from `missions`/`players` state — **this is exactly the
  shape the tablet A5 transaction table and stat-card row need to bind to** (Delta Matrix: 4 stat cards +
  5-column table match `stats` + a per-row mission/player join, not a new data shape).
- **Responsive dependency**: zero, same finding as UserDashboard — confirms Wave 6.1 A5 tablet work is
  CSS/layout-only for this hook.
- **Lazy Init side-effect**: `POST /api/mission-templates/generate` fired on every AdminDashboard mount,
  errors silently swallowed (`.catch(() => {})`) — not previously documented in 6.0B, flagged as a minor
  undocumented side-effect (not a correctness bug, but should be named explicitly in
  `MONGLE_W6_SCREEN_SPEC_FREEZE.md`'s A5 "preserved functions" list so a tablet rebuild doesn't drop it).

## C. Legacy spec assertion bodies (`tests/e2e/specs/`, 4 files, 107 lines total)

Full read: `01-login.spec.ts` (18), `02-mission.spec.ts` (29), `03-admin.spec.ts` (26), `04-flow.spec.ts`
(34).

- **Assertion style, confirmed by direct read of `02-mission.spec.ts`**: CSS-class-substring locators
  (`page.locator('[class*="missionList"]')`), URL-pattern assertions (`toHaveURL(/dashboard/)`),
  existence/visibility checks (`toBeVisible`), and one either-or count assertion
  (`hasMissions + hasEmptyMsg > 0`). **Zero pixel/layout/color/font assertions found** — corroborates
  6.0B's `E2E_COVERAGE_MAP_V2.md` claim ("Zero current tests assert on any approved-design visual
  property") with a second, independent read rather than trusting the prior claim blindly.
- **Login flow encoded in the spec**: player-card click → 4-digit PIN button sequence → URL redirect to
  `/dashboard`. This is the **only** place this session found the exact PIN-entry interaction pattern
  confirmed against live (if currently non-runnable) test code, useful evidence for A1's PIN screens
  (`1j`) beyond the static HTML.
- **Why currently unrunnable**: confirmed via `git status`/structure check, not re-run — `playwright.config.ts`
  (`tests/e2e/`) references `docker-compose.phase0.yml`, absence already confirmed by 6.0B (D12). Not
  re-verified by executing Docker this session (forbidden — no Docker was started).
- **Obsolescence assessment**: none of the 4 files' assertions are semantically obsolete relative to
  current routes (`/dashboard`, `/admin`) — they still target the right screens conceptually. They are
  **infra-blocked, not content-stale**. Recommendation carried to Implementation Sequence Freeze: these
  are candidates for **conversion to visual-regression assertions** once D12 is resolved and Wave 6.1
  screens exist, not for deletion.

## D. Accessibility

- **Sparse but non-zero, confirmed by direct grep + read**: only 6 of 74 `.tsx` files under
  `UserDashboard`/`AdminDashboard` use any `aria-*`/`role` attribute (grep count: 9 occurrences total).
  `NOT_VERIFIED` in 6.0AB is now `CONFIRMED_SPARSE`, not `CONFIRMED_ABSENT`.
- **Best-practice example found this session** (outside Admin/UserDashboard, but same repo, directly
  relevant to A4): `DoranLanding.tsx` — `aria-label` on the conversation `<section>` and message list,
  `role="list"`/`role="listitem"` on the room list, `aria-labelledby` linking the page heading. This is
  the **strongest accessibility pattern found anywhere in the audited code** and should be the reference
  pattern (not UserDashboard/AdminDashboard's sparser style) when Wave 6.1 builds new tablet DOM for
  A2–A5.
- **Landmark/heading order**: not systematically traced across all screens this session (would require a
  full per-page audit) — remains `NOT_VERIFIED_WITH_REASON: audit scope did not extend to a full
  landmark/heading-order trace across all current pages` for UserDashboard/AdminDashboard specifically.
- **Keyboard/focus/dialog/live-region**: `NOT_VERIFIED_WITH_REASON: requires interactive testing (real
  browser + keyboard simulation), out of this read-only session's method` — same limitation 6.0AB already
  disclosed, not newly resolved.
- **Responsive reading order**: per the Delta Matrix, zero DOM-duplication candidates were found across
  A2–A5's landscape/portrait pairs — meaning reading order is CSS-only-adaptable for every zone measured,
  a positive accessibility signal (no divergent DOM trees to keep in sync) though not itself proof that
  current *reading order* is already correct.

## E. A4 (`DoranLanding.tsx`, `/wagle`) — deepened beyond 6.0B

Full read: 267 lines (previously only referenced by grep/line-number in 6.0B).

- **Confirms D6 exactly**: `doranPreviewRooms` carries `GROUP`/`DIRECT`/`SERVICE` `kind` values; `SERVICE`
  rooms are rendered read-only (`isReadOnly = room.kind === 'SERVICE'`, no composer, explicit Korean
  notice "서비스 알림은 읽기 전용입니다."). This is 100% fixture data (`../doran/preview`), zero calls to
  any `doranApi`/live endpoint anywhere in this file — corroborates 6.0B's single largest flagged risk
  verbatim.
- **Confirms D7 exactly, including its own self-referential code comment**: lines 153-158 contain the
  *exact* comment 6.0B quoted ("Desktop split view는 첫 진입 시 기본 대화가 선택된 상태가 기본이다(§3 PM
  정책)"), plus additional undocumented detail not in 6.0B: the auto-select is gated by a `didAutoSelectRef`
  that fires **exactly once**, only after `pageState` first becomes `'normal'` (i.e., after family-context
  async load resolves), and explicitly does not re-fire if the user manually returns to the room list —
  this nuance should be preserved verbatim if D7 Option A ("confirm as intended") is chosen; a naive
  tablet reimplementation could easily break the "exactly once" guarantee.
- **Compose is fully simulated**: `handleSend` sets `pending`, then a hardcoded `window.setTimeout(...,
  500)` **always** transitions to `'failed'` with a manual retry button — there is no code path in this
  file that ever reaches a `'sent'` state. This is a stronger, more specific confirmation of "fixture-only,
  no live backend" than 6.0B's file-existence check alone provided.
- **Width-based branching, confirmed exact number**: `window.matchMedia('(min-width: 701px)')` — this is
  the literal, already-shipped desktop/mobile split point in current code, **useful as one input** (not
  the sole authority — Section 12 Item 4 remains `PM_DECISION_REQUIRED`) toward resolving the tablet CSS
  breakpoint question, since it shows the product's own prior, already-approved-enough-to-ship threshold.

## Verdict for this Gate

All items above are either `EVIDENCE_BACKED` (this session's own file reads, cited by path/line) or
explicitly `NOT_VERIFIED_WITH_REASON`. No code was modified to produce this audit. No item was marked
resolved by inference alone.
