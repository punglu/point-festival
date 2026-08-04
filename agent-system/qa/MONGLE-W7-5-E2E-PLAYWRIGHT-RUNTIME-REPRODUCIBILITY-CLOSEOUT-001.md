# Task QA Evidence — MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001

- Task ID: MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001
- Parent: MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001
- Role: Developer self-check evidence
- Status: CONDITIONAL / ENVIRONMENT_REQUIRED

## Runtime authority audit

`tests/e2e` is a standalone npm project; no `pnpm-workspace.yaml` exists.
The committed npm lock had already resolved `@playwright/test`, `playwright`,
and `playwright-core` to 1.58.2, while the manifest's caret range was not a
strict reproducibility contract. The task changed only `tests/e2e/package.json`
and its existing `package-lock.json` to exact `1.58.2` (two-line lock/manifest
alignment), replaced the runner's final `npx playwright` invocation with its
already-installed local binary, and documented the same local path. `npm ci` installed the locked local CLI and
`PLAYWRIGHT_BROWSERS_PATH=0 ./node_modules/.bin/playwright --version` reported
`1.58.2`; no interactive/latest/dlx/npx path was accepted.

## Browser runtime

The fixed local installer was invoked with `PLAYWRIGHT_BROWSERS_PATH=0`, placing
Chromium v1208 under ignored worktree `tests/e2e/node_modules/playwright-core/
.local-browsers/`. The Chromium package downloaded, but the installer did not
complete its required headless-shell component after more than five minutes
with an active CDN connection. It was terminated rather than using an
incomplete browser, a home-cache, a global package, or an unpinned fallback.

## Verdict

`CONDITIONAL / ENVIRONMENT_REQUIRED`: fixed CLI authority is established, but
the fixed Chromium runtime is incomplete, so no Playwright/Chromium/full-stack
10-test run occurred. Product, test assertions, migrations, seed, persistent
dev DB, and existing processes were not changed. Independent QA remains
pending; no QA PASS claim is made.

## Static verification

`frontend` `pnpm run lint` and `pnpm run build` both passed. The host reports
Node 26.2.0 outside the declared Node 20.x range as a warning only; no build
or lint error occurred. `git diff --check` passed and `check_all.py` reported
no warning for this Task lineage.

## Node 20 continuation — executed failure

Previous `CONDITIONAL / ENVIRONMENT_REQUIRED` evidence above is preserved.
Using nvm Node 20.20.2 / npm 10.8.2, the fixed local 1.58.2 installer completed
Chromium v1208, headless-shell, and FFmpeg under ignored package-local storage.
A real headless browser launch/page-title smoke passed.

Fresh isolated PostgreSQL `mc_qa_markpoint_node20_001` passed query readiness,
`init.sql` `ON_ERROR_STOP`, Alembic `0021`, `admin_auth`, and synthetic seed.
Current-worktree uvicorn 18096 and Vite 5195 both passed HTTP readiness. The
unchanged local-binary 10-test spec then executed and recorded **10 failed / 0
passed / 0 skipped**. All failures were `net::ERR_CONNECTION_REFUSED` at 5195:
the task-owned temporary launcher had ended both QA servers after readiness,
before the spec completed. This establishes `E2E-RUNTIME-F-001`, a test-
infrastructure lifecycle failure; it is not evidence of a product assertion or
API defect. No retry or launcher redesign was performed.

QA DB, task-owned PIDs/ports, Playwright screenshots/logs, and runtime files
were removed. Persistent dev stack and pre-existing dirty work remain intact.
Final developer verdict: **FAIL**. Independent QA is not awarded or claimed.
