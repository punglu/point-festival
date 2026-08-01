# MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001

- Task ID: `MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001`
- Kind: independent QA of the parent bundle `MONGLE-PARALLEL-W2-W4-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; QA-created disposable PostgreSQL 16.9 container, no host port published, removed at teardown
- evidence: `agent-system/qa/MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001.md`
- secrets_redacted: `true`
- Lifecycle: `GRADUATED`
- Decision: `DESIGN_APPROVED` (PM independent-QA directive, 2026-08-01)
- Verification: `CONDITIONAL` — see disposition below
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- End HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Note on this file

This handoff was written at graduation to satisfy the Closeout Contract's
one-archived-handoff requirement. The QA evidence remains the substantive
record and is where the measurements live; nothing here restates them as new
findings.

## Origin

PM directed an independent QA of the whole parent bundle — Track A (Wagle
durable messaging), Track B (Markpoint access), and the integration work that
joined them.

## Outcome

Verdict `PARENT_INDEPENDENT_QA_CONDITIONAL`. Every product-contract check was
re-derived from a QA-created disposable database rather than read from the
implementing tasks' reports: migration `0007` verified against the PostgreSQL
catalog, migration `0008` constraints, Track A durable messaging and ordering,
Track B access lifecycle, and the Markpoint → Wagle relay boundary asserted
against the source.

Two conditions were raised:

- `FRONTEND_RUNTIME_FIX` — a HIGH frontend regression found and fixed during QA.
- `TRACEABILITY_GAP` — the entire bundle is uncommitted working state.

## Disposition (2026-08-01, at graduation)

- `FRONTEND_RUNTIME_FIX`: PM-accepted.
- `TRACEABILITY_GAP`: PM-accepted as non-blocking. It remains open as an
  uncommitted-worktree item, not as a product gap.
- **This QA's own classification of the ~127 frontend Doran occurrences as a
  non-blocking follow-up was retracted by PM.** The standing decision is that
  the retired name must not be used in the current product at all, not only in
  the backend runtime — and this QA's own need to patch `DoranLanding.tsx` was
  itself evidence of active frontend usage. Discharged by
  `MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001`,
  `MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001` and
  `MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001`.

The verdict is left at `CONDITIONAL` as recorded. It is not retroactively
upgraded to PASS — the conditions were resolved by later tasks, which is a
different thing from this QA having passed unconditionally.

## Risks and Human Gate

- A verifier fixing a defect it found is a weak spot by construction. That fix was re-verified from a different session by `MONGLE-COMBINED-NAMING-AND-FRONTEND-INDEPENDENT-QA-001`.
- No commit or push was made.

## Next agent first action

None — the parent bundle is complete. See `agent-system/relay/current.md`.

## Forbidden Scope

Reopening D1–D8; redesigning migrations `0007`/`0008`; Wave 3
realtime/Push/PIN; Markpoint Mission/Ledger; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md` — its section was removed at graduation; the record now lives in `agent-system/graduated/2026-08.md`.
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-PARALLEL-W2-W4-PARENT-INDEPENDENT-QA-001.md`
- Independent QA: `self` — this task is itself the independent QA.
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: the `API-INTEG-*` rows carry this QA's re-derived results.
- CLOSEOUT GATE: `PASS`
