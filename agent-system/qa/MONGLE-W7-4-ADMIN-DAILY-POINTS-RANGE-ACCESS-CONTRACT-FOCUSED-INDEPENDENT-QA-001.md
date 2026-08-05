# QA Evidence — MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-FOCUSED-INDEPENDENT-QA-001

- Task ID: `MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-FOCUSED-INDEPENDENT-QA-001`
- author/agent: Independent QA session (fresh session, did not implement the change under review)
- observed_at: 2026-08-05 (session date; environment clock inside containers used UTC, seed fixture dates land in early August 2026)
- git_ref: `281d45a` (`origin/dev-newmarkp`) + the real repo's own uncommitted 2-file diff (`backend/app/domains/admin/router.py`, `frontend/src/pages/AdminDashboard/api/adminApi.ts`), reconstructed independently in a detached scratch worktree — real repo `dev-newmarkp` local HEAD stayed at `97bc09d` throughout, untouched
- environment: isolated Docker stack, project name `mongleqa` (Postgres 16.9-alpine on host port 15444, backend on host port 18011), frontend served natively via `pnpm run dev` (Vite, :5174, `VITE_DEV_PROXY_TARGET=http://localhost:18011`); separate isolated pytest DB, project name `mongleqapytest` (Postgres on host port 15445) + `alembic upgrade head` (22 migrations) + `database/init.sql`. All distinct from the developer's own leftover `mongle` stack (18001/15434), which was left running and untouched throughout.
- evidence: raw command transcript in this session; screenshots at `/tmp/qa-legacy-admin-*.png` and `/tmp/qa-account-admin-*.png` (ephemeral, not committed — regenerable via the same commands recorded here)
- secrets_redacted: `true`
- Verification: `PASS`
- Closeout Contract: `v1`
- Independent from implementer: `true`
- Independent QA: `complete`

## Scope reviewed

The 2-file uncommitted diff on `dev-newmarkp`'s real working tree, applied on top of `281d45a`:

- `backend/app/domains/admin/router.py` — new `GET /api/admin/daily-points/range`, `get_current_admin`-gated, pass-through to the unchanged `get_daily_points_range` service function.
- `frontend/src/pages/AdminDashboard/api/adminApi.ts` — `getDailyPointsRange` now calls `/api/admin/daily-points/range` instead of `/api/daily-points/range`.

Confirmed byte-identical to the diff claimed in the developer's own handoff (`agent-system/handoffs/active/MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-REMEDIATION-001.md`) — direct text diff of the two patch outputs (target-revision checkout vs `git -C /Users/mac/mac_Project/mongle_ui diff HEAD -- <2 files>`) was empty. Also independently spot-checked the developer's claim that both files are byte-identical in their pre-change state between `97bc09d` and `281d45a`: `git diff 97bc09d..281d45a -- <2 files>` in the real repo is empty — confirmed true, "281d45a + current diff" is well-defined.

## Target Revision construction (independently verified)

1. `git -C /Users/mac/mac_Project/mongle_ui worktree add --detach <scratch>/mongle-qa-281d45a 281d45a` — scratch path under this agent's own isolated scratchpad, not repository-adjacent.
2. Overlaid the CURRENT content of the real repo's 2 changed files onto the corresponding paths in the scratch checkout (`cp`, not `git apply`, to avoid any patch-context drift).
3. `git status --short` in the scratch checkout showed exactly those 2 files modified, nothing else.
4. Saved both diffs (`git diff -- <2 files>` in scratch checkout; `git diff HEAD -- <2 files>` in the real repo) to files and ran `diff` between them: exit 0, byte-identical.
5. Confirmed `backend/app/domains/auth/dependencies.py` (the DEFECT-001/002 admin-auth bridge this fix depends on) genuinely differs between `97bc09d` and `281d45a` — the real repo's own checked-out files at `97bc09d` do NOT yet have the Account→admin_auth bridge (`get_current_admin` in a `97bc09d` checkout unconditionally 401s any `role == "account"` token), which is why building from the real dirty working tree as-is (still on `97bc09d`) would have been the wrong Target Revision. Building from `281d45a` was necessary, not optional.

## Commands, exit codes, and results

### Authorization matrix — `GET /api/admin/daily-points/range` (new route)

| Identity | Expected | Observed | Result |
|---|---|---|---|
| Account-native Admin (`admin.a`, linked via `LegacyIdentityMapping` to `admin_auth.id=1`/`dad`) | 200 | 200 | PASS |
| legacy Admin (`dad`, `player_id=3`) | 200 | 200 | PASS |
| legacy Admin, QA-marker row with `player_id=NULL` (inserted for this check, deleted after) | 200 | 200 | PASS |
| ordinary player (`player_id=1`, PIN login) | 401/403 | 401 | PASS |
| non-Admin Account (`owner.a`, no admin_auth mapping) | 401/403 | 401 | PASS |
| unauthenticated (no `Authorization` header) | 401 | 401 | PASS |

Auth mechanism read directly from source (not inferred): `get_current_admin` (`backend/app/domains/auth/dependencies.py`, in the `281d45a` checkout) accepts `role == "admin"` directly, and for `role == "account"` calls `resolve_linked_admin_auth`, which requires a `LegacyIdentityMapping` row (`legacy_system="markpoint"`, `legacy_identity_type="admin_auth"`, `mapping_status="linked"`) tying the Account to a live `admin_auth` row. Any other role, or an Account with no such mapping, falls through to a 401 "Admin token required" — this is why the player and non-Admin-Account cases return 401 rather than 403 (matches the task's own accepted 401/403 either-way criterion).

### Regression — existing routes, unchanged behavior

| Route | Identity | Expected | Observed | Result |
|---|---|---|---|---|
| `GET /api/daily-points/range` | player, self | 200 | 200 | PASS |
| `GET /api/daily-points/range` | player, other `player_id` | 403 | 403 | PASS |
| `GET /api/daily-points/range` | Account-native Admin (deliberately NOT widened) | still 403 | 403 | PASS |
| `GET /api/admin/daily-points` (existing single-day admin route) | legacy Admin (`dad`) | 200 | 200 | PASS |
| `GET /api/account-context` | legacy Admin, `player_id=NULL` (DEFECT-002 bridge) | 403 `mapping_required` | 403 `{"detail":"계정 매핑이 필요합니다"}` | PASS |

### AdminDashboard UI — native `pnpm run dev` + disposable Playwright spec

Credited player 3 (아빠) `+15` via the pre-existing `POST /api/admin/daily-points/adjust` (legacy Admin token), then independently drove the real login UI (not token injection) for both identity types:

- Legacy Admin (`dad`, ID/PW form at `/` → 관리자 로그인): "플레이어 현황" card shows 아빠 `15pt` (not `0pt`), unchanged after a full page reload.
- Account-native Admin (`admin.a`, `/login` form → `/family` → navigated to `/admin`, admitted via `AdminProtectedRoute`'s `isAccountSession && contextIsAdmin` branch): same card shows 아빠 `15pt`, unchanged after reload.
- Viewport sweep (390×844, 820×1180, 1180×820) for both identities: `document.documentElement.scrollWidth > clientWidth` check returned `false` (no horizontal overflow) at all 6 combinations. Screenshots captured.
- Other three players (유빈/유현/엄마) correctly showed `0pt` (no cross-contamination), consistent with only player 3 having been credited.

Root cause of the original bug confirmed by reading `useAdminData.ts` directly: `getDailyPointsRange` calls were made per-player inside a single `Promise.all`; before this fix every call 403'd (player-only route rejecting Admin tokens), the whole `Promise.all` rejected on the first player, and `dailyPoints` state never left its initial `[]` — so `PlayerStatusCard`'s `totalEarned` was always `0` for every player. This diff does not touch `useAdminData.ts`; it fixes the underlying 403 by routing to a new Admin-scoped endpoint, which is sufficient because the `Promise.all` itself only needed its member calls to stop failing.

`useAdminData.ts` error handling itself (unchanged by this diff, checked because the task explicitly asks not to accept silent-`[]`-swallowing as a fix): a genuine failure still only logs `console.error` and leaves `dailyPoints` at its last value — not surfaced to the admin as a toast, not a newly introduced behavior, pre-existing and out of scope for this 2-file change. Flagged as a real but pre-existing gap, not a regression.

### Static / build / test gates (frontend/pnpm)

| Check | Result |
|---|---|
| `pnpm lint` | 0 issues |
| `pnpm run build` (`tsc -b && vite build`) | passed, 0 TS errors, 956ms |
| `git diff --check` (scratch Target Revision checkout) | exit 0 |
| `python3 agent-system/tools/check_all.py` | same warning set produced against the unmodified `281d45a` checkout (this diff touches no `agent-system/` file in the scratch checkout, so the tool's output is identical before/after by construction) — 0 new warnings attributable to this change |

### Backend pytest — full suite, isolated DB

- Environment: fresh `postgres:16.9-alpine` container (port 15445, project `mongleqapytest`), `alembic upgrade head` (22 migrations, clean), `pip install -r requirements-dev.txt` (`pytest==8.3.4`, `pytest-asyncio==0.26.0`, `httpx==0.28.1`) inside the already-built backend image, then `python -m pytest -q`.
- Result: **405 passed, 0 failed, 943 warnings, 276.20s.**
- This is a *stronger* result than the developer's own self-check (404 passed / 1 failed, same total of 405). The registered `KNOWN-W7-5-WAGLE-CONCURRENCY-001` condition (`test_wagle_reliable_service_slice.py::test_outbox_07_two_workers_no_double_claim` and siblings) did not manifest at all in this run — consistent with that row's own documented history of intermittent, non-deterministic failures across many independent runs (some clean, some not). Because the failure did not reproduce here, the task's own conditional instruction ("if you see it fail, produce A/B evidence") does not apply — there was nothing to A/B. A clean 405/405 run is itself independent evidence that this 2-file change does not introduce a new, deterministic failure in that suite.
- Container torn down after use (`docker compose -p mongleqapytest down -v`); confirmed removed.

## Findings

1. All 6 authorization checks on the new route pass exactly as specified — no widening beyond the 3 admin identity classes, no widening of the player-only route.
2. Both required regressions (player-only route self/other, Account-native Admin still blocked there) hold.
3. AdminDashboard balancing card defect is genuinely fixed for both credential systems, verified via real UI login flows (not token injection), holding across reload, at all 3 required viewports.
4. Frontend container build failure (`npm ci` against a repo with only `pnpm-lock.yaml`, no `package-lock.json`) independently reproduced — confirmed real and pre-existing, not something this task could or should fix (native `pnpm run dev` used instead, as directed).
5. Full backend suite: 405/405 clean, stronger than developer's self-check.
6. No fixture/mock stood in for auth or DB — every check used real JWTs from real `/api/auth/login`, `/api/auth/admin/login`, `/api/auth/account/login` responses against a real seeded Postgres.
7. Minor, pre-existing, out-of-scope observation: `useAdminData.ts`'s error path still only `console.error`s on a genuine failure rather than surfacing a toast — not introduced by this diff, not blocking.

## Final QA verdict

- Verdict: PASS

Independent from implementer: true. This session did not write the product code under review; it constructed its own verified Target Revision, its own isolated runtime, and measured every item in the required verification matrix directly.

## Closeout review

- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED`
- QA EVIDENCE: `UPDATED` (this file)
- COVERAGE MAP: `UPDATED` (append-only confirmation line added to the existing `API-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-001` row's Notes; `KNOWN-W7-5-WAGLE-CONCURRENCY-001` row cited, not edited)
- COVERAGE MAP Reason: independent execution evidence now exists for a row that previously only had developer self-check evidence; Verification/Confidence field graduates from "CONFIRMED (Developer self-check)" via an appended note, not a rewrite of developer-authored text.
- CLOSEOUT GATE: `PASS`
