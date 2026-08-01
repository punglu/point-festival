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
