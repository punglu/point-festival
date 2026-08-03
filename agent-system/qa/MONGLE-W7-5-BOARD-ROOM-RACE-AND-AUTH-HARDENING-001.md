# Task QA Evidence — MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001

- Task ID: MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001

```text
Targets: RE-QA-F-BOARD-ROOM-RACE (HIGH), RE-QA-F-ADMIN-LOGIN-BCRYPT (MEDIUM),
         RE-QA-F-2T-RUNNER-FLAKY (LOW)
         (agent-system/qa/MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md,
         confirmed present and read in full before any work started)
Status:  DEVELOPER_SELF_CHECK_COMPLETE -- NOT an Independent QA PASS
         declaration. Per PM direction, this task's own completion is
         reported to the Main Architect and a separate focused Independent
         Re-QA is expected next; this file does not substitute for it.
```

## Scope executed (fixed order, per PM direction, no per-step pause)

1. Existing board-room duplicate data + FK fanout audit.
2. Deterministic no-loss merge strategy.
3. Duplicate-merge migration.
4. DB unique invariant on the reserved family-board room.
5. Atomic get-or-create for GROUP `create_room`.
6. 5x10 concurrency regression test.
7. Legacy admin bcrypt 72-byte defense.
8. Admin long-password 401 regression test.
9. E2E runner Postgres-readiness + init.sql-failure-hiding removal.
10. Playwright runtime-artifact/tracked-dirty isolation.
11. Migration downgrade/re-upgrade verification.
12. Full backend suite x2 consecutively.
13. E2E runner x4 back-to-back (no pause) + Wagle 3x3 regression.

No `HUMAN_GATE` was triggered: the live persistent dev DB
(`mongle-db-1`/`mc_festival_phase0`, observed read-only only, never
mutated) held 0 existing duplicate board rooms, so there was no real
unmergeable data ambiguity to resolve. Full narrative detail, including two
real bugs found and fixed by the migration's own verification pass (a
participant-deletion ordering issue and a bulk-update sequence collision),
is in this task's handoff
(`agent-system/handoffs/active/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md`).

## RE-QA-F-BOARD-ROOM-RACE (HIGH) — fixed

```text
Fix:            backend/alembic/versions/0021_board_room_race_hardening.py
                (lossless duplicate merge + partial unique index
                uq_wagle_rooms_family_board_singleton, scoped to the
                reserved __family_board__ sentinel only);
                backend/app/domains/wagle/service.py::create_room (GROUP
                branch: pre-check + IntegrityError/rollback/refetch
                get-or-create, mirroring the existing DIRECT branch);
                backend/app/domains/wagle/models.py (mirrored Index()
                declaration)
Regression:     backend/tests/test_wagle_integration.py::
                test_02b_family_board_concurrent_creation_converges_on_one_room
                -- 5 concurrent HTTP requests x 10 fresh Families
Result:         every iteration: all 5 responses 201, all 5 share one
                room_id, exactly 1 non-deleted room row confirmed by direct
                count -- 0 duplicates across all 10 iterations
Migration verification: dedicated disposable DB (mc_migration_verify, port
                15499), synthetic seeded duplicates (3 rooms, overlapping +
                non-overlapping memberships, cross-room messages incl. a
                duplicate-membership sender, 2 reactions, 2 read-states)
                plus an untouched negative-control Family. Merge result:
                canonical = earliest created_at room; both memberships
                survived as exactly 2 active participants in canonical
                (no duplicates); all 4 messages survived, renumbered 1-4 in
                created_at order with sender correctly remapped; both
                reactions survived unchanged (key off message_id); read
                state correctly folded via GREATEST(0,1)=1; negative-
                control Family untouched. downgrade() dropped only the
                index (data stayed merged); re-upgrade() recreated the
                index with 0 errors.
```

## RE-QA-F-ADMIN-LOGIN-BCRYPT (MEDIUM) — fixed

```text
Fix:      backend/app/domains/auth/service.py::authenticate_admin --
          bcrypt.checkpw wrapped in try/except (ValueError, TypeError):
          password_matches = False, matching family/auth_service.py::
          verify_password's existing pattern. No schema max_length added
          (the fix is at the bcrypt call site, not input rejection).
Tests:    backend/tests/test_auth_admin_login.py, 6/6 pass:
  01: >72-byte ASCII password, seeded admin       -> 401 (not 500)
  02: >72-byte Korean (multi-byte) password        -> 401 (not 500)
  03: >72-byte password, unknown username           -> 401
  04: correct normal-length password                -> 200, real token
  05: incorrect normal-length password              -> 401
  06: schema itself still accepts a 500-char string (fix is not input
      rejection)
```

## RE-QA-F-2T-RUNNER-FLAKY (LOW) — fixed

```text
Fix:      tests/e2e/scripts/run-w75-full-spec.sh -- real `SELECT 1`
          query-readiness gate beyond pg_isready; `psql -v ON_ERROR_STOP=1`
          replacing the `init.sql ... || true` failure-hiding; explicit
          post-load `admin_auth` existence assertion; bounded 5-attempt
          retry around `alembic upgrade head`. tests/README.md updated to
          describe this instead of silently claiming zero-flake.
Verification: 4 consecutive invocations, immediately back-to-back, no
          manual pause: 10/10 passed, 0 skipped, every single time (17-19s
          each). Zero readiness failures across all 4, unlike the QA
          report's own 2-of-4 failure rate before this fix.
```

## Playwright runtime-artifact isolation (fixed, part of the same finding)

```text
Fix:      tests/e2e/test-results/ added to root .gitignore; the
          previously tracked .last-run.json untracked via `git rm --cached`
          (kept on disk, no commit performed).
Verified: across all 4 consecutive E2E runner runs above, `git status`
          showed the file only as a staged deletion (from the untracking),
          never re-appearing as a tracked-file modification.
```

## Wagle 3x3 viewport regression (this task's own required scope)

```text
Method:   ad hoc, uncommitted Playwright script (independently
          reimplemented, not a repository artifact, per prior QA
          precedent), against a dedicated disposable stack (Postgres
          15496, backend 18097, Vite 5196), torn down after use.
Viewports: 390x844, 820x1180, 1180x820
Screens:   3c (board post), 3d (comment), 3e (reaction + Popular Posts),
           each exercised in sequence within one test per viewport
Result:    3/3 passed. 0 horizontal overflow (checked after board load,
           after post appears, after comment renders, after Popular
           overlay opens -- 4 checkpoints x 3 viewports). 0 console/page
           errors. Popular endpoint returned 200 with the created post
           present, every viewport.
```

## Full backend suite (x2 consecutive)

```text
Environment: fresh disposable postgres:16.9-alpine (mc_qa_suite_db, port
             15435, matching conftest.py's own default), database/init.sql
             + alembic upgrade head (through migration 0021), torn down
             after use.
Run 1:       389 passed, 0 failed, 0 errors, 410.95s
Run 2:       389 passed, 0 failed, 0 errors, 435.93s (immediately following)
Test count independently confirmed via `pytest --collect-only`: 389 (not
             trusted from any prior report) -- 382 (prior Phase I count) +
             1 (test_02b) + 6 (test_auth_admin_login.py) = 389.
KNOWN-W7-5-WAGLE-CONCURRENCY-001: unaffected, both runs fully clean (no
             occurrence this pass).
```

## Static checks

```text
bash -n tests/e2e/scripts/run-w75-full-spec.sh: syntax OK
```
(`tsc`/`eslint`/`vite build` not re-run this pass -- no frontend product
code was changed by this task; only backend Python, one migration, and a
test-infra shell script were touched. This is disclosed as
`NOT_RE_RUN_THIS_PASS`, not silently assumed clean.)

## Baseline / environment integrity

```text
Worktree:    /Users/mac/mac_Project/mongle_ui, branch dev-newmarkp
Persistent dev stack (mongle-db-1/mongle-backend-1/mongle-frontend-1):
             observed read-only only (one investigatory query at task
             start), never used as a test-mutation target, confirmed still
             running unmodified throughout
Disposable infra used this task: mc_migration_verify (15499),
             mc_qa_suite_db (15435), the run-w75-full-spec.sh runner's own
             throwaway stack (x4, ports 15493/18096/5195), and a viewport-
             verify stack (15496/18097/5196) -- all confirmed removed via
             `docker ps -a` / `lsof` after use
Commit/push/merge/rebase: none performed, per PM direction
Concurrent writer note: agent-system/active.md and relay/current.md were
             found modified by another concurrent session (the
             `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)`
             task) during this task's own registration step. This task's
             edits were purely additive and did not touch that other
             task's section; no conflict occurred.
```

## 5-Gate Self-Check

- **Hallucination Guard**: the 389 test count was independently collected
  via `pytest --collect-only`, not assumed from arithmetic alone (though
  the arithmetic also checks out); the migration's merge correctness was
  verified by direct SQL inspection of every affected table, not inferred
  from the migration succeeding without error; the "0 existing duplicates"
  claim is a live query result against the persistent dev DB, not an
  assumption.
- **Omission Guard**: two real bugs found by this task's own migration
  verification (participant-deletion ordering, bulk-update sequence
  collision) are disclosed in the handoff and migration docstring, not
  silently fixed and hidden; the migration's own known limitation
  (`uq_wagle_messages_sender_client` collision on a genuine cross-room
  duplicate submission fails loud rather than guessing) is disclosed, not
  omitted.
- **Miswork Guard**: `bash -n` confirms the shell script's syntax; the
  migration was verified via a real disposable-DB round trip
  (upgrade/downgrade/re-upgrade), not merely read for plausibility; all
  temporary/scratch files (seed script, ad hoc viewport spec, scratch
  runner script) were deleted after use and confirmed absent.
- **Axis Alignment**: this Developer self-check is explicitly not an
  Independent QA PASS declaration; a clean 2-run backend suite does not
  retire `KNOWN-W7-5-WAGLE-CONCURRENCY-001`, which remains a separately
  registered condition; the migration being correct against synthetic
  duplicates does not imply real production data was ever at risk today
  (it was not -- 0 duplicates observed) -- both facts are stated, not
  merged into one claim.
- **Freshness/Evidence Consistency**: every count and status above was
  produced by a command run in this session against current HEAD and live
  disposable databases/browsers, not carried forward from the Re-QA
  report's own numbers (which concerned the *pre-fix* state).

## Final Declaration

```text
MONGLE_W7_5_BOARD_ROOM_RACE_AND_AUTH_HARDENING_DEVELOPER_SELF_CHECK_COMPLETE
RE_QA_F_BOARD_ROOM_RACE_FIXED_AND_REGRESSION_TESTED
RE_QA_F_ADMIN_LOGIN_BCRYPT_FIXED_AND_REGRESSION_TESTED
RE_QA_F_2T_RUNNER_FLAKY_FIXED_4_OF_4_CONSECUTIVE_RUNS_CLEAN
PLAYWRIGHT_ARTIFACT_TRACKING_ISOLATED
MIGRATION_MERGE_VERIFIED_LOSSLESS_AGAINST_SYNTHETIC_DUPLICATES
MIGRATION_DOWNGRADE_REUPGRADE_VERIFIED
BACKEND_SUITE_389_389_TWICE_CONSECUTIVELY
WAGLE_3X3_VIEWPORT_REGRESSION_CLEAN
NOT_DECLARED: INDEPENDENT_QA_PASS -- awaiting a separate focused
  Independent Re-QA per PM direction
NOT_DECLARED: W7_6_READY -- the W7.4 Live Consumer Integration Audit and
  the 13 PM/design decision gates from MONGLE-W7-5-DATA-AND-BEHAVIOR-
  WIRING-001 remain separately open, out of this task's scope
```

Commit/push/merge/rebase were not performed. Result reported to the Main
Architect; awaiting a separate focused Independent Re-QA before this task
or W7.6 readiness is treated as settled.
