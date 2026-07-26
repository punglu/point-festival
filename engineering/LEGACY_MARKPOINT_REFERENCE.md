# MarkPoint Legacy Reference Baseline

**Status: LEGACY REFERENCE / NOT FULLY VALIDATED (2026-07-26).**

This repository's current MarkPoint implementation is a contained reference for
the next platform, not a verified product contract. The Phase 0 containment work
protects the known current player/admin boundaries; it does not prove all legacy
calculations, state transitions, concurrency behavior, or historical data.

## Reference that may be retained

- Existing player and administrator journeys, screen vocabulary, and familiar workflow sequencing.
- The business terms mission, daily point, deduction, level, notification, feedback, and current 1:1 chat.
- The semantic meaning of current tables and candidate migration data, subject to source-by-source validation during migration.
- Existing screen information that users recognize.

## Not inherited as a platform contract

- Authentication and authorization implementation details, including any former caller-controlled `player_id` behavior.
- API response shape, error handling, transaction placement, silent failure behavior, hand-maintained frontend transport types, and legacy test results.
- Role/ownership rules, state-transition rules, idempotency semantics, concurrency behavior, and unverified aggregate calculations.

## New platform direction

- Write an explicit API contract for each new capability; do not copy legacy route behavior by default.
- Use server-side default-deny authorization, API plus DB-invariant tests, and current authenticated actor identity rather than a caller-supplied target ID.
- Introduce family tenancy, roles, room participation, idempotency, migrations, and adapters only through their own approved capability work.
- Minimize direct coupling to the legacy database. Migration uses a measured, reversible adapter and synthetic/anonymous fixtures; operating data is never copied into tests.

## Explicitly unvalidated legacy areas

- Complete point and level correctness, all mission/repeating lifecycle edges, all duplicate-request outcomes, historical data consistency, and all FE/BE type alignment.
- Physical-device/PWA behavior, keyboard/system Back behavior, Push delivery, operating DB backup/restore rehearsal, and initial Alembic schema comparison.

The route-by-route containment classification is maintained in
[LEGACY_API_SECURITY_MATRIX.md](LEGACY_API_SECURITY_MATRIX.md).
