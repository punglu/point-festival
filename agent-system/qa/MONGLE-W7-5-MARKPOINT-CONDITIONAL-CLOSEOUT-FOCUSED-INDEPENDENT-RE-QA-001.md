# Independent Re-QA — MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001

- Task ID: MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001
- Role: Independent QA
- Status: CONDITIONAL / ENVIRONMENT_REQUIRED

## Evidence

- `328d877` is reachable from `origin/dev-newmarkp`; its exact seven-file
  boundary matches Markpoint remediation and its correction sections preserve
  prior text append-only.
- `today_deducted` deterministic boundary test: 1 passed.
- The two formerly OS-timezone-fragile tests plus the new test: 3 passed each
  under Asia/Seoul, UTC, and America/New_York.
- Markpoint suite: 64 passed. Backend collect-only: 405. On one freshly
  initialized isolated PostgreSQL DB, with no reset or code change between:
  Run A **405 passed** (821.43s), Run B **405 passed** (849.08s).
- `docker` is not installed in the measured WSL environment. The required
  `run-w75-full-spec.sh` smoke was therefore not run; this is explicitly
  `ENVIRONMENT_REQUIRED`, not a skip/pass. The isolated DB and QA artifacts
  were removed and Git shows no runner-induced delta.

## Verdict

`MONGLE_W7_5_MARKPOINT_CONDITIONAL_CLOSEOUT_INDEPENDENT_RE_QA_PASS` is **not
declared** because the required Docker E2E 10/10 proof is absent. Run that
single smoke in a Docker-capable Mac environment, then re-check Git cleanup.
W7.5 remains `CONDITIONAL`/`HUMAN_GATE`; no W7.4/W7.6 claim is made.

## Continuation — final E2E evidence attempt (2026-08-04)

Previous verdict is preserved: `CONDITIONAL / ENVIRONMENT_REQUIRED`.

At `HEAD 328d877c162e300ffafbbc566a70d36bba4f3a2d` on `dev-newmarkp`, the
requested preflight measured `docker: command not found`; consequently
`docker version`, `docker compose version`, and `docker ps -a` could not run.
This is a measured `ENVIRONMENT_REQUIRED` condition, not an E2E failure and
not a substituted PASS. The README authority command
`tests/e2e/scripts/run-w75-full-spec.sh` was deliberately not invoked because
its required Docker Engine is unavailable.

Static inspection found no post-`328d877` change in the runner, README, or
E2E Playwright files; `.gitignore` remains pre-existing dirty work. The runner
uses an absolute in-worktree ignored runtime path and contains query readiness,
`init.sql` `ON_ERROR_STOP`, `admin_auth` assertion, bounded Alembic retry,
synthetic credential, backend/frontend readiness, and `trap cleanup`. No
runner container, temporary port/process, or runtime artifact was created by
this non-execution attempt.

Final verdict remains: **CONDITIONAL / ENVIRONMENT_REQUIRED**. No PASS
declarations are made.

## Continuation — non-Docker full-stack equivalent attempt (2026-08-04)

Previous verdict: `CONDITIONAL / ENVIRONMENT_REQUIRED`. Per explicit
architect direction, Docker was treated as an implementation detail and a
native equivalent was attempted: isolated real PostgreSQL database
`mc_qa_markpoint_nondocker_001` on 127.0.0.1:5432, `init.sql` with
`ON_ERROR_STOP`, Alembic `0021` head, `admin_auth` assertion, synthetic seed
and disposable admin credential, then current-worktree uvicorn on 18096 and
pnpm/Vite on 5195. Both HTTP readiness probes passed. The persistent dev
stack on 5432/8000/5173 was observed only and not stopped or written.

The same manual runner config/spec was invoked with the QA Vite base URL and
synthetic credential, but no Chromium test ran: `tests/e2e` has no installed
local Playwright package, so `npx` stopped at an interactive proposal to
install unpinned/latest `playwright@1.62.1`. This was declined and interrupted;
installing a different dependency version would not be the existing runner
contract. Classification: `ENVIRONMENT_REQUIRED` (missing fixed E2E runtime),
not product/test failure and not a skipped PASS.

Task-owned uvicorn/Vite PIDs, QA DB, and ignored in-worktree runtime logs were
removed; 18096/5195 are unbound and no Chromium/Playwright process remains.
No credential was written outside process memory or the disposable DB. During
this attempt three unrelated root untracked prompt files appeared; they were
not created or changed by this Task and were preserved. Final verdict remains
**CONDITIONAL / ENVIRONMENT_REQUIRED**.
