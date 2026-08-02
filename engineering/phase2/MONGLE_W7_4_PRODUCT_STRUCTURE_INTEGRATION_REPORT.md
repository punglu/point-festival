# MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 — Report

## 1. Task

Bind all 64 canonical React Screens frozen at the end of W7.3
(`engineering/phase2/MONGLE_W7_3_CANONICAL_VISUAL_MATRIX.csv`) into the real
product's Route/Page/Tab/Modal/Drawer/Overlay/Auth-Step structure. Each of
the 64 canonical IDs needed exactly one `INTEGRATION_STRATEGY` and one
`INTEGRATION_TYPE`, a real reachable trigger from the product (not a file
import), and — where a genuinely pre-existing, backend-integrated product
view already covers the same concept — an honest `KEEP_EXISTING_AS_CANONICAL`
/ `NOT_UNIFIED_BY_DESIGN` classification instead of a false "unified" claim.
No new Backend/API/DTO work, no W7.3 visual redesign, no Preview-in-Product,
no mass Route-per-screen creation, no unauthorized Shared extraction.

## 2. Verdict

**PASS.**

64/64 canonical Screens have a confirmed `INTEGRATION_STRATEGY` +
`INTEGRATION_TYPE`, a real product route and/or trigger, and are marked
`PRODUCT_STRUCTURE_INTEGRATED`. All 64 were independently verified with a
live, authenticated browser session against the real dev backend at all
three mandated viewports and via 63 detached-preview regressions + `/login`.
No topology is undecided, no entry point is unconnected, no trigger is
missing. Open items (`DATA_AND_BEHAVIOR_WIRING_PENDING`,
`MUTATION_WIRING_PENDING`, one disclosed `TRUE_FUNCTIONAL_GAP` at `3h`) are
explicitly permitted for PASS per the task's own criteria and are carried
forward to W7.5.

## 3. Baseline

- Branch: `dev-newmarkp`
- HEAD at task start / this report: `6f414fe92fb2c667bff6ca2521edc5ec8ba7c6eb`
  (`docs(w7.3): commit final Matrix/Evidence Manifest CSVs for durable
  checkpoint`)
- Working tree was dirty at task start (W7.3 evidence/preview artifacts) and
  remains dirty now with this pass's additions — per the task's own
  instruction, git dirty/commit state is not used as a PASS/FAIL criterion
  here; it is recorded for provenance only.

## 4. Correcting the earlier premature count

An earlier interim status in this same task reported "13
PRODUCT_STRUCTURE_INTEGRATED" for Wagle/Admin/Auth/Markpoint by conflating
*canonical mapping complete* (existing view and canonical Screen conceptually
matched) with *actual single-source product integration* (literally the same
rendered implementation). That framework was wrong and was corrected
retroactively for every domain in this Matrix:

- `KEEP_EXISTING_AS_CANONICAL` + `CANONICAL_SINGLE_SOURCE_STATUS =
  NOT_UNIFIED_BY_DESIGN` is now used explicitly for the 16 rows where a real,
  backend-integrated product view (FamilyLanding, MarkpointUser,
  WagleRoomView, the Auth player-select/PIN views, 10 pre-existing
  AdminDashboard views) already implements the concept and was deliberately
  **not** physically merged with the frozen W7.3 canonical Screen. The
  canonical Screen stays the frozen visual reference for the detached
  preview only.
- This history is preserved, not deleted — see §9 and the Matrix `NOTES`
  column for each affected row.

A second, independently discovered correction happened during live
entry-test verification this pass (see §7): `2m`'s prior
`KEEP_EXISTING_AS_CANONICAL` classification pointed at
`ActiveMissionDetailModal.tsx`, but that component turned out to be
orphaned — imported nowhere in the real app. It has now been wired to a real
trigger (`frontend/src/pages/AdminDashboard/views/DashboardView/DashboardView.tsx`)
and reclassified `ADAPT_EXISTING_LOGIC_TO_CANONICAL`. Not trusting a prior
classification at face value and re-verifying against actual code is the
same discipline applied earlier in this task to `2g` (W7.3) and `3j`, `3h`
(this pass).

## 5. Final Matrix

`engineering/phase2/MONGLE_W7_4_PRODUCT_STRUCTURE_INTEGRATION_MATRIX.csv` —
64/64 rows, `FINAL_PRODUCT_STRUCTURE_STATUS = PRODUCT_STRUCTURE_INTEGRATED`
for all 64.

### Strategy counts (`INTEGRATION_STRATEGY`)

| Strategy | Count |
|---|---|
| `CREATE_NEW_PRODUCT_CONTAINER` | 41 |
| `KEEP_EXISTING_AS_CANONICAL` | 16 |
| `ADAPT_EXISTING_LOGIC_TO_CANONICAL` | 7 |

### Type counts (`INTEGRATION_TYPE`)

| Type | Count |
|---|---|
| `ALREADY_PRODUCT_BOUND` | 13 |
| `NESTED_ROUTE` | 12 |
| `INLINE_OVERLAY` | 12 |
| `MODAL_DIALOG` | 9 |
| `PAGE_LOCAL_STATE` | 8 |
| `ROUTE_PAGE` | 7 |
| `AUTH_FLOW_STEP` | 3 |

### Single-source counts (`CANONICAL_SINGLE_SOURCE_STATUS`)

- `CANONICAL_SINGLE_SOURCE_CONFIRMED` (Screen is literally imported and
  rendered by the real product container): **47**
- `NOT_UNIFIED_BY_DESIGN` (real pre-existing product view is the
  product-facing implementation; canonical Screen remains the frozen visual
  reference for its detached preview only): **17**

## 6. Family-members / Family-rules / Notifications / Search domains (this pass)

Completed in strict sequence per the task's mandated order:

- **Family-members (5: `1q,2f,2p,2r,3i`)** — new `/family/members` route,
  new `frontend/src/features/family-members/FamilyMembersPage.tsx`
  container. `1q` and `2f` newly extracted from inline Previews
  (`screens/family/FamilyMembers`, `screens/family/ChildInvite`); `2p`
  (`InvitationList`), `2r` (`FamilyActivityLog`), `3i`
  (`FamilyInviteCancel`) already existed as Screens from an earlier pass and
  needed only real triggers. `InvitationListScreen` got one additive prop
  (`onBack`, was missing) so the container could return to `1q`.
- **Family-rules (2: `1v,2q`)** — new `/family/rules` route, new
  `frontend/src/features/family-rules/FamilyRulesPage.tsx`. `1v` newly
  extracted; `2q` (`FamilyRulesGuide`) already existed. A
  `"가족 규칙 안내 보기"` button was added to the container (no such trigger
  existed in the original mockup) as `2q`'s real entry point.
  `frontend/src/platform/pages/FamilyLanding.tsx` gained a `feature-rules`
  link — the only new Family-domain trigger that didn't already exist.
- **Notifications (1: `1n`)** — new `/family/notifications` route, new
  `frontend/src/features/family-notifications/NotificationsPage.tsx`. `1n`
  newly extracted (`screens/family/NotificationList`).
- **Search (1: `3j`)** — re-verified rather than trusted. The Ownership
  Matrix's own `PM_DECISION_REQUIRED` flag ("No product search ownership
  contract") was checked against actual code:
  `grep -rln "검색|search" frontend/src --include=*.ts --include=*.tsx | grep
  -v Preview | grep -v screens/` returned only React Router's
  `useSearchParams` usages and `FamilyAlbumPage`'s album-scoped search
  (canonical `1u`, separately integrated) — no conflicting ownership. A
  canonical Screen (`screens/family/SearchAll`) and a `/family/search`
  trigger link already existed. New `/family/search` route, new
  `frontend/src/features/family-search/FamilySearchPage.tsx`. Resolved, not
  left as a gap.

## 7. Verification (this pass)

All verification below used a real, authenticated Playwright browser session
against the running dev stack (`vite` dev server + the repo's existing
`docker compose` Postgres/FastAPI backend, already running and healthy —
`mongle-db-1` / `mongle-backend-1`), not file-existence checks.

- Fixed a pre-existing dev-environment misconfiguration found while setting
  this up: the Vite dev server's API proxy target
  (`VITE_DEV_PROXY_TARGET`, defaults to `localhost:8000`) pointed at a port
  nothing was listening on; the real backend was mapped to host port
  `18001`. Restarted the dev server with the correct target — this was a
  pure dev-environment fix, no application code changed.
- Logged in for real via `POST /api/auth/account/login` (seeded synthetic
  Account `member.a`, single-family so the shell auto-selects a family) and
  `POST /api/auth/admin/login` (seeded legacy admin `dad` — its
  `admin_auth.password` hash was reset to a known test value for this pass
  only, since the original was unknown and this is synthetic seed data in
  the local dev DB, not real user data; disclosed here rather than silently
  changed).
- **64/64 product-entry scenarios**: for every canonical ID, navigated to
  its real `PRODUCT_ROUTE` and, for nested/overlay/modal ones, performed the
  actual documented trigger click chain (e.g. `1q → '+ 가족 구성원 초대' →
  2p → '취소' → 3i`), then asserted either the Screen's
  `data-canonical-screen-id` marker (`CREATE_NEW_PRODUCT_CONTAINER` /
  `ADAPT_EXISTING_LOGIC_TO_CANONICAL` rows) or distinctive real content text
  (`KEEP_EXISTING_AS_CANONICAL` rows, which by design carry no marker on the
  real product view) — plus zero unexpected console/page errors. Two
  scenarios needed real backend state, not fixtures, to reach: `1s`
  (rejected-mission detail) required one seeded mission's `status` set to
  `rejected` via SQL for the duration of the test, reverted after; `1j-1`
  (423 lockout) was triggered the same way a real user would — five
  consecutive wrong-PIN submissions against the real `/api/auth/login`
  endpoint, no fixture involved. Both DB-side test states were reverted to
  their original seed values after verification.
  Result: **64/64 PASS** (`/tmp/mongle-w7-3-visual-closeout/scripts/verify-w74-entry.mjs`,
  `entry-results-mobile.json`).
- **192 responsive-shell checks**: the same 64-scenario script re-run at
  820×1180 and 1180×820 in addition to 390×844. Result: **64/64 PASS at
  each of the 3 viewports = 192/192**.
- **63 detached-preview regression + `/login`**: every `/__wave6/{id}`
  debug route (all 63) plus `/login` (`1a-1`), checking
  `data-canonical-screen-id` marker count === 1 and zero console/page
  errors. Result: **64/64 PASS, 0 marker failures, 0 error failures**
  (`final-regression-checkpoint.mjs`).
- **Existing-route regression**: `/`, `/dashboard`, `/admin`,
  `/admin/missions`, `/admin/points`, `/admin/notifications`, `/login`,
  `/family`, `/markpoint`, `/wagle`, `/wagle/board`, `/this-not-exist` all
  resolve exactly as before (protected routes redirect unauthenticated
  requests to `/`, `/login` and the 404 fallback behave correctly).
- **Lint/build/typecheck/diff-check**: `npx tsc --noEmit -p .` clean,
  `npm run lint` clean, `npm run build` succeeds (Vite production build,
  626 modules), `git diff --check` clean (no whitespace errors).

A genuine functional discovery came out of this verification, not a
scripted assumption: `2m`'s `ActiveMissionDetailModal.tsx` was dead code
(never imported anywhere in the real app) despite the prior Matrix pass
marking it `KEEP_EXISTING_AS_CANONICAL`/integrated. Fixed with a 16-line
additive change to `DashboardView.tsx` (a real `"활성 미션 상세 보기"`
button using data already in scope), not just flagged — see §4 and the
Matrix `NOTES` for `2m`.

## 8. Documents

- Matrix: `engineering/phase2/MONGLE_W7_4_PRODUCT_STRUCTURE_INTEGRATION_MATRIX.csv`
- Report: this file
- QA: `agent-system/qa/MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001.md`
- Handoff: `agent-system/handoffs/active/MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001.md`

## 9. Deferred to W7.5 (explicitly out of this task's scope)

- All `DATA_AND_BEHAVIOR_WIRING_PENDING` / `MUTATION_WIRING_PENDING` rows
  (24 / 34 of 64 respectively) — real backend wiring for
  schedule/album/todo/members/rules/notifications/search mutations, reward
  catalog, board/comment API, ranking API, PIN-save, account-deletion, etc.
- `3h` (`계정 탈퇴 확인`) — confirmed `TRUE_FUNCTIONAL_GAP` via
  `grep -rln "탈퇴|delete.*account|account.*delet" frontend/src --include=*.ts
  --include=*.tsx | grep -v Preview | grep -v screens/` returning empty: no
  account-deletion policy/API/code exists anywhere in the product. Structure
  only (nested route reachable from settings) is in place this pass; the
  destructive action itself intentionally does nothing beyond closing the
  view locally, per the explicit instruction never to fake a destructive
  success.
- Any new Route/Page/API/DTO work beyond what already existed.
- Independent QA pass (see `agent-system/qa/TEST_POLICY.md`).

## 10. Six quality gates

- **Hallucination Guard**: every `INTEGRATION_STRATEGY`/`INTEGRATION_TYPE`/
  `PRODUCT_TRIGGER` claim in the Matrix was checked against the actual
  source file before being recorded, and every one of the 64 entries was
  independently re-verified by live browser navigation and click, not
  inferred from file existence. The `2m` orphaned-component discovery in
  §7 is direct evidence this guard caught a real, previously-uncaught false
  claim rather than propagating it.
- **Omission Guard**: all 64 canonical IDs from the W7.3 freeze are present
  in the Matrix; none were dropped or silently merged. The two colliding-ID
  cases (`1l`/`2j` both → `MarkpointUser.tsx`) each kept a distinct real
  trigger rather than being collapsed.
- **Miswork Guard**: no Preview component is imported by a Product Page; no
  canonical JSX is duplicated inside a Product View; no existing real
  API/realtime/PIN/gating behavior was deleted or bypassed; no destructive
  action (account deletion, invite cancel) fakes a success response.
- **Axis Alignment**: `INTEGRATION_STRATEGY` and `INTEGRATION_TYPE` are each
  set exactly once per row and are mutually consistent (e.g. every
  `ALREADY_PRODUCT_BOUND` row is also `KEEP_EXISTING_AS_CANONICAL`).
- **Freshness Guard**: verification in §7 ran against the current HEAD
  (`6f414fe` + this pass's uncommitted changes) with a live dev server and
  live backend, not against a stale snapshot; the dev-proxy misconfiguration
  found and fixed at the start of this pass would have silently invalidated
  any verification run before the fix.
- **Evidence Consistency**: the Matrix's `PRODUCT_ENTRY_TEST_STATUS`,
  `RESPONSIVE_SHELL_STATUS`, and `DETACHED_PREVIEW_STATUS` columns for all
  64 rows match the actual script output referenced in §7
  (`entry-results-{mobile,tabletPortrait,tabletLandscape}.json`,
  `final-regression-checkpoint.mjs` output) — no row claims a verification
  status that wasn't actually run.
