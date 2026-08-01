# MONGLE-PARALLEL-W2-W4-001 Evidence

- Task ID: `MONGLE-PARALLEL-W2-W4-001`
- author/agent: `Claude Code` (Track A, acting as Parent Coordinator)
- observed_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`
- secrets_redacted: `true`
- Verification: `NOT_TESTED` at bundle level
- Self-check only: `true`
- Independent QA: `pending`
- Closeout Contract: `v1`

## What this record verifies

Bundle-level parallel safety only. Lane A's implementation evidence is in
`agent-system/qa/MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001.md`.

## Baseline is shared and materialized

```
git merge-base --is-ancestor 2f1c354 HEAD    -> exit 0
git cat-file -e HEAD:backend/alembic/versions/0005_account_credential_session.py -> present
git cat-file -e HEAD:backend/alembic/versions/0006_family_service_separation.py  -> present
git cat-file -e HEAD:backend/app/domains/family/auth_service.py                  -> present
git cat-file -e HEAD:backend/app/domains/family/dependencies.py                  -> present
git cat-file -e HEAD:agent-system/qa/MONGLE-W1-INDEPENDENT-QA-001.md             -> present
```

Wave 1 exists as commits, not as another working copy's uncommitted diff, so
both lanes can start from the same baseline without copying anything. The
bundle is therefore **not** `BLOCKED_BASELINE_NOT_MATERIALIZED`.

## Worktree occupancy — measured, and a deviation reported

```
git worktree list
  /Users/mac/mac_Project/mongle_ui                                     0d9280c [dev-newmarkp]
  /private/tmp/claude-501/.../scratchpad/data-backend-contract-worktree 9bcd1a5 (detached HEAD)
```

The task brief asks Track A to use a worktree separate from Track B. **Track A
instead ran in the repository root**, on explicit PM instruction to work there.
This is a deliberate deviation, recorded rather than silently accepted, and it
transfers the constraint: Track B must not use the repository root while Lane A
is open.

The second worktree listed is the historical detached
`data-backend-contract-worktree` (record-integrity audit finding F7). It is
**not** Track B's, was not created by this bundle, and is untouched — resolving
it is a Human Gate under `DEC-2026-005`.

## Conflict assessment: none possible today

Track B has not started and owns no file. Lane A's actual footprint, measured
from `git status`:

```
backend/app/domains/doran/{service,router,schemas}.py
backend/tests/test_wagle_durable_wave2.py
```

Checked explicitly for territory Track B is expected to own:

```
git status --porcelain -uall | grep -E "frontend/|mission|daily_point|deduction|
  cheer|feedback|notification|level_tier|admin/"   -> no matches
```

So every Markpoint, service-ownership and frontend file is untouched. Alembic
head is unchanged at `0006_family_service_separation` (Lane A added no
revision), so Lane B inherits a clean single head.

Shared-document discipline: Lane A's edits to
`MONGLE_TARGET_API_INVENTORY.md` and `MONGLE_REALTIME_MESSAGING_CONTRACT.md`
are confined to Wagle sections. No Track B section was written or predicted.

## Bundle state

```text
PARENT_BUNDLE_IN_PROGRESS
LANE_A: TRACK_A_IMPLEMENTATION_COMPLETE / TRACK_A_TESTS_PASS / INDEPENDENT_QA_PENDING
LANE_B: NOT_STARTED
```

The bundle is not graduated and must not be, until Lane B completes and both
lanes pass independent QA.

## Not measured

- Track B's working-copy path — it does not exist yet, and is deliberately not guessed.
- Any Lane B implementation claim — none is made here.
