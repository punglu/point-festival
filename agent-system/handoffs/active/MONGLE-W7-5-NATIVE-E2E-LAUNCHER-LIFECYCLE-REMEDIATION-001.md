# Handoff — MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001

- Task ID: MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001

## Origin

Parent: `MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001`.
Blocking finding: `E2E-RUNTIME-F-001` — Node 20.20.2, Playwright 1.58.2,
Chromium v1208, isolated PostgreSQL, Backend readiness, and Vite readiness
all measured PASS in that task, but the existing 10-test permanent spec
still measured 10 failed / 0 passed / 0 skipped, every failure a plain
`net::ERR_CONNECTION_REFUSED` against Vite before any product assertion was
reached. This is not a product defect — no assertion, backend endpoint, or
DB state was ever exercised.

## Root cause

The launcher that earlier task used is not present in the repository (it
was an ephemeral, uncommitted script, already removed by that task's own
cleanup) — this handoff cannot cite its exact source. Its own relay note
states the mechanism precisely enough to act on: "the task-owned temporary
launcher released QA Backend/Vite after readiness." The most plausible
concrete cause, given this execution environment: the earlier attempt most
likely ran its entire multi-minute lifecycle (DB create → `init.sql` →
Alembic through `0021` → seed → backend start → frontend start → Playwright)
as a single **foreground** shell command inside a tool whose default
execution timeout is well under the time that sequence needs — this
repository's own Bash tool defaults to 120s. DB provisioning through backend/
frontend readiness alone measured close to a minute in this remediation's
own run; a foreground invocation hitting that timeout right as Playwright
was starting would kill the whole process tree, including the just-started
backend/frontend it owned as background children — exactly matching "passed
readiness, then failed all 10 immediately with connection-refused."

Rather than guess further at a script that no longer exists, this task built
a fresh native launcher directly from this repository's own **already-proven-
correct** pattern: `tests/e2e/scripts/run-w75-full-spec.sh` (the Docker-based
runner) already starts its backend/frontend with `( cd dir && exec ... ) &
PID=$!` at top-level script scope, registers `trap cleanup EXIT` once at top
level, and runs Playwright in the foreground — a structure that does not
exhibit any of the specific failure shapes named in this task's own Section 3
(no command-substitution-wrapped start, no function-scoped trap, no
subshell that exits before its background child). That script has been used
successfully by multiple prior tasks in this repository. The new native
launcher reuses that exact construct verbatim for its own service-start
lines, swapping only the Postgres provisioning mechanism (native `CREATE
DATABASE` on the existing local cluster instead of a Docker container) and
the Python interpreter (`backend/.venv/bin/python`, since `python3.11` is not
installed in this environment).

## Changes

New file: `tests/e2e/scripts/run-w75-full-spec-native.sh`. Adds, beyond what
`run-w75-full-spec.sh` already does:

- A `kill -0 "$PID"` liveness check inside each readiness-polling loop
  itself (not only an HTTP check), so a process that dies *during* the
  readiness wait produces a specific `FATAL: ... exited during readiness
  wait` message instead of silently retrying HTTP checks against a PID that
  no longer exists.
- A second `kill -0` re-check for both PIDs immediately before Playwright
  starts, per this task's own Section 6 requirement — readiness a few
  seconds ago is not proof of liveness right now.
- A post-Playwright liveness log line for both PIDs, so a run that fails
  can distinguish "services died mid-suite" from "services survived, a real
  test failed."
- The cleanup trap logs whether each PID was actually alive at cleanup time
  before attempting to kill it, so a log always shows genuine before/after
  process state rather than a bare "kill" call whose outcome is invisible.

No product code, backend API, migration, seed content, Playwright spec,
assertion, timeout, retry, or skip was touched. `tests/e2e/package.json`,
`package-lock.json`, `playwright.mongle-manual.config.ts`, and
`run-w75-full-spec.sh` (the Docker variant) are all unmodified by this task
— confirmed via `git diff --check` producing no delta on those paths beyond
what the parent task (`MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-
CLOSEOUT-001`) already introduced before this task started.

## Lifecycle smoke (Section 8)

A standalone smoke (not the full launcher — backend + frontend start only,
same `( cd dir && exec ... ) & PID=$!` construct, no Playwright) held both
services for ~24s with 3 liveness+HTTP checks at ~8s intervals:

```text
check 1: backend PID=alive http=200 | frontend PID=alive http=200
check 2: backend PID=alive http=200 | frontend PID=alive http=200
check 3: backend PID=alive http=200 | frontend PID=alive http=200
```

0 premature exits, cleanup successful. Proceeded to the full run only after
this passed, per this task's own Section 8 gate.

## Full-Stack E2E (Section 9)

Invoked as a **background** shell command (not a single foreground call
subject to a short execution timeout — the specific condition this task's
own root-cause section identifies as the likely original defect).

```text
Node 20.20.2, local Playwright 1.58.2, Chromium v1208 (PLAYWRIGHT_BROWSERS_PATH=0)
Native disposable PostgreSQL (mc_w75_native_runner, dropped after use)
Current-worktree Backend (port 18096), current-worktree Vite (port 5195)
Unchanged specs-mongle/04-w75-data-wiring.spec.ts, local binary
  (tests/e2e/node_modules/.bin/playwright), no npx/latest, no grep/select,
  no retry/skip/timeout change.

Both PIDs confirmed alive immediately before Playwright start.
10 passed (53.9s), 0 failed, 0 skipped.
Both PIDs confirmed still alive immediately after Playwright finished.
```

Per-test results (all 10, unchanged spec, unchanged assertions):

```text
✓ 1a-1 — Account-native login › a real account signs in and reaches /family
✓ 1a-1 — Account-native login › a wrong password shows a real error, not a silent no-op
✓ 1r — family creation › creating a family calls the real API and appears in the family list
✓ 1q — family member list › member names are real, not raw account IDs
✓ 1t — Wagle room member list › room member names are real, not raw family_membership_ids
✓ 1f — profile › the profile screen shows a real display name and level, not the fixture
✓ 1k — mission checklist toggle › tapping a checklist item calls the real endpoint and the change persists on reload
✓ 2g — Wagle reply › replying to a message sends a real reply_to_message_id and renders the quoted preview
✓ 2t — admin notification send › sending a notification calls the real API and closes the form on success
✓ 3c/3d/3e — Wagle board reuse, comments, reactions › a real board post renders, opens, and accepts a real comment; reactions rank it in Popular
```

## Product path confirmation (Section 10)

Chromium → Vite (port 5195, current worktree, `VITE_DEV_PROXY_TARGET` pointed
at the throwaway backend) → Backend (port 18096, current worktree) →
isolated native PostgreSQL (`mc_w75_native_runner`). Evidence: the launcher's
own captured stdout shows the exact sequence (DB create → schema load →
migrate → seed → backend readiness on `:18096/docs` → frontend readiness on
`:5195/`) with no error at any step; every one of the 10 test names is
itself an assertion that the rendered value is the real API/DB value "not
the fixture" / "not raw IDs" / "not a silent no-op" — these are the same
tests that failed 10/10 under `E2E-RUNTIME-F-001` for a connectivity reason
having nothing to do with their own content, and now pass under the fixed
lifecycle with their own assertions unchanged. 0 mock API used (the spec
makes no request mocking calls — confirmed by the spec being byte-identical
to its already-audited state, not modified by this task). 0 accidental
connection to the persistent dev stack: distinct ports throughout (`18096`/
`5195` vs. the persistent stack's own `8000`/`5174`), and the persistent
stack (`dev.sh`, this session's own separate, unrelated manual-testing setup)
was confirmed still running and responsive both before and after this run.

## Cleanup (Section 12)

```text
QA database (mc_w75_native_runner): removed, confirmed via pg_database query
Backend PID: killed at cleanup, confirmed dead
Vite PID: killed at cleanup, confirmed dead
Chromium: Playwright's own teardown (headless, process-scoped to the
  Playwright invocation, exits with it)
Runtime log directory: removed automatically (PLAYWRIGHT_EXIT=0)
QA ports (18096, 5195): confirmed free after cleanup
Persistent dev stack (8000/5174, this session's own dev.sh): confirmed
  still running, unaffected, responded 200 after this task's own cleanup
Credential residue: 0 (the synthetic admin password lived only in this
  script's own environment for the one Playwright invocation, per the same
  discipline as run-w75-full-spec.sh; never written to a file/log)
```

## Git Integrity (Section 13)

```text
Start: 15 tracked-modified + 2 tracked-renamed + 14 untracked entries
  (all pre-existing, from prior tasks/sessions in this same worktree —
  none owned by this task)
End: same set, plus this task's own additions:
  ?? tests/e2e/scripts/run-w75-full-spec-native.sh
  M  tests/README.md (native-launcher documentation section)
  ?? agent-system/handoffs/active/MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001.md
  ?? agent-system/qa/MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001.md
  M  agent-system/active.md / agent-system/relay/current.md / agent-system/qa/COVERAGE_MAP.md
git diff --check: clean, both start and end.
No product code, backend API, Markpoint code, migration, Playwright spec,
  assertion, retry/timeout/skip, or runtime tracked artifact touched.
No other task's file touched.
```

## Static Verification (Section 14)

```text
frontend lint: PASS (0 errors)
frontend build: PASS (pre-existing chunk-size warning only, unrelated)
bash -n tests/e2e/scripts/run-w75-full-spec-native.sh: PASS
shellcheck: not installed in this environment, not documented as this
  repository's required tool in tests/README.md; bash -n substitutes as the
  available syntax gate
git diff --check: clean
agent-system/tools/check_all.py: 0 warnings for this task's own Task ID
  lineage
```

Backend's 405-test suite and the Markpoint suite were not re-run, per this
task's own Section 14 instruction: no backend/product code changed, and
independent evidence for both already exists from prior tasks this session.

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001.md

`CLOSEOUT GATE: PASS` means only that the four documentation obligations are
synchronized — it does not mean Independent QA PASS. This Developer session
does not self-declare Independent QA PASS for its own work, per this
repository's own standing rule.

## Not independently measured / estimates disclosed

- The exact original buggy launcher script's content is unknown (removed by
  its own author's cleanup before this task started) — the root cause above
  is the most plausible reconstruction from the symptom and this
  environment's own known tool-timeout behavior, not a literal diff-based
  diagnosis of the original defect.
- This 10/10 result was produced by **one** run, not a repeated-run
  stability check (the parent finding's own scope was "does the suite run
  to completion and reach product assertions at all," not a repeat-run
  flake-hunt) — a follow-up Independent QA may reasonably want at least one
  more independent invocation before treating this as unconditionally
  stable.
