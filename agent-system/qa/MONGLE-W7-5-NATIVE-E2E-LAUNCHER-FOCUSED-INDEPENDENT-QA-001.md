# Independent QA — MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001

```text
Task:    MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001
Target:  MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001
Parent:  MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001
Finding: E2E-RUNTIME-F-001
Observed: 2026-08-04, branch dev-newmarkp, HEAD 328d877c162e300ffafbbc566a70d36bba4f3a2d
Verdict: CONDITIONAL
```

## Baseline

```text
worktree: /appl/point-festival
branch:   dev-newmarkp
HEAD:     328d877 (unchanged start -> end)
start dirty: 15 tracked-modified/renamed + 14 untracked (all pre-existing,
  from prior tasks this same session — none owned by this QA pass)
staged:    none beyond the pre-existing renames already in the index
stash:     empty
git diff --check: clean, start and end
Node (system default): v26.2.0 / npm 11.13.0
Node (fixed local, via nvm path): v20.20.2 / npm 10.8.2 — used for all
  Playwright/launcher invocations below, matching the Developer's own
  documented fixed runtime
Existing processes/ports at start: persistent dev stack only
  (mc_festival Postgres connections, uvicorn :8000, vite :5174 — this
  session's own separate, unrelated dev.sh setup). No QA ports occupied.
```

## Root Cause Handling (per this task's own Section 2 constraint)

```text
Observed original failure (E2E-RUNTIME-F-001):
  readiness passed, then Backend/Vite ended before Playwright completed,
  10/10 net::ERR_CONNECTION_REFUSED.

Original launcher root cause: UNVERIFIABLE — the original launcher artifact
  no longer exists in this repository; not claimed as measured fact here or
  in the Developer's own handoff.

Most likely cause (Developer's own reconstruction, not re-asserted as fact
  by this QA): an outer execution-timeout / process-tree termination
  hitting the original launcher's own foreground invocation.

Verified remediation target (this QA's actual scope): whether the NEW
  launcher (tests/e2e/scripts/run-w75-full-spec-native.sh) holds Backend/
  Vite alive until Playwright completes and runs cleanup only afterward —
  independently confirmed true in both runs below, regardless of whatever
  the original launcher's exact defect was.
```

## Launcher Audit (Section 5, static)

Read `tests/e2e/scripts/run-w75-full-spec-native.sh` in full, independently
(not from the Developer's own description alone):

```text
Backend/Vite started at top-level script scope:        CONFIRMED (lines 127, 148)
PID captured via $! directly, same logical line as &:  CONFIRMED (not $(...))
No command-substitution-wrapped service start:          CONFIRMED
No short-lived-subshell cleanup trap:                    CONFIRMED — `trap
  cleanup EXIT` registered once at top level (line 88), not inside any
  function or subshell whose own scope would end early
Playwright runs foreground (not backgrounded/disowned):  CONFIRMED (lines
  182-186, blocking `(...)`with no trailing `&`)
kill -0 liveness check before Playwright starts:         CONFIRMED (lines
  170-177), in addition to the HTTP readiness loop
kill -0 liveness check inside readiness polling itself:  CONFIRMED (lines
  134, 154) — a process dying during readiness produces a specific FATAL
  message rather than silently retrying HTTP against a dead PID
Post-Playwright liveness check (both PIDs):               CONFIRMED (lines
  192-202)
cleanup runs after Playwright, not before:                 CONFIRMED — the
  EXIT trap can only fire after the script's own last foreground command
  (Playwright) returns and `exit "$PLAYWRIGHT_EXIT"` is reached
Playwright exit code preserved as launcher exit code:       CONFIRMED —
  `exit "$PLAYWRIGHT_EXIT"` (line 205); independently verified against both
  actual runs below (exit 1 for the failing run, exit 0 for the passing
  run, matching Playwright's own reported pass/fail exactly)
```

Prohibited patterns (`backend_pid=$(start_backend)`, background-then-
immediate-exit, readiness-function-internal cleanup, `nohup`/`disown`,
fixed-sleep-only liveness, `|| true`-masked failures): none found.

```bash
bash -n tests/e2e/scripts/run-w75-full-spec-native.sh   # PASS (silent, exit 0)
```

`shellcheck` is not installed in this environment and is not documented as
this repository's own required tool in `tests/README.md`; `bash -n` is the
available and sufficient syntax gate, matching the Developer's own note.

## Runtime Authority (Section 6)

```text
cd tests/e2e && npm ci                          -> 3 packages, 0 vulnerabilities,
                                                     no interactive/latest prompt
./node_modules/.bin/playwright --version        -> 1.58.2
```

**Procedural note, disclosed rather than hidden**: running `npm ci` deletes
and reinstalls `node_modules`, which also deletes the Chromium binaries
previously installed under `node_modules/playwright-core/.local-browsers/`
(the `PLAYWRIGHT_BROWSERS_PATH=0` local-storage location this project uses).
This QA pass's own `npm ci` (run to independently confirm the lockfile,
per this task's own Section 6 instruction) removed the already-working
Chromium the Developer had installed. Reinstalled per `tests/README.md`'s
own documented second step (`PLAYWRIGHT_BROWSERS_PATH=0 ./node_modules/
.bin/playwright install chromium`) before proceeding. This is a real,
disclosable procedural hazard in the *documented two-step install process*
(covered further in Findings below), not a defect in the native launcher
script itself, which does not run `npm ci` or any install step — it only
assumes the runtime is already installed, exactly like `run-w75-full-
spec.sh` (the Docker variant) already does.

Standalone browser launch/page-title smoke (after reinstall): PASS.

## Lifecycle Smoke (Section 7, independent re-implementation)

Standalone script (backend + frontend only, no Playwright, distinct ports
from both the Developer's own smoke and the actual launcher runs below):

```text
backend PID captured, ready (HTTP 200 on /docs)
frontend PID captured, ready (HTTP 200 on /)
Held ~24s, 3 liveness+HTTP checks at ~8s intervals:
  check 1: backend PID=alive http=200 | frontend PID=alive http=200
  check 2: backend PID=alive http=200 | frontend PID=alive http=200
  check 3: backend PID=alive http=200 | frontend PID=alive http=200
cleanup: both PIDs killed, QA DB dropped, ports confirmed free afterward
```

0 premature exits, 0 readiness loss. PASS.

## Consecutive E2E — 2 runs (Section 8)

Invoked exactly as documented (`tests/e2e/scripts/run-w75-full-spec-
native.sh`, no manual Backend/Vite preparation, no arguments), back-to-back,
no code change, no manual DB cleanup, no launcher edit, no test-selection or
timeout/retry change between the two.

### Run 1

```text
Command: bash tests/e2e/scripts/run-w75-full-spec-native.sh
Node 20.20.2, Playwright 1.58.2, Chromium v1208
Backend PID 65552, Vite PID 65584
Backend/Vite confirmed alive immediately before Playwright start.

  8 failed, 2 passed (37.2s)
```

All 8 failures were **browser-executable-launch-level errors**, not
connection-refused and not product-assertion failures:
`Executable doesn't exist at .../chromium_headless_shell-1208/...`
(2 tests), `spawn ETXTBSY` (2 tests), `Target page, context or browser has
been closed` / `browser.newContext` failures with `Invalid file descriptor
to ICU data received`, `Error loading V8 startup snapshot file`, and
repeated `GPU process launch failed` (4 tests). Tests 9 (`2t`) and 10
(`3c/3d/3e`) passed normally (6.8s/9.8s, real assertions exercised).
Backend PID 65552 and Vite PID 65584 both confirmed **still alive
immediately after Playwright finished** — `E2E-RUNTIME-F-001`'s own specific
failure shape (services dying, connection-refused) did **not** recur.
Cleanup executed after Playwright (`exit 1` preserved as the launcher's own
exit code); failing run's logs correctly preserved at
`tests/e2e/.runtime/w75-native-runner/run-20260804-150043-65512/`.

### Run 2

```text
Command: bash tests/e2e/scripts/run-w75-full-spec-native.sh (immediately following Run 1)
Backend PID 66224, Vite PID 66256
Backend/Vite confirmed alive immediately before Playwright start.

  10 passed, 0 failed, 0 skipped (1.2m / 72s)
```

Backend PID 66224 and Vite PID 66256 both confirmed still alive immediately
after Playwright finished. Cleanup executed, `exit 0` preserved. Runtime
directory auto-removed per the launcher's own success-path cleanup.

### Finding QA-F-001 — concurrent external session collision during this exact test window (HIGH relevance to attribution, not a defect in the launcher's own lifecycle logic)

Investigating an unexpected third runtime directory found between Run 1 and
Run 2 (`tests/e2e/.runtime/w75-native-runner/run-20260804-150329-66690/`,
containing only a `launcher.log`) revealed:

```text
--- creating disposable native Postgres database (mc_w75_native_runner on existing local cluster) ---
ERROR:  database "mc_w75_native_runner" is being accessed by other users
DETAIL:  There are 6 other sessions using the database.
ERROR:  database "mc_w75_native_runner" already exists
```

A live process check at that moment showed a **separate, independently-
running process tree** (`bash tests/e2e/scripts/run-w75-full-spec-
native.sh`, PID 66938, parent orchestration PID 66917, under a completely
different shell/session ancestry than this QA session's own — confirmed via
`ps --forest`, which showed two distinct `claude --dangerously-skip-
permissions` process groups unrelated to this session's own PID tree) —
i.e., **another concurrently-active Claude Code session on this same
machine was independently invoking the identical native launcher, using the
same fixed database name (`mc_w75_native_runner`) and the same fixed ports
(`18096`/`5195`), overlapping this QA session's own Run 1/Run 2 window.**
This is consistent with `agent-system/relay/current.md`'s own currently-
visible `MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-
RE-QA-001` entry, whose own text describes a continuation "under explicit
PM/architect direction" attempting the same non-Docker E2E path.

This does not indict the launcher's own process-lifecycle logic (Backend/
Vite still held correctly through Playwright in both of *this* session's own
runs, exactly as required), but it is the more concrete, evidence-backed
explanation for Run 1's browser-launch flakiness than a generic guess: two
independent full native stacks (each its own Postgres load + Alembic +
Chromium launch under WSL) contending for CPU/IO/file-lock timing at once is
a directly plausible cause of `spawn ETXTBSY` (a file the kernel still
considers open by another process at exec time) and GPU/V8 init failures
under memory/IO pressure. Confirmed clean now: `ss`/`pg_stat_activity` show
no QA-named resources remaining, and this stray process is no longer running
(exited on its own between this investigation's two checks).

**This is also a design finding, independent of attribution**: the native
launcher's fixed resource names (`mc_w75_native_runner`, ports `18096`/
`5195`) provide no isolation against a second concurrent invocation — of
this launcher, of `run-w75-full-spec.sh`'s own Docker variant using the same
override-able-but-defaulted ports, or of another task/session doing the
same thing. This is not a new defect introduced by this task (the Docker
variant has the identical fixed-default-port limitation, and this
repository's own documentation already tells callers to override the port
env vars "if those collide with something else already running" — a
reactive, not preventive, mitigation), but it is a directly relevant
`TEST_ISOLATION_DEFECT`-shaped gap when multiple agent sessions may run
concurrently against the same worktree, which this repository's own
governance model explicitly allows for.

## Full-Stack Evidence (Section 9)

```text
Chromium (Playwright, local v1208) -> Vite (this worktree, :5195,
  VITE_DEV_PROXY_TARGET pointed at :18096) -> Backend (this worktree,
  :18096) -> isolated native PostgreSQL (mc_w75_native_runner, dropped
  after each run).
```

Evidence beyond the bare pass/fail count: the launcher's own captured
stdout for both runs shows the full real sequence (DB create → `init.sql`
→ Alembic 0000→0021 → `PHASE1_SYNTHETIC_SEED_OK`/`WAVE6_TARGET_FIXTURE_OK`
→ backend `/docs` readiness → frontend `/` readiness) with no error prior to
Playwright in either run. Run 2's 10 passing test titles are themselves
real-data assertions ("member names are real, not raw account IDs", "a real
account signs in and reaches /family", etc.) — unchanged from the spec this
task was forbidden to modify, and unchanged from the Developer's own prior
single-run evidence. 0 mock API (the spec file is confirmed byte-identical
to its already-audited state — this QA made no edit to it). 0 accidental
connection to the persistent dev stack: distinct ports throughout (`18096`/
`5195` vs. the persistent stack's own `8000`/`5174`), and the persistent
stack was independently confirmed responsive both before this QA started
and after it finished.

## Cleanup (Section 10)

```text
After Run 1 (failed): QA DB dropped by trap cleanup, both PIDs killed and
  confirmed dead, runtime log preserved (failing-run policy) at its own
  timestamped path — correct per the launcher's own documented contract.
After Run 2 (passed): QA DB dropped, both PIDs killed and confirmed dead,
  runtime log auto-removed (passing-run policy).
Final independent re-check (after both runs, and after the concurrent-
  session investigation above): QA ports (18096, 5195) free; no
  QA-named database remains; `pg_stat_activity` shows only `mc_festival`
  (2 connections, this session's own separate persistent dev.sh stack) and
  system connections — 0 QA residue.
Persistent dev stack (8000/5174): confirmed responsive before and after
  this entire QA pass, unaffected.
Credential residue: 0 (synthetic admin password never written to a file/log
  by the launcher; this QA introduced no credential of its own).
```

## Failure-Path Cleanup Audit (Section 11, static + Run 1's own real evidence)

Run 1 itself is real evidence of the failure path, not merely a static
read: Playwright exited non-zero (`1`), and the trap cleanup still executed
correctly (both PIDs killed, DB dropped, exit code `1` preserved as the
launcher's own exit code, log correctly preserved rather than deleted).
Static read of `cleanup()` confirms: readiness-failure branches (`FATAL:
backend/frontend never became ready`) exit before either PID variable would
be unset, so a partially-started stack (e.g. backend up, frontend never
started) still reaches the trap with `BACKEND_PID` set and `FRONTEND_PID`
empty — the cleanup function's own `[ -n "$FRONTEND_PID" ]` guard correctly
skips killing an empty PID rather than erroring. `INT`/`TERM` are not
separately trapped (only `EXIT`), which is consistent with `run-w75-full-
spec.sh`'s own existing pattern (bash's own `EXIT` trap already fires on a
received `SIGINT`/`SIGTERM` that isn't otherwise caught, for a foreground
script) — not a new gap introduced by this task.

## Git Integrity (Section 12)

```text
Start: 15 tracked-modified/renamed + 14 untracked (pre-existing)
After Run 1: identical (0 delta — the launcher's own runtime artifacts live
  under gitignored tests/e2e/.runtime/)
After Run 2: identical (0 delta)
End of this QA pass: start set + only this QA's own new records (this
  report, its own handoff-equivalent, active.md/relay/Coverage Map updates)
git diff --check: clean throughout
runner-induced Git delta: 0
existing dirty damage: 0
```

## Static / Governance Checks (Section 13)

```text
frontend lint:  PASS (0 errors)
frontend build: PASS (pre-existing chunk-size warning only, unrelated)
bash -n on the native launcher: PASS
git diff --check: clean
agent-system/tools/check_all.py: 0 warnings for this Task ID lineage
```

Backend's 405-test suite and the Markpoint suite were not re-run, per this
task's own explicit Section 13 instruction — no product/backend code was
touched by the remediation this QA verifies.

## Document Consistency (Section 14)

Cross-checked against `MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-
CLOSEOUT-001`'s own QA evidence (original `FAIL`, `E2E-RUNTIME-F-001`,
preserved verbatim, not rewritten) and `MONGLE-W7-5-NATIVE-E2E-LAUNCHER-
LIFECYCLE-REMEDIATION-001`'s own Developer self-check (10/10, single run).
This Independent QA's own two-run result (8 failed / 10 passed) is reported
as this QA's own fresh, independently-measured evidence — not conflated
with the Developer's own prior single-run number, and the Developer's own
report is not altered.

## 5-Gate Self-Check

- **Hallucination Guard**: both runs were actually executed in this
  session, not assumed; the concurrent-session collision was independently
  investigated via live process inspection (`ps --forest`, `pg_stat_
  activity`) rather than asserted from the log alone; the original
  launcher's root cause is stated as `UNVERIFIABLE`, matching this task's
  own Section 2 constraint, not re-asserted as the "120s timeout" fact from
  the Developer's own handoff.
- **Omission Guard**: the `npm ci`-wipes-Chromium procedural hazard and the
  concurrent-session collision are both disclosed as findings, not
  smoothed over to present a cleaner narrative than what actually happened.
- **Miswork Guard**: 0 product/test/migration/seed edits; 0 assertion/
  retry/timeout/skip change; 0 persistent-dev-stack impact; 0 runner-
  induced Git delta; the stray concurrent process was observed, not killed
  or otherwise interfered with (not this task's own resource to manage).
- **Axis Alignment**: this verdict addresses `E2E-RUNTIME-F-001`'s own
  lifecycle scope only. It does not declare `MONGLE_W7_5_DATA_AND_
  BEHAVIOR_WIRING_PASS`, `W7_4_LIVE_CONSUMER_INTEGRATION_PASS`, or W7.6
  readiness. Developer's own 10/10 self-check is not treated as equivalent
  to this Independent QA's own result.
- **Freshness/Evidence Consistency**: every number above came from commands
  run in this session against current HEAD, on databases created fresh in
  this session, not carried forward from the Developer's own prior run.

## Verdict rationale

`E2E-RUNTIME-F-001`'s own specific defect shape (Backend/Vite dying,
`net::ERR_CONNECTION_REFUSED` before any product assertion) was
**independently confirmed absent in both runs** — the new launcher's core
lifecycle contract (hold services until Playwright completes, cleanup only
after, exit code preserved) held in the passing run, the failing run, and
the failure-path cleanup itself. That is the actual object of this task's
verification and it holds.

However, this task's own literal PASS gate ("Run 1: 10/10, Run 2: 10/10")
was not achieved: Run 1 recorded 8 failures, of a class this QA
investigated and attributes with reasonable confidence to a **concurrent,
externally-running session independently exercising the same launcher and
the same fixed resource names during this exact test window** (Finding
QA-F-001) — not to a reintroduction of the target defect, and not to a
product/test change. Per this repository's own established precedent for
exactly this shape of evidence (a mixed fail-then-pass pair is held short of
a "two consecutive clean runs" gate rather than accepted as eventually-
clean — see `MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001`'s
own Backend-suite gate history), this QA does not declare `PASS`. Per
Section 16's own instruction not to treat an unrun/incomplete gate as
`PASS`, and given the specific gap here is a non-product, environment-
contention evidence gap rather than a reintroduced product or lifecycle
defect, the correct verdict is **`CONDITIONAL`**.

```text
MONGLE_W7_5_NATIVE_E2E_LAUNCHER_FOCUSED_INDEPENDENT_QA_CONDITIONAL
E2E_RUNTIME_F_001_LIFECYCLE_CONTRACT_INDEPENDENTLY_VERIFIED_HELD
  (both runs: Backend/Vite alive before AND after Playwright; cleanup only
  after Playwright; exit code preserved in both the passing and failing run)
NATIVE_FULL_STACK_SERVICE_LIFECYCLE_INDEPENDENTLY_VERIFIED
NATIVE_FULL_STACK_E2E_TWO_CONSECUTIVE_CLEAN_RUNS_NOT_YET_ACHIEVED
  (Run 1: 8 failed / 2 passed, browser-executable-level, not connection-
  refused; Run 2: 10 passed / 0 failed / 0 skipped)
CONCURRENT_SESSION_RESOURCE_COLLISION_FOUND_AND_DISCLOSED (QA-F-001)
FULL_STACK_CLEANUP_INDEPENDENTLY_VERIFIED (both runs, including the
  failure path)
RUNTIME_GIT_CLEAN_INDEPENDENTLY_VERIFIED
W7_5_CODE_DEFECT_HARDENING_SCOPE_NOT_YET_UNCONDITIONALLY_CLOSED
OVERALL_W7_5_REMAINS_CONDITIONAL_HUMAN_GATE
```

Not declared, per this task's own Section 17 restriction:
`MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`,
`FULL_PRODUCT_BEHAVIOR_WIRING_COMPLETE`, `PM_DECISIONS_RESOLVED`,
`W7_4_LIVE_CONSUMER_INTEGRATION_PASS`,
`READY_FOR_W7_6_COMMON_COMPONENT_EXTRACTION`.

## Recommended next step

A follow-up pass re-running the same two-consecutive-invocation protocol at
a time confirmed to have **no other concurrent session using the same
launcher/fixed resource names** (or after the launcher is hardened with
collision-safe resource naming, e.g. a PID/timestamp-suffixed DB name and
port range the way its own runtime log directory already is) would be
expected, on this evidence, to produce a genuinely clean consecutive pair —
Run 2 here already demonstrates the launcher itself sustains a full clean
10/10 pass once uncontended. This QA does not perform that follow-up run
itself, to avoid a retry-until-pass pattern within a single QA session.

```text
W7.5 code-defect hardening (E2E-RUNTIME-F-001 lineage): CONDITIONAL
  (lifecycle contract verified held; two-clean-consecutive-runs gate
  pending an uncontended re-run)
W7.5 overall: CONDITIONAL / HUMAN_GATE (unchanged)
W7.4: REOPENED, LIVE_CONSUMER_INTEGRATION_AUDIT PENDING (unchanged)
W7.6: BLOCKED (unchanged)
```

No commit, push, merge, or rebase was performed by this QA pass.

## Correction — second concurrent Independent QA session identified (append-only, original verdict above preserved verbatim)

The "separate, independently-running process tree (PID 66938, parent
orchestration PID 66917)" this report's own Finding `QA-F-001` investigated
was **another Independent QA session running this exact Task ID**
(`MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001`) against this
same worktree at the same time — this section is that session's own
corroborating pass, written after the fact once both sessions' existence
was discovered (this session found its own new, unexpected file appearing
mid-run and paused to ask the PM how to proceed rather than overwrite it).
Both sessions were unaware of each other; both hit the identical
`mc_w75_native_runner` "being accessed by other users" collision from
opposite sides. Per PM direction, this is appended rather than overwriting
the verdict above (`rules.md` Invariant 5, write-once/append-only; the same
precedent already on record in `relay/current.md`'s "Concurrent writer
claim coexistence" entry).

### This session's own evidence

Same worktree, branch `dev-newmarkp`, HEAD `328d877` unchanged throughout.
Node 20.20.2 / npm 10.8.2 (nvm), Playwright 1.58.2, Chromium v1208 installed
fresh under `PLAYWRIGHT_BROWSERS_PATH=0` (the pre-existing
`~/.cache/ms-playwright` held mismatched revisions `1223`/`1228`, correctly
not used). Static launcher audit independently re-confirmed identical to
the findings above (top-level `& PID=$!` pattern, no command-substitution
wrap, single top-level `trap cleanup EXIT`, foreground Playwright, pre-flight
`kill -0` re-check, post-run liveness log, exit-code preservation); `bash -n`
PASS. Lifecycle smoke (standalone backend+frontend, distinct DB/ports): 24s
hold, 3/3 liveness+HTTP checks clean, cleanup confirmed.

**First pair** (executed before this session discovered the file above):
a first provisioning attempt failed immediately on the identical
`mc_w75_native_runner`/"6 other sessions" collision (the other side of this
report's own `QA-F-001`); by the next check seconds later the database had
been dropped and 0 sessions remained. Retried:
- Run 1: **10 passed, 0 failed, 0 skipped** (1.1m). Backend PID 66988 /
  Vite PID 67004, both confirmed alive immediately before and immediately
  after Playwright.
- Run 2 (immediately following, no manual DB cleanup, no code change):
  **10 passed, 0 failed, 0 skipped** (1.0m). Backend PID 67725 / Vite PID
  67741, both confirmed alive before and after.
- Cleanup confirmed for both: QA DB dropped, both PIDs killed and confirmed
  dead, ports freed, runtime directories auto-removed (exit 0), persistent
  dev stack (`8000`/`5174`) unaffected.

**Second pair** (fresh, run after confirming via direct process/DB/port
checks that the other session had finished and no contention remained):
- Run 1: **10 passed, 0 failed, 0 skipped** (41.2s). Backend PID 68734 /
  Vite PID 68771, both confirmed alive before and after Playwright.
- Run 2 (immediately following): **10 passed, 0 failed, 0 skipped** (49.0s).
  Backend PID 69211 / Vite PID 69228, both confirmed alive before and
  after.
- Cleanup confirmed for both: DB dropped, PIDs dead, ports free, runtime
  dirs auto-removed, persistent dev stack responsive before and after.

Four total runs this session, 0 failures in any of them once outside the
collision window — including the very first pair, which already completed
cleanly despite this session's own pre-flight collision with the other
session's tail-end teardown.

Full-stack path evidence, cleanup, and static/governance re-checks
(`bash -n`, frontend `lint` PASS 0 errors, frontend `build` PASS —
pre-existing chunk-size warning only, `git diff --check` clean) match the
shape already recorded above; `agent-system/tools/check_all.py` additionally
surfaces one warning specific to this Task ID's own lineage —
`missing fields: Handoff` — a pre-existing gap in this Task ID's own
`active.md` registration (this QA-evidence-as-handoff convention matches
`MONGLE-W1-INDEPENDENT-QA-001` and others already in this repository), not
a defect introduced by either session's own work.

Git integrity: `git status --short`/`git diff --check` before and after
this session's own work show only this section's own edit plus the routine
`active.md`/`relay/current.md`/Coverage Map updates — 0 runner-induced
delta beyond that, `HEAD` unchanged (`328d877`).

### Revised verdict

The "Recommended next step" above (an uncontended re-run) has now been
independently performed, twice over. The specific, and only, gap that held
the verdict above to `CONDITIONAL` — two consecutive clean runs not yet
achieved, attributed to concurrent-session resource contention — is closed
by this session's own fresh, uncontended evidence (two separate clean pairs,
4/4 runs passing).

```text
E2E_RUNTIME_F_001_INDEPENDENTLY_VERIFIED_REMEDIATED
NATIVE_FULL_STACK_SERVICE_LIFECYCLE_INDEPENDENTLY_VERIFIED
NATIVE_FULL_STACK_E2E_TWO_CONSECUTIVE_RUNS_PASS (two separate pairs, 4/4 runs, all 10/10)
FULL_STACK_CLEANUP_INDEPENDENTLY_VERIFIED
RUNTIME_GIT_CLEAN_INDEPENDENTLY_VERIFIED
CONCURRENT_SESSION_COLLISION_ROOT_CAUSE_CONFIRMED_FROM_BOTH_SIDES
W7_5_CODE_DEFECT_HARDENING_SCOPE: CLOSED
```

Combining both sessions' evidence: the original `CONDITIONAL` verdict above
is superseded by this corroborating pass — not because its own measurement
was wrong (`QA-F-001` correctly diagnosed the mechanism, from its own side),
but because the one condition it was waiting on has now been independently
supplied. Effective combined verdict, code-defect-hardening scope only (per
Section 17's own restriction, unchanged in every other respect):

```text
W7.5 code-defect hardening (E2E-RUNTIME-F-001 lineage): CLOSED
W7.5 overall: CONDITIONAL / HUMAN_GATE (unchanged)
W7.4: REOPENED, LIVE_CONSUMER_INTEGRATION_AUDIT PENDING (unchanged)
W7.6: BLOCKED (unchanged)
```

Not declared, same restriction as above:
`MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`,
`FULL_PRODUCT_BEHAVIOR_WIRING_COMPLETE`, `PM_DECISIONS_RESOLVED`,
`W7_4_LIVE_CONSUMER_INTEGRATION_PASS`,
`READY_FOR_W7_6_COMMON_COMPONENT_EXTRACTION`.

No commit, push, merge, or rebase performed by this corroborating pass.
