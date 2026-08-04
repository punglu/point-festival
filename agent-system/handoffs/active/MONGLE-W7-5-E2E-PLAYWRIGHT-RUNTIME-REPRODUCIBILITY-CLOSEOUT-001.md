# Handoff — MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001

- Task ID: MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001
- Parent: MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001
- Role: Developer remediation
- Closeout Contract: v1
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001.md

## Start baseline

`dev-newmarkp` at `328d877c162e300ffafbbc566a70d36bba4f3a2d`; worktree was
already dirty with other active-task Agent System changes, frontend npm→pnpm
migration files, and prompt files. Persistent native PostgreSQL/uvicorn/Vite
on 5432/8000/5173 are excluded and protected.

## Authority audit

`tests/e2e` is a standalone npm project: no `pnpm-workspace.yaml` exists. Its
committed npm lock resolves all Playwright packages to 1.58.2; initial local
runtime was absent. Manifest/lock were narrowed to exact 1.58.2, `npm ci`
passed, and the local CLI reported 1.58.2. Fixed local browser installation
used `PLAYWRIGHT_BROWSERS_PATH=0`; Chromium v1208 reached ignored package-local
storage but its required headless-shell component did not complete after over
five minutes. Installer terminated; no fallback/latest/global/home-cache used.

## Commands and outcomes

- `npm install --package-lock-only --save-dev --save-exact @playwright/test@1.58.2`
  produced a two-line exact-range alignment, no dependency drift.
- Runner now invokes `tests/e2e/node_modules/.bin/playwright`, removing its
  interactive `npx` fallback without changing config/spec/test semantics.
- `npm ci`: 3 locked packages installed, audit 0 vulnerabilities.
- Local CLI: `Version 1.58.2`.
- Browser install incomplete as above; therefore no Backend/Vite/Playwright
  full-stack run and no 10-test result is claimed.
- `frontend` pnpm lint and build passed (Node 26 out-of-engine warning only);
  `git diff --check` passed; `check_all.py` emitted no warning for this Task.
- Node 20.20.2/npm 10.8.2 completed fixed Chromium v1208/headless-shell/FFmpeg
  installation and real launch smoke. Isolated DB, Backend 18096, and Vite
  5195 readiness passed. The unchanged local-binary spec then executed **10
  failed / 0 passed / 0 skipped** because the task-owned temporary launcher
  released Backend/Vite after readiness; all failures were 5195 connection
  refusal. Finding `E2E-RUNTIME-F-001`: test-infrastructure lifecycle failure.
  No retry/redesign per scope. QA DB/PIDs/ports/screenshots/logs removed.

## Closeout Synchronization

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: NO_CHANGE_REQUIRED
- COVERAGE MAP Reason: failed execution did not reach a product assertion or
  API result, so behavior coverage classification did not change.
- CLOSEOUT GATE: BLOCKED
- CLOSEOUT GATE Reason: `E2E-RUNTIME-F-001` is unresolved.
