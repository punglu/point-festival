# MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001

- Task ID: `MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `6c633679c6708a21920f0e4b306bc1e36a2ea72d`
- Scope: repository-boundary policy and linked guidance only.
- Forbidden scope: creation, deletion, relocation, or cleanup of any external
  directory; product/test/config/CI/Docker/DB changes.

## Result

The bootstrap, Claude entrypoint, Agent System rules, and a write-once PM
decision prohibit agent-created project material outside the Git worktree.
Current documentation that named an external capture path now labels it
historical-only and blocks recreation until a separately approved in-worktree
replacement exists.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001.md`
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: policy-only change; no test path, behavior, execution,
  tier, journey, or coverage state changed.
- CLOSEOUT GATE: `PASS`
