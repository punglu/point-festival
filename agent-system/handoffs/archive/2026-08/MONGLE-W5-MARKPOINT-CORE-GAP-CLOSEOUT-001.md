# MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001

- Task ID: `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001`
- Predecessors: `MONGLE-W4-MARKPOINT-MISSION-LEDGER-001`, `MONGLE-W5-MARKPOINT-FUNCTIONAL-COVERAGE-GAP-COMPLETION-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9; throwaway backend image with container-only dependencies
- evidence: `agent-system/qa/MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001.md`
- secrets_redacted: `true`
- Lifecycle: `IMPLEMENTED_AWAITING_INDEPENDENT_QA`
- Decision: `DESIGN_APPROVED` (PM Wave 5 Core Closeout directive, 2026-08-01)
- Verification: `PASS` (self-check only)
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
- End HEAD: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Origin

PM accepted the preceding FAIL as accurate and directed a single session to
drive every Core `PARTIALLY_COVERED` and the one `MISSING_REQUIRED_IN_WAVE_5`
to zero by implementation and verification — not by re-investigation or Matrix
rewriting.

## Worktree and changed files

- New: `alembic/versions/0011_markpoint_family_config.py`, `tests/test_markpoint_core_gap_wave5.py` (54 tests), `tests/test_markpoint_http_authorization_wave5.py` (15 tests).
- Modified: `markpoint_target/{models,service,router,schemas}.py`, `app/models/all_models.py`, `frontend/src/generated/openapi.d.ts` (regenerated), plus the Coverage Matrix and the Agent System records.
- **No frontend product code** — Wave 6 is out of scope. **No legacy backfill, no dual-write, no `MarkpointParticipant`, no Wagle DB access.**
- Existing dirty state from the preceding Wave 5 and audit tasks was preserved.

## Commands and outcomes

```
alembic heads                      -> 0011_markpoint_family_config (single)
fresh 0000 -> head                 -> PASS
downgrade -1 / re-upgrade          -> residual 0 / restored
legacy backfill after upgrade      -> 0 rows
core gap tests                     -> 54 passed
HTTP authorization matrix          -> 15 passed
backend pytest --collect-only      -> 312
backend pytest -q                  -> 312 passed, 0 failed   (was 238)
OpenAPI regenerated                -> 140 paths, doran 0, naran 0
frontend tsc --noEmit              -> EXIT=0
git diff --check                   -> clean
```

Coverage Matrix now: `COVERED_TARGET 10`, Core `PARTIALLY_COVERED 0`,
`MISSING_REQUIRED_IN_WAVE_5 0`, `UNCLASSIFIED 0`, `DEFERRED_TO_WAVE_6_UI 1`,
`PM_DECISION_REQUIRED 3` (unchanged), `REPLACED_BY_* 2`.

## Defects

**No product defect was found in the code under closeout.** Five test failures
occurred during development and all five were mine: three wrong level-boundary
expectations (I mis-derived `excess // last_gap`), a test that tried to backdate
a ledger row with `UPDATE` — refused by a DB trigger, i.e. the product working —
and two ORM/schema mistakes on my side. Each is recorded in §22 of the report
next to what it initially looked like.

## Known gaps / carried forward

- Independent QA has not run.
- `MP-U01` stays `DEFERRED_TO_WAVE_6_UI`: every backend capability the dashboard needs is implemented and tested; only the rendering is Wave 6.
- `MP-S01` Cheer, `MP-S02` Feedback, `MP-S03` in-app Notification remain `PM_DECISION_REQUIRED` — **not** retired, not reclassified, and they did not block this closeout.
- Legacy `configs` / `daily_points` / `mission_templates` retirement is Wave 7 cutover, not this task.

## Risks and Human Gate

- **The legacy rolling-window docstring contradicts its own code**: the code gives a Monday a 14-day window, the docstring claims 7 ("이번 주만"). The **code** is preserved. Do not "fix" this to match the docstring without PM approval — it changes how many missions every Monday generates.
- **Bulk approval is all-or-nothing** because no approved contract defines partial success. Adding per-item results is a contract change, not an improvement.
- **The Ledger is append-only and the database enforces it** (`markpoint_ledger_no_update`, `markpoint_ledger_no_delete`). A correction is a reversal plus an optional replacement; never edit a row.
- **Level input is `lifetime_earned`, never `current_balance`** — using the balance would drop a child's level when they spend points.
- **Guard A and Guard B are server-side and Family-scoped.** Do not add a force override: none is defined by contract, and an override is where a guard quietly stops meaning anything.
- No commit or push was made. Branch and HEAD unchanged.

## Next agent first action

Wave 5 independent QA. Re-derive from a fresh disposable database: migration
`0011` fresh/downgrade/re-upgrade with zero legacy backfill; both cycle guards
from the *other* Family's side; concurrent materialization and the
bulk-vs-single approval race; the append-only property by attempting an
`UPDATE`; the level boundary matrix including the exact-last-tier branch; and
the full HTTP matrix, especially that a **family owner** is refused every admin
capability.

## Forbidden Scope

Wave 6 frontend; Cheer/Feedback/in-app Notification implementation; reward
catalog; legacy data backfill or dual-write; `MarkpointParticipant`; direct
Wagle DB or model access; editing or deleting a Ledger row; a cycle-guard force
override; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: two new source-backed rows for the Markpoint Core capabilities and the HTTP authorization matrix.
- CLOSEOUT GATE: `PASS`
