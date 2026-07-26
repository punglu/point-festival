# PHASE2-DORAN-MESSAGING-CONTRACT-001

- Task ID: `PHASE2-DORAN-MESSAGING-CONTRACT-001`
- Branch: `dev`
- Start HEAD: `18f4fb097ed689143785994f5250e56970c103fb`
- End HEAD: `pending — documentation commit follows`
- Final Commit: `pending — documentation commit follows`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`

## Scope

Define the Doran room, participant, message, read-state, synchronization,
authorization, Push boundary, and legacy 1:1 migration contracts. This is
design-only: no product code, schema, migration, WebSocket, Push, or UI change.

## Existing Dirty State

User-owned `CLAUDE.md` modification and root/docs deletions; start unstaged
SHA-256 `eae6f749b838eedb02780242c71d6cc285f97335f39d0728669f593877cbdf5f`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/PHASE2-DORAN-MESSAGING-CONTRACT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE2-DORAN-MESSAGING-CONTRACT-001.md`
- Independent QA: `not_applicable — contract design; implementation QA required`
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: `No executable product test or runtime evidence is added by this design-only task.`
- CLOSEOUT GATE: `PASS`

## Source inspection and design outputs

- Read the approved Phase 1 Account/Family/RBAC contract and Permission Matrix.
- Measured legacy chat as Player sender/receiver rows with per-row `is_read`,
  `created_at`/ID pagination, 15-second frontend polling, and no Room/Family
  model; treated it as legacy reference only.
- Added the seven linked `engineering/phase2/` contract documents: domain,
  data model, permission matrix, sync/WebSocket boundary, migration, threat
  model, and implementation plan.
- Recorded suite-isolation and screenshot-evidence durability as design
  prerequisites, not as an implementation claim.
