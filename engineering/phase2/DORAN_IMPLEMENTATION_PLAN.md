# Doran Foundation Implementation Plan

**Prerequisite:** PM approval of the five gates in
[Doran Messaging Contract](DORAN_MESSAGING_CONTRACT.md). No package starts
against a shared mutable test database without deterministic isolation.

1. **Data foundation** — Alembic revision, Room/Participant/Message/read-state
   tables, indices, sequence allocation, seed registry, upgrade/downgrade.
2. **Authorization and HTTP** — Family-scoped guards, Room lifecycle,
   participant and message APIs, client-message idempotency, cursor lists,
   read-state monotonicity, API+DB tests.
3. **Sync** — authenticated WebSocket adapter, versioned events, cursor
   reconnect, revocation behavior, duplicate/out-of-order tests.
4. **Frontend Doran** — generated API types, family-scoped cache, Room UX,
   optimistic idempotent send, accessibility, responsive journeys.
5. **Legacy adapter/migration rehearsal** — reviewed mapping report, dry run,
   checksums, dual-read boundary, rollback rehearsal. Operating migration is a
   separate Human Gate.
6. **Device and Push** — Account Session/device foundation first, then minimal
   Push payload, opt-out/read/badge handling, real-device evidence.

Every package has a dedicated setup/teardown strategy (suite DB, transaction
rollback, or deterministic reset), plus independent QA covering Family IDOR,
participant visibility, sender spoofing, idempotency, ordering, and DB
invariants.
