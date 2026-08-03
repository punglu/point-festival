# Task QA Evidence — MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001

- Task ID: MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001

```text
Target:  MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001
Origin:  MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001 (verdict FAIL,
         confirmed present and read in full before any work started)
Status:  DEVELOPER_SELF_CHECK_COMPLETE -- NOT an Independent QA PASS
         declaration. Reported to the Main Architect; a separate focused
         Independent Re-QA is expected next.
```

Full narrative (root cause, fix, and every verification run's exact
numbers) is in this task's own handoff:
`agent-system/handoffs/active/MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001.md`.
This file is the compact evidence record required by Closeout Contract v1.

## HARDENING-QA-F-001 (HIGH) — fixed

```text
Fix: backend/alembic/versions/0021_board_room_race_hardening.py --
  _merge_duplicate_board_rooms() now selects the participant survivor by
  considering every row across the whole duplicate room set (canonical's
  own rows included, not only loser rows): an active row anywhere always
  wins; only when none exists is a deterministic terminal (left) survivor
  chosen. Read-state now translates each participant's pre-merge sequence
  into the new merged numbering (an explicit mapping built while
  renumbering messages) instead of folding a stale raw integer.
Independent confirmation the old code actually had this defect: a
  throwaway copy of the pre-remediation function, run against the exact
  QA-reported shape (canonical left, loser older-left+newer-active) on a
  disposable database, then rolled back, produced {left: 2, active: 0} --
  matching HARDENING-QA-F-001's own reported evidence verbatim.
New regression: backend/tests/test_migration_0021_participant_merge.py,
  10 cases against real PostgreSQL (not mocks) -- 10/10 pass, including
  the exact reproduction shape (case 7) and a related milder variant
  (case 3, single-candidate shape).
Re-verified lossless merge + round trip: dedicated disposable DB
  (mc_migration_verify_v2, port 15499, torn down after use) -- the
  previously-lost membership now survives active with left_at NULL, all
  4 messages/2 reactions/3 read-states (correctly translated) survived,
  an untouched negative-control Family stayed byte-for-byte unchanged,
  downgrade -1 dropped only the index (data stayed merged), re-upgrade
  head recreated the index with 0 errors.
```

## HARDENING-QA-F-002 (MEDIUM) — fixed

```text
Fix: tests/e2e/scripts/run-w75-full-spec.sh -- backend/frontend logs now
  go to an absolute, timestamped, in-worktree, gitignored runtime
  directory (tests/e2e/.runtime/w75-runner/run-<timestamp>-<pid>/),
  printed by the script, removed on a passing run and kept (path
  re-printed) on a failing run. tests/e2e/.runtime/ added to root
  .gitignore. tests/README.md updated.
Bug this fix's own first verification caught: an initial relative-path
  version silently failed the backend/frontend log redirect inside the
  `cd backend && ...` / `cd frontend && ...` subshells (path resolved
  against the wrong directory), so neither service actually started and
  all 10 Playwright tests failed on the very first re-run -- root-caused
  via the empty log directory, fixed by making the path absolute, and the
  readiness loops were additionally hardened to fail loudly instead of
  silently proceeding to a guaranteed-failing Playwright run.
Verification: 4 consecutive invocations, no manual pause --
  Run 1: 10 passed, 0 skipped, 0 failed (16.6s)
  Run 2: 10 passed, 0 skipped, 0 failed (16.6s)
  Run 3: 10 passed, 0 skipped, 0 failed (16.6s)
  Run 4: 10 passed, 0 skipped, 0 failed (16.4s)
  git status delta on tests/e2e/ after all 4: none beyond pre-existing
  dirty state. docker ps -a: 0 leftover containers.
```

## Full verification suite

```text
Focused (4 files incl. new migration matrix): 49 passed
Full backend suite (pytest --collect-only): 399 tests
Run 1: 399 passed, 0 failed, 0 errors, 382.65s
Run 2: 399 passed, 0 failed, 0 errors, 379.22s
Wagle 3x3 viewport regression: 3/3 passed, 0 overflow, 0 console/page errors
tsc --noEmit / eslint / vite build / git diff --check: all clean
```

## Static/governance check finding (this task's own scope)

`agent-system/tools/check_all.py` found that the prior task's own
Closeout Synchronization block and QA-evidence header were written as
prose/code-fence text, not the `- Field: value` Markdown list-item lines
`check_closeout.py`'s parser actually requires -- causing false "handoff/QA
evidence missing" warnings for an already-real, already-complete task.
Fixed: added `- Task ID: ...` lines and converted the Closeout
Synchronization block to list-item fields in both
`agent-system/handoffs/active/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md`
and
`agent-system/qa/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md`;
gave this remediation task its own dedicated handoff/QA-evidence files
(this file and its handoff) since the checker recognizes at most one Task
ID per document.

## 5-Gate Self-Check

- **Hallucination Guard**: the pre-remediation defect was independently
  reproduced against a throwaway copy of the old code (not assumed from
  the QA report's prose); the 399 test count was collected via
  `pytest --collect-only`, not computed by arithmetic alone (though 389+10
  also checks out); the log-path bug was found by actually running the
  fixed script, not by code review alone.
- **Omission Guard**: the log-path bug found during this task's own
  verification is disclosed as a real defect this remediation introduced
  and then fixed, not silently corrected; the read-state sequence-
  translation gap (not separately flagged by Independent QA but adjacent
  to F-001) is disclosed as an additional fix, not hidden; the governance/
  tooling format defect in the prior task's own records is disclosed, not
  quietly patched without mention.
- **Miswork Guard**: `git diff --check` clean; all temporary/scratch files
  (seed scripts, throwaway old-algorithm copy, ad hoc viewport spec)
  deleted after use and confirmed absent; `docker ps -a` confirms 0
  leftover containers after every verification pass.
- **Axis Alignment**: fixing F-001/F-002 does not imply
  `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`, W7.6 readiness, or W7.4
  completion -- none of those are declared; a clean 2-run backend suite
  does not retire `KNOWN-W7-5-WAGLE-CONCURRENCY-001`.
- **Freshness/Evidence Consistency**: every count/status above came from a
  command run in this session against current HEAD and live disposable
  databases/browsers, not carried forward from either QA report's own
  numbers.

## Final Declaration

```text
MONGLE_W7_5_HARDENING_QA_FAIL_FINDINGS_REMEDIATED
MIGRATION_0021_ACTIVE_PARTICIPANT_SEMANTICS_FIXED
MIGRATION_0021_LOSSLESS_MERGE_COVERAGE_ADDED
BOARD_ROOM_CONCURRENCY_FIX_PRESERVED
E2E_RUNNER_REPOSITORY_BOUNDARY_COMPLIANT
E2E_RUNNER_FOUR_CONSECUTIVE_RUNS_PASS
PLAYWRIGHT_RUNTIME_GIT_CLEAN
TASK_OWNED_TEST_FAILURE_ZERO
REMEDIATION_EVIDENCE_FROZEN
READY_FOR_HARDENING_FOCUSED_INDEPENDENT_RE_QA
```

Not declared: `MONGLE_W7_5_HARDENING_FOCUSED_INDEPENDENT_QA_PASS`,
`MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`,
`FULL_PRODUCT_BEHAVIOR_WIRING_COMPLETE`,
`READY_FOR_W7_6_COMMON_COMPONENT_EXTRACTION`,
`W7_4_LIVE_CONSUMER_INTEGRATION_PASS`. W7.4 remains `REOPENED`; W7.5
overall remains `CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`.
Commit/push/merge/rebase were not performed.
