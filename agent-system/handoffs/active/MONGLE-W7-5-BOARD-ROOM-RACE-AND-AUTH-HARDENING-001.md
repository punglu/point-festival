# Handoff — MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001

- Task ID: MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001

## Origin

Opened directly from PM/Main-Architect direction relaying the `FAIL` verdict
of `MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001`
(`agent-system/qa/MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md`), read and
verified present in the repository before any work started (not taken on
trust from the pasted verdict alone).

## Scope

Fix, in fixed order, no per-step PM check-in:

1. Existing board-room duplicate data + FK fanout audit.
2. Deterministic no-loss merge strategy (HUMAN_GATE only on real
   unmergeable ambiguity).
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

## Step 1 — Duplicate data + FK fanout audit (2026-08-03)

Observed the persistent dev DB read-only (`mongle-db-1`, database
`mc_festival_phase0`, container never mutated):

```sql
SELECT family_group_id, title, count(*) FROM wagle_rooms
WHERE title='__family_board__' AND deleted_at IS NULL
GROUP BY family_group_id, title HAVING count(*) > 1;
-- 0 rows

SELECT count(*) FROM wagle_rooms;               -- 2
SELECT count(*) FROM wagle_rooms WHERE title='__family_board__'; -- 1
-- 0 duplicate-titled GROUP rooms of any title, not just the board sentinel
```

**Finding: 0 existing duplicate board-room rows in the only observed live
environment.** The race is real and reproducible under concurrency (per the
Re-QA's own load test), but has not left surviving duplicate data here. No
`HUMAN_GATE` triggered — there is no ambiguous real data to decide between.
The merge migration is still written and tested generically (idempotent
no-op when clean, real merge when not), verified against synthetic seeded
duplicates in a disposable DB per PM's own required completion criteria
("기존 중복 room의 message/reaction/comment/member 데이터 유실 0").

FK fanout into `wagle_rooms.id` (all `ON DELETE RESTRICT`, from
`backend/app/domains/wagle/models.py`):

- `wagle_direct_pairs.room_id` — DIRECT rooms only; a GROUP-type family board
  is never a target, but the merge routine checks generically.
- `wagle_participants.room_id` (composite FK with `family_group_id`) — active
  membership per room; `uq_wagle_active_participant` enforces one active row
  per `(room_id, family_membership_id)`, which the merge must respect when
  re-pointing.
- `wagle_messages.room_id` (composite FK) — `uq_wagle_messages_room_sequence`
  and `uq_wagle_messages_sender_client` both key off `room_id`, so moving a
  message into the canonical room requires sequence renumbering, not a bare
  `UPDATE`.
- `wagle_service_bindings.room_id` (composite FK) — a Service Principal bound
  to a duplicate room; must be repointed or the duplicate cannot be deleted.
- `wagle_message_reactions.message_id` → `wagle_messages.id` (not
  `room_id`), so reactions follow their message automatically once the
  message itself is moved; no separate handling needed.
- `wagle_participant_read_states.participant_id` → `wagle_participants.id`;
  moves/collapses with its owning participant row.

## Steps 2-8 — merge strategy, migration, service fix, tests, bcrypt fix (2026-08-03)

- Merge strategy (canonical = earliest `created_at`; participants promoted
  one row per membership with `joined_sequence` reset to 0; messages
  re-pointed and globally renumbered by `created_at`; reactions untouched
  (key off `message_id`); read-states folded via `GREATEST`; bindings
  re-pointed or dropped on collision; loser rooms soft-deleted) implemented
  in `backend/alembic/versions/0021_board_room_race_hardening.py`, plus the
  partial unique index (`uq_wagle_rooms_family_board_singleton`), mirrored
  in `backend/app/domains/wagle/models.py`.
- `backend/app/domains/wagle/service.py::create_room`'s GROUP branch now
  does a pre-check + `IntegrityError`/rollback/refetch get-or-create for the
  reserved board title only (mirrors the existing DIRECT-branch pattern);
  ordinary GROUP rooms are untouched.
- `backend/tests/test_wagle_integration.py::
  test_02b_family_board_concurrent_creation_converges_on_one_room` — 5
  concurrent HTTP requests x 10 fresh Families, asserts one room id and one
  surviving row every iteration.
- `backend/app/domains/auth/service.py::authenticate_admin` now wraps
  `bcrypt.checkpw` in `try/except (ValueError, TypeError): password_matches
  = False`, matching `family/auth_service.py::verify_password`'s existing
  pattern. New `backend/tests/test_auth_admin_login.py` (6 tests: oversized
  ASCII/multi-byte password both 401 not 500, unknown-username oversized
  password 401, correct/incorrect normal-length password unchanged
  behavior, schema still accepts a long password since the fix is at the
  bcrypt call site, not input rejection).
- `tests/e2e/scripts/run-w75-full-spec.sh`: added a real `SELECT 1`
  query-readiness gate beyond `pg_isready`, removed the `init.sql ... ||
  true` failure-hiding (now `-v ON_ERROR_STOP=1`, no swallow), added an
  explicit post-load `admin_auth` existence assertion, and a bounded
  (5-attempt) retry around `alembic upgrade head` for the one remaining
  transient (`ConnectionResetError`) QA observed. `tests/README.md` updated
  to describe this instead of silently claiming zero-flake.
- `tests/e2e/test-results/` added to root `.gitignore`; the previously
  tracked `.last-run.json` untracked via `git rm --cached` (file kept on
  disk, no commit performed) so future Playwright runs no longer drift a
  tracked file.

## Step 11 — migration downgrade/re-upgrade verification (2026-08-03)

Dedicated disposable database (`mc_migration_verify`, port 15499, `postgres:
16.9-alpine`, torn down after use via `docker rm -f` + confirmed absent from
`docker ps -a`). `database/init.sql` loaded, `alembic upgrade
0020_wagle_message_reactions`, then seeded synthetic data with a throwaway,
uncommitted script (deleted after use): Family A with 3 duplicate
`__family_board__` rooms (overlapping membership across rooms, non-
overlapping membership, cross-room messages including a duplicate-
membership sender, 2 reactions, 2 read-state rows with different values),
plus Family B with a single clean board room as a negative control.

```text
upgrade head (0021):        succeeded on the 3rd attempt -- 2 real bugs
  found and fixed by this exact verification run, not
  merely exercised by it:
    1. participant deletion was ordered before the message sender remap
       that referenced those same participant rows -- FK RESTRICT
       violation, fixed by moving the remap earlier.
    2. a bulk multi-row `UPDATE ... room_id = canonical WHERE room_id IN
       (losers)` collided immediately on (room_id, sequence) the moment two
       rooms' messages shared a sequence number -- fixed with a two-phase
       per-row move (temporary negative sequence, then real ascending
       1..N), see the migration's own updated docstring.
family_group 2 (dup'd):     1 active board room after merge (was 3)
family_group 3 (clean):     1 active board room, byte-identical to before
messages (family 2):        4 of 4 survived, sequence 1-4, sender remapped
                            correctly to the canonical participant
messages (family 3):        1 of 1 untouched
participants (family 2):    2 active (mem1, mem2), both in canonical room,
                            no duplicate active row for either membership
reactions (family 2):       2 of 2 survived, still pointing at their
                            original message ids
read-state (family 2):      GREATEST(0, 1) = 1 for the merged mem1 identity
                            -- confirmed correct, not merely present
unique index:               uq_wagle_rooms_family_board_singleton present
                            after upgrade
downgrade -1:               index dropped; data verified still merged
                            (1 room per family, not un-merged)
re-upgrade head:            index recreated with 0 errors (0 duplicates
                            remained to conflict with it)
```

Verdict: migration is correct and lossless against a genuinely non-trivial
synthetic case, not just the empty-production no-op path. Disposable DB and
seed script both torn down/deleted after use.

## Steps 12-13 — full verification suite (2026-08-03)

- Full backend suite, fresh disposable `postgres:16.9-alpine`
  (`mc_qa_suite_db`, port 15435, `conftest.py`'s own default creds/DB name),
  `database/init.sql` + `alembic upgrade head` (through `0021`), run twice
  consecutively: **389 passed, 0 failed, 0 errors** both times (410.95s,
  435.93s). Test count independently confirmed via `pytest --collect-only`:
  389 (382 prior + 1 new concurrency test + 6 new admin-login tests).
  `KNOWN-W7-5-WAGLE-CONCURRENCY-001` did not occur in either run. DB torn
  down after use.
- `tests/e2e/scripts/run-w75-full-spec.sh` run 4 times immediately
  back-to-back, no manual pause: **10/10 passed, 0 skipped, every time**
  (16.7-19.1s each) -- zero readiness failures, unlike the Re-QA's own
  2-of-4 failure rate before this task's fix. `git status` on
  `tests/e2e/test-results/` showed only the staged-deletion from
  untracking across all 4 runs, never a re-dirtied tracked file.
- Wagle 3x3 viewport regression (390x844/820x1180/1180x820 x
  3c/3d/3e-in-sequence), ad hoc uncommitted Playwright script against a
  dedicated disposable stack (Postgres 15496, backend 18097, Vite 5196):
  **3/3 passed**, 0 horizontal overflow (4 checkpoints x 3 viewports), 0
  console/page errors, Popular endpoint 200 with the created post present
  every time. Stack torn down; scratch script and copied spec file deleted
  after use.

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md

`CLOSEOUT GATE: PASS` means only that the four documentation obligations
above are synchronized -- it does NOT mean `Lifecycle: COMPLETED`,
Independent QA PASS, PM approval, or graduation. Per PM direction, this
task's own Verification remained Developer-self-check-only; the focused
Independent QA that followed
(`MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001`) returned `FAIL`, whose
remediation is `MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001` (its own
dedicated handoff:
`agent-system/handoffs/active/MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001.md`).
Coverage Map: 4 new rows this task added
(`API-W7-5-BOARD-ROOM-RACE-HARDENING-001`,
`API-W7-5-ADMIN-LOGIN-BCRYPT-HARDENING-001`,
`E2E-W7-5-2T-RUNNER-READINESS-001`, `E2E-W7-5-3X3-VIEWPORT-001`), plus
`KNOWN-W7-5-WAGLE-CONCURRENCY-001` extended with runs 14-15.

## Not independently measured / estimates disclosed

- Frontend static checks (`tsc --noEmit`, `eslint`, `vite build`) were not
  re-run this task -- no frontend product code changed (only backend
  Python, one Alembic migration, and a test-infra shell script). Marked
  `NOT_RE_RUN_THIS_PASS`, not assumed clean.
- The migration's defensive handling of a `wagle_service_bindings`
  collision-on-repoint branch was exercised only by code review, not by a
  synthetic test case with an actual Service binding on a duplicate board
  room -- no real or synthetic data has ever had one, and the branch's own
  logic (delete-on-collision, else repoint) is a direct, small extension of
  the already-tested message/participant repoint pattern.

## Summary for Main Architect

All three findings from `MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001`
(`RE-QA-F-BOARD-ROOM-RACE` HIGH, `RE-QA-F-ADMIN-LOGIN-BCRYPT` MEDIUM,
`RE-QA-F-2T-RUNNER-FLAKY` LOW) are fixed and regression-tested. Migration
`0021` is verified lossless against synthetic duplicates and its own
downgrade/re-upgrade cycle. Full backend suite 389/389 twice consecutively;
E2E runner 4/4 consecutive clean runs; Wagle 3x3 viewport regression clean.
No `HUMAN_GATE` was triggered -- the live persistent dev DB held 0 existing
duplicate board rooms. This Developer completion is **not** self-declared
as Independent QA PASS; per PM direction, a separate focused Independent
Re-QA is the required next step before W7.6 readiness is reconsidered. The
W7.4 Live Consumer Integration Audit and the 13 PM/design decision gates
from `MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001` remain separately open, out
of this task's scope.
