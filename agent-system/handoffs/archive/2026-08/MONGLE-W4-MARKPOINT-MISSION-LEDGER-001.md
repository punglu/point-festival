# MONGLE-W4-MARKPOINT-MISSION-LEDGER-001

- Execution-wave mapping: Wave 5 — Markpoint Mission / Ledger / Balance /
  Level / Reward. The Backlog task's `W4` ID is retained as authoritative.
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED — D4, D5-B/C, D7 and D8 are frozen.
- Verification: NOT_TESTED
- Execution: RUNNING
- Closeout Contract: v1
- Baseline: `dev-newmarkp` @ `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`;
  Alembic head `0009_wagle_realtime_push_pin`.
- Writer: single owner for Markpoint Target domain and its migration.
- Forbidden: Legacy data backfill/dual-write, MarkpointParticipant,
  FamilyAdmin/registrant automatic ServiceAdmin, Wagle direct DB/model import,
  Wave 6 UI, reward catalog, commit/push/merge/rebase/PR.

## Event branch matrix (DEC-2026-003)

| Event | Actor / precondition | API expectation | Durable state | Wagle event | Test / cleanup |
|---|---|---|---|---|---|
| Mission create/assign | ACTIVE Membership; active Markpoint; `markpoint.missions.manage`; assignee in same Family | 201 Target mission | mission + audit only; no ledger | none | API/DB same-family deny; disposable DB teardown |
| Completion submit | explicit assignee; allowed mission state | state becomes submitted | no reward before approval | none | API/DB transition/duplicate deny |
| Approval | explicit ServiceAdmin permission; submitted mission | success or idempotent existing success | approved mission + one reward ledger + projection + outbox atomically | `mission.approved` via port | concurrency/failure injection; disposable DB teardown |
| Rejection/cancel/reversal | manager; valid transition | state transition allowed only by contract | reversal ledger only if prior reward; projection atomic | approved event only (other event types deferred) | DB unique reversal + rollback tests |
| Manual adjustment | `markpoint.points.adjust`; same-family beneficiary; reason | 201 / idempotent retry | one append-only ledger + projection + audit | `points.adjusted` via port | authorization/idempotency tests |
| Wagle relay | Markpoint service principal/binding is valid | port result only | source-event unique outbox event, no Wagle direct write | Wagle consumes through existing adapter | adapter/dedup/cross-family tests |

## Current implementation evidence

`0010_markpoint_target_ledger` now implements fresh Target mission/ledger/
balance/audit persistence and the explicit create/submit/approve/manual-
adjustment/reversal slice. Evidence is in the matching QA record. Remaining:
manager rejection/cancellation/expiry, template management API, exhaustive
HTTP/failure-injection coverage, and Wagle delivery retry verification.
