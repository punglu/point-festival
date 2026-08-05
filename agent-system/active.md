# Active Tasks

Only open tasks belong here. Lifecycle, decision, verification, and execution
are separate axes.

## MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001

- Task ID: MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001
- Kind: Developer Agent focused remediation — DEFECT-001 (`/admin`
  unreachable for a genuine Account-native Admin identity) and DEFECT-002
  (legacy Admin JWT with null `player_id` crashes `/api/account-context`)
  only, as raised by `MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-
  INDEPENDENT-QA-001`. DEFECT-003 (Wagle), Auth/Family/Markpoint policy
  blockers, and W7.6 explicitly out of scope.
- Lifecycle: IN_PROGRESS (awaiting PM review / Independent QA)
- Decision: NOT_REVIEWED
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  both defects freshly REPRODUCED before any edit (disposable seed data,
  matches the QA task's own findings exactly). FIXED: DEFECT-002 by
  reordering `_legacy_identity` to check `role=="admin"` before the
  `"player_id" in user` presence test (backend/app/domains/family/
  service.py). DEFECT-001 by widening `require_admin`
  (backend/app/dependencies.py) **and** a second, independently-duplicated
  `/api/admin/*` guard `get_current_admin` (backend/app/domains/auth/
  dependencies.py) discovered mid-task — `/api/admin/*` never actually
  routed through `require_admin` — both now accept an Account-native token
  whose account resolves via the existing `LegacyIdentityMapping` bridge
  to a linked `admin_auth` row; added `AccountContextResponse.is_admin`
  (additive field) so the frontend has a real signal instead of decoding a
  JWT role Account tokens never carry; `AdminProtectedRoute`
  (frontend/src/App.tsx) consults it with a real loading state (no
  admin-content flash), and the non-admin Account-session redirect target
  fixed from the 404-prone `/dashboard` to the real `/family` home
  (`AuthPage`'s own `isLoggedIn` redirect corrected the same way; legacy
  non-admin player sessions keep their existing, correct `/dashboard`
  redirect unchanged). A third, previously-unknown blocker surfaced only
  once the route guard became reachable: `AdminDashboard`'s `MobileHeader`
  unconditionally polls `/api/chat/unread` (legacy-only), and the global
  401-interceptor in `httpClient.ts` read that 401 as session-expired and
  force-logged-out an otherwise-correctly-authorized Account-native Admin
  within ~1s — fixed with a 1-line addition to the existing
  `OPTIONAL_ACCOUNT_ENDPOINTS` precedent (same mechanism already used for
  `/api/me/wagle/`, not a new one). RUNTIME_VERIFIED: all 5 required
  scenarios (Account-native Admin linked / legacy Admin valid-player /
  legacy Admin null-player / authenticated non-Admin / unauthenticated)
  pass via real UI-driven login — deep-link (`/admin/players`) and
  session-restore-on-reload hold for A/B/C, logout clears the session
  correctly for A/B, 3-viewport (390×844/820×1180/1180×820) check on
  `/admin` clean (0 overflow, 0 page errors), regression smoke across
  `/login`,`/`,`/family`,`/markpoint`,`/wagle`,`/admin` clean. `pnpm run
  lint`/`build` clean; `git diff --check` clean; `check_all.py` clean
  (report-only, 0 new warnings under this Task ID). Backend pytest suite
  BLOCKED — this WSL session has no Docker, the isolated test DB
  (`docker-compose.phase2.yml`, port 15435) is unreachable; a pre-existing
  environment constraint, not something this task could fix within scope
  — substituted with extensive live-`curl` verification against the
  running dev backend across every identity permutation. One new,
  pre-existing, out-of-scope defect found and explicitly NOT fixed:
  `GET /api/daily-points/range` 403s for every Admin session (legacy or
  Account-native alike, confirmed identical before/after this task's
  changes) because it requires `role=="player"` literally — leaves the
  Admin dashboard's weekly point-chart widget empty; does not block
  `/admin` access or cause logout; tracked as
  `API-W7-4-ADMIN-DASHBOARD-DAILY-POINTS-RANGE-PLAYER-ONLY-GAP-001`.
  Deep-link-return-to-original-destination-after-login checked and found
  absent for *every* protected route in the app (not just Admin, not
  introduced now) — systemic, pre-existing, out of this task's minimal
  scope. This is a developer self-check per Invariant 6 — NOT self-declared
  as `INDEPENDENT_QA_PASS`, `W7_4_CLOSED`, or `W7_6_READY`.
- Execution: SUCCEEDED (developer self-check execution; both defects
  fixed and runtime-verified within declared scope; substantive verdict
  is DEVELOPER_SELF_CHECK_COMPLETE, not INDEPENDENT_QA_PASS)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001.md
- Constraints: DEFECT-001/002 identity-resolution/route-guard/redirect
  contract only; no RBAC change, no new admin role, no DB schema/migration
  change, no family-scoped permission invented, no rewiring of the legacy
  `/api/admin/*` business-logic layer itself; DEFECT-003/Auth/Family/
  Markpoint policy blockers/W7.6 untouched; all QA-owned seed data
  (3 disposable accounts, 2 family groups, 3 `admin_auth` rows, 1
  `legacy_identity_mappings` row, 1 disposable player, 1 service
  subscription) additive-only, fully cleaned up by ID-scoped `DELETE`,
  final row counts independently re-verified against the true pre-task
  baseline; the 2 pre-existing real `admin_auth` rows (`dad`/`mom`) and 4
  pre-existing real `players` rows read-only, confirmed unaffected; all
  disposable `*.local.py`/`*.local.mjs` scripts removed, confirmed via
  final `git status`; persistent dev stack reused (backend restarted
  twice, only to pick up its own code edits — required since `uvicorn`
  runs without `--reload` in this WSL native stack).
- Next Action: (1) a genuinely independent (separate session) QA pass
  should re-verify DEFECT-001/002's fix per
  `MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-FOCUSED-INDEPENDENT-QA-001`,
  since this task's own results are disclosed self-verification only,
  per Invariant 6; (2) `API-W7-4-ADMIN-DASHBOARD-DAILY-POINTS-RANGE-
  PLAYER-ONLY-GAP-001` (this task's own new finding) needs a dedicated
  follow-up task; (3) DEFECT-003 (Wagle) remains open, out of this task's
  scope; (4) W7.6 should not start until this task's own Independent QA
  lands and the DEFECT-003/Auth/Family/Markpoint policy-blocker list is
  reviewed.

## MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001

- Task ID: MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001
- Kind: Independent (partial) QA of the whole W7.4 Wagle/Admin/Auth/Family/
  Markpoint single-source lineage. Read-only — no product code changed.
- Lifecycle: IN_PROGRESS (awaiting PM review; DEFECT-001/002 remediation
  needed before this axis can close)
- Decision: NOT_REVIEWED
- Verification: **CONDITIONAL** — see full reasoning in this task's own QA
  evidence §16. **Independence qualification (headline finding)**: Wagle
  and Admin were already committed at this session's own starting HEAD
  (implemented by a genuinely separate prior session) — real independence
  holds. Auth/Family/Markpoint were implemented by this exact session
  earlier in the same conversation — their results here are disclosed
  self-verification, not Independent QA, per `agent-system/rules.md`
  Invariant 6.
  **Wagle**: first-ever real browser runtime check for this integration
  (implementer's own handoff disclosed none was possible for them) — a
  real room+message created via the actual HTTP API rendered correctly
  through canonical `1d`; board nav, 3 viewports, Preview regression all
  clean. Found and disclosed 1 real backend defect (below).
  **Admin**: also the first real runtime attempt, but blocked by **2 real,
  high-severity, pre-existing defects** (confirmed untouched by any of the
  5 W7.4 domain tasks' own diffs) that make `/admin` currently unreachable
  for any session with the standard admin-account shape — see DEFECT-001/
  002 below. Fell back to code-level verification (all 10 canonical
  Screens confirmed imported with 0 fixture leakage except the
  already-disclosed `2o` blocker), which supports the implementer's own
  claims.
  **Auth**: reproduced the previously-never-verified locked-profile guard
  live (disposable locked test player, cleaned up) — genuinely closes that
  disclosed gap. `1a` real-data flow re-confirmed.
  **Family/Markpoint**: denominators re-confirmed (32/8); `2f`/`2p`/`3i`
  re-confirmed still fixture, `2y` re-confirmed genuinely real (matches
  the implementer's own correction, no new stale classification found);
  Markpoint's CSS-bug fix re-verified holding, the protected weekly-list
  DOM contract JSX re-confirmed 0-diff.
  **Cross-domain**: all 55 extracted canonical Screens independently
  re-confirmed at exactly 2 real consumers (Product+Preview) each, 0
  orphans, 0 Product→Preview imports, `AdminDataGrid` genuinely
  screen-local (1 real consumer). Matrix: 64/64 rows, 0 duplicates,
  write-once columns re-diffed byte-unchanged against HEAD (fresh script,
  not the implementers' own claim).
  **3 defects found, disclosed, not fixed** (read-only QA):
  DEFECT-001 (HIGH) — `AdminProtectedRoute` accepts only the legacy
  `isAdmin` flag, which real `accountLogin` never sets; DEFECT-002 (HIGH)
  — legacy admin JWTs fail `/api/account-context` resolution whenever
  `admin_auth.player_id` is null (the normal case), due to
  `_legacy_identity`'s `"player_id" in user` presence-only check;
  DEFECT-003 (MEDIUM) — Wagle's `_require_permission` crashes
  (`500 MultipleResultsFound`) when a membership holds 2+ roles granting
  the same permission. All 3 pre-existing, not regressions from this
  wave's work.
- Execution: SUCCEEDED (QA execution; substantive verdict is CONDITIONAL,
  not PASS)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001.md
- Constraints: read-only — no product/backend/CSS/test/fixture/migration
  change; no test skip/relaxation; defects disclosed, not fixed; no
  commit/push/merge/rebase; existing dirty (Auth/Family/Markpoint's own
  uncommitted output) left exactly as found; persistent dev stack never
  restarted; all QA-owned DB seeding additive-only and fully cleaned up
  (independently re-verified 0-row/unchanged counts).
- Next Action: (1) open a dedicated remediation task for DEFECT-001/002 —
  likely highest priority, since it blocks real Admin usability entirely,
  independent of any Screen's own correctness; (2) fold DEFECT-003 into
  Wagle's existing hardening lineage or a new task; (3) a genuinely
  independent (separate session) QA pass should still re-verify Auth/
  Family/Markpoint, since this pass's own results for those three are
  disclosed self-verification only; (4) W7.6 should not start until
  DEFECT-001/002 are resolved or explicitly triaged and the already-open
  PM/design/infrastructure decision list is reviewed. W7.5 overall
  remains `CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`.

## MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Kind: Developer Agent implementation task — re-derive the Markpoint
  domain's full canonical denominator from current code, verify `1x`'s real
  ownership, and single-source every implementation-ready Markpoint screen
  into the real product. Same lineage as the Wagle/Admin/Auth/Family
  single-source integration tasks above.
- Lifecycle: IN_PROGRESS (awaiting PM review / Independent QA)
- Decision: NOT_REVIEWED
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  Markpoint denominator re-derived from `find frontend/src/screens/
  markpoint` (6 pre-existing directories) + `1c` (newly extracted this
  task, had none before — same "static ui-only stub, never live-wired"
  shape found for `1j`/`1j-1` and `1b`) + `1x` (investigated per this
  task's own data/screen/navigation/container ownership-axis instruction:
  grep-confirmed zero real Product Entry/Container/navigation exists
  anywhere for it in either frontend or backend, so it's counted by data
  ownership only, deferred, not force-implemented) = **8**.
  **`1c` (포인트 잔치) — root screen, same pattern as Family Home**:
  `/markpoint` (`MarkpointUser.tsx`) is a real 550-line page whose own
  docblock is explicit about never re-deriving balance/mission-status
  client-side and about keeping spendable `current_balance` visually
  separate from EXP `lifetime_earned`. The frozen canonical visual only
  partially overlaps its structure. Resolved by composing only the
  canonical Screen's header+profile-card zones
  (`showWeeklySection={false}`, a new prop added for exactly this) into
  the real page — real weekly day-list, deductions list, and all 6 real
  overlay flows (mission detail/reject, level-up, 3 reward flows) are
  byte-identical to before, confirmed by diff. Two concrete constraints,
  found *before* writing layout code, ruled out adopting the canonical
  Screen's own week-picker/cheer-message/single-day-list/history zones
  into the Product: no backend "family cheer message" capability exists
  anywhere (would be fabricating user content), and a committed E2E spec
  (`tests/e2e/specs-mongle/03-target-ui.spec.ts`) already has a DOM
  contract on the real always-expanded weekly day-list
  (`<ol>/<li>`/`data-today`/`submit-mission-*`) the canonical single-day
  picker does not reproduce — reading that spec first, not discovering the
  conflict after breaking it. The Preview renders the **full** canonical
  Screen via its own fixture; only the Product's own composition uses a
  subset. **Real CSS bug found and fixed during composition**: an invalid
  `font: 700 12px/normal inherit` shorthand (carried over verbatim from
  the original Preview) was silently dropped by the browser, letting an
  unrelated, pre-existing, unscoped `header button{font-size:24px}` rule
  from a different stylesheet elsewhere in the repo leak onto this
  canonical `<header><button>` and inflate it to 144×48px, starving the
  sibling title text into a 21px column that wrapped one character per
  line. Fixed with real longhand CSS properties plus a strengthened
  `.header .logout` selector, confined to this task's own new file.
  **`1k`/`1l`/`1s`/`2c`/`2h`/`2j`**: grep found all 6 already imported and
  real-wired inside `MarkpointUser.tsx`'s own overlay logic; direct source
  read re-confirmed each one's own already-disclosed real-vs-static
  boundary (`1k`'s static photo-evidence notice, `2c`'s disclosed
  `bonusPoints:0`/manual-only trigger — both real infrastructure/business-
  rule gaps, not wiring gaps) — none modified. 1 implemented + 6 preserved
  + 1 deferred = 8 = denominator.
  Static validation clean (`pnpm lint`/`build`, `git diff --check`). Real
  runtime verification executed: real login via a disposable, additive-
  only synthetic seed account (never the repository's own blanket-delete
  `phase1_seed_synthetic.py`), full cleanup independently re-verified at
  exactly 0 rows; canonical `1c` header/profile render with real (honest
  zero-state) data, `markpoint-balance`/`-level`/`-remaining` test-ids
  exact-text-verified against the same contract the committed spec
  asserts, reward-shop overlay + real logout both exercised live, 3
  responsive viewports on both Product and Preview, Preview regression
  (full Screen still renders). Not independently re-run this task: the
  committed `03-target-ui.spec.ts`/`04-w75-data-wiring.spec.ts` suites
  themselves (their own seeded accounts absent from this DB; provisioning
  them safely was declined — see this task's own handoff) — their DOM
  contract is preserved by 0-diff non-modification of the code they
  depend on, not re-proven by execution; disclosed, not silently skipped.
- Execution: SUCCEEDED (for the 1 implementation-ready target and the 6
  confirmed-already-real rows; 1 row correctly deferred with fresh
  evidence, not forced through)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-MARKPOINT-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- Constraints: no backend/migration/policy/KST-UTC change; no Auth/Family/
  Admin/Wagle code touched; no Preview deletion; no Product → Preview
  import; no fabricating cheer-message data; no breaking the committed
  weekly-day-list E2E contract; no W7.6 start; no commit/push/merge/
  rebase; this Developer session does not self-declare Independent QA
  PASS.
- Next Action: PM review + a focused Independent QA pass — ideally
  including an actual run of `03-target-ui.spec.ts`/`04-w75-data-wiring.
  spec.ts` in an environment where the proper seeded synthetic accounts
  can be provisioned without a blanket-delete risk (a genuinely isolated/
  disposable database, as `tests/README.md` already specifies elsewhere).
  `1x` remains open pending a genuine PM/design decision on whether and
  where a weekly-report feature should be surfaced — no new decision item
  introduced. W7.6 remains out of this task's scope, untouched.

## MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Kind: Developer Agent implementation task — re-derive the Family domain's
  full canonical denominator from current code, prioritize Family Home
  (`1b`), and single-source every implementation-ready Family screen into
  the real product. Same lineage as the Wagle/Admin/Auth single-source
  integration tasks above/below.
- Lifecycle: IN_PROGRESS (awaiting PM review / Independent QA)
- Decision: NOT_REVIEWED
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  Family denominator re-derived from `find frontend/src/screens/family`
  (31 pre-existing directories) + `1b` (newly extracted this task, had none
  before — same "static ui-only stub, never live-wired" shape the Auth
  task found for `1j`/`1j-1`) = **32**. `1c/1k/1l/1s/2c/2h/2j` (Markpoint),
  `1d/1t/2b/2g/3c/3d/3e` (Wagle), 11 Admin rows, the 5 Auth rows (this
  session's own prior task), `1z` (specimen), and `1x` (주간 리포트, a
  Markpoint-shaped unbuilt stub) all confirmed `NOT_FAMILY_DOMAIN` by
  directory/file read.
  **`1b` (Family Home) — top priority per task brief**: `/family`
  (`platform/pages/FamilyLanding.tsx`) is a real, richly-reasoned page
  (multi-family selector, family-admin-vs-service-admin badge separation,
  7 feature links, permission list) that the frozen canonical visual only
  partially overlaps. Resolved by composition, not force-fit: extracted
  `screens/family/FamilyHome/FamilyHomeScreen.tsx` (zones 1-4 only; the
  bottom dock stayed Preview-only, DEVICE_CHROME-equivalent since the real
  route already has `MongleAppShell`'s own nav there), built a new
  `FamilyHomeContainer` Product Adapter that mounts the canonical Screen
  **above** every pre-existing real section (unmodified, not replaced).
  Widened the tile contract (`highlighted`/`available` split) so 가족
  일정/앨범/할 일 correctly show real/available instead of the frozen
  mockup's stale "준비중" (all three are live product features today).
  Real data: greeting name from existing `useAuthStore`, "가족 최근 활동"
  from the existing real `family_activity_log` API (2r's own, filtered to
  positive-tone events — no red/neutral slot exists in the frozen 3-tone
  visual), notification-bell unread from a real API check. Extracted the
  activity-log→display mapping into `shared/family/activityLogFormat.ts`
  for reuse (2nd real consumer now exists), 0 behavior change to `2r`
  itself (confirmed by diff).
  **31 pre-existing Family sub-screens**: a grep across every real Family
  feature page found **all 31 already imported and rendered** — the
  structural single-sourcing work was already done by
  `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001`; this task's own contribution
  is re-deriving that from current code (not trusting the claim) and
  sorting real-vs-blocked with fresh evidence, since the W7.4 Matrix's own
  readiness column predates that later work. Result: **15 preserved**
  (`1f,1g,1h,1n,1o,1p,1q,1r,1w,2k,2n,2q,2r,2u,2y` — confirmed real by
  direct source read + runtime spot-check), **16 deferred**
  (`1i,1u,1v,2f,2p,2v,2w,2z,3a,3f,3g,3h,3i,3j,3k,3l` — each re-confirmed by
  fresh source read, not force-integrated). Two corrections found via
  direct code read overriding staler prose: `2f/2p/3i` (Matrix said
  `READY_FOR_WIRING`; current code confirms a later W7.5 note — still
  fixture-only, invitation-model `POLICY_BLOCKED`) and `2y` (a W7.5 note
  grouped it under a missing-input-control gap; current code's own
  docblock says "2y real" — the newer evidence, taken as authoritative,
  reclassified to preserved). 1 + 15 + 16 = 32 = denominator.
  Static validation clean (`pnpm lint`/`build`, `git diff --check`). Real
  runtime verification executed: real login via a disposable, additive-only
  synthetic seed account (never the repository's own blanket-delete
  `phase1_seed_synthetic.py`, whose own docstring restricts it to isolated
  DBs), full cleanup independently re-verified at exactly 0 rows across
  every touched table; canonical `1b` render + tile navigation + 3
  responsive viewports + Preview regression, plus a 9-route spot-check
  across the rest of the Family domain, all clean, 0 console/page errors.
- Execution: SUCCEEDED (for the 1 implementation-ready target and the 15
  confirmed-already-real rows; 16 rows correctly deferred with fresh
  evidence, not forced through)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-FAMILY-HOME-AND-DOMAIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- Constraints: no backend/migration/RBAC change; no Auth code touched; no
  Admin/Wagle/Markpoint feature change; no Preview deletion; no Product →
  Preview import; no forcing any of the 16 deferred rows through their real
  blockers; no W7.6 start; no commit/push/merge/rebase; this Developer
  session does not self-declare Independent QA PASS.
- Next Action: PM review + a focused Independent QA pass. The 16 deferred
  rows require already-open PM/design/infrastructure decisions prior tasks
  surfaced (invitation-model policy, missing input controls, storage/
  calendar-sync infrastructure, account-deletion policy, settings-policy
  decisions, the PIN-digit mismatch shared with the Auth task) — no new
  decision item introduced. Markpoint domain and W7.6 remain untouched,
  out of this task's scope.

## MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Kind: Developer Agent implementation task — bind the Auth-owned canonical
  Screen(s) the latest `MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_MATRIX.csv`
  marks implementation-ready into the real product, single-source with the
  Detached Preview. Same pattern as the graduated Wagle/Admin single-source
  integration tasks (`MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001`,
  `MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001`), applied to Auth.
- Lifecycle: IN_PROGRESS (awaiting PM review / Independent QA)
- Decision: NOT_REVIEWED
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  Auth denominator re-derived from the existing 64-row Live Consumer Audit
  Matrix (not a keyword search) at **5**: `1a`, `1a-1`, `1j`, `1j-1`, `2s`.
  `1r`/`1u`/`2w` considered and excluded `NOT_AUTH_DOMAIN` — all three
  live under `screens/family/*` in the actual codebase, confirmed by
  direct directory read, despite Auth-sounding labels. Of the 5: `1a`
  (profile-select step of the real, fully-functional legacy `/` flow)
  implemented via a new `ProfileSelectorContainer` Product Adapter
  consuming the canonical `ProfileSelectorScreen`, scoped to the select
  step only — PIN entry and admin login (the flow's other two modes) left
  byte-for-byte untouched, since their own canonical Screens don't exist
  yet and merging with `/login`'s separate Account-model login is a real
  design decision out of this task's authority. `1a-1` already complete,
  regression-reviewed only (0 diff). `1j`/`1j-1` deferred —
  `DESIGN_DECISION_REQUIRED`, confirmed by direct code read: only static
  `ui-only` stubs exist, no canonical Screen contract, undefined "PIN
  찾기" behavior, and the frozen `1j-1` visual's attempt-count/retry-timer
  copy has no backing real API field (`/api/players` returns only
  `is_locked: boolean`, confirmed via live curl). `2s` deferred — re-cites,
  does not reopen, the pre-existing `DESIGN_CONTRACT_MISMATCH`/
  `HUMAN_GATE` (4-digit Screen vs. 6-digit backend PIN) from
  `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001` Phase B. Prop contract
  widened additively (`ProfileSelectorProfile.id?`, `onSelect` payload
  prefers id, falls back to name) — Preview fixture unaffected (0 diff,
  no `id` in fixture, same no-op callback as before). Locked-profile guard
  reproduced at the Container level (mirrors legacy `PlayerCard`'s
  `disabled`), not in the frozen Screen visual. Static validation clean
  (`pnpm lint`/`build`, `git diff --check`). **Real runtime verification
  executed** (not disclosed as pending, unlike the Wagle/Admin
  predecessors) — native `./dev.sh` stack (uvicorn + Vite + local
  PostgreSQL, no Docker), a throwaway Playwright script confirmed the
  canonical `1a` Screen renders real backend player data, selecting a
  real profile correctly navigates to the untouched real PIN screen with
  correct context, and back-navigation returns cleanly; 0 DB mutation; 3
  responsive viewports (390×844/820×1180/1180×820) 0 horizontal overflow.
  **Self-caught correction this session**: a first CSV-column-update pass
  accidentally reformatted all 64 rows' line endings (`csv.writer`
  default `\r\n` vs. the file's own `\n`) even though only 5 rows'
  content changed; caught via `git diff --stat` before proceeding,
  reverted, redone with the correct line terminator — final diff exactly
  5 rows.
- Execution: SUCCEEDED (for the 1 implementation-ready target; 3 rows
  correctly deferred with evidence, not forced through)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-AUTH-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- Constraints: no backend/migration/DB/RBAC/PIN-policy/session-storage
  change of any kind; no touching `PinInputView`/`PinInput`/
  `AdminLoginView`/`pages/A1AccountLogin/**`/`useAuthStore`; no forcing
  `1j`/`1j-1`/`2s` through their real blockers; no W7.6 start; no
  commit/push/merge/rebase; this Developer session does not self-declare
  Independent QA PASS.
- Next Action: PM review + a focused Independent QA pass (per
  `.claude/agents/test-agent.md`) of this task's own claims, particularly
  the widened `ProfileSelectorProfile`/`onSelect` prop contract and the
  container-level locked-profile guard (verified by code inspection only,
  no live-locked-account exercise this session). `1j`/`1j-1`/`2s` remain
  genuinely open pending PM/design decisions already surfaced by prior
  tasks — this task introduces no new decision item. W7.5 overall remains
  `CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`.

## MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001

- Task ID: MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001
- Kind: read-only audit of the 64 canonical Screens' actual live-product
  consumption status (Route/Page/Tab/Modal/Overlay/Auth Step), classifying
  each into exactly one Primary Classification. Not implementation; no
  product/test/migration/seed code touched.
- Lifecycle: IN_PROGRESS
- Decision: NOT_REVIEWED
- Verification: CONDITIONAL — canonical denominator (64) independently
  re-derived from `frontend/src/App.tsx`'s own current route table (63
  distinct `/__wave6/*` preview IDs + `1a-1`, which has no preview route
  of its own, only the real `/login` route; `2d` confirmed absent, a
  numbering gap not a missing screen) — not carried forward from the
  disputed W7.4 self-report or from either pre-existing `engineering/
  phase2/` CSV matrix (neither of which is 64 rows on its own). Full
  64/64 matrix built, 0 unclassified, 0 duplicate, classification sum = 64:
  `LIVE_CANONICAL_INTEGRATED` 22, `PARTIALLY_INTEGRATED` 20,
  `LEGACY_LIVE_UI_ACTIVE` 4, `CANONICAL_PREVIEW_ONLY` 10, `POLICY_BLOCKED`
  4, `INFRASTRUCTURE_BLOCKED` 3, `NO_LIVE_CONSUMER_REQUIRED` 1. Confidence:
  HIGH 39 / MEDIUM 14 / LOW 11. `/family`, `/markpoint`, `/wagle`
  independently re-confirmed `LEGACY_LIVE_UI_ACTIVE` for their own
  canonical ID (1b/1c/1d) — exactly matching the W7.4 reopen's own finding
  — while several *other* canonical Screens were found genuinely live as
  real modals nested inside those same three legacy-shaped pages (e.g.
  `1k`/`1l`/`1s`/`2c`/`2h`/`2j` inside `/markpoint`; `1t`/`2g` inside
  `/wagle`; `3c`/`3d`/`3e` at `/wagle/board`), a finer-grained picture than
  the reopen's own whole-route framing captured. `CONDITIONAL` rather than
  `PASS` because 11 of 64 rows carry `LOW` confidence (nested Screens
  present in a real render chain whose own write/create backend wiring
  could not be confirmed from docblock evidence alone this pass) and 5
  `CANONICAL_PREVIEW_ONLY` rows have a plausible-but-unconfirmed
  AdminDashboard overlap — per this task's own rule, unresolved items are
  not rounded up to `PASS`. 8 Gap Groups (GAP-A through GAP-H) identified
  and detailed with per-screen membership and required PM/design/
  infrastructure decisions. Full detail: `engineering/phase2/MONGLE_W7_4_
  LIVE_CONSUMER_INTEGRATION_AUDIT_REPORT.md` and its companion matrix CSV.
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001.md
- Constraints: no product/test/migration/seed edit; no route/component
  add/remove/rename; no CSS/token change; no package manifest change; no
  existing test weakened; no commit/push/merge/rebase; this task does not
  declare W7.5-overall-PASS or W7.6-READY.
- Next Action: superseded by
  `MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-CONDITIONAL-CLOSEOUT-
  REMEDIATION-001` below, which resolved all 11 `LOW`-confidence rows and
  built the PM Decision Docket this Next Action originally called for. See
  that entry for the current Next Action. W7.5 overall remains
  `CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`.

## MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-CONDITIONAL-CLOSEOUT-REMEDIATION-001

- Task ID: MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-CONDITIONAL-CLOSEOUT-REMEDIATION-001
- Kind: remediation of the `CONDITIONAL` verdict above. Resolves all 11
  `LOW`-confidence rows via fresh source-code evidence, verifies
  `POLICY_BLOCKED`/`INFRASTRUCTURE_BLOCKED` grounds, sub-classifies frozen-
  design actionability, builds a PM Decision Docket and an Implementation
  Readiness axis, proposes a non-started Wave A–F grouping. Not
  implementation; no product/test/migration/seed code touched; no route
  wiring, canonical migration, legacy removal, CSS/design-asset edit,
  API/store wiring, common-component extraction, or W7.6 start.
- Lifecycle: IN_PROGRESS (pending PM review / independent QA)
- Decision: NOT_REVIEWED
- Verification: CONDITIONAL — LOW confidence resolved 11 -> 0 via direct
  source reads (`ProfilePage.tsx`, `FamilyMembersPage.tsx`,
  `AdminDashboard/views/{MissionView,PlayerView,DashboardView}`,
  `BasicModalPreview/index.tsx`). 6 rows reclassified
  `CANONICAL_PREVIEW_ONLY` -> `LEGACY_LIVE_UI_ACTIVE` (`1m`, `2a`, `2e`,
  `2i`, `2l`, `2x` — AdminDashboard's own real, bespoke hooks). 5 rows
  confidence-only upgraded to HIGH (`1u`, `1z`, `2f`, `2p`, `3i`). 2 rows
  reclassified `POLICY_BLOCKED` -> `INFRASTRUCTURE_BLOCKED` (`2b`, `2v` —
  no storage abstraction exists in the backend at all). Final:
  `LIVE_CANONICAL_INTEGRATED` 22, `PARTIALLY_INTEGRATED` 20,
  `LEGACY_LIVE_UI_ACTIVE` 10, `CANONICAL_PREVIEW_ONLY` 4, `POLICY_BLOCKED`
  2, `INFRASTRUCTURE_BLOCKED` 5, `NO_LIVE_CONSUMER_REQUIRED` 1 (sum 64).
  Confidence: HIGH 51 / MEDIUM 13 / LOW 0. New Implementation Readiness
  axis: `ALREADY_COMPLETE` 14, `READY_FOR_LEGACY_REPLACEMENT` 10,
  `READY_FOR_PARTIAL_INTEGRATION_COMPLETION` 7, `READY_FOR_WIRING` 8,
  `DESIGN_DECISION_REQUIRED` 9, `POLICY_DECISION_REQUIRED` 6,
  `INFRASTRUCTURE_PREREQUISITE_REQUIRED` 8, `NO_IMPLEMENTATION_REQUIRED`
  2 (sum 64). PM Decision Docket: 12 decisions, each with concrete
  Option A/B/C, none pre-resolved by this task. `CONDITIONAL` retained
  (not `PASS`) because the underlying product/design/policy/infrastructure
  decisions this task surfaces remain genuinely open — this task closes
  the measurement gap, not the decisions themselves. Full detail:
  `engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_INTEGRATION_AUDIT_REPORT.md`
  Remediation Addendum section and the matrix CSV's new columns.
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md
- Constraints: no product/test/migration/seed edit; no route wiring;
  no canonical-screen migration; no legacy removal; no CSS/design-asset
  edit; no API/store wiring; no common-component extraction; no W7.6
  start; no test skip/disable; no commit/push/merge/rebase; original
  parent audit's own Primary_Classification/Confidence columns and
  handoff/QA-evidence files preserved unmodified (write-once).
- Next Action: PM review of the 12-item Decision Docket and the proposed
  Wave A–F grouping. No Wave may start before its own named decision (see
  Docket) lands and PM approves. W7.5 overall remains
  `CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`.

## NON-BLOCKING TEST INFRASTRUCTURE DEBT

### NATIVE-E2E-FIXED-RESOURCE-CONTENTION-GAP-001

- Task ID: NATIVE-E2E-FIXED-RESOURCE-CONTENTION-GAP-001
- Status: OPEN
- Priority: MEDIUM
- Blocking: NO — `NON_BLOCKING_FOR_W7_5_CODE_DEFECT_CLOSEOUT`
- Category: `TEST_INFRASTRUCTURE` / `PARALLEL_EXECUTION_ISOLATION`
- Discovered-By: `MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001`
- Scope: `tests/e2e/scripts/run-w75-full-spec-native.sh` (native full-stack
  E2E launcher) only. Not `E2E-RUNTIME-F-001` (that finding's own lifecycle
  scope is `CLOSED` — see `MONGLE-W7-5-CODE-DEFECT-HARDENING-CLOSEOUT-001`
  below; this is a separate, newly-found gap, not a reopening of that one).
- Fixed resources observed: database `mc_w75_native_runner`; backend port
  `18096`; Vite port `5195` (all launcher-default, override-able only via
  env vars, not collision-detected).
- Observed evidence: two independent Claude Code QA sessions ran this exact
  launcher concurrently against the same worktree, both using the same
  default DB name and ports. A direct collision was captured
  (`database "mc_w75_native_runner" is being accessed by other users... 6
  other sessions` / `already exists`) mid-sequence. During the same overlap
  window, one session's own first Playwright run recorded 8 browser-
  executable-level failures (`Executable doesn't exist`, `spawn ETXTBSY`,
  GPU/V8 init failures — not connection-refused, not product-assertion
  failures). After the collision window ended, the identical launcher
  passed 10/10 across 4 further consecutive runs (two separate pairs, one
  session each). **Precise causal claim**: concurrent fixed-resource
  contention (the DB/port collision) is directly verified by evidence; its
  exact contribution to every individual browser-runtime error above is the
  most likely explanation given the timing, but is not proven test-by-test
  — recorded as `NOT_FULLY_PROVEN_PER_FAILURE`, not asserted as certain.
- Impact if unaddressed: concurrent invocations of this same native launcher
  (by two agent sessions, or a session plus a leftover/orphaned prior
  invocation) can race on `CREATE DATABASE`/`DROP DATABASE`, collide on
  Backend/Vite port binding, risk one session's cleanup tearing down
  another session's still-in-use resources, and produce browser-runtime
  flakiness that could be misread as a product or lifecycle defect rather
  than an environment-contention artifact.
- Current operating rule (until a structural fix lands): **do not run this
  native launcher concurrently with another invocation of itself.** Before
  starting it, check: (1) is `mc_w75_native_runner` already present/in use;
  (2) is port `18096` occupied; (3) is port `5195` occupied; (4) does a
  `run-w75-full-spec-native.sh` process already exist. If any check finds
  an occupied resource, do not proceed — treat as `RESOURCE_BUSY` and stop,
  rather than force through or kill another session's process/DB/port.
- Future remediation direction (not yet implemented): run-ID-based unique
  DB naming; dynamically allocated or reserved-and-locked unique Backend/
  Vite ports; a per-run runtime directory (already present for logs, not
  yet for DB/port allocation); launcher-written ownership metadata (PID, DB
  name, ports, run ID, start time) that `cleanup()` checks before acting,
  so it can never touch a resource it did not itself create; a regression
  test that runs two launcher instances in parallel and asserts both
  complete cleanly with 0 cross-contamination.
- Closure criteria: two or more native launcher invocations run genuinely
  in parallel, each with its own independent DB/backend-port/Vite-port,
  each reaching 10 passed / 0 failed / 0 skipped, with 0 cross-cleanup, 0
  cross-session contamination, 0 Git dirty, and 0 QA resource residue from
  either run.
- Next Action: unscheduled — MEDIUM priority, non-blocking. PM to decide
  when to schedule the structural fix; the interim operating rule above is
  sufficient to keep single-session use safe in the meantime.

## MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001

- Task ID: MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001
- Kind: independent QA of `MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-
  REMEDIATION-001`'s own native launcher, verifying `E2E-RUNTIME-F-001`'s
  own lifecycle contract (Backend/Vite held until Playwright completes,
  cleanup only afterward, exit code preserved) across 2 independently
  executed consecutive runs. Read-only/verification role.
- Lifecycle: IN_PROGRESS
- Decision: NOT_REVIEWED
- Verification: CONDITIONAL — launcher static audit clean (top-level
  `( ) & PID=$!` pattern, single top-level `trap cleanup EXIT`, foreground
  Playwright, pre/post `kill -0` liveness checks, exit-code preservation,
  no prohibited pattern found); lifecycle smoke PASS (24s hold, 3/3
  liveness+HTTP checks); **Run 1: 8 failed / 2 passed (37.2s)**, all 8
  failures browser-executable-launch-level (`Executable doesn't exist`,
  `spawn ETXTBSY`, GPU/V8 init failures) — **not** connection-refused, both
  service PIDs confirmed alive before AND after Playwright regardless;
  **Run 2: 10 passed / 0 failed / 0 skipped (72s)**, both PIDs alive
  before/after. Investigation found a genuine confound: a **separate,
  concurrently-running Claude Code session on this same machine**
  independently invoked the identical launcher with the same fixed DB name
  (`mc_w75_native_runner`) and ports (`18096`/`5195`) during this exact test
  window (confirmed via live process-tree inspection — a distinct `claude
  --dangerously-skip-permissions` process unrelated to this session's own
  ancestry — and a captured mid-sequence `database ... being accessed by 6
  other sessions` collision), most plausibly contributing to Run 1's
  browser-launch flakiness under resource contention. `E2E-RUNTIME-F-001`'s
  own specific defect shape (services dying, connection-refused) did **not**
  recur in either run — the actual object of this task's verification holds.
  The literal "10/10 twice consecutively" gate was not achieved this pass,
  per this repository's own established precedent (a mixed fail-then-pass
  pair does not satisfy a two-consecutive-clean-runs gate). Cleanup verified
  correct in both the passing and failing run; final state confirmed fully
  clean (0 QA residue, persistent dev stack unaffected); static checks and
  `git diff --check` clean; 0 runner-induced Git delta.
- Execution: SUCCEEDED
- QA Evidence: agent-system/qa/MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001.md
  (this QA evidence file serves as its own handoff, same lightweight
  convention as `MONGLE-W1-INDEPENDENT-QA-001` / `MONGLE-W7-5-MARKPOINT-
  PROJECTION-FOCUSED-INDEPENDENT-QA-001` — no `Closeout Contract: v1`
  declared, no separate Handoff file)
- Environment: Node 20.20.2 (nvm-managed) / Playwright 1.58.2 / Chromium
  v1208, native local PostgreSQL 16, this session's own separate persistent
  dev.sh stack (8000/5174) confirmed untouched throughout.
- Constraints: no product/test/migration/seed/Playwright-spec/assertion
  edit (confirmed byte-identical to HEAD, start and end); no commit/push/
  merge/rebase.
- Next Action: a follow-up re-run of the same two-consecutive-invocation
  protocol at a time with no other concurrent session using the same
  launcher/fixed resource names (or after adding collision-safe resource
  naming to the launcher itself) is expected, on this evidence, to produce
  a genuinely clean consecutive pair — Run 2 already demonstrated a full
  clean 10/10 once uncontended. This QA does not perform that follow-up
  itself (avoiding retry-until-pass within one QA session). W7.5 overall
  remains `CONDITIONAL`/`HUMAN_GATE`; W7.4 remains `REOPENED`; W7.6 remains
  `BLOCKED`.
- **Correction (append-only, same day)**: the "separate, concurrently-
  running Claude Code session" this entry's own investigation found was a
  second Independent QA session running this exact Task ID against the
  same worktree — that session's own corroborating pass (appended to this
  task's own QA Evidence file) independently re-ran the same
  two-consecutive-invocation protocol twice, after confirming no contention
  remained: **first pair 10/10 + 10/10, second (fully uncontended) pair
  also 10/10 + 10/10** — 4/4 runs clean once outside the collision window.
  The one gap this entry's own verdict was waiting on (an uncontended
  re-run) is now independently supplied. Revised verification:
  `E2E-RUNTIME-F-001`'s own lifecycle contract and the two-consecutive-
  clean-runs gate are both independently satisfied.
- Execution (revised): **SUCCEEDED, code-defect-hardening scope CLOSED**
  (per Section 17-equivalent restriction — this does not extend to
  `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`, W7.4, or W7.6 readiness).
  W7.5 overall remains `CONDITIONAL`/`HUMAN_GATE`; W7.4 remains `REOPENED`;
  W7.6 remains `BLOCKED`.

## MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001

- Task ID: MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001
- Kind: fix `E2E-RUNTIME-F-001` (native launcher released Backend/Vite
  immediately after readiness instead of holding them until Playwright
  finished) with a lifecycle-safe native full-stack E2E runner. Not product
  feature work.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM task direction, this session)
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  root cause reconstructed (original launcher script no longer exists;
  most plausible mechanism is a foreground multi-minute invocation hitting
  this environment's own ~120s tool execution timeout right as Playwright
  started, killing the whole process tree including its own backgrounded
  Backend/Vite). New `tests/e2e/scripts/run-w75-full-spec-native.sh` reuses
  `run-w75-full-spec.sh`'s own already-proven `( cd dir && exec ... ) &
  PID=$!` top-level-scope pattern verbatim, adds `kill -0` liveness
  re-checks inside readiness polling and immediately before Playwright
  starts, and was itself invoked as a background command (not foreground)
  to avoid the same timeout trap. Lifecycle smoke (standalone
  backend+frontend, no Playwright): held 24s, 3/3 liveness+HTTP checks
  clean. Full run: both PIDs confirmed alive immediately before Playwright
  start, **10 passed, 0 failed, 0 skipped (53.9s)**, both PIDs still alive
  immediately after Playwright finished. Cleanup confirmed: QA DB removed,
  both PIDs killed, QA ports free, runtime log auto-removed, persistent
  dev stack (`dev.sh`, this session's own separate stack) confirmed
  unaffected. Static checks (frontend lint/build, `bash -n`, `git diff
  --check`, `check_all.py`) all clean.
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001.md
- Parent: MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001
  (below), whose own `E2E-RUNTIME-F-001` finding this task closes.
- Constraints: no product/backend/migration/seed/Playwright-spec/assertion
  change; no retry/timeout/skip change; no commit/push/merge/rebase; this
  Developer session does not self-declare Independent QA PASS.
- Next Action: a follow-up focused Independent Re-QA should independently
  re-run `tests/e2e/scripts/run-w75-full-spec-native.sh` (ideally more than
  once, since this task's own 10/10 is a single run, not a repeat-run
  stability check) before `E2E-RUNTIME-F-001` is treated as unconditionally
  closed. `MONGLE_W7_5_MARKPOINT_CONDITIONAL_CLOSEOUT_FOCUSED_INDEPENDENT_
  RE_QA_001` (above) can then resume its own remaining Docker/native E2E
  smoke requirement using this runner. W7.5 overall remains
  `CONDITIONAL`/`HUMAN_GATE`; W7.4 remains `REOPENED`; W7.6 remains
  `BLOCKED`.

## MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001

- Task ID: MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001
- Kind: developer remediation of the fixed local Playwright/Chromium runtime
  reproducibility gap discovered by the parent focused Independent Re-QA.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM task direction, 2026-08-04)
- Verification: FAIL (own runtime-reproducibility scope) — Node 20 fixed
  local Playwright 1.58.2 and Chromium launch passed, but the unchanged spec
  recorded 10 failed / 0 passed / 0 skipped because the task-owned native
  launcher did not retain Backend/Vite through execution (`E2E-RUNTIME-F-001`).
  **`E2E-RUNTIME-F-001` itself is now remediated by
  `MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001` (above,
  Developer self-check: 10/10 passed) — this task's own `FAIL` line is kept
  as its own historical record, not rewritten, per Invariant 5; the finding
  it names is closed pending Independent Re-QA of the remediation.**
- Execution: FAILED (own scope; superseded by the remediation task above)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001.md
- Parent: MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001
- Constraints: no product/test/migration/seed change; no latest/dlx/npx
  install; preserve the persistent dev stack and all existing dirty work; this
  developer task cannot award Independent QA PASS.
- Next Action: superseded — see
  `MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001` above.

## MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001

- Task ID: MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001
- Kind: narrowly scoped independent re-QA of
  `MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001`: verify its
  commit-governance correction, Markpoint test hardening, backend stability,
  and one Docker E2E smoke. No feature implementation.
- Lifecycle: SUSPENDED
- Decision: DESIGN_APPROVED (PM direction, 2026-08-04)
- Verification: CONDITIONAL / ENVIRONMENT_REQUIRED — independent static
  lineage audit passed; deducted-side regression passed; the two KST-anchor
  tests passed under Asia/Seoul, UTC, and America/New_York; Markpoint suite
  and backend suite both passed; backend full suite passed **405/405 twice**
  consecutively on the same fresh disposable PostgreSQL DB. Docker is absent
  in this measured WSL environment, so the required E2E 10/10 smoke was not
  runnable and no PASS declaration is valid. A 2026-08-04 native equivalent
  reached isolated DB + current-worktree Backend + pnpm/Vite readiness, but
  the identical Playwright spec could not start because `tests/e2e` lacks its
  fixed local Playwright runtime and `npx` proposed unpinned latest install;
  declined. `ENVIRONMENT_REQUIRED` remains.
- Execution: BLOCKED (only Docker E2E smoke remains)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001.md
- Constraints: independent verification only; no product/test/migration/seed
  edits; no commit/push/merge/rebase/reset/clean/stash; do not reopen migration
  0021, board-room 5×10, or four-run E2E evidence unless the measured diff
  reaches those files. W7.5 overall remains `CONDITIONAL`/`HUMAN_GATE` until
  this task has actual E2E evidence.
- Next Action: on a Docker-capable Mac, execute exactly
  `tests/e2e/scripts/run-w75-full-spec.sh` once at this HEAD; require 10
  passed / 0 failed / 0 skipped and no runner-induced Git delta before
  changing this task's verdict. Do not re-open excluded lineage without a
  diff-triggering reason.

## MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001

- Task ID: MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001
- Kind: dispose of the 3 non-blocking findings (`QA-F-001`/`QA-F-002`/
  `QA-F-003`) from `MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-
  QA-001` (verdict `CONDITIONAL`), plus attempt the E2E smoke that
  verdict's own remaining gap named. Opened directly by PM from that QA
  task's own findings; not new feature work.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM direction, this session, 6-item scope list
  given verbatim)
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  commit `328d877` scope re-audited fresh (7 files, no scope creep);
  `QA-F-001` corrected via an appended `## Correction` section in both the
  Developer task's QA Evidence and Handoff (original stale claim preserved,
  not rewritten, per Invariant 5); `QA-F-002` closed with a new permanent
  deterministic test
  (`test_projection_kst_boundary_independent_of_server_local_timezone_deducted_side`,
  3/3 consecutive PASS); `QA-F-003` closed by replacing the two
  originally-failing tests' own `date.today()` anchor with
  `datetime.now(service.KST).date()` — zero assertion value changed
  (diff-confirmed against HEAD), re-verified passing under `TZ=Asia/Seoul`/
  `TZ=UTC`/`TZ=America/New_York` (previously 1/3 under
  `America/New_York`). Backend full suite run twice, back-to-back, same
  disposable DB, no reset, no code change between runs: **405/405 both
  runs** (404 + 1 new test), 0 task-owned failure,
  `KNOWN-W7-5-WAGLE-CONCURRENCY-001` did not recur. **E2E runner smoke NOT
  performed** — this session has no Docker either (same WSL constraint);
  recorded `ENVIRONMENT_REQUIRED`, genuinely still open, not treated as
  PASS. Per PM's own explicit instruction, the WSL constraint is not
  grounds to declare this item done.
- Execution: SUCCEEDED (for scopes 1-4 and 6; scope 5/E2E smoke NOT
  executed — see Verification above)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md
- Environment: native local PostgreSQL 16, disposable database
  (`mc_qa_markpoint_verify`, created fresh this task, dropped after use; no
  Docker in this WSL environment). Persistent local dev stack (`mc_festival`,
  this session's own separate `dev.sh`) untouched.
- Constraints: no product code change (out of scope — the fix itself was
  already independently verified correct); test-file assertion values never
  changed; no skip/reorder/retry-only; no commit/push/merge/rebase.
- Next Action: an E2E runner smoke pass (`tests/e2e/scripts/run-
  w75-full-spec.sh`, expect 10/10) in a Docker-capable environment is the
  one genuinely outstanding item before this finding's own hardening scope
  can be treated as unconditionally closed. A separate focused Independent
  Re-QA of this closeout task's own 4 completed scopes is the correct next
  step to actually change the parent QA task's `CONDITIONAL` verdict — this
  task does not self-declare that change. W7.5 overall remains
  `CONDITIONAL`/`HUMAN_GATE`; W7.4 remains `REOPENED`; W7.6 remains
  `BLOCKED`.

## MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001

- Task ID: MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001
- Kind: independent QA of `MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-
  REMEDIATION-001`'s own remediation of `RE-QA-F-003` (KST/UTC date-boundary
  defect in Markpoint Target projection). Read-only/verification role; no
  product, test, or migration code change.
- Lifecycle: IN_PROGRESS
- Decision: NOT_REVIEWED
- Verification: CONDITIONAL — root cause independently re-derived via a
  live raw-SQL session-timezone experiment (not by re-reading the
  Developer's own deleted diagnostic); both originally-failing tests 5/5
  consecutive; 5 new deterministic timezone tests 5/5; combined
  Markpoint-adjacent suite 124/124 (broader than the Developer's own
  63-test scope); OS-process-timezone cross-check (Asia/Seoul/UTC/
  America-New_York) and DB-session-timezone cross-check (forced UTC) both
  confirm the product fix itself is timezone-invariant; Hardening backend
  smoke (migration 0021 + board-room + admin bcrypt) 34/34; full backend
  suite run independently twice, back-to-back, same disposable DB, no
  reset: **404/404 both runs**, 0 task-owned failure, the
  `KNOWN-W7-5-WAGLE-CONCURRENCY-001` condition did not recur in either
  run. `CONDITIONAL` rather than `PASS` because of 3 disclosed findings
  (QA-F-001: the Developer's own records say "no commit performed" while
  the fix is actually already committed and pushed at current HEAD,
  `328d877` — governance staleness, not a product defect; QA-F-002: none
  of the 5 committed deterministic tests exercises `today_deducted` at an
  explicit KST/UTC boundary, independently closed as correct-but-untested
  via a QA-only throwaway diagnostic, not a permanent test; QA-F-003: the
  two pre-existing originally-failing tests use their own naive
  `date.today()` as anchor and fail under `TZ=America/New_York`, a
  pre-existing test-fragility unrelated to this fix) and because the E2E
  Playwright runner could not be executed in this QA session's own
  Docker-less WSL environment (`ENVIRONMENT_REQUIRED`, diff-audited as
  unaffected by this remediation regardless). Full detail: `agent-system/
  qa/MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001.md`.
- Execution: SUCCEEDED
- QA Evidence: agent-system/qa/MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001.md
  (this QA evidence file serves as its own handoff, same convention as
  `MONGLE-W1-INDEPENDENT-QA-001` — no `Closeout Contract: v1` declared for
  this lightweight, read-only QA pass, so no separate Handoff file was
  created)
- Environment: native local PostgreSQL 16 on a disposable database
  (`mc_qa_markpoint_verify`, created and dropped this session; no Docker
  available in this WSL environment), not the Docker-based disposable
  Postgres prior QA passes on this task family used. Persistent local
  dev stack (`mc_festival`, this session's own separate `dev.sh`) and any
  NAS/production system were untouched.
- Constraints: no product/test/migration/seed edit (confirmed byte-identical
  to HEAD at both start and end of this QA session); no commit/push/merge/
  rebase.
- Next Action: superseded by
  `MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001` (below), which
  PM opened directly from this QA task's own 3 findings (QA-F-001/002/003)
  and disposed of them: QA-F-001 corrected in place (append-only, see the
  Developer task's own QA Evidence/Handoff), QA-F-002 closed with a new
  permanent deterministic test, QA-F-003 closed by removing the two
  pre-existing tests' own `date.today()` dependence. The E2E runner smoke
  in a Docker-capable environment remains genuinely outstanding — still not
  performed, this WSL session has no Docker either. `RE_QA_F_003`
  code-defect correctness itself was already independently verified by this
  task and is not reopened. W7.5 overall remains `CONDITIONAL`/`HUMAN_GATE`;
  W7.4 remains `REOPENED`; W7.6 remains `BLOCKED`.

## MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001

- Task ID: MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001
- Kind: fix the blocking finding from
  `MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001` (verdict `FAIL`):
  `RE-QA-F-003`, `today_earned`/`today_deducted` measuring 0 instead of the
  real ledger total, deterministically on a repeat backend-suite run. Not
  new feature work.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM direction, this session, following the
  Re-QA's own FAIL verdict)
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  root cause measured via a reproduction matrix (fresh-DB-only failure,
  fresh-second-DB failure, full-suite-context failure — all ruling out
  run-count/fixture-order/persisted-state causes) plus a direct DB/clock
  trace, classified `DATE_TIMEZONE_BOUNDARY_DEFECT`: `own_projection`'s
  `anchor = date.today()` read the server process's OS-local timezone
  while `_sum_ledger` compared `occurred_at` under the DB session's own
  UTC date. Fixed by reusing the codebase's own established KST convention
  (`daily_point/service.py`'s `KST = ZoneInfo("Asia/Seoul")`) for both the
  anchor default and the ledger day-boundary SQL. 5 new deterministic
  regression tests added (don't depend on live wall-clock timing). Focused
  tests 5/5 consecutive; Markpoint suites 63/63. **Backend full-suite
  stability gate**: the first reported pair (Run 1 403/404 with one
  Wagle-domain known-condition failure, Run 2 404/404) was correctly held
  short of PASS by PM review — the gate requires two *consecutive* clean
  runs, not eventually-clean. A dedicated closure-only pass on a fresh
  disposable DB, with zero further code changes, then produced **Run A
  404/404 and Run B 404/404, both clean, immediately consecutive, no
  retry needed** — gate now genuinely satisfied. Hardening-lineage smoke
  (migration 0021 matrix, board-room concurrency, admin bcrypt) 34/34; E2E
  runner 1x 10/10; static checks clean. Per PM direction, not a
  self-declared Independent QA PASS.
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md
- Constraints: assertions/expected values never changed (30/7 stayed 30/7);
  no skip/reorder/retry-only; no commit/push/merge/rebase. W7.4 REOPENED
  status and its own audit remain untouched, out of scope.
- Next Action: reported complete; awaiting
  `MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-RE-QA-001` (or
  equivalent). W7.5 overall remains `CONDITIONAL`/`HUMAN_GATE`; W7.4
  remains `REOPENED`; W7.6 remains `BLOCKED`.

## MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001

- Task ID: MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001
- Kind: fix the two blocking findings from
  `MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001` (verdict `FAIL`)
  against `MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001`:
  `HARDENING-QA-F-001` (migration `0021` active-participant semantics loss,
  HIGH) and `HARDENING-QA-F-002` (E2E runner `/tmp` repository-boundary
  policy violation, MEDIUM). Not new feature work.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM direction, this session, following the
  Hardening Independent QA's own FAIL verdict and recommended remediation)
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  both findings fixed and regression-tested. `HARDENING-QA-F-001`:
  migration `0021`'s participant-survivor algorithm rewritten (active
  precedence across the whole duplicate set); independently confirmed the
  old code actually produced the QA's exact `{left:2, active:0}` result (a
  throwaway copy, rolled back); 10-case regression matrix
  (`test_migration_0021_participant_merge.py`) 10/10; re-verified lossless
  merge + downgrade/re-upgrade round trip on a fresh disposable DB.
  `HARDENING-QA-F-002`: E2E runner logs moved to an in-worktree, gitignored,
  per-run path; this fix's own first verification attempt (relative path)
  caused all 10 Playwright tests to fail, root-caused and fixed (absolute
  path + hardened readiness checks); re-verified 4/4 consecutive clean
  runs, no manual pause, 0 git drift. Full backend suite 399/399 twice
  consecutively (389 prior + 10 new). Wagle 3x3 viewport regression clean.
  Static checks (tsc/eslint/vite build/git diff --check) clean.
  `check_all.py` also surfaced a real governance-format defect in the
  parent task's own Closeout/QA-evidence records (prose instead of the
  required `- Field: value` list items) — fixed, see this task's own
  handoff. Per PM direction, not a self-declared Independent QA PASS.
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001.md
  (original Independent QA FAIL preserved verbatim in
  agent-system/qa/MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001.md, not
  overwritten)
- Scope (fixed order, HUMAN_GATE only on genuine data-semantics ambiguity —
  none found): 1. Confirm repo state + Independent QA evidence. 2. Redesign
  migration 0021's participant-survivor algorithm. 3. Preserve read-state
  through sequence renumbering. 4. 10-case migration regression matrix.
  5. Re-verify lossless merge + downgrade/re-upgrade round trip. 6. Move
  E2E runner logs from `/tmp` to an ignored in-worktree runtime path.
  7. Re-run E2E runner x4 consecutive + concurrency + admin bcrypt +
  focused tests. 8. Full backend suite x2 + Wagle 3x3 + static checks.
  9. Refreeze QA evidence/handoff/Coverage Map/active/relay.
- Constraints: no self-declared Independent QA PASS; no W7.5-overall-PASS or
  W7.6-readiness declaration. No commit/push/merge/rebase. W7.4 REOPENED
  status and its own audit remain untouched, out of scope.
- Next Action: reported complete to the Main Architect; awaiting
  `MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001`. W7.4 REOPENED and
  the 13 PM/design decision gates from
  `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001` remain separately open.

## MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001

- Task ID: MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001
- Kind: fix the two `PRODUCT_DEFECT` findings from
  `MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001`
  (`RE-QA-F-BOARD-ROOM-RACE` HIGH, `RE-QA-F-ADMIN-LOGIN-BCRYPT` MEDIUM) plus
  the `RE-QA-F-2T-RUNNER-FLAKY` LOW test-infrastructure finding, before any
  W7.6 common-component extraction work starts. Opened directly from PM/
  architect direction relaying that Re-QA's own FAIL verdict.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM direction, this session, following the
  Re-QA FAIL verdict's own recommended next step)
- Verification: DEVELOPER_SELF_CHECK_COMPLETE / INDEPENDENT_QA_PENDING —
  all 13 scope steps done: migration `0021` merge verified lossless against
  synthetic seeded duplicates plus downgrade/re-upgrade round trip; GROUP
  `create_room` atomic get-or-create regression-tested (5 concurrent x 10
  fresh Families, always 1 room); admin bcrypt fix regression-tested (6/6);
  E2E runner fixed and verified 4/4 consecutive clean runs (10/10 each);
  Wagle 3x3 viewport regression clean; full backend suite 389/389 twice
  consecutively. No `HUMAN_GATE` triggered — 0 existing duplicate board
  rooms found in the only observed live environment. Per PM direction, this
  is explicitly not a self-declared Independent QA PASS — see this task's
  own QA evidence Final Declaration and handoff Closeout Synchronization.
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md
- Scope (fixed order, no PM check-ins between steps per PM direction):
  1. Full audit of existing board-room duplicate data + FK fanout.
  2. Deterministic no-loss merge strategy (HUMAN_GATE stop only if a real
     unmergeable data ambiguity is found).
  3. Duplicate-merge migration.
  4. DB unique invariant on the reserved family-board room.
  5. Atomic get-or-create for GROUP `create_room`.
  6. 5x10 concurrency regression test.
  7. Legacy admin bcrypt 72-byte defense.
  8. Admin long-password 401 regression test.
  9. E2E runner Postgres-readiness + init.sql-failure-hiding removal.
  10. Playwright runtime-artifact/tracked-dirty isolation.
  11. Migration downgrade/re-upgrade verification.
  12. Full backend suite x2 consecutively.
  13. E2E runner x4 back-to-back (no pause) + Wagle 3x3 regression.
- Investigation finding (2026-08-03, pre-migration): the live persistent dev
  DB (`mongle-db-1` / `mc_festival_phase0`, observed read-only only, never
  mutated) currently holds exactly 1 board room per family and 0 duplicate
  `(family_group_id, title)` GROUP-room rows — the race is real and
  reproducible under concurrency (per the Re-QA's own load test) but has not
  yet produced surviving duplicate rows in this environment. The merge
  migration is still required and is written generically/idempotently (a
  no-op where no duplicates exist), verified against synthetic seeded
  duplicates in a disposable DB, not skipped because production happens to
  be clean today.
- Constraints carried from PM direction: do not self-declare Independent QA
  PASS on completion; report Developer completion to Main Architect and wait
  for a separate focused Independent Re-QA. No commit/push/merge/rebase.
- Next Action: **superseded by the focused Independent QA result below** —
  `MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001` returned `FAIL`
  (`HARDENING-QA-F-001` active-participant semantics loss in migration
  `0021`, HIGH; `HARDENING-QA-F-002` E2E runner `/tmp` policy violation,
  MEDIUM). Remediation is now open as
  `MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001` (above). The W7.4 Live
  Consumer Integration Audit and the 13 PM/design decision gates from
  `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001` remain separately open, out of
  this task's scope.

## MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001

- Task ID: MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001
- Kind: wire the 64 W7.4-bound canonical Screens to real data, mutations,
  auth/permission, and error states — reuse existing Backend/API where
  possible, extend minimally where partial, build new vertical Slices only
  where genuinely missing; no policy-undecided feature built ahead of a PM
  decision.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM task direction, this prompt)
- Verification: FAIL
- Verification detail: Phase J, current, authoritative — Focused
  Independent Re-QA of Phase I's own remediation — driven by exactly one
  confirmed `PRODUCT_DEFECT`: the board-room duplicate-creation race,
  reproduced 10/10 under real concurrency, blocks W7.6 per this task's
  own governing instruction. Every other Phase I claim independently
  re-verified clean (F1 fix + 7 tests, Playwright evidence-gap fix, 2
  more clean backend-suite runs at 382/382, 3×3 Wagle viewport
  regression). 2 new findings beyond Phase I's scope: the F2 runner is
  flaky on back-to-back invocation (2/4 attempts failed on DB-readiness
  timing, not on test content), and the legacy admin login
  (`auth/service.py::authenticate_admin`) has the same unfixed bcrypt-
  72-byte defect class Phase H fixed elsewhere. See `agent-system/qa/
  MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md` for full evidence.
  **PM correction, same day**: final functional completion of the 3
  canonical main screens (`1b`/`1c`/`1d`) is additionally unverified —
  see `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)` below.
  `W7_6_READINESS: BLOCKED`.
- Execution: RUNNING
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md
- Registration note: opened directly from this session's own W7.4 continuation
  (same conversation, same worktree) after confirming per rules.md Invariant 9
  that no existing `active.md`/`graduated/` entry, alias, or git history
  already covers this scope. **Discovered while registering**: W7.3 and W7.4
  (below) had real completed code, reports, handoffs, and QA-evidence files
  but were never added to `active.md`, `graduated/`, or `relay/current.md` —
  the same registration-gap failure shape `PHASE0-AGENT-SYSTEM-RECORD-
  INTEGRITY-AUDIT-002` exists to catch. Fixed as a bounded LOCAL-FIX
  registration alongside opening this task, not left for a future audit to
  find again.
- Registration note (corrected): W7.3 and W7.4 were briefly added here as
  `IMPLEMENTED_AWAITING_INDEPENDENT_QA` active entries in an earlier edit this
  same session. Per PM direction and the real graduation precedent already in
  this repository (`graduated/2026-08.md`'s `MONGLE-FE-ROUTE-NAMESPACE-
  MIGRATION-001` / `MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001` rows, both
  graduated explicitly labeled "Self-reported only, never independently
  QA'd"), completed self-check-only work belongs in `graduated/`, not
  `active.md` — `active.md` is for open work. W7.3 and W7.4 are now graduated
  below in `agent-system/graduated/2026-08.md` with the same disclosed,
  not-independently-QA'd status. `relay/current.md` now points at this task.
- Progress (checkpoint): Phase 0 COMPLETE (64/64).
  **`PHASE_B_PROCESSING_COMPLETE = 6/6`** — a throughput count, not a
  functionality count. Split explicitly per PM direction so it is never
  read as "6 screens work":
  - **`PHASE_B_FUNCTIONALLY_WIRED = 4/6`** — `1a-1`, `1r`, `1q`, `2t` call
    real backend endpoints, verified end-to-end.
  - **`PHASE_B_HUMAN_GATE = 2/6`** — `1u`, `2s`, correctly found blocked on
    a real 4-digit-Screen-vs-6-digit-backend PIN mismatch and reclassified
    (`DESIGN_CONTRACT_MISMATCH`/`HUMAN_GATE`) rather than forced through.
  **Phase C: COMPLETE — 11/11 rows processed** (`1t`, `1f`, `1k`, `1s`,
  `2c`, `2g`, `2o`, `2p`, `2z`, `3b`, `3i`). Row-count-complete is not the
  same as functionally-wired: 3 fully wired (`1t`'s member-list half,
  `1s`, `2g`), 3 capability-split `SCREEN_PARTIALLY_COMPLETE` (`1f`, `1k`,
  `2z` — the Matrix now carries `CAPABILITY_ID`/`CAPABILITY_STATUS`/
  `POLICY_DEPENDENCY` columns so a screen-level status can never hide a
  per-capability gap again), 1 reclassified to `NO_CHANGE_REQUIRED` (`2c`
  — no level-up bonus mechanic exists anywhere, disclosed 0 not
  fabricated), 2 new `DESIGN_CONTRACT_MISMATCH`/`DESIGN_CONTRACT_GAP` rows
  found by attempting the wiring (`2o` — legacy admin/family-scope
  authorization bridge; `3b` — backend ready, frozen Screen has no input
  controls), and `2p` reclassified `POLICY_BLOCKED` (its `Invitation` type
  is keyed on `email`, which D2 already excludes from the Account-native
  model entirely — folded into the same invitation-model gate as `2f`/
  `2w`/`3i`). Verified end-to-end via the same **permanent** Playwright
  spec (4 new cases: `1f`/`1k`/`2g`) plus 15 new backend tests
  (`test_w75_phase_c_extensions.py`), against a fresh isolated disposable
  Postgres + throwaway backend, zero residue after teardown. One additive
  migration this phase (`0012_profile_mission_fields`): `accounts.bio`/
  `birthday`/`avatar_color`, `markpoint_missions.description`/`.checklist`
  (all nullable, no backfill). Full backend suite: 332/333 — the 1
  non-matching test (`test_wagle_service_binding.py::
  test_01_user_jwt_blocked_from_service_ingress`) confirmed pre-existing
  and unrelated via `git stash` against clean HEAD, not fixed here (out of
  scope). Backend-suite `KNOWN_CONDITION` (non-deterministic Wagle-
  concurrency-test contention across 4 Phase B/C runs) is now formally
  registered in `agent-system/qa/COVERAGE_MAP.md`
  (`KNOWN-W7-5-WAGLE-CONCURRENCY-001`) — stabilizing the actual contention
  remains separate, not-yet-scheduled work. Full detail in this task's
  Report §9/Handoff/QA evidence.
- **Phase D: 10 of 11 backend Slices built, all 19 candidate screens
  processed** (`engineering/phase2/MONGLE_W7_5_PHASE_D_SLICE_MAPPING.md`
  built first, per PM direction, so a Slice shared by several screens was
  built once — `SLICE-SCHEDULE` for 4 screens, `SLICE-ALBUM-METADATA` for
  4, `SLICE-REWARD-CATALOG` for 3). 7 new additive migrations
  (`0013`→`0019`: Todo, Family Rules, Notification Preferences, Schedule,
  Album metadata, Reward Catalog, Account-native Notification list); 2
  Slices needed no migration at all (`SLICE-FAMILY-ACTIVITY-LOG` reads the
  existing `MarkpointAuditEvent`; `SLICE-SEARCH` reads Missions + Wagle
  messages) plus `REUSE-WAGLE-ROOMS-AS-BOARD` (`3c`/`3d`) reuses
  `WagleRoom`/`WagleMessage` with a body-encoding convention, zero schema
  change. New `markpoint_target.service.self_spend` gives Reward
  redemption a self-service point-debit path (`require_access` only,
  never the admin-only `POINTS_ADJUST` `adjust_points` needs — a real
  child cannot hold that permission). **Recurring finding across 6 rows**
  (`1i`, `1v`, `2y`, plus Phase C's `2z`/`3b`, and Phase D's own `3j`):
  backend built and tested, but the frozen canonical Screen has no input
  control to drive it from at all — needs a PM/design decision, not more
  backend work. `SLICE-WAGLE-ATTACHMENTS` (`2b`) correctly not built —
  `POLICY_REQUIRED`, same storage-infra gate as `2v`/`1p`/`2z`.
  `SLICE-WAGLE-BOARD-REACTIONS` (`3e`) correctly not built —
  `NEW_SLICE_REQUIRED`, no reaction concept exists in Wagle even after
  `3c`/`3d` landed. 34 new backend tests
  (`test_w75_phase_d_slices.py`), full backend suite re-run twice (a
  concurrent synthetic-seed-script run on the first pass triggered 2
  additional `KNOWN_CONDITION` errors, both confirmed clean on isolated
  and clean-re-run verification — added as further evidence to
  `KNOWN-W7-5-WAGLE-CONCURRENCY-001`, not a new defect).
  `3c`/`3d` additionally live-verified in a real Chromium session via an
  ad hoc Playwright script (not committed): a real HTTP-created post
  rendered and opened, a real comment sent through the Screen's own input
  rendered in the thread. Full detail in this task's Report §10-11/
  Handoff/QA evidence.
- **Phase E/F (this checkpoint) — scope reconciliation, `3e` build,
  closeout-readiness.** Supersedes the "Next Action" paragraph immediately
  below, which is kept for its own historical detail but is now stale on
  `3e`'s status and the gate count. Full detail:
  `engineering/phase2/MONGLE_W7_5_PM_DECISION_PACKAGE.md` (new document)
  and this task's QA evidence "Phase E"/"Phase F" sections.
  - **`3e` (`SLICE-WAGLE-BOARD-REACTIONS`) resolved and built**, not left
    `NEW_SLICE_REQUIRED`: both `3c`/`3e`'s own frozen Screens already
    render `♥ likes · 💬 comments`, so this was `IMPLEMENTATION_REQUIRED`.
    Migration `0020_wagle_message_reactions`, toggle service/router
    endpoints, 8 new backend tests (all pass), real counts wired into both
    Screens. The reaction toggle's own click target is still missing from
    both frozen type contracts — tracked as a canonical PM gate, not
    silently done.
  - **Phase C recounted 11/11** (a prior tally line above summed to 10 by
    arithmetic slip, not a missing row). Phase D's 21-screen/11-Slice scope
    confirmed as the true original scope, not a phantom expansion.
  - **Real defects found and fixed this checkpoint**: a Matrix
    `API_READINESS` field-overwrite (`1q`/`1u`/`2s`, now preserved via a
    new `ORIGINAL_API_READINESS` column); two taxonomy mislabels (`1f`
    streak/badge → `POLICY_REQUIRED`, `2b`'s stale `FINAL_W7_5_STATUS` →
    `POLICY_BLOCKED`); 6 frontend fixture-fallback-on-error defects
    (`FamilyMembersPage`/`FamilyTodoPage`/`FamilyRulesPage`/
    `FamilySchedulePage`/`FamilyAlbumPage`/`ProfilePage` all fell back to
    fake fixture data on a real load failure — fixed to show a real empty
    state); and, while actually running the permanent `3c/3d/3e`
    Playwright spec for the first time, a test-navigation defect
    (`page.goBack()` doesn't return to `WagleBoardPage.tsx`'s
    component-state board view — fixed to use the composer's own back
    control) plus a seed-script FK delete-order defect
    (`phase1_seed_synthetic.py`, fixed). Spec now passes 1/1 for real.
  - **"14 total" gate count below was a miscount**: 17 raw screen-level
    flags actually named, consolidating to **13 canonical PM/design
    gates** once true duplicates merge (family-invitation model:
    `2f`/`2w`/`2p`/`3i` → 1 gate; PIN-digit mismatch: `1u`/`2s` → 1 gate).
    Full per-gate table (question, evidence, recommended option,
    alternatives, default-if-deferred, W7.5-PASS-blocking status) plus
    `2b`'s own 16-field/4-option storage Decision Package are in the PM
    Decision Package document.
  - Full backend suite, cleanest run of the task: 374 passed, 1 failed
    (pre-existing, unrelated, confirmed via `git blame`), 0 errors.
    `KNOWN-W7-5-WAGLE-CONCURRENCY-001` remains registered and unresolved
    (separate, not-yet-scheduled work).
  - **Verdict for this checkpoint: `CONDITIONAL`/`HUMAN_GATE`** — never
    plain `PASS` while the 13 canonical gates remain genuinely open. All
    resolvable implementation is complete; nothing further is
    code-blocked. Independent QA per `.claude/agents/test-agent.md` is
    intentionally still not started — that is the correct next step once
    PM reviews the Decision Package, not a gap in this checkpoint.
  - **Phase G addendum (same checkpoint)**: full `0012`→`0020` migration
    downgrade chain verified for real against a dedicated throwaway DB
    (every downgrade is a real inverse, full round trip clean, 3
    representative schema changes confirmed via direct inspection). A
    broader frontend functional-state audit found and fixed 6 more real
    defects, and — most significantly — found `NotificationsPage.tsx`
    (`1n`) had never actually been wired to its own already-built,
    already-tested backend, directly contradicting this task's own Phase D
    "fully real end-to-end" claim for `1n`. Fixed now, real end to end.
    This is a correctness correction, not a scope change — `1n` was
    already counted as wired in the Matrix.
  - **Phase H (current, authoritative — Final Pre-Independent-QA
    Reconciliation and Evidence Freeze)**: the "13 canonical gates" figure
    itself had a defect — `GATE-2B` (Wagle storage, an infrastructure
    question, not a product-policy question) had been folded into that
    13. Corrected: **13 PM/design gates + 1 separate infrastructure gate
    (`GATE-2B`) = 14 total decision items**; the reaction-toggle
    click-target gap (`3c`/`3e`) is now its own canonical gate,
    `GATE-3E-REACTION-TOGGLE`, filling the 13th slot without `2b`. Phase
    D's own denominator corrected to a non-contradictory split:
    `PHASE_D_TOTAL_SLICES_ORIGINAL_SCOPE=11` (2b is inside this 11, never
    a 12th), `CODE-IMPLEMENTABLE_SLICES_COMPLETE=10/10`,
    `INFRASTRUCTURE-BLOCKED_SLICE=1`. The pre-existing `bcrypt`
    backend-suite failure was investigated and safely fixed (3-line
    length guard in `wagle/service_actor.py`, verified against all 6
    required safety conditions) — **backend suite is now genuinely
    375/375, 0 failed, 0 errors**, re-verified twice. The Playwright `2t`
    skip is resolved — **10/10 passed, 0 skipped** — using a synthetic,
    disposable-only credential in a throwaway DB, same precedent as this
    task's own Phase B `2t` API-level check. A genuine Backend Guide
    boundary gap (`family_activity_log`/`family_search` querying another
    domain's ORM model directly) was found and fixed via 3 new
    dotted-reference functions, 0 behavior change, 0 regressions. One more
    real fixture-fallback defect found and fixed:
    `ProfilePage.tsx`'s 4 secondary stat fetches silently swallowed
    failures, letting fake fixture numbers render as if real — fixed to
    show a real "unavailable" state. All 9 migrations cross-checked
    against their models column-by-column, zero drift. Full verification
    suite re-run clean (backend 375/375, E2E 10/10, `tsc`/`eslint`/`vite
    build` clean, `check_all.py` shows no W7.5-specific warning). **Verdict:
    `IMPLEMENTATION_EVIDENCE_FROZEN` / `READY_FOR_PM_REVIEW` /
    `READY_FOR_INDEPENDENT_QA`** — never `PASS`, since the 14 decision
    items remain genuinely open. No commit/push/merge/rebase performed.
  - **Phase I (current, authoritative — MONGLE-W7-5-INDEPENDENT-QA-
    REMEDIATION-001)**: developer remediation of 4 findings (F1/F2/F3/F5)
    reported against this task. **Disclosure**: the named Independent QA
    report (`agent-system/qa/MONGLE-W7-5-INDEPENDENT-QA-001.md`) does not
    exist in this repository, its git history, or any task registry —
    every technical claim was independently reproduced against current
    source and a live disposable database rather than trusted from an
    unlocatable document. **F1**: `list_popular_posts`'s `range=week`/
    `month` genuinely 500'd (an `int` bound into a `text || 'days'`
    interval expression PostgreSQL has no operator for) — reproduced with
    the exact original error text, fixed with a 5-line diff
    (`:days * INTERVAL '1 day'`), 7 new regression tests added and proven
    real via a revert-and-reconfirm round trip. Fixing the permanent
    Playwright spec's own page-wide-text false-positive assertion (which
    would pass even on a 500, since the board's post list stays mounted
    underneath the Popular Posts overlay) surfaced a second, genuinely new,
    unrelated defect — a board-room-creation race between the app's own
    mount effect and the test's identical find-or-create logic — fixed at
    the test level only per this checkpoint's no-new-migration constraint;
    the same race in real concurrent multi-device usage is disclosed to PM,
    not fixed. A related frontend defect (Popular Posts fetch failure
    indistinguishable from a genuine empty result) was also found and
    fixed. **F2**: `tests/e2e/scripts/run-w75-full-spec.sh` (new,
    documented in `tests/README.md`) makes the full permanent spec,
    including `2t`, reproducible with zero manual steps — verified 10/10,
    0 skipped, twice consecutively. **F3**: full backend suite run twice
    consecutively post-fix — 382 passed (375 + 7 new tests), 0 failed on
    run 1; see QA evidence for run 2's confirmed exact count.
    `KNOWN-W7-5-WAGLE-CONCURRENCY-001` remains registered, unaffected.
    **F5**: `tests/e2e/test-results/.last-run.json` had drifted from its
    committed HEAD value (this checkpoint's own Playwright runs
    regenerate it) — restored via `git checkout --` on that one tracked
    file each time it drifted. **Verdict: `REMEDIATION_EVIDENCE_FROZEN` /
    `READY_FOR_FOCUSED_INDEPENDENT_RE_QA`** — never `PASS`. No commit/
    push/merge/rebase performed.
  - **Phase J (current, authoritative — `MONGLE-W7-5-FOCUSED-INDEPENDENT-
    RE-QA-001`)**: independent re-QA of Phase I's own remediation claims.
    **Verdict: `FAIL`**, driven by exactly one item: the board-room
    duplicate-creation race Phase I disclosed as a test-level workaround
    is confirmed, by real concurrency reproduction (5 concurrent requests
    × 10 iterations, 10/10 iterations produced duplicate rooms, most with
    all 5 requests each creating a separate room), to be a genuine
    `PRODUCT_DEFECT` — `wagle_rooms` has no unique constraint on
    `(family_group_id, title)` and `create_room`'s GROUP-room branch has
    no existing-room lookup or `IntegrityError` handling at all (unlike
    its own DIRECT-room branch, which has both). This blocks W7.6 per
    this task's own governing instruction. Everything else independently
    re-verified clean: F1's fix and its 7 new tests (15/15, confirmed to
    assert real DB state, not status-codes-only), the Playwright
    evidence-gap fix (confirmed structurally incapable of a stale-DOM
    false positive), 2 more consecutive clean backend-suite runs
    (382/382 both), and the 3×3 Wagle viewport regression (9/9 checks
    clean). Two new findings beyond Phase I's own scope: (1) the F2
    runner (`run-w75-full-spec.sh`) failed 2 of 4 independent back-to-back
    invocations on disposable-Postgres-readiness timing — reliable only
    given a short pause between runs, not "zero manual steps" as
    documented; (2) `backend/app/domains/auth/service.py::
    authenticate_admin` (legacy admin login, fully unauthenticated) still
    has the *exact same class* of bcrypt-72-byte defect Phase H fixed in
    `service_actor.py` — reproduced a real 500 with a 153-byte password
    against the seeded `dad` account; the modern Account-native login
    already guards against this (`try/except` in `verify_password`), the
    legacy admin path does not. Also recovered the missing `agent-system/
    qa/MONGLE-W7-5-INDEPENDENT-QA-001.md` artifact (labeled
    `RECOVERED_FROM_REPORTED_INDEPENDENT_QA_RESULT`, distinguishing
    `REPORTED_PREVIOUSLY` from `INDEPENDENTLY_REPRODUCED_NOW`, since no
    original file/log ever existed in this repository). Zero product/
    test/migration/seed code changed by this QA pass (SHA-256-verified
    against its own start-of-session manifest). Full detail: `agent-
    system/qa/MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md`.
  - **PM correction, 2026-08-03 (same day, official status update)**:
    W7.5's own feature/defect verification performed to date (Phases
    B–J) remains valid and is not retracted by this correction. However,
    **final functional completion of the three canonical main screens
    (`1b`/`1c`/`1d` — `/family`, `/markpoint`, `/wagle`) is NOT verified**
    — see `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)`
    above for the reopened W7.4 scope-and-evidence defect this is tied
    to. W7.5's own data/behavior wiring on top of whichever page
    currently occupies each of those three routes is unaffected on its
    own terms (a correctly-wired legacy-design page is not un-wired by
    a design-reskin gap), but neither W7.4 nor W7.5 currently has
    evidence that those three routes render their own canonical design.
    **`W7_6_READINESS: BLOCKED`** — the Board Room race (`PRODUCT_
    DEFECT`, confirmed above) and the legacy-admin bcrypt defect must be
    resolved first; this was already true from Phase J's own verdict and
    is unchanged by this correction, stated here again for a single
    combined readiness record.
- Next Action (historical, Phase D checkpoint — see Phase E/F above for
  current state): Phase D's two remaining items (`2b`, `3e`) and the
  6-Screen missing-input-control gap all need PM/design decisions before
  further code — none of it blocks calling W7.5's implementation phases
  complete for PM review. 14 total `POLICY_REQUIRED`/`POLICY_BLOCKED`/
  `DESIGN_CONTRACT_MISMATCH`/`DESIGN_CONTRACT_GAP`/`NEW_SLICE_REQUIRED`
  rows now stand across the whole task (`3h`, `2f`/`2w`/`2p`/`3i`, `1t`'s
  D6-P2 mute setting, `1u`/`2s`'s PIN-digit mismatch, `2o`'s auth bridge,
  `1i`/`1v`/`2y`/`2z`/`3b`/`3j`'s missing input controls, `2b`, `3e`).
  Independent QA per `.claude/agents/test-agent.md` has not started for
  any phase.

## MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Kind: Developer Agent implementation task — bind the Wagle-owned
  canonical Screens the latest Matrix/remediation marked
  implementation-ready into the real product, single-source with the
  Detached Preview. Not an audit; the first code-level follow-through on
  `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)`'s own
  `CONFIRMED_CANONICAL_RESKIN_MISSING: 1b, 1c, 1d` finding, for the `1d`
  third of that finding specifically (Wagle scope only; `1b`/`1c` are
  Family/Markpoint domains, out of this task's charter).
- Lifecycle: IN_PROGRESS
- Decision: NOT_REVIEWED (developer self-check only; no Independent QA yet)
- Verification: CONDITIONAL — Wagle target set re-derived from the current
  Matrix (7 rows, not the stale 6-item prior candidate list — `1d` was
  missing from that list). Of 7: `1d` implemented
  (`READY_FOR_LEGACY_REPLACEMENT` → product-integrated, single canonical
  source with `FamilyChatPreview`); `1t`/`2g`/`3d` already complete,
  regression-reviewed, unmodified; `2b`/`3c`/`3e` deferred on pre-existing,
  genuine infrastructure/design blockers this task's charter forbids
  resolving unilaterally. Static validation clean (lint/build/typecheck/
  `git diff --check`/`check_all.py`), but no browser/E2E runtime was
  available in this environment (no local `backend/.venv`, no local
  PostgreSQL) — disclosed as NOT_EXECUTED rather than assumed PASS.
- Execution: DEVELOPER_SELF_CHECK_COMPLETE (implementation done; runtime
  verification pending a session with a usable backend/Postgres runtime)
- Closeout Contract: v1
- Mid-task note: a "SCOPE CORRECTION" instruction arrived claiming
  `frontend/src/platform/**` (this task's edit target) was unapproved
  "Doran" draft work from a supposedly-shared worktree with
  `minecraft_points_festivals`. Independently verified false (separate
  `.git` clones, not a shared worktree; no `DoranLanding.tsx` anywhere in
  this repository) before any protected-path edit occurred; PM confirmed
  and cancelled it; no rollback needed. Full detail in this task's own
  handoff/QA evidence.
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- Next Action: focused runtime/E2E re-verification
  (`tests/e2e/specs-mongle/03-target-ui.spec.ts` Journey 4,
  `04-w75-data-wiring.spec.ts`) once a Postgres/backend runtime is
  available in-session; then the same single-source pattern for `1b`
  (Family) and `1c` (Markpoint) to close out
  `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001`'s full 3-screen finding;
  or `MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001` per this
  task's own report.

## MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001

- Task ID: MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001
- Kind: Developer Agent implementation task, resolving the 3 screens
  (`2e`, `2i`, `2l`) `MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-
  INTEGRATION-001` (below) deferred. PM decision Option 1: expand each
  canonical Screen's data/input/behavior contract to losslessly absorb
  the real product's own richer functionality, rather than deleting real
  features or keeping legacy/custom screens permanently parallel.
- Lifecycle: IN_PROGRESS
- Decision: NOT_REVIEWED (developer self-check only; no Independent QA yet)
- Verification: CONDITIONAL — all 3 screens implemented and
  product-integrated with 0 loss of existing real functionality (verified
  via `git diff --name-only` showing 0 changes to every already-real
  component composed via slot/renderRow: `WeeklyGrid.tsx`,
  `MissionCard.tsx`, `MissionCardEdit.tsx`, `ProposedMissionSection.tsx`,
  `PlayerStatusCard.tsx`, `BalanceSection.tsx`, `RecentAlerts.tsx`,
  `WeeklyActivityChart.tsx`). `2e`: canonical Screen now composes the real
  WeeklyGrid/ProposedMissionSection as slots, a new Screen-local
  `AdminDataGrid` common component (assembled from this repo's own
  existing table/card-grid conventions, not invented) hosts the mission
  row list, plus newly-real client-side status-filter/search. `2i`: 6 real
  dashboard sections composed as named slots — the charter's own
  explicitly-listed strategy for a "real structure differs from frozen
  mockup" shape, same pattern already open for `1b`/`1c`/`1d` (cross-
  referenced below). `2l`: canonical form gained real multi-assignee/
  quick-point/date-mode fields and a payload-carrying `onCreate`, wired
  into `NewMissionModal.tsx`'s existing real `Promise.all` fan-out. Static
  validation clean (lint/build/typecheck/`git diff --check`/
  `check_all.py`); no browser/E2E runtime available in this environment,
  the same disclosed gap carried by both prior tasks in this lineage.
- Execution: DEVELOPER_SELF_CHECK_COMPLETE (all 3 screens implemented;
  runtime verification pending a session with a usable backend/Postgres
  runtime)
- Closeout Contract: v1
- Mid-task self-correction: an initial `2e` design typed the proposed-
  mission list directly into the canonical model and reimplemented its
  card rendering, which would have silently orphaned the real
  `ProposedMissionSection.tsx` — caught by this task's own
  `grep -rl "ProposedMissionSection"` check before the report was
  written, corrected to a `proposedSlot` composition prop. Disclosed in
  the QA evidence.
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001.md
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-ADMIN-CANONICAL-CONTRACT-EXPANSION-001.md
- Next Action: focused runtime/E2E re-verification across the whole W7.4
  lineage (Wagle + Admin Wave 1 + this expansion) once a Postgres/backend
  runtime is available in-session; `2o` remains its own separate,
  unresolved infrastructure blocker (no policy API exists); then
  re-derive the Matrix for the next domain (Auth is an unverified guess).

## MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001

- Task ID: MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001
- Kind: Developer Agent implementation task, following the same pattern as
  `MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-INTEGRATION-001` — bind
  Admin-owned implementation-ready canonical Screens into the real
  product, single-source with the Detached Preview, extracting only
  genuinely-repeated common components.
- Lifecycle: IN_PROGRESS
- Decision: NOT_REVIEWED (developer self-check only; no Independent QA yet)
- Verification: CONDITIONAL — Admin target set re-derived from the current
  Matrix (10 rows: `1m, 2a, 2e, 2i, 2l, 2m, 2o, 2t, 2x, 3b`). Of 8
  implementation-ready rows, 5 implemented (`1m, 2a, 2m, 2x, 3b`); `2t`
  already complete, unmodified; `2o` remains its pre-existing
  infrastructure blocker, unmodified. 3 rows (`2e, 2i, 2l`) — all
  `READY_FOR_LEGACY_REPLACEMENT` in the Matrix — were found during actual
  implementation to have a real structural conflict: their frozen
  canonical mockup's own no-payload callback contract cannot carry the
  materially richer real functionality already relied upon in
  `MissionView.tsx`/`DashboardView.tsx`/`NewMissionModal.tsx` (multi-
  assign creation, WeeklyGrid/template/import machinery, a 6-section real
  dashboard) without either deleting real capability or redesigning the
  frozen visual — both outside this task's authority. Deferred with full
  evidence rather than forced either way; `2i`'s conflict is the same
  shape already open for `1b`/`1c`/`1d` under the REOPENED entry below.
  Static validation clean (lint/build/typecheck/`git diff --check`/
  `check_all.py`); no browser/E2E runtime available in this environment,
  same disclosed gap as the Wagle predecessor.
- Execution: DEVELOPER_SELF_CHECK_COMPLETE (implementation done for the
  blocker-free set; runtime verification and the 3 deferred screens'
  PM/design decision both pending)
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-INTEGRATION-001.md
- Next Action: PM decision on `2e`/`2i`/`2l`'s newly-discovered structural
  conflicts (recommend folding into the same reconciliation the REOPENED
  entry below already owns for `1b`/`1c`/`1d`); focused runtime/E2E
  re-verification for both this task and the Wagle predecessor once a
  Postgres/backend runtime is available in-session; then re-derive the
  Matrix for the next domain (Auth is an unverified guess, not confirmed).

## MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)

- Task ID: MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001
- Kind: bind the 64 W7.3-frozen canonical Screens into the real product's
  Route/Page/Tab/Modal/Drawer/Overlay/Auth-Step structure.
- Lifecycle: IN_PROGRESS
- Lifecycle detail: reopened — was `graduated/2026-08.md`, self-reported
  PASS, 2026-08-03.
- Decision: HUMAN_GATE
- Verification: `SCOPE_AND_EVIDENCE_DEFECT`
  - `LIVE_CONSUMER_INTEGRATION_COVERAGE: UNKNOWN`
  - `CONFIRMED_CANONICAL_RESKIN_MISSING: 1b, 1c, 1d`
- Execution: SUSPENDED (no active implementation session; reopened for
  scope correction only)
- Closeout Contract: v1
- Reopen basis (per `rules.md` Invariant 10 — explicit new PM decision):
  PM directive, 2026-08-03, correcting this task's own self-reported
  "64/64 `PRODUCT_STRUCTURE_INTEGRATED`" claim. Found during an unrelated
  W7.5 QA conversation: `frontend/src/App.tsx`'s own code comment (lines
  ~149-159) already discloses that `/family`, `/markpoint`, and `/wagle`
  are "existing, backend-integrated, tested route entry points... used
  as-is, not reskinned to the W7.3 canonical mockups" — i.e., this task's
  own "64/64 `PRODUCT_STRUCTURE_INTEGRATED`" count treated "a route
  resolves to *some* page" as equivalent to "a route resolves to *its own
  canonical mockup's design*" for these three, which are materially
  different claims. Canonical mockups for all three already exist and are
  reachable directly: `1b` (가족 홈) at `/__wave6/1b`
  (`FamilyHomePreview`), `1c` (포인트 잔치) at `/__wave6/1c`
  (`PointFestivalPreview`), `1d` (가족 대화) at `/__wave6/1d`
  (`FamilyChatPreview`) — none of the three live consumer pages
  (`FamilyLandingPage`, `MarkpointUserPage`, `WagleLanding`) render this
  design; each is a materially different, pre-existing legacy/functional
  layout kept for its real business logic (subscription gating,
  balance-vs-EXP distinction, per-family permissions — App.tsx's own
  stated reason for not reskinning them).
- What is and is not disputed by this reopen: the routing/structural
  claim this task made — that 64 canonical Screens each resolve to a real
  route somewhere in the product — is not itself shown false by this
  finding. What is unverified is a narrower, more specific claim this
  task's own "`PRODUCT_STRUCTURE_INTEGRATED`" language could be read to
  imply for `1b`/`1c`/`1d` specifically: that the resolved route renders
  *that Screen's own* canonical design. `LIVE_CONSUMER_INTEGRATION_
  COVERAGE: UNKNOWN` records that this task never separately measured
  "route exists and resolves" from "route renders the canonical design"
  for every one of the 64 rows — `1b`/`1c`/`1d` are the 3 *confirmed*
  instances of the gap, not necessarily the only ones; the other 61 have
  not been re-audited under this stricter distinction.
- Not affected by this reopen: `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001`'s
  own data/behavior wiring work (real API calls, real auth, real mutation
  states) on top of whichever page currently occupies each route remains
  valid on its own terms regardless of which visual design that page
  uses — a correctly-wired legacy-design page is not un-wired by this
  finding. See that task's own active.md entry for its own added caveat.
- Next Action: **superseded by `MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-
  AUDIT-001` (above)**, which performed exactly the full 64-row re-audit
  this Next Action called for — `LIVE_CONSUMER_INTEGRATION_COVERAGE` is no
  longer `UNKNOWN`: full matrix built, `1b`/`1c`/`1d` re-confirmed
  `LEGACY_LIVE_UI_ACTIVE` (this reopen's own finding independently
  verified, not disputed), 8 Gap Groups identified for the other 61 rows.
  That audit's own verdict is `CONDITIONAL` (11 LOW-confidence rows), so
  this reopen's own `SCOPE_AND_EVIDENCE_DEFECT` verification is now
  measured rather than unknown, but not yet fully closed. PM review of
  that audit's Gap Groups is the current Next Action; no code change has
  been made under this reopen or the audit that measured it.
- Handoff: agent-system/handoffs/active/MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001.md
- Handoff detail: moved back from `handoffs/archive/2026-08/` to
  `handoffs/active/` under this reopen (original file, relocated only).
- QA Evidence: none new under this reopen; original graduated entry
  (`agent-system/graduated/2026-08.md`) carries a cross-reference to this
  reopened record.
- Cross-reference (2026-08-04): `MONGLE-W7-4-WAGLE-SINGLE-SOURCE-PRODUCT-
  INTEGRATION-001` (above) implemented the `1d` third of this entry's own
  `CONFIRMED_CANONICAL_RESKIN_MISSING: 1b, 1c, 1d` finding — `WagleLanding`
  → `WagleRoomView` now renders the canonical `FamilyChatScreen` (1d),
  single-sourced with `FamilyChatPreview`, code-review-verified (runtime
  E2E pending). `1b` (Family) and `1c` (Markpoint) remain unaddressed —
  this reopen's finding is not fully closed until both are done.
- Cross-reference (2026-08-05): `MONGLE-W7-4-ADMIN-SINGLE-SOURCE-PRODUCT-
  INTEGRATION-001` found the identical "real page richer than frozen
  mockup" shape for `2i` (보호자 대시보드) — `DashboardView.tsx` already
  exceeds 2i's simple mockup with 6 real sections. Recommends folding
  `2i`'s reconciliation into this same open finding rather than treating
  it as a separate question; not yet actioned by PM.
- Cross-reference (2026-08-05, update): `MONGLE-W7-4-ADMIN-CANONICAL-
  CONTRACT-EXPANSION-001` resolved `2i` via PM-approved contract
  expansion (children/slot composition for the 6 real sections) rather
  than a `1b`/`1c`/`1d`-style reskin decision — `2i` is now IMPLEMENTED,
  single-sourced, all 6 real sections preserved unchanged. This does NOT
  resolve `1b`/`1c`/`1d`'s own still-open reskin-vs-real-page question;
  those three remain unaddressed under this reopen's own finding.

## MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001

- Task ID: MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001
- Kind: detached React canonical port for Matrix-filtered W7.2-ready screens only.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (latest PM task direction)
- Verification: NOT_TESTED
- Execution: RUNNING
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001.md
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001.md
- QA Evidence: agent-system/qa/MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001.md

## MONGLE-W6-R2-1C-POINT-FESTIVAL-MOBILE-VISUAL-001

- Task ID: MONGLE-W6-R2-1C-POINT-FESTIVAL-MOBILE-VISUAL-001
- Lifecycle: COMPLETE
- Decision: DESIGN_APPROVED (PM canonical screen direction, 2026-08-01)
- Verification: GPT_VISUAL_GATE_PASS / SOURCE_SEPARATION_PASS
- Execution: SUCCEEDED
- Closeout Contract: v1
- Scope: mobile-only, presentation-only preview route `/__wave6/1c` for
  canonical screen `1c` / `포인트 잔치`; no dashboard replacement or API/session
  connection.
- A1 protection: required — no A1 source, route, or screenshot mutation.
- Measured evidence: 1c GPT visual review and zero-change source separation both
  passed. The three 375/390/430 post-move PNG hashes are byte-identical to the
  pre-move captures; browser audit remains API/WebSocket/storage/navigation 0.
  1e admin canonical measurement is next; tablet remains not started.

## Approved Target decision baseline (D1–D8)

`engineering/phase2/MONGLE_TARGET_DECISION_FREEZE.md` is the Target product
contract SSOT. **D1–D8 are `APPROVED` / `FROZEN` (PM, 2026-08-01).** No task may
record D1–D8 as its blocker, and no task may reopen, narrow or widen them
without a new PM decision. An approved decision is binding design, not evidence
that anything implementing it exists.

## D6-P1–D6-P8 — deferred Wagle implementation policies

- Status: `DEFERRED_TO_RELEVANT_TASK_START_GATE`
- Current default: **none — no default value has been chosen for any row.** Do
  not infer one from legacy behaviour, from another product, or from an existing
  fixture.
- Decision deadline: before the Start Gate of the related implementation task.
- If undecided: that task **cannot start** and must not be promoted to
  `READY_FOR_IMPLEMENTATION`.
- Decomposition impact: `NON_BLOCKING_FOR_DECOMPOSITION` — the D6 core contract,
  the Wave plan and every unrelated task proceed normally.

| Decision ID | Deferred policy | Blocks the Start Gate of |
|---|---|---|
| D6-P1 | Push 알림 본문 공개 수준 | PWA Push subscription/payload task |
| D6-P2 | Room별 mute 및 알림 설정 | Room notification-settings task |
| D6-P3 | Push 묶음 기준(foreground 억제 포함) | Push dispatch task |
| D6-P4 | 읽음 표시 방식 | Read-state UI task |
| D6-P5 | 온라인 상태·마지막 접속 공개 여부 | Presence task |
| D6-P6 | 메시지 수정·삭제 정책 | Message mutation task |
| D6-P7 | 메시지·시스템 이벤트 보존 기간 | Retention task |
| D6-P8 | 오프라인 발신 Queue의 v1 포함 여부 | Offline outbound queue task |

## MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001

- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001
- Kind: backend fix + regression tests — registers, root-cause-fixes and
  hardens the previously uncommitted/unregistered credential-surface change
  that closes backend gap "BG-1" (`MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`'s
  `BLOCKED` finding)
- Lifecycle: IMPLEMENTED_AWAITING_INDEPENDENT_QA
- Decision: DESIGN_APPROVED (PM, via "그래" — item 5 of the 5 reviewed PM
  decision items, then "근본적 해결을해라 / 임시 해결말고" directing a
  root-cause fix rather than a documented workaround)
- Verification: SELF_CHECK_PASS / INDEPENDENT_QA_BLOCKED_THEN_CORRECTED /
  INDEPENDENT_RE_QA_CONDITIONAL (targeted repair evidence PASS twice; complete
  independent full-suite regression NOT_RUN_TO_COMPLETION)
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001.md
- Result: the pre-existing uncommitted fix in `app/dependencies.py` /
  `family/service.py` (widened `get_current_user` role set to
  `{player, admin, account}`) was re-measured live and confirmed working
  (`/api/account-context` 401→200 for an Account token), then root-cause
  corrected: its Account-branch had duplicated
  `family/dependencies.py::get_current_account`'s Session-liveness check
  verbatim (own docstring admitted it). Extracted to one shared function,
  `auth_service.resolve_account_from_session_claim`, now the single call
  site both entry points delegate to. All 38 `Depends(get_current_user)`
  usages across 8 files enumerated for unsafe direct `user["sub"]`
  extraction (the identity-confusion/IDOR risk an `account`-role `sub`
  being an `account_id`, not a `player_id`, could create) — none found;
  the one direct-extraction site (`feedback/router.py`) sits behind an
  explicit role gate that rejects `account` tokens first.
- Test evidence: 33/33 Wave 1 account-auth tests, 41/41 Wagle/family tests,
  5/5 new regression tests (`test_bg1_credential_surface_unification.py`),
  full suite 317 passed / 0 failed / 0 errors (re-run twice; an
  interleaved first run's 3 failed/11 errors traced to pre-existing
  cross-file batch DB-connection contention unrelated to this change —
  same files 86/86 clean standalone).
- Environment: disposable `postgres:16.9-alpine` (port 15435, matches
  `tests/conftest.py`), `database/init.sql` + `alembic upgrade head` →
  `0011`, throwaway Python 3.11 venv (system default 3.9 cannot import this
  codebase). Container and venv torn down after use, zero residue.
- **Correction applied 2026-08-01** after
  `MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001` (verdict
  `BLOCKED`, below): a validly-signed Account token with a non-numeric
  `sid` reached `resolve_account_from_session_claim`'s unguarded
  `int(session_id)` and raised an unhandled `ValueError` (500) instead of
  401. Pre-existed in both original duplicated copies; carried forward, not
  introduced, by the consolidation — still had to be fixed before BG-1
  closes. Fixed with the same `try`/`except (TypeError, ValueError)` → 401
  pattern already used for `sub` two lines below. Added regression test 6
  (`test_non_numeric_sid_is_rejected_as_401_not_a_server_error`), confirmed
  via `git stash` to fail pre-fix and pass post-fix. Full suite re-run
  clean on a freshly recreated disposable DB. Detail in the handoff's own
  "Correction applied after independent QA" section and QA evidence §8.
- Next Action: complete an uncontended independent full-backend regression
  before BG-1 is treated as closed for Wave 6 Target UI purposes. The `sid`
  repair itself passed independent targeted QA twice; no lifecycle closure is
  inferred from that bounded result.

## MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001

- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: CONDITIONAL
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
- Handoff Path: agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md

## PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002

- Task ID: PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002
- Kind: second execution of the `AGENT_SYSTEM_INTEGRITY_AUDIT_PROMPT.md` brief.
  A new ID because `-001` is already in `graduated/2026-08.md` with its handoff
  archived, and Invariant #1 forbids one Task ID resolving to both an open and
  a closed location. That graduated row itself names "a separate future task"
  as the owner of findings F1–F4; this is it.
- Lifecycle: IMPLEMENTED_AWAITING_INDEPENDENT_QA
- Decision: DESIGN_APPROVED (standing PM brief, re-issued 2026-08-01)
- Verification: CONDITIONAL (self-check) / INDEPENDENT_QA_PENDING
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002.md
- QA Evidence: agent-system/qa/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002.md
- Baseline: `dev-newmarkp` @ `25c8d0c`, unchanged start → end. No commit.
- Clean: Invariant #1 violations 0; graduated rows with a dead git ref 0 (29
  checked); missing archived handoffs 0; `SUCCEEDED` handoffs declaring absent
  files 0; `CLAUDE.md` still a 46-line thin pointer with no re-accumulated
  state. The predecessor's two named untracked commits (`0393971`, `91eb98e`)
  are now traceable — that finding is closed by evidence, not assertion.
- Applied (registration/consistency only, no status raised): the **9 F1–F4
  registrations** (block above, all `NOT_TESTED`); three Closeout blocks whose
  field values shared a line with their explanations and so parsed as empty;
  two graduated Wave 3 handoffs still declaring `handoffs/active/` paths.
  `check_closeout.py` warnings **14 → 6**.
- **A correction to my own finding, kept visible rather than replaced:** F-B was
  first recorded as "gate PASS while handoff and QA evidence do not exist". That
  was wrong — both files exist and the gate is properly backed; the defect was
  that the checker could not parse the block. I had reported a checker message
  as a fact about the repository without opening the files it named, which is
  the exact failure this audit exists to catch.
- Concurrent writer: `MONGLE-W4-MARKPOINT-MISSION-LEDGER-001` was added to this
  file by another writer **during** the audit. My edit was verified purely
  additive (62 insertions, their section intact). Their files were not touched.
- Open findings left for their owners: F-A (2 docs-only untraceable commits),
  F-C (that task's handoff/QA carry no `- Task ID:` line), F-D (3 open tasks
  with no handoff), and the long-standing `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2`
  gap.
- Independent QA: **complete — CONDITIONAL** (2026-08-01,
  `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001`, see
  below). Every clean-finding claim (Invariant #1: 0 violations,
  re-checked directly against the current file set; graduated git refs:
  spot-checked, all exist; row-count reconciliation: 29 at this task's own
  snapshot = 18 in `2026-08.md` + 11 in `2026-07.md`, both independently
  recounted) re-confirmed true. **One new registration gap found that
  post-dates this task's own git_ref snapshot and could not have been
  caught by it**: `MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001` (below) —
  the same failure shape this audit exists to catch, recurring immediately
  after the previous pass. Registered as part of the independent QA's own
  in-scope registration-fix authority, following this task's own F1–F4
  precedent.
- PM Disposition (2026-08-01): items 1 (F-C) and 2 (nine F1–F4 tasks) are
  resolved — item 1 self-resolved, item 2 graduated as historical to
  `graduated/2026-08.md` (self-reported only, not independently QA'd).
  Item 3 (`42fa4ae`/`9220859`) resolved as `NO_RETROACTIVE_TASK_ID` /
  `PRE_SYSTEM`. Full disposition text in this task's own QA evidence.
- Next Action: item 4 (`PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2`, flagged
  as next priority) remains open. Item 5's re-verification is **complete —
  see `MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001`** below: the BG-1 fix was
  found already present but unregistered, root-cause corrected (a
  duplicated security check consolidated into one shared function), and
  regression-tested; independent QA of that task is the new open item.

## PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001

- Task ID: PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001
- Kind: independent QA of `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002`,
  re-running the `AGENT_SYSTEM_INTEGRITY_AUDIT_PROMPT.md` brief's own 8-step
  method against current repository state rather than re-reading -002's
  report as evidence.
- Lifecycle: IN_PROGRESS (evidence complete; PM decision pending)
- Decision: DESIGN_APPROVED (process task)
- Verification: CONDITIONAL
- Verification detail: `INVARIANT_1_CLEAN` (re-confirmed), `GRADUATED_REFS_
  CLEAN` (re-confirmed), `NEW_UNREGISTERED_TASK_FOUND_AND_FIXED`
  (`MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`)
- Execution: SUCCEEDED
- Closeout Contract: v1
- Branch / Start HEAD: `dev-newmarkp` / `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
  (unchanged end, no commit)
- Result: -002's own claims re-verified against the live repository, not
  accepted from its report: Invariant #1 (0 overlap between `active.md`
  headers and `graduated/*.md` rows, re-extracted and `comm -12`'d
  directly); 4 graduated git refs spot-checked via `git cat-file -e` (all
  exist); `check_closeout.py`/`check_active.py`/`check_handoff_refs.py`
  re-run live (not read from a prior log) — confirmed -002's F-B/F-C format
  fixes are actually in effect (those specific warnings no longer appear);
  confirmed `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2`'s QA-evidence and
  Closeout-block gaps are still present, unchanged (2 checker warnings).
  **New finding**: `MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001` has real
  product code (10 new + 6 modified frontend files, matching this session's
  own `git status` exactly), a real QA report with an honest `BLOCKED`
  verdict (no false PASS), but was registered in **neither** `active.md`
  nor `graduated/` — and its own Closeout Synchronization block falsely
  claimed `ACTIVE: UPDATED` and a specific `HANDOFF Path` that did not
  exist, independently confirmed by `check_closeout.py`'s own live output
  ("QA evidence declares Closeout Contract v1 but no active or archived
  handoff exists"), not merely by this session's manual grep. Fixed: task
  registered in `active.md` (below), the missing handoff synthesized from
  its own already-real QA evidence content (no fabrication — every claim in
  the handoff traces to a section of the existing report), and the QA
  report's own Closeout Synchronization block corrected to match what is
  now actually true. The task's own substantive verdict (`BLOCKED` on
  backend gap BG-1) was **not** touched or re-judged — that is product
  verification, out of this registration-integrity audit's scope.
- Handoff: agent-system/qa/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001.md (QA evidence serves as handoff, same convention as MONGLE-W1-INDEPENDENT-QA-001)
- QA Evidence: agent-system/qa/PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002-INDEPENDENT-QA-001.md
- Next Action: PM decision on whether `MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`'s
  `BLOCKED` verdict (backend credential-surface gap "BG-1") is accepted as
  the accurate current Wave 6 blocker, and whether independent QA of its
  substantive frontend/backend-gap claims is warranted before the
  recommended follow-up (a backend task unifying the credential surface) is
  opened.

## MONGLE-W1-INDEPENDENT-QA-001 (independent QA of Wave 1)

- Task ID: MONGLE-W1-INDEPENDENT-QA-001
- Kind: independent QA / test / minimal defect correction
- Execution Target: MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001 (six Wave 1
  Backlog tasks: `MONGLE-W1-CREDENTIAL-SESSION-DB-CONTRACT-CORRECTION-001`,
  `MONGLE-W1-SCOPED-RBAC-001`, `MONGLE-W1-ACCOUNT-CREDENTIAL-001`,
  `MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001`,
  `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001`,
  `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001`)
- Lifecycle: IN_PROGRESS (evidence complete; PM graduation decision pending,
  per the same pattern as `MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001`)
- Decision: DESIGN_APPROVED (this QA task itself is process, not a new
  product decision; D1–D8 remain frozen and out of scope for re-approval)
- Verification: PASS
- Execution: SUCCEEDED
- Closeout Contract: v1
- Result: `WAVE_1_INDEPENDENT_QA_PASS` / `WAVE_1_LIFECYCLE_COMPLETE` /
  `READY_FOR_WAVE_2_START_REVIEW`. All six Wave 1 Backlog tasks and the
  `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001` bundle independently re-verified:
  104/104 backend tests reproduced from a freshly created disposable Postgres
  16.9 container (not the implementer's leftover environment), migration
  `0000`→`0006` fresh-upgrade / `downgrade -1`+re-upgrade / full downgrade-to-
  `0004`+re-upgrade all confirmed by direct SQL (zero residue/duplicates), the
  8 new API routes exercised at real HTTP level, token/session/RBAC/
  cross-family/last-admin/FamilyAdmin-issuance boundaries independently
  re-checked against source. No new defect found; the pre-existing
  `0001`-seed FamilyAdmin→ServiceAdmin auto-grant (already fixed by the
  implementer's migration `0006`) was independently confirmed fixed, not
  merely re-read. Two minor test-coverage gaps recorded, not defects (see QA
  Evidence §10/§15/§26). git_ref unchanged, no commit/push.
- Branch / Start HEAD: `dev-newmarkp` / `da7ea7403aefef33a90d622940724b0c53ee88` — re-measured at start, see relay
- Start dirty state: 34 modified tracked files + untracked entries carried
  over from prior sessions (Wave 1 bundle's own changes plus pre-existing
  unrelated dirty files). Preserved, not reset/restored/cleaned/stashed.
- Allowed file areas (defect-correction scope, Wave 1 approval boundary
  only): `backend/app/domains/family/**`, `backend/app/domains/auth/**`,
  `backend/alembic/versions/0005*`, `backend/alembic/versions/0006*`,
  `backend/app/models/all_models.py`, `backend/app/config.py`,
  `backend/tests/**`, the Target Table/Column/API/Role Matrix docs already
  owned by Wave 1, `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`,
  `agent-system/qa/COVERAGE_MAP.md`, `agent-system/active.md`,
  `agent-system/relay/current.md`.
- Forbidden: re-opening D1–D8; scope beyond the six Wave 1 tasks; Doran/Wagle/
  Markpoint domain code; frontend source; `database/init.sql`; migrations
  `0000`–`0004`; any Legacy backfill; commit/push/merge/rebase/PR; touching
  the 33 other pre-existing dirty files unrelated to Wave 1.
- Test environment: disposable, volume-less PostgreSQL container (never the
  persistent `mc-db` dev runtime).
- Defect-correction condition: only confirmed Wave 1 defects, minimal fix,
  targeted + regression re-test, no scope creep.
- PASS/FAIL exit condition: per the task's own Lifecycle section (§23) —
  PASS requires all six Wave 1 tasks' requirements, migration reproduction,
  new-API HTTP tests, session security, multi-family isolation, RBAC,
  FamilyAdmin issuance and regression all independently verified, five gates
  clean.
- QA Evidence: `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`
- Next Action: PM decision on graduating this task and
  `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001` (plus the six Backlog tasks it
  executed) to `graduated/`; separately, PM review of the `0006` RBAC
  registry correction on its own merits (process review of an
  already-independently-verified-correct fix). Wave 2 Start Review is
  unblocked by this PASS.

## MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001 (execution bundle)

- Task ID: MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001
- Kind: execution bundle — an identifier for one single-writer session, **not** a
  new product task. It does not replace or supersede any Backlog Task ID.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED (PM autonomous-execution directive, 2026-08-01)
- Verification: PASS (self-check, now independently confirmed — see below)
- Execution: SUCCEEDED
- Closeout Contract: v1
- Result: all six Wave 1 Backlog tasks implemented. 33 new tests, **104/104**
  backend suite passing, zero regressions, HEAD unchanged, no commit. Verdict
  `WAVE_1_IMPLEMENTATION_COMPLETE` / `WAVE_1_TESTS_PASS` /
  `WAVE_1_QA_CONDITIONAL` / `NOT_READY_FOR_WAVE_2` **superseded by independent
  QA PASS below.**
- Security finding (fixed): the `0001` seed auto-granted
  `markpoint.missions.manage`/`markpoint.points.adjust` to FAMILY `owner`/`admin`,
  violating D4's no-automatic-ServiceAdmin rule and bypassing the
  ServiceSubscription gate. Removed in migration `0006`. Current product impact
  verified nil (no route reads those codes yet); it would have activated at the
  Wave 4/5 Markpoint authorization transform.
- QA Evidence: agent-system/qa/MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001.md
- Independent QA: **complete — PASS** (2026-08-01, `MONGLE-W1-INDEPENDENT-QA-001`,
  see `agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md`). Security, DB and
  authorization boundaries, and the `0006` RBAC registry correction were all
  independently re-verified against source and a freshly created disposable
  DB, not accepted from this bundle's own report.
- Branch / Start HEAD: `dev-newmarkp` / `da7ea7403aefef33a90d622940724b0c53ee8873`
- Start dirty state: 28 modified tracked files + 65 untracked entries, all owned
  by prior sessions/tasks. Preserved, not reset/restored/cleaned/stashed.
- Backlog Tasks executed by this bundle, in fixed order:
  `MONGLE-W1-CREDENTIAL-SESSION-DB-CONTRACT-CORRECTION-001` (1B),
  `MONGLE-W1-SCOPED-RBAC-001` (1C),
  `MONGLE-W1-ACCOUNT-CREDENTIAL-001` (1D),
  `MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001` (1E),
  `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001` (1F-1),
  `MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001` (1F-2).
- Allowed file areas: `backend/app/domains/family/**`,
  `backend/app/domains/auth/**` (new Account-native modules only),
  `backend/alembic/versions/**` (new revisions only),
  `backend/app/models/all_models.py`, `backend/tests/**`,
  `engineering/phase2/MONGLE_TARGET_{TABLE,COLUMN}_DICTIONARY.md`,
  `MONGLE_TARGET_API_INVENTORY.md`, `MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md`,
  `MONGLE_IMPLEMENTATION_BACKLOG.md`, `MONGLE_DOD_AND_TEST_MATRIX.md`,
  `agent-system/qa/**` (this bundle's own evidence + Coverage Map),
  `agent-system/active.md`, `agent-system/relay/current.md`.
- Forbidden areas: the 28 pre-existing dirty files not listed above; Wagle/Doran
  domain code; Markpoint domain code (`mission`, `daily_point`, `deduction`,
  `cheer`, `feedback`, `notification`, `level_tier`, `admin`); frontend source;
  `database/init.sql`; existing migrations `0000`–`0004`; any Legacy data
  backfill; commit/push/merge/rebase/PR.
- Next Action: independent QA **complete — PASS** (2026-08-01). Remaining:
  PM review of the `0006` RBAC registry correction on its own merits, and PM
  decision on graduating this bundle plus the six Backlog tasks to
  `graduated/`. The five Wave 1 FE slices and Wave 2 are unblocked by this QA
  PASS to proceed to their own Start Gates / Start Review.

## MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001

- Task ID: MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: A1_IMPLEMENTATION: COMPLETE / A1_PM_VISUAL_GATE: PENDING /
  A1_INTEGRATION: **DONE — see location correction below** / A1_FINAL:
  CONDITIONAL (PM verdict, 2026-07-31).
  **Location correction (MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001, 2026-08-01,
  originally found by PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001 F6):** the
  previous sentence here claimed this task's code and evidence "live in an
  isolated worktree, never committed to this branch"
  (`/Users/mac/mac_Project/mongle_ui-a1-visual-worktree`, branch
  `w6-2-a1-visual`, pinned at HEAD `9bcd1a5`). That is no longer true and is
  retained above only as the superseded claim. Merge commit `a1fe979`
  (`merge: integrate A1 mobile visual publishing candidate`) already landed the
  A1 reports and real product code into this branch, and the named worktree path
  is confirmed absent from disk (`git worktree list` + direct path check,
  2026-08-01). **This corrects only "where the files are", not the task's
  Verification/Decision status** — A1_PM_VISUAL_GATE and independent QA remain
  outstanding exactly as before. PM
  directed 5 follow-up items: settings icon wired to the existing admin-login
  entry (DONE, re-verified — lint/build/target-E2E PASS, click-through
  confirmed), lock-notice copy kept generic with no invented counts/times
  (already satisfied pre-PM-decision), level/job-title/lock-detail kept as
  documented DATA gaps rather than hardcoded (already satisfied), the Avatar
  status-dot clip NOT worked around in A1 files (already satisfied — see
  MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001, handled as its own task instead).
- Handoff: engineering/phase2/MONGLE_W6_2_A1_MOBILE_VISUAL_PUBLISHING_REPORT.md,
  MONGLE_W6_2_A1_VISUAL_DELTA.md, MONGLE_W6_2_A1_TOKEN_PRIMITIVE_GAPS.md
  (all three are now present in **this** worktree via `a1fe979`; the earlier
  "inside the isolated A1 worktree, not this one" note is superseded — see the
  Location correction in the Phase Note. No `agent-system/handoffs/active/`
  file exists for this task; its reports serve as the handoff.)
- QA Evidence: none in this worktree — self-check only, recorded in the three
  reports above
- Independent QA: not started — gated behind A1_PM_VISUAL_GATE and the Avatar
  fix's own independent QA
- Next Action: PM Visual Gate review of the three A1 reports (Visual Delta's
  remaining sign-off items: pre-login level-pill 401, missing job-title/lock-
  detail API fields, rewritten lock-notice copy). **Revised 2026-08-01:** the
  "integrate A1 into this authoritative worktree ... then remove the isolated
  worktree" steps are already done (`a1fe979`; path confirmed absent), so what
  remains is the PM Visual Gate plus re-running
  lint/build/target-E2E/auth-flows/admin-entry/screenshot/console **here**
  against the merged code, gated behind the Avatar fix's own independent QA.

## PHASE2-DORAN-MESSAGING-CONTRACT-001

- Task ID: PHASE2-DORAN-MESSAGING-CONTRACT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_REQUIRED
- Handoff: agent-system/handoffs/active/PHASE2-DORAN-MESSAGING-CONTRACT-001.md
- QA Evidence: agent-system/qa/PHASE2-DORAN-MESSAGING-CONTRACT-001.md
- Independent QA: not_applicable — contract design; implementation QA required
- Next Action: PM review of five bounded Doran messaging gates before Foundation implementation
- PM Decision Snapshot (2026-08-01): `D6: APPROVED` — WebSocket foreground realtime, PWA Web Push, durable DB SSOT, transactional Outbox, at-least-once delivery, idempotent deduplication, per-Room ordering, reconnect recovery, multi-family Push and failure isolation are mandatory implementation contract. `D6-P1` through `D6-P8`: `DEFERRED_TO_RELEVANT_TASK_START_GATE` and `NON_BLOCKING_FOR_DECOMPOSITION`; each directly related task must resolve its policy at its own Start Gate. Register: the D6-P table at the top of this file.

## PHASE0-DOC-STALENESS-PREVENTION-001

- Task ID: PHASE0-DOC-STALENESS-PREVENTION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-DOC-STALENESS-PREVENTION-001.md
- QA Evidence: agent-system/qa/PHASE0-DOC-STALENESS-PREVENTION-001.md
- Independent QA: not_applicable — documentation/process rule change; no
  product code, DB, or auth touched
- Next Action: PM review of the new Documentation change routing tiers,
  Invariants 9-11, and Prohibited actions list in rules.md; decide whether to
  port the source template's structural-validation script into
  agent-system/tools/

## PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2

- Task ID: PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: SELF_CHECKED / INDEPENDENT_QA_PENDING — registration gap found and
  corrected 2026-07-31 (task existed in handoffs/qa since commit `a1575e0`,
  2026-07-26, but was never added here). Later commits `0393971` (service
  principal and room binding), `91eb98e` (reliable service event delivery) and
  `779cc70` (`fix(mission): serialize point-bearing status transitions`, the
  direct child of `91eb98e`, which adds
  `backend/tests/test_doran_reliable_service_slice.py`) extended the Doran
  domain with no `active.md`/`graduated/` task record; the "remaining work"
  list in the handoff is stale relative to current code. `779cc70` was added to
  this list by MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001 (2026-08-01), per
  PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001 finding F5; all three commits
  are confirmed ancestors of HEAD `da7ea74`. Precision note: technical
  documentation for this work does exist at
  `engineering/phase2/DORAN_FOUNDATION_GAP_ANALYSIS.md` (including a named
  independent-QA reference `PHASE2-DORAN-R2B1-FOCUSED-QA-001` = PASS) — what is
  missing is the Agent System **registration**, not all documentation.
- Handoff: agent-system/handoffs/active/PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2.md
- QA Evidence: agent-system/qa/PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2.md
- Independent QA: pending — mandatory for security, DB, and service boundaries
- Next Action: PM triage — decide whether to register/re-scope the unregistered
  follow-up Doran work (`0393971`, `91eb98e`, `779cc70`) as its own task(s),
  update the R2 handoff's checkpoint to match current code, then run
  independent QA before any completion or push claim. Wave 2 depends on this
  domain, so its actual state must be verified from source rather than from
  the stale handoff.

## PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001

- Task ID: PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_REQUIRED
- Handoff: agent-system/handoffs/active/PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001.md
- QA Evidence: agent-system/qa/PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001.md
- Independent QA: not_applicable — contract design; Foundation implementation requires independent QA
- Next Action: PM review of five bounded Phase 1 architecture gates before Foundation implementation

## PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001

- Task ID: PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: PHASE0 LEGACY CONTAINMENT COMPLETE / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001.md
- QA Evidence: agent-system/qa/PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001.md
- Independent QA: complete — PASS (independent read-only security QA)
- Next Action: Phase 0 automated baseline is ready for PM closeout confirmation; push is authorized by this task's passing conditions

## PHASE0-AUTOMATED-GAP-CLOSEOUT-001

- Task ID: PHASE0-AUTOMATED-GAP-CLOSEOUT-001
- Lifecycle: SUSPENDED
- Decision: DESIGN_APPROVED
- Verification: BLOCKED
- Execution: FAILED
- Phase Note: BLOCKED / CORE DEFECT — CURRENT USER OWNERSHIP AND MUTATION AUTHORIZATION
- Handoff: agent-system/handoffs/active/PHASE0-AUTOMATED-GAP-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/PHASE0-AUTOMATED-GAP-CLOSEOUT-001.md
- Independent QA: required for a follow-up core authorization/ownership fix
- Next Action: PM triage and a bounded core authorization/ownership repair task; do not resume automated closeout or push first

## PHASE0-DEV-RUNTIME-RECOVERY-001

- Task ID: PHASE0-DEV-RUNTIME-RECOVERY-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / SELF_CHECKED
- Handoff: agent-system/handoffs/active/PHASE0-DEV-RUNTIME-RECOVERY-001.md
- QA Evidence: agent-system/qa/PHASE0-DEV-RUNTIME-RECOVERY-001.md
- Independent QA: not_applicable — tooling and isolated runtime self-check
- Next Action: PM review; retain the isolated runtime volume only if follow-up regression work needs it

## PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001

- Task ID: PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001.md
- QA Evidence: agent-system/qa/PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001.md
- Independent QA: not_applicable — documentation localization; PM review required
- Next Action: PM review of localized engineering contracts and five bounded gates

## PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001

- Task ID: PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: PHASE0 AUTOMATED BASELINE COMPLETE / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001.md
- Independent QA: not_applicable — implementation changed docs, tooling, generated API types, and tests only; no core code or contract behavior changed
- Next Action: PM review, then PHASE0-DEVICE-AND-OPERATIONS-GATE-001 for physical-device and operating-DB rehearsal gates

## MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001

- Task ID: MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: SELF_CHECKED / INDEPENDENT_QA_PENDING — fix implemented (overflow
  clip moved from `.avatar` to a new `.avatarInner` wrapper; `statusDot` is now
  an unclipped sibling). Self-check: 29/29 static contract tests pass (26
  pre-existing + 3 new), lint PASS, build PASS, target E2E
  (specs-mongle/01-shell.spec.ts, iphone+desktop) 27 passed/1 correctly-scoped
  skip/0 failed against a freshly rebuilt image containing the fix, manual
  visual regression check of existing non-status consumers (RoomItem/
  ChatHeader on /wagle) confirmed unchanged. PM-directed 2026-07-31, split out
  of the A1 mobile visual publishing
  task. The shared `Avatar` primitive's `.avatar` rule sets `overflow: hidden`
  to clip its image/fallback to a circle, but `.statusDot` is positioned at
  `right:0; bottom:0` on the same element, so the clip cuts the status dot
  into a quarter-circle instead of a full ringed dot. Zero existing consumers
  (`ChatHeader`/`MessageBubble`/`RoomItem`/`DoranLanding`) pass the `status`
  prop today; A1's `PlayerCard` (isolated worktree, not yet integrated) is the
  first real caller to expose this. PM directed this be fixed as its own task
  rather than worked around in A1's files, per Frontend Development Guide and
  Test Policy (preserve primitive contract, use tokens, verify all Avatar
  size/status combinations, lint/build, component/static tests, A1 target
  Playwright, existing-consumer regression; no test deletion/skip/loosening).
- Handoff: agent-system/handoffs/active/MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001.md
- Independent QA: pending — shared Foundation primitive change
- Next Action: implement the fix in the main worktree, verify against every
  Avatar size/status combination and every existing consumer, then hand off
  for independent QA before A1 integration proceeds

## MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001

- Task ID: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: SELF_CHECKED / READY_FOR_PM_CONTRACT_FREEZE (2026-07-31,
  corrected framing). PM redirected this task's central axis mid-flight,
  after the first pass (Axis A, see below) had already reached its own
  ready-for-freeze verdict: Mongle is a new platform owning Account/Group/
  Membership/Role/Permission/Auth/Session; 와글와글 is a new realtime
  messenger on Mongle; 마크포인트 잔치 is a new service built on Mongle's
  user/group/permission/session structure; the legacy point-festival system
  is reference material only, never the SSOT. HEAD unchanged at `6c63367`
  throughout both phases — no code was touched by the correction, only
  documentation framing.
  Phase 1 (Axis A, LEGACY_CURRENT_STATE — retained, not discarded): full
  DB/backend inventory (5 migrations, 17 domain models, 34 live-verified
  relations, 71/71 backend tests passed against a throwaway isolated
  Postgres instance) — see the 7 documents listed below, now banner-marked
  as Axis A.
  Phase 2 (Axis B, TARGET_MONGLE_ARCHITECTURE — the corrected work, 10 new
  documents): key finding — a substantial part of what PM described as new
  platform-owned structure **already exists**, built before this correction
  as the `PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001` Foundation
  (Account/FamilyGroup/FamilyMembership/Role/Permission/ServiceSubscription)
  and the Doran messaging domain (Room/Participant/Message/ReadState/
  ServicePrincipal/ServiceBinding) — both confirmed KEEP_AS_IS, not legacy
  being replaced. The two genuinely missing platform capabilities:
  Account-native Authentication/Session (does not exist in any form — 3
  candidate designs proposed, none decided) and MarkPoint's re-hosting onto
  Membership ownership (business logic 100% reusable per direct source
  read; 7 tables need an ownership-FK TRANSFORM from `player_id` to
  `family_membership_id`; ~70 routes need an auth-dependency swap from
  legacy PLAYER_ONLY/ADMIN_ONLY to Group Role/Permission checks). Every
  legacy table/route/auth-mechanism classified
  (REFERENCE_ONLY/KEEP_AS_IS/REUSE_LOGIC_ONLY/MIGRATE_DATA/TRANSFORM/
  REPLACE/DEPRECATE/DELETE_CANDIDATE/UNDECIDED) with evidence; no
  user-group/role/permission name was invented — 5 explicit
  PM_DECISION_REQUIRED items recorded instead (Group-vs-Family generalization,
  Auth/Session model choice among 3 options, whether the already-seeded
  Role/Permission codes are final, MarkPoint's target URL-scoping
  convention, and two data-migration questions for existing identities and
  point/mission history).
- Handoff: engineering/phase2/MONGLE_TARGET_ARCHITECTURE_RECONCILIATION_REPORT.md
  (current final report). Axis A (7 docs, retained/banner-marked, not
  superseded in content): MONGLE_DATA_BACKEND_CONTRACT_RECONCILIATION_REPORT.md
  (superseded verdict only), MONGLE_DATA_NAMING_CONTRACT_V0_1.md,
  MONGLE_CURRENT_TABLE_DICTIONARY.md, MONGLE_CURRENT_COLUMN_DICTIONARY.md,
  MONGLE_BACKEND_API_CONTRACT_INVENTORY.md, MONGLE_SCREEN_DATA_CONTRACT_MATRIX.md,
  MONGLE_DB_BACKEND_GAP_REPORT.md.
  Axis B (10 new docs):
  MONGLE_TARGET_BUSINESS_GLOSSARY.md, MONGLE_TARGET_USER_GROUP_ROLE_MATRIX.md,
  MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md, MONGLE_TARGET_TABLE_DICTIONARY.md,
  MONGLE_TARGET_COLUMN_DICTIONARY.md, MONGLE_TARGET_API_INVENTORY.md,
  MONGLE_REALTIME_MESSAGING_CONTRACT.md, MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md,
  MONGLE_LEGACY_TO_TARGET_MAPPING.md, MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md.
  **Location correction (MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001, 2026-08-01,
  originally found by PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001 F6):** this
  entry previously stated all 18 documents "live inside the isolated
  data-backend worktree (`/Users/mac/mac_Project/mongle_ui-data-backend-worktree`,
  branch `data-backend-contract-reconciliation`), not this one." That is no
  longer true. Merge commit `da7ea74`
  (`merge: integrate data backend contract reconciliation`) landed all 18
  documents into **this** worktree, and the named path is confirmed absent from
  disk (`git worktree list` + direct path check, 2026-08-01). Note that a
  *different*, undocumented external worktree remains on disk at
  `/private/tmp/claude-501/.../scratchpad/data-backend-contract-worktree`
  (detached HEAD `9bcd1a5`) — flagged as F7 by the same audit, **not touched**,
  and requiring PM direction under `DEC-2026-005` rather than unilateral
  cleanup. No `agent-system/handoffs/active/` file exists for this task; its
  reports serve as the handoff. **This corrects only "where the files are",
  not this task's Verification/Decision status.**
- QA Evidence: none in this worktree — self-check only across both phases
  (migration-chain execution + 71/71 pytest pass + `git diff --check`/
  `git status` clean after every document write are real executed evidence)
- Independent QA: not started
- Contract Freeze outcome (2026-08-01): **the Freeze was issued.** PM approved
  D1–D8 in `engineering/phase2/MONGLE_TARGET_DECISION_FREEZE.md`, which resolves
  4 of this task's 5 `PM_DECISION_REQUIRED` items: Group-vs-Family
  generalization (D1 — family platform, `family_groups`/`family_memberships`
  retained, generic Group rejected), the Auth/Session model (D2/D3 — id +
  platform password, FamilyAdmin-provisioned Accounts, Account-scoped
  persistent Session, optional Account+Device Wagle PIN), Markpoint's target
  URL scoping (D7 — `/families/{familyId}/markpoint` with server-side
  revalidation), and both data-migration questions (D8 RESET — no Legacy
  identity or point/mission history import). The 5th item, whether the seeded
  Role/Permission **code strings** are final, remains `REQUIRES_PM_REVIEW` /
  `NON_BLOCKING` and is confirmed at the Wave 1 scoped-RBAC Start Gate. For the
  frozen documents and the recalculated plan see
  `MONGLE-APPROVED-DECISIONS-FREEZE-AND-DECOMPOSITION-001`, which graduated
  2026-08-01 — its record is now in `agent-system/graduated/2026-08.md` and its
  report is `engineering/phase2/MONGLE_APPROVED_DECISIONS_FREEZE_AND_DECOMPOSITION_REPORT.md`
  (reference updated by MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001; the previous
  "above" pointer became dangling when that section left this file).
- Next Action: this task's Freeze dependency is satisfied; the remaining open
  items are its own closeout, not a PM decision. FE<->API<->DB vertical wiring
  and any Markpoint ownership work now follow the recalculated Wave plan and
  each task's own Start Gate — a passed Freeze is not by itself implementation
  authorization. Independent QA of this
  task's own claims is a secondary open item, not a blocker for the Freeze
  decision. Once PM has reviewed, the isolated data-backend worktree/branch
  should be cleaned up the same way as A1's (do not remove before that
  review, do not leave it dangling after). MONGLE-TEST-GOVERNANCE-PORTING-001
  below is waiting specifically on this Next Action.

## MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001

- Task ID: MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED (commit `0c2a040`) / INDEPENDENT_QA_PASS (2026-07-31) — this
  task's own report retains its self-assigned CONDITIONAL verdict/sentinel verbatim
  (preserved, not edited); a separate agent session independently verified the Foundation
  commit's exact file diff and token values against the live repository and found no
  discrepancy (see `agent-system/qa/MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001.md`). The
  Closeout Addendum in `MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md` now reads
  `FINAL_VERIFICATION: PASS`. This is the Closeout Contract's documentation-sync gate, not
  a PM graduation decision — Lifecycle stays IN_PROGRESS pending the PM's own decision on
  whether to graduate this task.
- Handoff: agent-system/handoffs/active/MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001.md
- Independent QA: complete — PASS (2026-07-31, separate agent session; see QA Evidence)
- Next Action: PM decision on whether to graduate this task (and its two siblings below)
  now that independent QA has passed; if so, move all three to `graduated/2026-07.md` and
  their handoffs to `handoffs/archive/2026-07/` per the normal graduation procedure.

## MONGLE-W6-1-E2E-HARNESS-RECOVERY-001

- Task ID: MONGLE-W6-1-E2E-HARNESS-RECOVERY-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: READ_ONLY_CHECK_COMPLETE / INDEPENDENT_QA_PASS (2026-07-31) — retracted a
  prior turn's "missing script" claim as a path-lookup error:
  `tests/e2e/scripts/start-mongle-phase1.sh` was present, tracked, executable, and
  byte-identical to its origin commit (`7f1ce9e`) the whole time; no restoration was needed
  or performed. Independently re-verified (SHA-256, `git diff`, `shellcheck`/`bash -n`) by a
  separate agent session as part of the bundled Wave 6.1 QA pass.
- Handoff: agent-system/handoffs/active/MONGLE-W6-1-E2E-HARNESS-RECOVERY-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-1-E2E-HARNESS-RECOVERY-001.md
- Independent QA: complete — PASS (2026-07-31, separate agent session; see QA Evidence)
- Next Action: PM decision on whether to graduate this task alongside its two siblings.

## MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001

- Task ID: MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: INDEPENDENT_QA_PASS (2026-07-31) — self-check evidence (lint PASS, build
  PASS, two independent cold-start Playwright rounds both 66 passed / 0 failed / 4
  intentional skipped with an identical test-identity set, before/after visual diff
  0.000%-0.022% fully attributable to a dynamic seed timestamp, 0 dimension changes, 0
  unexpected console errors, Docker cleanup confirmed at every teardown) was independently
  re-verified by a separate agent session: two fresh cold-start rounds (also 66/0/4,
  identical test-identity set), lint/build re-run, Docker teardown re-confirmed, HEAD/dirty
  state and commit ancestry cross-checked. One correction: the seed-timestamp root cause was
  misattributed to `phase1_seed_synthetic.py` (that script has no Mission-table code; the
  actual source is the `Mission` model's `server_default=func.now()`) — the broader
  conclusion is unaffected; recorded in the Closeout Addendum and `COVERAGE_MAP.md` rather
  than editing this report's original prose.
- Handoff: agent-system/handoffs/active/MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-1-FOUNDATION-E2E-CLOSEOUT-001.md
- Independent QA: complete — PASS (2026-07-31, separate agent session; see QA Evidence)
- PM_EVIDENCE_ACCEPTANCE: APPROVED (2026-07-31) — see the Closeout Addendum in
  `engineering/phase2/MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION_REPORT.md`, now reading
  `FINAL_VERIFICATION: PASS`.
- Next Action: the Wave 6.1 governance-only commit landed as `6c63367` (docs +
  these Agent System records; Avatar-fix code and any A1 code were correctly
  excluded, per plan). Remaining PM decisions: (a) whether to graduate these
  three tasks now that independent QA has passed, (b) whether to keep or
  remove the `mongle-frontend-toolchain` container.

## MONGLE-TEST-GOVERNANCE-PORTING-001

- Task ID: MONGLE-TEST-GOVERNANCE-PORTING-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTATION_COMPLETE / SELF_CHECK_COMPLETE — documentation-only
  test-governance port. No product/test code, package script, CI, Docker, E2E,
  DB, Foundation re-verification, Avatar QA, A1 integration, or DATA-A work was
  performed. Existing Agent System locations remain the policy/Coverage Map
  SSOT; `tests/README.md` is the command/artifact SSOT. The repository
  bootstrap and Claude entrypoint link thinly to the Test Policy and applicable
  FE/BE guide compliance rules.
- Handoff: agent-system/handoffs/active/MONGLE-TEST-GOVERNANCE-PORTING-001.md
- QA Evidence: agent-system/qa/MONGLE-TEST-GOVERNANCE-PORTING-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT

## MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001

- Task ID: MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: Documentation-only minimal guide supplement. Frontend page
  responsibility/source-growth rules and API-schema-first type wording are in
  scope; existing backend giant-source/UoW rules are retained without
  duplication.
- Handoff: agent-system/handoffs/active/MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001.md
- QA Evidence: agent-system/qa/MONGLE-FE-BACKEND-GUIDE-SUPPLEMENT-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT

## MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001

- Task ID: MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: PM decision recorded before feature development: reserve
  `e2e_tester` as a logical synthetic-E2E identity; require isolated data and
  feature event-branch matrices. No account, credential, fixture, DB row, CI,
  or test implementation is created by this documentation task.
- Handoff: agent-system/handoffs/active/MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001.md
- QA Evidence: agent-system/qa/MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT

## MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001

- Task ID: MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: Plan-only enforcement decision: CI/Alembic/dotted-call guard,
  new-spec naming, and synthetic E2E fixture provisioning are reserved as
  separate tasks after DATA-A/A1 contract review; no implementation is
  authorized by this plan.
- Handoff: agent-system/handoffs/active/MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001.md
- QA Evidence: agent-system/qa/MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT

## MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001

- Task ID: MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: Absolute prohibition on agent-created project material outside
  the Git worktree, including `/tmp`, repository-adjacent directories, and
  external worktrees. Historical external paths are documentation only.
- Handoff: agent-system/handoffs/active/MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001.md
- QA Evidence: agent-system/qa/MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001.md
- Independent QA: NOT_REQUIRED_FOR_DOCS_ONLY
- Next Action: WAIT_FOR_DATA_A_RESULT
## MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001

- Task ID: MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS (recovery baseline only; not visual QA)
- Execution: SUCCEEDED
- Closeout Contract: v1
- Handoff: agent-system/handoffs/active/MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001.md
- QA Evidence: agent-system/qa/MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001.md
- Result: canonical archive remeasured; noncanonical connected UI routes detached;
  API, session, authorization, and realtime code parked pending R8 integration.
