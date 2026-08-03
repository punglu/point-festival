# Independent Re-QA — MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001

```text
Targets: MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001;
         MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001
Observed: 2026-08-03/04 KST; branch dev-newmarkp;
          HEAD f8003c50f2db4df5f3af1276f921812038cfb3bc
Verdict: FAIL
```

## Baseline

The worktree began dirty with the remediation files untracked and pre-existing
implementation changes; stash was empty. Persistent `mongle-*` runtime was
not used. E2E runs introduced no new Git delta. QA made no product, test,
migration, or seed edit; this report and the required relay occupancy record
are QA metadata only.

## Remediation checks that passed

- **0021 structure:** one linear head from `0020_wagle_message_reactions`;
  sentinel-only partial unique index constrained by GROUP/title/deleted state;
  ordinary GROUP duplicate titles remain permitted.
- **Survivor/read-state audit:** source considers all participant rows,
  makes active win, clears `left_at` for active survivors, and translates
  old `(room_id, sequence)` read cursors to the globally renumbered sequence.
- **Real PostgreSQL focused command:**
  `pytest -q tests/test_migration_0021_participant_merge.py tests/test_wagle_integration.py tests/test_auth_admin_login.py tests/test_w75_phase_d_board_reactions.py`
  → **49 passed**, 1 warning, 46.57s. The 10-case matrix includes the exact
  canonical-left + loser-old-left + loser-new-active shape and directly calls
  the 0021 merge routine against seeded DB rows.
- **E2E boundary and repeatability:** runner has no `/tmp`/HOME artifact path;
  runtime is absolute, in-worktree and ignored under `tests/e2e/.runtime/`.
  README command was run four times immediately back-to-back. Runs 1–4 each
  yielded **10 passed, 0 failed, 0 skipped** (16.6s, 16.4s, 16.6s, 16.7s).
  Each used query readiness, `init.sql` `ON_ERROR_STOP`, Alembic head,
  synthetic credential, service readiness and trap cleanup; no runner-induced
  Git dirty or surviving runner container was observed.

## Blocking finding

### RE-QA-F-003

```text
Severity: HIGH
Category: PRODUCT_DEFECT / backend-suite regression (Markpoint)
Evidence: current full-suite Run 2 failed deterministically; focused rerun
  failed again on the same disposable PostgreSQL.
Tests:
  tests/test_markpoint_core_gap_wave5.py::test_projection_derives_every_figure_from_the_ledger
  tests/test_markpoint_core_gap_wave5.py::test_projection_isolates_date_boundaries
Observed: own_projection(..., anchor=date.today()) returned today_earned=0,
  expected 30 and 7 respectively.
Reproduction: DATABASE_URL=<fresh disposable DB> python3.11 -m pytest -q
  <the two IDs above>  -> 2 failed in 1.69s.
Impact: backend full-suite two-run stability gate is unsatisfied; daily
  earned-point projection is incorrect in this environment.
Required remediation: investigate/fix the Markpoint projection date-boundary
  behavior, then re-run the entire suite twice independently.
```

## Backend suite

```text
Collected: 399 (actual pytest --collect-only)
Run 1: 399 passed, 1 warning, 409.77s
Run 2: 397 passed, 2 failed, 1 warning, 413.60s
Focused reproduction: 2 failed, 1 warning, 1.69s
```

Run 2 therefore cannot be treated as a known-condition-free PASS, regardless
of migration and runner remediation passing. No PASS declaration is valid.

## Scope boundaries and cleanup

The exact 10-case test exercises merge data, participants, lifecycle and
read-state rows against PostgreSQL; E2E's final Wagle board case exercised
post/comment/reaction/Popular behavior. A separate bespoke synthetic merge
fixture and standalone 3×3 script were not completed after the mandatory
backend gate deterministically failed; neither is represented as PASS.
The disposable database was used only for QA and must be removed during task
cleanup. W7.5 overall remains CONDITIONAL/HUMAN_GATE; W7.4 is REOPENED and
W7.6 remains blocked. No W7.4/W7.6 completion claim is made.
