# Task QA Evidence — MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001

- Task ID: MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001

```text
Parent:  MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001 (verdict FAIL)
Finding: RE-QA-F-003
Status:  DEVELOPER_SELF_CHECK_COMPLETE -- NOT an Independent QA PASS
         declaration. A separate focused Independent Re-QA is expected next.
```

Full narrative (reproduction matrix, direct DB/clock trace, fix detail,
every verification run's exact numbers) is in this task's own handoff:
`agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md`.

## Root-cause classification

```text
DATE_TIMEZONE_BOUNDARY_DEFECT
```

Confirmed by measurement, not assumed:
- Matrix A (fresh DB, focused tests only): failed on the very first
  invocation (not "passes once, fails later").
- Matrix B (second, never-touched DB): Run 1 and immediate Run 2 both
  failed identically -- rules out PERSISTED_PROJECTION_STATE_DEFECT and
  any run-count dependence.
- Matrix D (56 other Markpoint tests run first, then the 2 failing ones):
  same 2 failed, others unaffected -- rules out
  TEST_FIXTURE_ISOLATION_DEFECT.
- A standalone diagnostic script (deleted after use) reproduced the exact
  mechanism directly: Python `date.today()` (server OS-local timezone,
  effectively UTC+9 on this machine) returned a date one day ahead of the
  Postgres session's own UTC-based `func.date(occurred_at)` extraction,
  for the ~9 hours/day where KST local time has crossed midnight but UTC
  has not. `today_earned`/`today_deducted` (single-day equality checks)
  went to 0; `weekly_earned`/`weekly_deducted` (multi-day range checks)
  stayed correct, matching the exact partial-failure shape observed.

## Fix

```text
backend/app/domains/markpoint_target/service.py:
  + KST = ZoneInfo("Asia/Seoul") / _today_kst() helper (same convention
    app/domains/daily_point/service.py already established)
  All 7 `date.today()` call sites -> `_today_kst()`
  _sum_ledger() and own_summary()'s ledger day-boundary SQL: `func.date(
    occurred_at)` -> `func.date(func.timezone("Asia/Seoul", occurred_at))`
```

No assertion loosened, no expected value changed (30/7 stayed 30/7), no
test skipped/reordered/retried-only. Legacy `mission/service.py` /
`mission_template/service.py` / `config/service.py` / `admin/router.py`
(also naive `date.today()`) deliberately not touched -- out of
`RE-QA-F-003`'s scope, and `mission_template`'s rolling-window day-count
contract is a separately PM-locked concern.

## Permanent regression coverage

```text
backend/tests/test_markpoint_core_gap_wave5.py, 5 new tests:
  test_projection_kst_boundary_independent_of_server_local_timezone
  test_projection_different_anchor_dates_isolate_correctly
  test_projection_repeated_calls_same_db_return_identical_figures
  test_projection_cross_family_isolation_for_today_earned
  test_projection_empty_ledger_returns_zero_not_error
```

The first test is deterministic (explicit UTC timestamps chosen to fall on
different UTC/KST calendar dates) rather than depending on live wall-clock
timing, unlike the two originally-failing tests -- it fails on the
pre-fix code regardless of when it runs, not only during a live UTC/KST
divergence window.

## Verification

```text
Focused (2 originally-failing tests) x5 consecutive: 2 passed every time
Related Markpoint suites: 63 passed (58 prior + 5 new)
Backend full suite (fresh disposable DB, port 15435):
  collect-only: 404 (399 prior + 5 new)
  Run 1: 403 passed, 1 failed (test_wagle_realtime_wave3.py::
    test_dispatcher_is_safe_to_run_twice_on_the_same_event) -- standalone
    re-run: 1 passed. Matches the pre-existing, already-registered
    KNOWN-W7-5-WAGLE-CONCURRENCY-001 condition, unrelated to this task.
  Run 2: 404 passed, 0 failed, 0 errors -- same Wagle test did not recur
Hardening smoke (migration 0021 matrix + board-room concurrency + admin
  bcrypt): 34 passed
E2E runner, 1 invocation: 10 passed, 0 skipped, 0 failed; 0 git drift
Backend import + OpenAPI generation: clean
tsc / eslint / vite build / git diff --check: clean
```

### Closure verification (additional pass, 2026-08-04, no code changed)

The result above (Run 1 403/404 + standalone re-run, then Run 2 404/404)
was correctly held short of the project's own stability gate, which
requires two CONSECUTIVE clean runs of the same pair, not "eventually
clean." A dedicated closure-only pass, on a brand-new disposable database,
with zero product/test/migration/seed edits:

```text
collect-only: 404 (unchanged)
Run A: 404 passed, 0 failed, 0 errors, 425.44s
Run B: 404 passed, 0 failed, 0 errors, 365.02s (immediately following,
  same DB, no reset/recreation/selection change between the two)
```

Both passed on the first attempt; no retry-until-pass was used or would
have been accepted (the Wagle known condition did not recur in either
run). Re-confirmed on the same DB before teardown: the 2 originally-failing
tests 5/5 consecutive, the 5 new KST-boundary regression tests 5/5.
Container removed, confirmed absent via `docker ps -a`. `git status`/
`git diff --check` after this pass are byte-identical to this pass's own
starting state (same 5 modified + 2 untracked files already listed above,
0 new dirty, 0 damage, 0 commits).

## 5-Gate Self-Check

- **Hallucination Guard**: the root cause was traced with a live
  side-by-side Python-clock/DB-clock/raw-ledger-row dump, not inferred
  from the failure message alone; the 404 test count was collected via
  `pytest --collect-only`; the Wagle test's KNOWN_CONDITION nature was
  confirmed by an actual standalone re-run, not assumed from its name.
- **Omission Guard**: `own_summary`'s identical-defect sibling call site
  (not named by the failing tests) is disclosed as fixed alongside
  `_sum_ledger`, not silently left broken; the Run 1 Wagle failure is
  disclosed with its own standalone-repro evidence, not hidden by only
  reporting Run 2's clean result.
- **Miswork Guard**: `git diff --check` clean; the standalone diagnostic
  script was deleted after use; all disposable Docker containers
  confirmed removed after each verification pass.
- **Axis Alignment**: fixing RE-QA-F-003 does not imply
  `MONGLE_W7_5_HARDENING_FOCUSED_INDEPENDENT_RE_QA_PASS`,
  `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`, or W7.6 readiness -- none
  of those are declared.
- **Freshness/Evidence Consistency**: every count/status above came from a
  command run in this session against current HEAD and a live disposable
  database, not carried forward from the parent Re-QA report's own numbers
  (which concerned the pre-fix state).

## Final Declaration

`BACKEND_FULL_SUITE_TWO_CONSECUTIVE_RUNS_PASS` below is backed by the
**Closure verification** pass (Run A/B, both 404/404), not by the earlier
mixed Run 1 (403/404)/Run 2 (404/404) pair reported first — that pair was
correctly held short of this gate by PM review, since the project's own
stability bar requires two consecutive clean runs of the same pair, not a
failure followed eventually by a clean one.

```text
MARKPOINT_PROJECTION_REPEAT_RUN_ROOT_CAUSE_IDENTIFIED
MARKPOINT_TODAY_EARNED_REPEAT_RUN_STABILITY_FIXED
MARKPOINT_DATE_BOUNDARY_REGRESSION_COVERAGE_ADDED
BACKEND_FULL_SUITE_TWO_CONSECUTIVE_RUNS_PASS
TASK_OWNED_FAILURE_ZERO
READY_FOR_MARKPOINT_PROJECTION_FOCUSED_INDEPENDENT_RE_QA
```

Not declared: `MONGLE_W7_5_HARDENING_FOCUSED_INDEPENDENT_RE_QA_PASS`,
`MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`,
`READY_FOR_W7_6_COMMON_COMPONENT_EXTRACTION`. W7.5 overall remains
`CONDITIONAL`/`HUMAN_GATE`; W7.4 remains `REOPENED`/audit pending; W7.6
remains `BLOCKED`. Commit/push/merge/rebase were not performed.
