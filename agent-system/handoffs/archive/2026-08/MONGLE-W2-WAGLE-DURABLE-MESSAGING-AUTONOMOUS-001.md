# MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001

- Task ID: `MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001` (Lane A)
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9 container on `127.0.0.1:15435`, removed at teardown
- evidence: `agent-system/qa/MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001.md`
- secrets_redacted: `true`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `PASS` (self-check only) — round 1 was `REJECTED_PENDING_NAMING_CORRECTION` by PM; corrected and fully re-run
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- End HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged — no commit)
- Final Commit: `not applicable — no commit performed; the PM performs commit/push`

## Backlog tasks executed

`MONGLE-W2-WAGLE-DURABLE-COMMAND-001`,
`MONGLE-W2-WAGLE-TRANSACTIONAL-OUTBOX-001`,
`MONGLE-W2-WAGLE-ORDERING-CURSOR-001`,
`MONGLE-W2-WAGLE-ROOM-LIST-READ-MODEL-001`.

Two of the four were already implemented before this Wave (durable send with
idempotency; room-local ordering and the forward-only read cursor). They were
verified by test rather than rebuilt — a DoD is met when the behaviour is
pinned, not when the code merely exists.

## Worktree and changed files

- Changed Files — modified (3): `backend/app/domains/doran/{service,router,schemas}.py`. New (1): `backend/tests/test_wagle_durable_wave2.py`. Records/docs: `engineering/phase2/MONGLE_TARGET_API_INVENTORY.md`, `MONGLE_REALTIME_MESSAGING_CONTRACT.md`, `MONGLE_IMPLEMENTATION_BACKLOG.md`, `agent-system/qa/COVERAGE_MAP.md`, `agent-system/active.md`, `agent-system/relay/current.md`, this handoff and its QA evidence.
- Existing Dirty State: the working tree was **clean** at start (HEAD `0d9280c`, everything previously committed). Nothing was reset, restored, checked out, cleaned or stashed.

## Commands and outcomes

```
git merge-base --is-ancestor 2f1c354 HEAD        -> exit 0 (Wave 1 baseline in HEAD)
git cat-file -e HEAD:<5 Wave-1 paths>            -> all present
alembic heads / current (fresh DB)               -> single head 0006_family_service_separation
alembic upgrade head from database/init.sql base -> PASS (0000 -> 0006)
pytest tests/test_wagle_durable_wave2.py -q      -> 20 passed (post-correction, fresh DB)
pytest -q (whole tests/ directory)               -> 145 passed, 0 failed
  of which Lane A owns 124 (20 Wave 2 + 104 pre-existing); 21 are Track B's
```

- Tests Run: backend unit/integration/API/DB as above.
- Tests Not Run: WebSocket/Push/Service Worker/PIN/presence (out of Wave 2 scope, none exists); frontend lint/build and Playwright (no frontend change, no FE consumer). Actor-separation and Room-binding denial have no *new* tests because the 26 pre-existing Doran service tests already cover them and ran green inside this run.

## Start Gate answer

The Backlog asked Track A to verify whether message persistence and the Outbox
enqueue already shared one transaction. **They did not.** `send_message` wrote
no Outbox row at all, so D6's atomicity requirement was unmet rather than
loosely met, and Wave 3's dispatcher would have had nothing to consume for human
messages. Closing that is this Lane's central change.

## Completed / remaining

- Known Gaps:
  - Independent QA has not run. Mandatory before completion, graduation or push.
  - Outbox **consumption** (dispatcher, WebSocket, Push) is Wave 3 and absent by contract.
  - Unread count does not include SERVICE_ACTION messages, inherited from `read_state()` and matched deliberately so the list and per-room endpoints agree. The user-visible rule is `D6-P4`, still undecided — flagged for Wave 3, not silently changed here.
  - No frontend consumer exists for `/room-summaries`.
- Not Measured / Estimated: none.
- QA Status: self-check only.
- Coverage Map Review: `UPDATED` — three new source-backed rows, re-run and re-stated after the naming correction.

## Migration

**No revision was created.** The naming correction changed emitted *values*,
not schema, so it added no revision either. Both changes needed only the existing
`service_outbox_events` table and the existing `(room_id, sequence)` index, so
Alembic remains at a single head `0006_family_service_separation`. Track A's
sole-migration-writer role still holds for Lane B; an empty revision would have
added a meaningless head and was not written.

## Risks and Human Gate

- Durability, transaction boundary and family isolation are security-relevant surfaces; independent QA should re-derive the atomicity claim rather than accept this report's test count.
- The parent bundle must not be graduated until Lane B completes.
- No commit or push was made. The PM performs `git push`.

## Next agent first action

Independent QA of Lane A: re-verify that no message can exist without its Outbox
event (and vice versa) from a database this QA creates itself, force a
post-persist failure independently, confirm the two rooms' sequence spaces are
genuinely independent, and check `/room-summaries` for cross-family leakage.
Read the current source; do not accept this report's 124/124 as the verdict.
Also re-audit the naming contract: assert over stored Outbox rows that no newly
emitted identifier carries `doran`, since round 1 of this Lane failed exactly there.

## Forbidden Scope

Markpoint product code; service ownership/activation code; Track B reports or
handoffs; frontend; WebSocket; Web Push; Service Worker; Wagle PIN; presence;
message edit/delete policy; legacy message backfill; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: three new source-backed rows for real executed tests.
- CLOSEOUT GATE: `PASS`
