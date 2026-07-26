# Phase 1 Foundation Implementation Plan

**Status: TARGET PLAN / PM_REVIEW_REQUIRED (2026-07-26)**

## Work packages

1. **Schema and registry foundation** — approved Alembic baseline/revision,
   target tables, minimal permission/role seeds, constraints, and indexes.
2. **Account and Membership authorization** — Account session identity,
   Membership resolution, default-deny permission guards, family/resource
   boundary checks, and Account-session extension points.
3. **Legacy identity adapter** — dry-run mapping report, reviewed mapping rows,
   legacy login compatibility, MarkPoint Player resolution, and rollback switch.
4. **Family governance API** — groups, Membership lifecycle, roles,
   owner-transfer safeguards, and audit/transaction boundaries.
5. **MarkPoint adapter** — family-scoped Player mapping and incremental
   conversion of new/changed MarkPoint endpoints; no blanket legacy rewrite.
6. **Frontend foundation** — Account session/current Family/permission selector,
   family switcher when API contract is approved, and `/dashboard` compatibility
   adapter.
7. **Rollout and cleanup** — dual-path verification, monitored cutover, then a
   separately approved legacy credential/role retirement plan.

## Test and QA plan

Every package that changes schema, migration, auth, RBAC, ownership, or legacy
mapping requires isolated API + DB assertions and independent QA. At minimum:

- Account/Membership creation and lifecycle;
- duplicate active Membership prevention;
- multiple Role union and role removal;
- inactive Membership/account denial;
- cross-family resource denial with DB non-mutation;
- self versus delegated permission boundary;
- subscription/service-role denial;
- last-owner removal/transfer atomicity;
- legacy mapping ambiguity/dry-run/rollback;
- session behavior after Membership or Role changes.

Use synthetic data only. Test implementation cannot weaken existing assertions
or claim operating data validation. Independent QA must separately inspect schema
invariants, migration/reversibility, JWT/session behavior, route guards, DB
non-mutation, and the mapping report.

## Rollout checkpoints

1. PM resolves the five gates below.
2. Foundation schema/API design is reviewed before migration implementation.
3. Backup/restore rehearsal and schema comparison pass before any operating DB
   stamp or data migration.
4. Adapter parity and mapping report are accepted before new auth becomes
   canonical.
5. Legacy login/role removal is a later, separately approved change.

## PM Gates (maximum five)

| Decision item | Options | Recommendation | Impact | Default if undecided |
| --- | --- | --- | --- | --- |
| Owner cardinality and transfer | exactly one owner; multiple owners with minimum one | allow multiple active owners, require at least one, atomic transfer/removal | schema constraints, governance UI, recovery | do not implement owner removal/transfer; retain owner-protected workflow |
| Role scope storage | one scoped `roles` registry; split family/service role tables; unscoped roles | one `roles` table with explicit scope plus separate assignment paths | query, admin UI, migration complexity | implement family roles only; defer service-role assignment |
| Family context transport | path; header; body/query; selected context server-side | explicit API context selected per request, server checks membership/resource; final wire location must be approved | API shape, frontend switcher, audit | no cross-family resource APIs; resolve only server-known default/context |
| Explicit grants/denies in v1 | role-only; grants; grants + denies | role-to-permission plus service roles only | schema and policy complexity | default deny; no per-user exception rows |
| Initial Family mapping | one legacy household; operator-selected grouping; invite/onboarding only | operator-reviewed mapping report; no automatic owner/relationship inference | migration timeline and user access | create no active Membership for ambiguous rows |
