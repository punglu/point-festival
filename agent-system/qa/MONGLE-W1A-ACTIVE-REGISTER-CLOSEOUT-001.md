# MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001 Evidence

- Task ID: `MONGLE-W1A-ACTIVE-REGISTER-CLOSEOUT-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `da7ea7403aefef33a90d622940724b0c53ee8873`
- environment: local worktree `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`
- secrets_redacted: `true`
- Verification: `NOT_TESTED`
- Self-check only: `true`
- Independent QA: `not_applicable` — registration/governance record edits only; no product code, DB, auth, or test behaviour touched
- Closeout Contract: `v1`

## What this task claimed, and the measurement behind each claim

Every correction applied to `agent-system/active.md` by this task was measured
in this session rather than carried over from the earlier audit's write-up.

### Claim 1 — the A1 isolated-worktree location claim was false

```
test -d /Users/mac/mac_Project/mongle_ui-a1-visual-worktree   -> ABSENT
git worktree list                                            -> path not listed
git log --oneline -1 a1fe979
  a1fe979 merge: integrate A1 mobile visual publishing candidate
```

Result: the path does not exist, and the merge that landed A1 into this branch
is an ancestor of HEAD. The `active.md` claim "live in an isolated worktree,
never committed to this branch" was therefore false at the time of correction.
`PASS` — correction is factually grounded.

### Claim 2 — the DATA-A isolated-worktree location claim was false

```
test -d /Users/mac/mac_Project/mongle_ui-data-backend-worktree -> ABSENT
ls engineering/phase2/MONGLE_TARGET_BUSINESS_GLOSSARY.md
   engineering/phase2/MONGLE_TARGET_TABLE_DICTIONARY.md
   engineering/phase2/MONGLE_REALTIME_MESSAGING_CONTRACT.md    -> all present
git log --oneline -1 da7ea74
  da7ea74 merge: integrate data backend contract reconciliation
```

Result: path absent, documents present in this worktree, merge is HEAD itself.
`PASS` — correction is factually grounded.

Separately confirmed still-true and **left untouched**: a different,
undocumented external worktree at
`/private/tmp/claude-501/-Users-mac-mac-Project-mongle-ui/7815dbc1-.../scratchpad/data-backend-contract-worktree`
(detached HEAD `9bcd1a5`) appears in `git worktree list`. Human Gate under
`DEC-2026-005`; not resolved by this task.

### Claim 3 — `779cc70` belongs in the Doran R2 record

```
git merge-base --is-ancestor 0393971 HEAD  -> exit 0
git merge-base --is-ancestor 91eb98e HEAD  -> exit 0
git show --stat 779cc70
  779cc70 fix(mission): serialize point-bearing status transitions
  backend/app/domains/mission/service.py             |  54 +++--
  backend/tests/test_doran_reliable_service_slice.py | 126 +++++++++
```

Result: all three commits are real and merged. `PASS`.

Precision correction recorded alongside it: the pre-existing phrase "no
agent-system task record at all" slightly overstated the gap —
`engineering/phase2/DORAN_FOUNDATION_GAP_ANALYSIS.md` does document this work
and names `PHASE2-DORAN-R2B1-FOCUSED-QA-001` = PASS. What is genuinely absent
is the **Agent System registration** (`grep` of `active.md` and
`graduated/*.md` for that QA task ID returns no match), not all documentation.

## Structural self-check after editing

```
grep -c "^## " agent-system/active.md            -> 22   (was 23; one section graduated)
grep -c "^- Task ID:" agent-system/active.md     -> 20   (22 minus the 2 non-task headers) — consistent
grep -n "FREEZE-AND-DECOMPOSITION-001 above"     -> no match (dangling cross-reference repaired)
git diff --check                                 -> clean
awk pipe-count over graduated/2026-08.md         -> every row 5 columns, uniform
python3 agent-system/tools/check_closeout.py     -> see below
```

The `check_closeout.py` run after the first edit pass surfaced three real
defects in this task's own output, all corrected before closing:

1. `QA evidence is missing` / `QA Evidence Path is missing` — this file did not exist. Created.
2. `ACTIVE` / `QA EVIDENCE` / `CLOSEOUT GATE has invalid or missing value: empty` — the checker's field regex requires the value to end the line, and the handoff's Closeout block had trailing `— explanation` prose on those lines. Reformatted to bare values with the explanations moved below the block.
3. `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001: HANDOFF Path is not an allowed repository path` — that handoff still pointed at `handoffs/active/`, which **this task invalidated** by moving the file to `handoffs/archive/2026-08/` on graduation. Path corrected in that file; its findings and verdict were not altered.

## Known remaining warnings not caused by, and not resolved by, this task

- `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2: QA evidence is missing` and `Closeout Synchronization block is missing` — pre-existing defects in that task's own records. Correcting them requires deciding that task's closeout state, which is outside this task's PM-confirmed scope and belongs to the PM triage its `Next Action` already calls for.

## Not measured / estimated

None. No value in this task's corrections was inferred, remembered, or copied
from an earlier report without re-running the command that establishes it.
This task ran no test suite, no migration, no Docker, and no DB query — none
is applicable to a registration-only change.
