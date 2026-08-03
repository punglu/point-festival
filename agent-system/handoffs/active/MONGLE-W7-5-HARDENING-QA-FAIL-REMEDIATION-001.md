# Handoff — MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001

- Task ID: MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001

## Origin

Opened directly from PM/Main-Architect direction relaying the `FAIL` verdict
of `MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001`
(`agent-system/qa/MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001.md`),
confirmed present and read in full before any work started. Target:
`MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001` (its own handoff:
`agent-system/handoffs/active/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md`).

Two blocking findings:

```text
HARDENING-QA-F-001 (HIGH)   Migration 0021 active-participant semantics loss
HARDENING-QA-F-002 (MEDIUM) E2E runner repository-boundary policy violation
```

## HARDENING-QA-F-001 — root cause and fix

`backend/alembic/versions/0021_board_room_race_hardening.py`'s
`_merge_duplicate_board_rooms()` picked its participant survivor by
querying only **loser**-room rows, ordered by `joined_at ASC` with no
`status` filter, whenever canonical held no *already-active* row for a
membership. Reproduced by Independent QA: canonical `left`, loser
(older `left`, newer `active`) -> the older `left` row was promoted and the
genuinely `active` row was merged away and deleted, leaving `active: 0,
left: 2` for that membership.

Fix: rewrote the participant-survivor selection to consider **every** row
across the whole duplicate room set (canonical's own rows included, not
just loser rows). If any row anywhere is `active`, it always wins
(preferring one already in canonical, else the earliest to join). Only when
no active row exists anywhere is a deterministic terminal (`left`) survivor
chosen (canonical's own row first, else the most recently left, else the
most recently joined). `joined_at` merges to the earliest across the set;
`left_at` clears to `NULL` when the final state is active, or merges to the
latest `left_at` otherwise.

While rewriting, also fixed a related-but-not-independently-flagged gap:
read-states were previously folded via a raw `GREATEST(...)` on the
*pre-merge* sequence number, which becomes meaningless once messages are
globally renumbered during the same merge (the same raw integer can end up
pointing at a completely different message). Now every participant's own
`last_read_sequence` (survivors included, not only rows being merged away)
is translated through an explicit old-`(room_id, sequence)`-to-new-sequence
mapping built while renumbering messages, then folded via `GREATEST`.

### Independent confirmation of the old defect

Before writing regression tests, the exact QA-reported shape was run
against a throwaway copy of the *pre-remediation* function (not the
repository's own file — a scratch copy, deleted after use) on a disposable
database, then rolled back:

```text
OLD BUGGY RESULT (case7 shape): [{'status': 'left', 'count': 2}]
```

Matches `HARDENING-QA-F-001`'s own reported evidence (`left=2, active=0`)
verbatim — the regression test added below is a genuine regression test,
not a coincidentally-passing one.

### New permanent regression matrix

`backend/tests/test_migration_0021_participant_merge.py` — 10 cases against
real PostgreSQL (not mocks), using a `board_singleton_index_dropped` fixture
that drops the migration's own unique index for the test's duration only
(restored in a `finally`, confirmed not to affect other test files) so
duplicate rows can be seeded, then invokes the migration's own
`_merge_duplicate_board_rooms` via `AsyncConnection.run_sync` (the same
async/sync bridge Alembic's own `env.py` uses):

1. canonical active, loser active
2. canonical active, loser left
3. canonical left, loser active (single-candidate shape — independently
   confirmed against the old algorithm to leave a stray duplicate left row,
   a milder variant of the same defect class)
4. canonical left, loser left
5. no canonical participant, one loser active
6. no canonical participant, multiple loser active
7. canonical left, loser older-left + newer-active — **the exact
   `HARDENING-QA-F-001` reproduction shape**
8. multiple active, different read-states (confirms sequence-translation
   fix, not just status preservation)
9. multiple left, different lifecycle timestamps
10. a different Family with the same membership shape (cross-family
    isolation)

All 10 pass. Also re-ran alongside the existing focused suite
(`test_wagle_integration.py`, `test_auth_admin_login.py`,
`test_w75_phase_d_board_reactions.py`) to confirm the index-drop/restore
fixture does not bleed into other files: 49/49 passed.

### Re-verified lossless merge + round trip

Fresh disposable database (`mc_migration_verify_v2`, port 15499, torn down
after use). Seeded Family A with the exact `HARDENING-QA-F-001` shape
(membership 3: canonical `left`, loser older-`left` + newer-`active`) plus
an ordinary untouched membership (1) and a cross-room-duplicated membership
(2), all sharing messages/reactions/read-states, plus Family B as an
untouched negative control (matching the original
`BOARD-ROOM-RACE-AND-AUTH-HARDENING-001` verification's own scenario shape,
re-run against the fixed algorithm):

```text
membership 3 (the QA bug): active, left_at NULL -- fixed, confirmed
messages: all 4 survived, sequence 1-4, sender correctly remapped
reactions: both survived
read-states: 1, 3, 4 -- correctly translated into the merged sequence
  numbering (membership 2's cross-room read position correctly resolves to
  its own later message, not a stale raw integer that would now point at
  an earlier one)
Family B: byte-for-byte untouched
downgrade -1: index dropped only; data (including membership 3's `active`
  status) stayed merged, not un-merged
re-upgrade head: index recreated with 0 errors
```

## HARDENING-QA-F-002 — root cause and fix

`tests/e2e/scripts/run-w75-full-spec.sh` redirected its throwaway
backend/frontend logs to `/tmp/mc_w75_spec_runner_*.log` -- outside the
worktree, which `AGENTS.md`/`agent-system/rules.md` prohibit. Independent QA
correctly refused to run the required four back-to-back invocations under
this violation.

Fix: every invocation now computes its own absolute, timestamped,
in-worktree, gitignored runtime directory
(`tests/e2e/.runtime/w75-runner/run-<timestamp>-<pid>/`) before starting the
backend/frontend, prints its path, and removes it automatically on a
passing run (kept, with the path re-printed, on a failing run for
diagnosis). `tests/e2e/.runtime/` added to root `.gitignore`.
`tests/README.md` updated to describe this instead of the old `/tmp` path.

### A real bug this fix's own first verification run caught

The first attempt used a **relative** path for the log files
(`tests/e2e/.runtime/w75-runner/run-.../*.log`). Since the backend/frontend
are started via `( cd backend && ... > "$LOG" )` / `( cd frontend && ... >
"$LOG" )` subshells, the relative path resolved against the wrong directory
after the subshell's own `cd` — the redirect failed silently (background
subshell, no propagated error), uvicorn/vite never actually started, and
**all 10 Playwright tests failed** on the very first re-run. Root-caused via
the log directory itself being empty (no `backend.log`/`frontend.log` at
all) rather than assumed. Fixed by making the runtime directory an absolute
path (computed via `$(pwd)` before either subshell's own `cd`), and
additionally hardened the backend/frontend readiness loops to fail loudly
(rather than silently proceed to a guaranteed-failing Playwright run) if the
service never becomes reachable within the existing 30-attempt window.

### Verification

```text
Run 1: 10 passed, 0 skipped, 0 failed (16.6s)
Run 2: 10 passed, 0 skipped, 0 failed (16.6s) -- immediately following
Run 3: 10 passed, 0 skipped, 0 failed (16.6s) -- immediately following
Run 4: 10 passed, 0 skipped, 0 failed (16.4s) -- immediately following
```

No manual pause between any of the 4 runs. `git status` on `tests/e2e/`
after all 4 shows only the pre-existing dirty state (the modified spec file
and the staged `.last-run.json` deletion from the prior task, plus an
unrelated pre-existing scratch file) — no new drift introduced by any run.
`docker ps -a` confirms 0 leftover containers after all 4.

## Full verification suite (post-fix)

```text
Focused (test_wagle_integration.py + test_auth_admin_login.py +
  test_w75_phase_d_board_reactions.py + test_migration_0021_participant_
  merge.py): 49 passed
Full backend suite (pytest --collect-only): 399 tests (389 prior + 10 new
  migration-matrix tests)
Run 1: 399 passed, 0 failed, 0 errors (382.65s)
Run 2: 399 passed, 0 failed, 0 errors (379.22s)
Wagle 3x3 viewport regression (ad hoc, uncommitted, dedicated disposable
  stack): 3/3 passed, 0 overflow, 0 console/page errors
tsc --noEmit: clean
eslint: clean
vite build: clean (pre-existing chunk-size warning only, unrelated)
git diff --check: clean
```

## Static/governance checks — a real defect found and fixed in this task's
own prior records

`agent-system/tools/check_all.py` flagged
`MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001` and this task itself
for missing Handoff/QA-evidence recognition. Root cause: the prior task's
own Closeout Synchronization block and QA-evidence header used prose/code-
fence formatting, not the `- Field: value` Markdown list-item lines
`check_closeout.py`'s parser actually requires. Fixed: added a real
`- Task ID: ...` line to both
`agent-system/handoffs/active/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md`
and
`agent-system/qa/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md`,
converted that handoff's Closeout Synchronization block to list-item
fields, and gave this remediation task its own dedicated handoff/QA-evidence
files (this file and its counterpart) rather than sharing the parent task's
files — the checker recognizes at most one Task ID per document, so sharing
was not actually representable in its model despite being a reasonable
reading of the PM's own "same task lineage" framing.

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001.md

Coverage Map: one new row
(`API-W7-5-MIGRATION-0021-PARTICIPANT-MERGE-MATRIX-001`, the 10-case
regression matrix), corrections appended to
`API-W7-5-BOARD-ROOM-RACE-HARDENING-001` and
`E2E-W7-5-2T-RUNNER-READINESS-001` (both findings this task fixed), and
`KNOWN-W7-5-WAGLE-CONCURRENCY-001` extended with runs 16-17 (399/399 both).

`CLOSEOUT GATE: PASS` means only that the four documentation obligations
above are synchronized — it does NOT mean `MONGLE_W7_5_DATA_AND_BEHAVIOR_
WIRING_PASS`, Independent QA PASS, W7.6 readiness, or W7.4 Live Consumer
Integration completion. Per PM direction, this task does not self-declare
Independent QA PASS; the result is reported to the Main Architect, and a
separate `MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001` is the
required next step. W7.4 remains `REOPENED`; W7.5 overall remains
`CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`.

## Not independently measured / estimates disclosed

- The `wagle_service_bindings` collision-on-repoint branch in the migration
  was not re-exercised by a new synthetic test this pass (unchanged by this
  remediation, already disclosed as review-only in the prior task's
  handoff).
- Frontend static checks were re-run this pass (unlike the prior task, which
  disclosed them as skipped) since a governance/tooling pass benefits from a
  full baseline; no frontend product code changed either pass.
