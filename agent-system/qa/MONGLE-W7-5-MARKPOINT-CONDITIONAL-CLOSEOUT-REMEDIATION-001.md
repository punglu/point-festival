# Task QA Evidence — MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001

- Task ID: MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001

```text
Parent:  MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001 (verdict CONDITIONAL)
Findings closed: QA-F-001, QA-F-002, QA-F-003 (of that task's own 4 open items)
Finding still open: E2E runner smoke in a Docker-capable environment
Status:  DEVELOPER_SELF_CHECK_COMPLETE -- NOT an Independent QA PASS
         declaration. A separate focused Independent Re-QA is expected next.
```

Full narrative (commit audit, correction text, exact test diffs, every
verification run's exact numbers) is in this task's own handoff:
`agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md`.

## Disposition of the parent QA task's 4 open items

1. **QA-F-001 (commit/push documentation staleness)** — corrected. Both
   `agent-system/qa/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md`
   and its handoff now carry an appended `## Correction` section stating the
   actual fact (commit `328d877`, pushed to `origin/dev-newmarkp`) without
   rewriting the original (now-stale) claim, per `rules.md` Invariant 5.
   Commit `328d877`'s file scope was independently re-audited: exactly 7
   files, all within the Markpoint remediation's own declared scope.
2. **QA-F-002 (deducted-side test coverage gap)** — closed with a new
   permanent, deterministic test,
   `test_projection_kst_boundary_independent_of_server_local_timezone_deducted_side`,
   mirroring the existing earned-side test exactly. 3/3 consecutive PASS.
3. **QA-F-003 (pre-existing OS-timezone test fragility)** — closed. The two
   originally-failing tests' own `anchor = date.today()` /
   `today = date.today()` replaced with `datetime.now(service.KST).date()`.
   Re-verified under `TZ=Asia/Seoul`, `TZ=UTC`, `TZ=America/New_York`: all
   3 now pass (previously 1/3 under `America/New_York`). Zero assertion
   value changed — confirmed via direct diff against the committed HEAD
   blob.
4. **E2E runner smoke** — **not closed**. This session has no Docker
   either (same WSL constraint as the parent QA task). Recorded as
   `ENVIRONMENT_REQUIRED`, not treated as a passed or skippable item.

## Verification

```text
Fresh disposable Postgres (native local cluster, mc_qa_markpoint_verify,
  created via database/init.sql + alembic upgrade head through 0021,
  dropped after use -- not carried over from the parent QA session).

collect-only: 405 tests (404 + 1 new)

Targeted (2 fixed tests + 1 new test), 3 consecutive iterations: 3 passed
  every time.
Same 3 tests under TZ=Asia/Seoul / TZ=UTC / TZ=America/New_York:
  3/3 passed in all three environments (QA-F-003 closed).
Core Markpoint suite (test_markpoint_core_gap_wave5.py +
  test_markpoint_target_wave5.py): 64 passed (63 prior + 1 new), 96.72s.

Backend full suite, two consecutive runs, same DB, no reset, no code change
  between them:
  Run A: 405 passed, 0 failed, 0 errors, 772.22s
  Run B: 405 passed, 0 failed, 0 errors, 718.37s
  KNOWN-W7-5-WAGLE-CONCURRENCY-001 did not recur in either run.

git diff --check: clean.
Product code (backend/app/domains/markpoint_target/service.py): untouched
  by this task -- not in scope, already independently verified correct.
Test code (backend/tests/test_markpoint_core_gap_wave5.py): diff-confirmed
  to contain exactly 2 anchor-line replacements + 1 new appended test, 0
  assertion changes.
```

## 5-Gate Self-Check

- **Hallucination Guard**: the commit-scope re-audit was re-run fresh in
  this task rather than trusted from the parent QA session's own cached
  result; the TZ cross-check was re-executed against all 3 environments
  rather than assumed fixed from the code change alone.
- **Omission Guard**: the still-open E2E smoke gap is stated plainly here
  and in the handoff, not folded into a "3 of 4 closed, effectively done"
  framing.
- **Miswork Guard**: `git diff --check` clean; the two documentation
  corrections were appended, not edited in place, preserving the original
  (now-stale) claims per Invariant 5; the disposable QA database was
  dropped after use; the persistent local dev stack was left untouched.
- **Axis Alignment**: closing QA-F-001/002/003 does not imply
  `MONGLE_W7_5_MARKPOINT_PROJECTION_FOCUSED_INDEPENDENT_QA_PASS` (the E2E
  gap is still open), `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`, or W7.6
  readiness. None of those are declared.
- **Freshness/Evidence Consistency**: every count above came from a command
  run in this session against current HEAD on a newly created disposable
  database, not carried forward from either the Developer's original
  remediation numbers or the parent QA session's own numbers.

## Final Declaration

```text
MARKPOINT_COMMIT_PUSH_DOCUMENTATION_CORRECTED
MARKPOINT_COMMIT_SCOPE_RE_AUDITED_CLEAN
MARKPOINT_TODAY_DEDUCTED_DETERMINISTIC_REGRESSION_ADDED
MARKPOINT_PRE_EXISTING_TEST_OS_TIMEZONE_FRAGILITY_CLOSED
BACKEND_FULL_SUITE_TWO_CONSECUTIVE_RUNS_PASS
TASK_OWNED_FAILURE_ZERO
E2E_RUNNER_SMOKE_STILL_ENVIRONMENT_REQUIRED_NOT_RUN
READY_FOR_MARKPOINT_CLOSEOUT_FOCUSED_INDEPENDENT_RE_QA
```

Not declared: `MONGLE_W7_5_MARKPOINT_PROJECTION_FOCUSED_INDEPENDENT_QA_PASS`
(the parent QA task's own verdict is not overwritten by this task — a
separate focused Independent Re-QA is the correct next step to actually
change that verdict), `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`,
`READY_FOR_W7_6_COMMON_COMPONENT_EXTRACTION`. W7.5 overall remains
`CONDITIONAL`/`HUMAN_GATE`; W7.4 remains `REOPENED`; W7.6 remains `BLOCKED`.
No commit/push/merge/rebase were performed.
