# PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2

- Task ID: `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2`
- Start HEAD: `0828a6d181e633b099eb0747cb3191fe78d80903`
- Branch: `dev`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `RUNNING`
- Closeout Contract: `v1`

R2 supersedes any earlier Doran Foundation implementation prompt. It implements
only the secure DB/HTTP foundation: no legacy-chat cutover, WebSocket, Push,
completed UI, E2EE, or operating migration.

Existing user dirty SHA-256: `eae6f749b838eedb02780242c71d6cc285f97335f39d0728669f593877cbdf5f`.

## Current implementation checkpoint

- Declared files: `backend/app/domains/doran/**`, `backend/alembic/versions/0002_doran_messaging_foundation.py`, Family permission adapter/model registration, Phase 2 contracts, and this task's evidence records.
- Added Doran Room, canonical DIRECT pair, participation-period Participant,
  Message, and participant Read State models and the `0002` revision.
- Added the Family-scoped HTTP router and service boundaries for Room,
  Participant, Message/tombstone, cursor, and read cursor operations.
- Static migration evidence: `alembic upgrade head --sql` and
  `alembic downgrade 0002_doran_messaging_foundation:0001_account_family_rbac --sql` generated PostgreSQL DDL successfully.
- Remaining: isolated PostgreSQL migration execution, deterministic synthetic
  fixture/reset, API/DB authorization and concurrency tests, generated OpenAPI
  type verification, regressions, and independent QA. No completion or push is
  authorized from this checkpoint.
