# Legacy Identity Mapping and Migration Plan

**Status: TARGET CONTRACT / PM_REVIEW_REQUIRED (2026-07-26)**
**Legacy source:** contained MarkPoint only; no operating database was accessed.

## Measured legacy identity surfaces

| Legacy surface | Current meaning | Target treatment |
| --- | --- | --- |
| `players` | MarkPoint participant/profile with global `player`/`admin` role | candidate MarkPoint service profile; not automatically Account |
| `player_auth` | one PIN credential for one Player | legacy credential input to an approved adapter/migration path |
| `admin_auth` | username/password administrator credential, optional Player reference | candidate Account credential/identity input; not automatic owner |
| mission/daily point/deduction/feedback/notification | data keyed to `players.id` | retain legacy reference; link through explicit Player mapping |
| chat sender/receiver | 1:1 participant IDs pointing to Player | retain legacy participant identity until a later messaging model |
| legacy `role`/`is_admin` | globally scoped compatibility values | mapping candidate only; never direct target Family Role truth |

## Mapping policy

```text
Legacy Admin/User credential ──> candidate Account
Legacy Player ────────────────> MarkPoint service profile / participant
explicit reviewed relation ───> LegacyIdentityMapping
legacy global role ───────────> initial family/service-role candidate, never automatic final grant
```

Do not infer identity because username/display name matches. Do not infer that
dad/mom labels create owner roles. Do not activate a soft-deleted legacy user as
an active Membership. Do not merge duplicate Players without an operator-reviewed
mapping decision. Ambiguous, duplicate, orphaned, and invalid references remain
in a mapping report for human resolution.

## Recommended migration sequence

1. Take approved operating backup and perform schema comparison; do not access
   operating data before that Human Gate.
2. Add target schema through an approved Alembic revision after bootstrap
   baseline is frozen.
3. Seed the minimal Permission registry and approved family/service Roles.
4. Produce a dry-run report: legacy credentials, Players, soft-deleted rows,
   duplicates, missing references, and candidate mappings.
5. Create Accounts only for approved candidate identities; record source ID and
   mapping status rather than silently merging.
6. Apply PM-approved Family Group creation rule; create active Memberships only
   from reviewed mappings.
7. Assign initial roles through an explicit mapping table/report. Preserve any
   unknown legacy role as unresolved rather than granting access.
8. Link MarkPoint Player identities through `legacy_identity_mappings` and use a
   read adapter/dual-read period to preserve `/dashboard` compatibility.
9. Run row counts, foreign-key/orphan checks, authorization API+DB tests, and
   operator reconciliation before switching canonical authentication.
10. Move new sessions to Account identity only after verified adapter parity;
    retain a rollback point and do not delete legacy role/credential data in the
    first rollout.

## Rollback and safety

Each migration must be reversible at the adapter cutover boundary. Preserve the
legacy login path until the migration report is accepted, record every mapping
decision, and do not use production personal data as test fixtures. Rollback
means disabling the new adapter/session path and restoring from approved backup
only under the operating plan; it never means executing ad hoc destructive SQL.
