# Operating DB Backup and Migration Rehearsal Plan

**Status: APPROVED PLAN / HUMAN_GATE_REQUIRED.** This document authorizes no database connection, backup, migration, or restore by itself.

## Preconditions and ownership

- PM names the operating environment, data owner, approved maintenance window, encrypted storage location, retention period, and rollback owner.
- Verify the target database identity, server version, extensions, roles, privileges, schema names, migration head, available disk space, and external file/object-store dependencies before any write.
- Do not copy operating personal data into local fixtures. Use anonymized or synthetic data for rehearsal unless the owner explicitly approves a protected procedure.

## Backup set

Create and checksum separate artifacts as appropriate:

| Artifact | Purpose |
| --- | --- |
| Full logical backup | complete schema and data recovery |
| Schema-only backup | DDL, constraints, indexes, sequences, and extensions review |
| Data-only backup | controlled data restore/reconciliation |
| Roles/privileges export | access restoration; stored under strict access controls |
| External file manifest | attachments/object storage mapping and integrity check |

Use `pg_dump`/`pg_restore` commands chosen for the measured PostgreSQL version; do not copy a command from this plan into production without owner review.

## Rehearsal sequence

1. Record baseline row counts for users/players, family or authority relations, missions/templates, daily points/ledger-equivalent data, `players.total_earned`, level tiers, deductions, notifications, chats/messages, configuration, and soft-deleted rows.
2. Export backup artifacts; record SHA-256 checksums, encryption method, storage location, retention expiry, operator, and timestamps without secrets.
3. Restore into an isolated non-operating PostgreSQL target with matching roles, extensions, sequences, constraints, and external-file access policy.
4. Compare schema, migration/version state, row counts, key aggregates, soft delete visibility, and sampled authorization boundaries.
5. Run the approved application smoke/API invariant set against the restored target only.
6. Document success criteria, observed deviations, and a rollback point before any production migration is approved.

## Alembic adoption after baseline freeze

1. Compare current operating schema with `database/init.sql` and proposed ORM metadata; resolve drift by explicit PM decision, never by blind autogenerate.
2. Create or approve the first baseline/stamp procedure only after the backup rehearsal passes.
3. Each later ORM/schema change includes one linear Alembic revision, upgrade behavior, downgrade/rollback statement, expected row-count/invariant effect, and isolated rehearsal evidence.
4. No migration can be applied merely because it exists in Git.

## Human gates remaining

- operating credential and maintenance-window authorization
- backup destination, encryption, retention, and restore-owner approval
- external attachment/object-store restoration method
- first schema comparison and Alembic baseline/stamp approval
