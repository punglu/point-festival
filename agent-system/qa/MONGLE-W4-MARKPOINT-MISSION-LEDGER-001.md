# MONGLE-W4-MARKPOINT-MISSION-LEDGER-001 — Wave 5 implementation evidence

## Executive Verdict

`WAVE_5_CORE_CONDITIONAL`: fresh Target ownership, approval reward,
append-only ledger, balance projection, level read, RBAC checks, and durable
Markpoint-to-Wagle Outbox path are implemented. It is not eligible for
independent QA or lifecycle graduation: rejection/cancellation/expiry,
template management routes, complete HTTP authorization matrix, and all
failure-injection cases remain.

## Baseline and Mapping

Branch `dev-newmarkp`, start HEAD
`25c8d0ccfa0406e2b458da7e8ca251ac8737b840`. The Wave 5 execution label maps
to authoritative Backlog task `MONGLE-W4-MARKPOINT-MISSION-LEDGER-001`; no
duplicate W5 task was created. No commit/push/reset/shared DB was used.

## Contract and Schema

Legacy player-owned Mission/Template/point tables and `players.total_earned`
remain reference-only. D5 uses FamilyGroup ownership and FamilyMembership
identity; D8 uses fresh empty schema, no backfill. `0010_markpoint_target_ledger`
follows 0009 and creates target Mission/Template, Ledger, Balance and Audit
tables. Composite membership/family FKs reject cross-family references; ledger
has nonzero amount, family/idempotency uniqueness, one-reversal uniqueness and
PostgreSQL update/delete rejection triggers.

## Implemented Slice

Explicit assignee mission create/submit/approve; approval atomically appends a
reward entry, updates balance, audits and enqueues `mission.approved`. Reversal
is a new negative entry. Manual adjustment requires reason, permission and
idempotency key. `/api/me/markpoint/*` serves own mission/ledger/balance/level
after server-derived membership/access validation. The existing outbox Worker
now accepts Target owner `markpoint`, provisions its ServicePrincipal and
uses Wagle's approved binding/service boundary; no Markpoint Wagle-table
import was added.

## Executed Evidence

Disposable PostgreSQL 16.9-alpine, initialized from repository
`database/init.sql`: fresh `0000 -> 0010`, downgrade `0010 -> 0009`, and
re-upgrade `0009 -> 0010` passed; single head is 0010.

- `tests/test_markpoint_target_wave5.py`: 4 passed.
- Target + Wave 4 access: 25 passed.
- Wagle service binding/reliable slice: 28 passed.
- `python -m compileall -q app`: passed.
- In-memory OpenAPI contains the new family routes and `/api/me/markpoint/*`.

The initial empty-DB attempt failed because 0000 deliberately stamps the
pre-existing legacy baseline; it passed after the documented init schema was
applied. This is bootstrap evidence, not a Target migration defect.

## Remaining / Lifecycle

Missing: manager rejection/cancel/expiry, template create/manage API, full
HTTP contract tests, level boundary coverage, relay retry/failure test and all
specified partial-transaction injections. `CONDITIONAL — APPROVED_CORE_SLICE_IMPLEMENTED; NOT_READY_FOR_FULL_LIFECYCLE_CLOSEOUT`.
