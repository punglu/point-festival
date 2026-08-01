# Current Relay

Current Task: none — `MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001`
released its write claim on 2026-08-01.

- Outcome: **the `MONGLE-PARALLEL-W2-W4-001` bundle is COMPLETE and graduated**,
  together with both frontend naming tasks and both independent QAs. The three
  verifications the combined QA had left blocked were executed against the
  current worktree:
  - clean isolated production build — PASS (`✓ built in 1.00s`)
  - current-source Playwright — **90 collected / 86 passed / 0 failed / 4 skipped / 0 retries**
  - focused backend Wagle seam test — **3 collected / 3 passed**
- The browser is **proven**, not assumed, to have run the build made from this
  worktree: worktree ⇄ image label ⇄ served fingerprint all equal
  `cf5ed0ac…e736`, plus a content-hashed entry-bundle match, plus an in-page
  assertion on all five projects.
- Evidence: `agent-system/qa/MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001.md`.

## Next Task

**Next Wave Start Review.** Nothing in the naming bundle is pending. Before any
new implementation task, note the outstanding traceability item below.

## What changed in the E2E harness — read before running E2E

- **`reuseExistingServer` is now `false`.** A leftover `mc_phase1` stack makes
  the next run fail loudly (`http://localhost:13001 is already used`) instead of
  silently reusing it. That is deliberate: `reuseExistingServer: true` was the
  wider of the two stale-image paths — when the port already answers, Playwright
  skips the start script entirely, so a `--build` inside it never runs. Run
  `tests/e2e/scripts/stop-mongle-phase1.sh` first if a stack is up.
- **A current-source guard runs at the end of bring-up.** It compares the
  worktree source fingerprint, the fingerprint labelled into the running image,
  and the fingerprint the browser fetches from the served app. It **recomputes**
  the worktree value rather than trusting `MONGLE_FRONTEND_FINGERPRINT` — if it
  is ever changed to trust the env var, it stops being a guard. Verified by
  making it fail against a planted stale image, not by reading its PASS output.
- **`frontend/.dockerignore` now exists.** Before it, `COPY . .` layered the
  host's darwin-arm64 `node_modules` over the tree `npm ci` had just installed
  for linux-arm64/musl. The build survived only because Rollup picks its native
  binary by platform at runtime and the musl one happened to remain reachable —
  a coincidence, not a contract. Do not remove `node_modules` from that file;
  the guard fails if you do.
- **`backend/requirements-dev.txt` now exists.** The repository previously
  declared no test dependencies at all, while `tests/README.md` and
  `engineering/TESTING_GUIDE.md` both document `python3 -m pytest -q`. On a host
  without `pytest-asyncio` that produces a collection error which reads exactly
  like a product failure. `pytest-asyncio` is pinned `0.26.0` because
  `backend/pytest.ini` sets `asyncio_default_test_loop_scope`, which 0.25.x
  silently ignores — measured here as a teardown error while the tests passed.

## Rules that stay in force

- **Anything new in the messaging domain is Wagle.** Do not emit the historical
  name in a new event, API, DB or test contract. It is legitimate only inside
  migrations `0002`–`0005` and `0007` (as the rename's source), in Axis-A and
  historical documents, and in past commit messages.
- **The retired namespace is deliberately assembled as `'na' + 'ran'`** in
  `frontend/src/shared/storage/activeFamilyStorageMigration.ts` and in
  `tests/e2e/specs-mongle/01-shell.spec.ts`. Do not inline it as a literal — a
  repository-wide sweep would rewrite it into the canonical key and turn the
  migration into a no-op that discards every user's selected Family. Two such
  sweep-induced inversions have already happened.
- **The shipped bundle contains exactly one `naran` occurrence and must.** It is
  the constant-folded migration source; without it the one-time migration cannot
  read the old key in a real browser. Do not "fix" it to zero.
- Access = ACTIVE subscription AND ACTIVE membership AND no ACTIVE restriction.
  Mission participation is not an input, and no `MarkpointParticipant` aggregate
  exists.
- FamilyAdmin is never automatically ServiceAdmin. Migration `0006` removed
  `markpoint.missions.manage` / `markpoint.points.adjust` from every FAMILY-scope
  role. An E2E assertion that a FAMILY owner *sees* "미션 관리" was found pinning
  that escalation in place and has been inverted — do not restore it.

## Carried-forward items the next writer must not mistake for settled

- **`TRACEABILITY_GAP` — nothing in this bundle is committed.** The renamed
  Wagle domain and tests, migrations `0005`–`0008`, the Markpoint access/relay
  code, the frontend naming work, the storage-migration module, the harness
  corrections, the Target documents and the Agent System records are all
  uncommitted working state at `0d9280c`. PM performs commit/push.
- **Outbox consumption is Wave 3.** Events are recorded durably; nothing
  delivers them. `claim_batch()` exists for a future dispatcher.
- **The relay has no production caller yet** — Markpoint's Wave 5 product code
  will be the first.
- **Unread excludes SERVICE_ACTION messages**, inherited from `read_state()` and
  matched deliberately so list and detail agree. The user-visible rule is
  `D6-P4`, undecided — do not "fix" it as a bug without that decision.
- **No frontend component-test framework exists** — only
  `tokenContract.test.mjs`. Screen behaviour is pinned at the API-contract seam
  and by the Playwright suite.
- **`docker-compose.phase2.yml` still does not exist**, though
  `backend/tests/conftest.py` targets `127.0.0.1:15435`. The disposable-DB setup
  is done by hand and needs `psql -v ON_ERROR_STOP=1` plus a real readiness
  check — without both, a silently failing `init.sql` looks like a mass product
  failure.
- **9 documented-but-unregistered tasks** remain unregistered by PM decision.
- **Undocumented external worktree** under `/private/tmp/claude-501/...` —
  Human Gate under `DEC-2026-005`.
- **`PHASE0-AUTOMATED-GAP-CLOSEOUT-001`** is still `SUSPENDED` with measured
  authorization defects in the legacy mission/daily-point/notification routes.

## Worktree state

HEAD `0d9280c`, unchanged throughout. Branch `dev-newmarkp`. No commit, push,
merge, rebase or PR was made by any task in this bundle. Nothing belonging to
another task was reset, restored, cleaned or stashed. The host's `node_modules`
was never deleted or overwritten — every frontend build ran in a throwaway
container with its own dependency tree.
