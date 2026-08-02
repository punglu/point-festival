# Task QA Evidence — MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001

| Gate | Evidence | Result |
| --- | --- | --- |
| Lint | `frontend: npx tsc --noEmit -p .` then `npm run lint` | PASS |
| Production build | `frontend: npm run build` (Vite, 626 modules) | PASS |
| Diff integrity | `git diff --check` | PASS, 0 whitespace errors |
| Existing runtime | `mongle-db-1`, `mongle-backend-1` (already running, healthy, real Postgres + FastAPI) | healthy, unmodified |
| Dev-proxy fix | `vite` dev server restarted with `VITE_DEV_PROXY_TARGET=http://localhost:18001` (was defaulting to `localhost:8000`, nothing listening) | fixed, disclosed in Report §7 |
| 64/64 product-entry scenarios | Playwright, real account (`member.a`) + real legacy admin (`dad`) login against the live backend, real trigger click chains, `/tmp/mongle-w7-3-visual-closeout/scripts/verify-w74-entry.mjs` | 64/64 PASS |
| 192 responsive-shell checks | same 64 scenarios re-run at 390×844, 820×1180, 1180×820 | 64/64 PASS at each viewport |
| 63 detached-preview regression + `/login` | `final-regression-checkpoint.mjs`, marker count + console/page error check | 64/64 PASS, 0 marker fail, 0 error fail |
| Existing-route regression | `/`, `/dashboard`, `/admin`, `/admin/missions`, `/admin/points`, `/admin/notifications`, `/login`, `/family`, `/markpoint`, `/wagle`, `/wagle/board`, `/this-not-exist` | all resolve as expected (unauth redirect to `/`, 404 fallback correct) |
| Matrix completeness | `engineering/phase2/MONGLE_W7_4_PRODUCT_STRUCTURE_INTEGRATION_MATRIX.csv` | 64/64 `PRODUCT_STRUCTURE_INTEGRATED` |

## Test-data / environment notes (full disclosure)

- Account login used the repo's own pre-existing seeded synthetic accounts
  (`backend/scripts/phase1_seed_synthetic.py`, `SEED_PASSWORD =
  "Synthetic!Pass9"`) already present in the running dev DB. No seed/reset
  script was re-run (it deletes rows before inserting — running it against
  the already-populated dev DB would have been destructive and was avoided).
- The legacy admin credential (`admin_auth` row for player `dad`, id 3) had
  an unknown password hash. It was reset to a known bcrypt hash for this
  pass only, since this is synthetic seed data in a local dev DB, not real
  user data. Not reverted (no original value to revert to) — disclosed here
  for full transparency rather than left unmentioned.
- Two DB rows were temporarily mutated to reach specific real states, then
  reverted after verification:
  - `markpoint_missions.id=4.status` → `rejected` (to reach `1s`, the
    rejected-mission-detail screen) → reverted to `pending_approval`.
  - `players.id=2.is_locked` was briefly tried and found to be the *wrong*
    mechanism (it disables player selection entirely rather than producing
    the PAGE_LOCAL_STATE 423 flow `1j-1` actually needs) — reverted to
    `false` immediately, not used in the final test. `1j-1` was instead
    reached the way a real user reaches it: 5 consecutive wrong-PIN
    submissions against the real `/api/auth/login` endpoint, which trips
    `MAX_LOGIN_ATTEMPTS`/`lock_until` server-side. `player_auth` login
    attempt counters for player 2 were reset to `0`/`NULL` after each test
    run and are `0`/`NULL` at the end of this pass (verified by direct
    query).

## Genuine gap found and fixed during verification (not just flagged)

`2m`'s prior classification (`KEEP_EXISTING_AS_CANONICAL`, pointing at
`ActiveMissionDetailModal.tsx`) turned out to be wrong on live verification:
the component was never imported anywhere in the app. Fixed with a 16-line
additive change to
`frontend/src/pages/AdminDashboard/views/DashboardView/DashboardView.tsx`
(new `"활성 미션 상세 보기"` button, reuses data already in scope — no new
API call). Re-verified after the fix: PASS. See Report §4 and §7.

## Limits

This evidence is a structural product-integration verification: real routes,
real triggers, real authenticated navigation, zero console/page errors, and
zero visual/marker regressions. It does not validate business-logic
correctness of the underlying (mostly pre-existing) API endpoints, and does
not constitute the independent QA pass called for by
`agent-system/qa/TEST_POLICY.md` / `.claude/agents/test-agent.md` — that
remains `INDEPENDENT_QA_PENDING`, which the task's own PASS criteria list as
an acceptable open item.

24 of 64 rows are `DATA_AND_BEHAVIOR_WIRING_PENDING` and 34/64
`MUTATION_WIRING_PENDING` — real backend data/mutation wiring for these
screens is explicitly deferred to W7.5, not attempted here (no new
Backend/API/DTO work was in scope for this task). One row (`3h`, account
deletion) is a disclosed `TRUE_FUNCTIONAL_GAP`: no backend policy or code
for account deletion exists anywhere in the product (confirmed via
repo-wide grep before classifying), so the destructive action intentionally
does nothing beyond closing the view locally.
