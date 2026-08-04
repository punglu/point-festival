# Test Execution, Environment, and Artifact Guide

This is the command, environment, secret-handling, artifact, and cleanup SSOT.
Test selection and Coverage Map updates are governed by
[`agent-system/qa/TEST_POLICY.md`](../agent-system/qa/TEST_POLICY.md); current
coverage status is in
[`agent-system/qa/COVERAGE_MAP.md`](../agent-system/qa/COVERAGE_MAP.md).

## Actual package managers and commands

- Frontend package manager: `npm` (the supported Node/npm range is declared in
  `frontend/package.json`). Available checks are `cd frontend && npm run lint`
  and `cd frontend && npm run build`.
- E2E package manager: `npm`, from `tests/e2e/`. The available scripts are
  `npm test` and `npm run test:headed`; both invoke the default
  `playwright.config.ts`.
- Mongle shell Playwright uses its explicit existing config, not a package
  script: `cd tests/e2e && npx playwright test --config playwright.mongle.config.ts`.
- Backend pytest config is `backend/pytest.ini`; the measured invocation is
  `cd backend && python3 -m pytest -q`.
- Existing API checks have no package script: `PHASE0_API_BASE_URL=http://localhost:18000 bash tests/api/test_weekly_api.sh` and
  `PHASE0_API_BASE_URL=http://localhost:18000 python3 tests/api/e2e_scenario_test_v2.py`.
- No additional test script is defined: `SCRIPT_NOT_YET_DEFINED`.

## W7.5 full permanent spec (`04-w75-data-wiring.spec.ts`), including `2t`

`tests/e2e/scripts/run-w75-full-spec.sh` is a self-contained, no-manual-steps
runner for the full permanent `specs-mongle/04-w75-data-wiring.spec.ts`, added
during `MONGLE-W7-5-INDEPENDENT-QA-REMEDIATION-001` because Independent QA had
no documented way to reproduce the spec's `2t` (admin notification send) case,
which requires a `MONGLE_W75_ADMIN_PASSWORD` for the seeded legacy admin
account ("dad") that nothing in the repository previously generated for them.

Run it with no arguments and no environment setup:

```bash
tests/e2e/scripts/run-w75-full-spec.sh
```

## Fixed local Playwright runtime

`tests/e2e` is an npm project, not a pnpm workspace. Its committed
`package-lock.json` pins `@playwright/test`, `playwright`, and
`playwright-core` to `1.58.2`. Install exactly that locked runtime with:

```bash
cd tests/e2e && npm ci
cd tests/e2e && PLAYWRIGHT_BROWSERS_PATH=0 ./node_modules/.bin/playwright install chromium
```

`PLAYWRIGHT_BROWSERS_PATH=0` keeps the matching Chromium beside the local
package under ignored `node_modules`, not in a user-home cache. Invoke the
local binary (or the package's `npm test` script); do not use an interactive
`npx`/latest install path.

It brings up a dedicated, disposable `postgres:16.9-alpine` container (never
the shared `mc_phase0`/`mc_phase1` Compose stacks and never the persistent dev
stack on `15434`/`18001`/`13001`), runs `alembic upgrade head`, runs the
repository's own `backend/scripts/phase1_seed_synthetic.py`, generates a
random password locally and writes only its bcrypt hash into that disposable
database's `admin_auth` row for `dad` (the plaintext is exported to the
script's own environment for the one Playwright invocation below and is never
written to a file, logged, or persisted anywhere), starts a throwaway backend
and frontend against that database, runs the full spec, and tears everything
down on exit (`trap cleanup EXIT`) whether the run passed or failed. Exit code
is Playwright's own exit code.

The throwaway backend/frontend logs for each invocation live at
`tests/e2e/.runtime/w75-runner/run-<timestamp>-<pid>/` — an ignored,
in-worktree, per-run directory (`tests/e2e/.runtime/` is gitignored), printed
by the script itself. This replaces an earlier version that wrote to
`/tmp/mc_w75_spec_runner_*.log`, which violated the repository-boundary
policy (`AGENTS.md`/`agent-system/rules.md`) and blocked Independent QA from
running this script at all (`HARDENING-QA-F-002`,
`MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001`). On a passing run the
per-run directory is removed automatically; on a failing run it is kept
(path printed) as diagnostic evidence.

Default ports are `15493` (Postgres), `18096` (backend), `5195` (frontend);
override with `MONGLE_W75_DB_PORT` / `MONGLE_W75_BACKEND_PORT` /
`MONGLE_W75_FRONTEND_PORT` if those collide with something else already
running. Expected result: **10 passed, 0 skipped, 0 failed**, including on
back-to-back consecutive invocations with no manual pause between them
(`RE-QA-F-2T-RUNNER-FLAKY`, fixed in
`MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001`: the script now waits
for Postgres to accept a real query, not just `pg_isready`, loads
`database/init.sql` with `ON_ERROR_STOP=1` and no error-swallowing `|| true`,
asserts `admin_auth` exists afterward, and retries `alembic upgrade head` a
few times before failing loudly).

### Native (no-Docker) equivalent

`tests/e2e/scripts/run-w75-full-spec-native.sh`, added by
`MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001`, is the same
runner for environments with no Docker: it provisions a disposable database
on an already-running **native** local PostgreSQL cluster instead of a
`postgres:16.9-alpine` container (`CREATE DATABASE`/`DROP DATABASE` against
`127.0.0.1:5432`, same role the environment's own local dev setup already
uses), then follows the identical `init.sql` → `alembic stamp
0000_legacy_schema_baseline` → `alembic upgrade head` → seed → synthetic
admin password → backend → frontend → Playwright → cleanup sequence.
Requires the fixed local Playwright runtime above already installed, and
`backend/.venv` (not `python3.11`) as its Python interpreter. Same
`MONGLE_W75_BACKEND_PORT`/`MONGLE_W75_FRONTEND_PORT` overrides; Postgres
port is fixed at the local cluster's own `5432` (`MONGLE_W75_NATIVE_DB_PASSWORD`
overrides the DB role password if it differs from the environment's default).
Expected result: **10 passed, 0 skipped, 0 failed** — independently confirmed
once, 53.9s, both backend and frontend PIDs alive immediately before
Playwright started and immediately after it finished.

This script exists because a task-owned temporary native launcher used
earlier released the backend/frontend processes immediately after readiness
instead of holding them until Playwright finished, so every test failed with
`net::ERR_CONNECTION_REFUSED` before reaching any product assertion
(`E2E-RUNTIME-F-001`) — most plausibly because that earlier attempt ran its
entire multi-minute lifecycle as a single foreground command inside a tool
with a default ~120s execution timeout, which would kill the whole process
tree (including its own backgrounded services) right around when Playwright
was starting. `run-w75-full-spec-native.sh` reuses `run-w75-full-spec.sh`'s
own already-proven `( cd dir && exec ... ) & PID=$!` pattern verbatim for
starting each service (top-level scope, never inside a `$(...)` command
substitution or a function whose return would end the backgrounding
subshell), adds a `kill -0 "$PID"` liveness re-check immediately before
Playwright starts (not just an HTTP readiness check, which alone cannot
distinguish "ready" from "ready, then already dying"), and must itself be
invoked as a **background** shell command (not a single foreground call
subject to a short execution timeout) in any environment where the launcher
is driven by a tool with its own command timeout.

## Environment and data safety

`e2e_tester` is the reserved logical identity for synthetic E2E work. It is
not provisioned by this documentation contract and never implies an operating
credential or real-data access. Provision it only through the separately
approved task required by the
[E2E synthetic-data boundary and event-matrix decision](../agent-system/decisions/DEC-2026-003-e2e-synthetic-data-and-event-matrix.md).

The default E2E config starts the isolated `mc_phase0` Compose runtime. The
Mongle config starts and tears down isolated `mc_phase1`. Their source of truth
is the corresponding Playwright config and scripts; do not run either against
an operating DB, NAS, or an unrelated running Compose project. Docker is not
needed for static checks, frontend lint/build, or pytest unless the selected
test itself needs services.

Use only synthetic data. A synthetic writer must use a marker, record exact
primary keys and creation scope, separate it from business data, remove it at
the end, and demonstrate repeat-safe cleanup. Without an isolated environment
and that fixture discipline, classify destructive automation as
`UNSAFE_ON_SHARED_DB` rather than running it.

## Secrets and artifacts

Keep environment files and credentials local; never paste tokens, passwords,
personal data, or raw secret-bearing logs into a report or artifact. Existing
test files may use synthetic credentials; they are not operating credentials.

Playwright is configured for failure screenshots. Default output is under
`tests/e2e/test-results/` and Playwright's default report directory when a
reporter creates one. The Mongle capture manifest's `/tmp` path is historical
only. Under the repository-boundary decision, do not run or update a workflow
that creates external project artifacts until a separately approved task moves
its output inside the worktree. Do not add generated screenshots, video, or
trace files to Git unless a task explicitly approves a sanitized artifact.
Preserve failure screenshot/video/trace evidence only as needed and redact
secrets before sharing.

The Mongle config's global teardown calls
`tests/e2e/scripts/stop-mongle-phase1.sh`; if a run is interrupted, use that
existing script from its documented context to clean up only `mc_phase1`.
Never use global Docker prune or stop another Compose project.

## Failure report minimum

Record task ID, command, exit code, HEAD, environment, selected tests/cases,
artifact location, DB/data scope, and one policy classification:
`PRODUCT_DEFECT`, `TEST_DEFECT`, `FIXTURE_OR_DATA`, `ENVIRONMENT`,
`KNOWN_CONDITION`, or `UNRELATED_FAILURE`. If execution conditions are absent,
record one `BLOCKED` category from the Test Policy instead of reporting PASS.
