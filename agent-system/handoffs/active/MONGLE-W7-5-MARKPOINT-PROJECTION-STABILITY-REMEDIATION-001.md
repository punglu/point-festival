# Handoff — MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001

- Task ID: MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001

## Origin

Parent: `MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001` (verdict
`FAIL`, `agent-system/qa/MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001.md`,
confirmed present and read in full before any work started). Blocking
finding: `RE-QA-F-003` — `tests/test_markpoint_core_gap_wave5.py::
test_projection_derives_every_figure_from_the_ledger` and `::
test_projection_isolates_date_boundaries` measured `today_earned=0`
instead of `30`/`7`, deterministically on a full-suite second run.

## Reproduction matrix (measured, not assumed)

```text
Matrix A (fresh DB, focused tests only): FAILED immediately on the very
  first invocation -- 2 failed in 1.56s. Not "passes once then fails."
Matrix B (a second, brand-new, never-touched DB): Run 1 FAILED, Run 2
  (immediate) FAILED -- identical result both times. Rules out any
  run-count or persisted-projection-state cause outright: a database that
  has never executed any test before still fails on its very first run.
Matrix D (full Markpoint suite, 56 other tests, then the 2 tests together):
  same 2 tests failed, the other 56 passed -- rules out test-order/
  fixture-isolation dependence.
Classification: DATE_TIMEZONE_BOUNDARY_DEFECT (not
  PERSISTED_PROJECTION_STATE_DEFECT, not CACHE_INVALIDATION_DEFECT, not
  TEST_FIXTURE_ISOLATION_DEFECT -- each specifically ruled out by the
  matrix results above, not by assumption).
```

## Direct DB/clock inspection (root-cause trace)

A standalone diagnostic script (not pytest, no autouse teardown; deleted
after use) reran the exact test steps and printed, before calling
`own_projection`:

```text
PYTHON date.today() = 2026-08-04
PYTHON now utc       = 2026-08-03 15:34:12+00:00
DB now/current_date/TIMEZONE = (2026-08-03 15:34:12+00, 2026-08-03, 'UTC')
RAW LEDGER ROWS: occurred_at = 2026-08-03 15:34:12 UTC (both rows)
PROJECTION: today = 2026-08-04, today_earned = 0, today_deducted = 0,
            weekly_earned = 30, weekly_deducted = 12   (period-range sums
            unaffected -- only the single-day equality/range check breaks)
```

`own_projection`'s `anchor = anchor or date.today()` reads the Python
process's OS-local system clock (this machine's TZ is effectively
KST/UTC+9), while `_sum_ledger`'s `func.date(MarkpointLedgerEntry.
occurred_at)` extracted the calendar date under the Postgres session's own
`TIMEZONE` setting (`UTC`, confirmed via `current_setting('TIMEZONE')`).
For roughly nine hours out of every day (KST 00:00–09:00, while UTC is
still the previous calendar day), the two disagree by exactly one day —
`today_earned`/`today_deducted` (single-day equality/range checks) go to
0; `weekly_earned`/`weekly_deducted` (multi-day range checks) stay correct
because the off-by-one-day boundary still falls inside the same week.

This also explains the parent Re-QA's own "Run 1 passed, Run 2 failed"
observation: the ~410s full-suite runtime made it plausible for the local
KST midnight boundary to be crossed mid-run, or for the two runs to
straddle it — not a DB-state artifact of "run count" itself.

## Fix

`backend/app/domains/markpoint_target/service.py` already had an established
sibling convention to reuse: `app/domains/daily_point/service.py` defines
`KST = ZoneInfo("Asia/Seoul")` and uses it for exactly this kind of
Family-facing calendar-date question. Applied the same convention here
instead of inventing a new one:

- Added `KST = ZoneInfo("Asia/Seoul")` and a `_today_kst() -> date` helper.
- Replaced all 7 `date.today()` call sites (`expire_stale_missions`,
  `own_summary`, `read_family_config`, `update_family_config`,
  `rolling_window`, `own_projection`, `own_weekly_detail`) with
  `_today_kst()`. `rolling_window`'s own day-count arithmetic (the
  PM-approved 14-day-on-Monday contract) is untouched — only which
  absolute calendar date counts as "today" changed, not how many days the
  window spans.
- `_sum_ledger`'s day-boundary comparison now converts `occurred_at` to KST
  before extracting the date: `func.date(func.timezone("Asia/Seoul",
  MarkpointLedgerEntry.occurred_at))`, instead of the plain UTC-session
  `func.date(occurred_at)`. Same fix applied to `own_summary`'s identical
  inline comparison (a second call site with the same defect class, not
  itself named by the failing tests, but sharing the exact same bug —
  left unfixed it would have been an inconsistent half-fix).
- Legacy `mission/service.py`, `mission_template/service.py`,
  `config/service.py`, `admin/router.py` (also using naive `date.today()`)
  were deliberately NOT touched — out of `RE-QA-F-003`'s scope (Wave 5
  Target implementation only), and `mission_template`'s own rolling-window
  day-count contract is a separately PM-locked concern per `relay/
  current.md`'s own "Markpoint rules the next writer must not undo."

No assertion was loosened; no expected value was changed; no test was
skipped or reordered.

## Permanent regression coverage (5 new tests)

`backend/tests/test_markpoint_core_gap_wave5.py`:

1. `test_projection_kst_boundary_independent_of_server_local_timezone` — a
   ledger entry at a UTC instant chosen to fall on a *different* UTC vs.
   KST calendar date (00:30 KST = 15:30 UTC the previous day); asserts the
   KST date sees it and the UTC-adjacent date does not. Deterministic —
   does not depend on what real time it happens to run at, unlike the two
   originally-failing tests.
2. `test_projection_different_anchor_dates_isolate_correctly` — two
   entries on two different explicit dates, queried by each date's own
   anchor.
3. `test_projection_repeated_calls_same_db_return_identical_figures` —
   `own_projection` called twice in a row against the same ledger; asserts
   byte-identical results (RE-QA-F-003's own "correct once, then wrong on
   a later read" symptom, made deterministic).
4. `test_projection_cross_family_isolation_for_today_earned` — Family B
   must never see Family A's same-day ledger entries.
5. `test_projection_empty_ledger_returns_zero_not_error` — a member with
   no ledger rows gets all-zero figures, not an exception.

## Verification

```text
Focused (2 originally-failing tests), 5 consecutive runs: 2 passed each
  time (1.5-1.8s each).
Related Markpoint suites (test_markpoint_core_gap_wave5.py +
  test_markpoint_target_wave5.py): 63 passed (58 prior + 5 new).
Backend full suite (fresh disposable DB, port 15435):
  collect-only: 404 tests (399 prior + 5 new)
  Run 1: 404 collected, 403 passed, 1 failed
    (test_wagle_realtime_wave3.py::
     test_dispatcher_is_safe_to_run_twice_on_the_same_event) --
    standalone re-run: 1 passed. Matches the already-registered,
    pre-existing `KNOWN-W7-5-WAGLE-CONCURRENCY-001` condition (Wagle
    asyncio.gather concurrency-test contention under full-suite load,
    unrelated to Markpoint/date code, present before this task started).
    Not a task-owned failure.
  Run 2: 404 passed, 0 failed, 0 errors (414.17s) -- the same Wagle test
    did not recur.
Hardening non-regression smoke: test_migration_0021_participant_merge.py +
  test_wagle_integration.py + test_auth_admin_login.py -- 34 passed.
E2E runner (tests/e2e/scripts/run-w75-full-spec.sh), 1 invocation:
  10 passed, 0 skipped, 0 failed (17.6s). git status delta on tests/e2e/:
  none.
Backend import + OpenAPI generation: clean.
tsc --noEmit / eslint / vite build: clean (pre-existing chunk-size build
  warning only, unrelated).
git diff --check: clean.
```

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md

`CLOSEOUT GATE: PASS` means only that the four documentation obligations
above are synchronized — it does NOT mean
`MONGLE_W7_5_HARDENING_FOCUSED_INDEPENDENT_RE_QA_PASS`,
`MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`, or W7.6 readiness. Per the
parent task's own direction, this is a Developer remediation only; a
separate focused Independent Re-QA is the required next step. W7.4 remains
`REOPENED`/audit pending; W7.5 overall remains `CONDITIONAL`/`HUMAN_GATE`;
W7.6 remains `BLOCKED`.

## Closure verification (2026-08-04, additional pass — no code changed)

PM correctly held this task open after the first report: the prior
Backend full-suite evidence was Run 1 (403/404, one Wagle known-condition
failure) then Run 2 (404/404) — not two consecutive passes, since the
project's own stability gate requires PASS on both runs of the same pair,
not "eventually clean." No product, test, migration, or seed file was
touched this pass; the entire pass is verification only, on a brand-new
disposable database.

```text
Fresh disposable Postgres (port 15435, mc_qa_closure_verify, torn down
  after use). database/init.sql + alembic upgrade head (through 0021).
collect-only: 404 tests (unchanged from the prior report).

Run A: 404 passed, 0 failed, 0 errors, 1 warning, 425.44s
Run B: 404 passed, 0 failed, 0 errors, 1 warning, 365.02s (immediately
  following, same DB, no reset/container recreation/test-selection change
  between the two)
```

Both runs passed cleanly on the first attempt — no retry-until-pass was
needed, and none would have been accepted if needed (the Wagle known
condition did not recur either time).

Re-confirmed on this same database afterward, before teardown:

```text
The 2 originally-failing tests, 5 consecutive runs: 2 passed every time
  (1.68s-2.05s each)
The 5 new KST-boundary regression tests: 5 passed
```

Cleanup: `docker rm -f mc_qa_closure_verify` confirmed via `docker ps -a`
(absent). `git status`/`git diff --check` after this entire pass are
byte-identical to the state at the start of this pass (5 modified + 2
untracked files, the same ones this task's own prior report already
listed) — 0 new dirty, 0 damage to pre-existing dirty state, 0 commits.

## Not independently measured / estimates disclosed

- The E2E runner was run once (not the full 4-consecutive protocol) per
  this task's own explicit instruction — a fuller repeat-run check is
  deferred to the follow-up Independent Re-QA.
- `agent-system/tools/check_all.py` was run after this task's own document
  registration; any warning for a Task ID other than this one belongs to
  a different task and is not addressed here.
