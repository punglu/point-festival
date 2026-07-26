# Account, Family, and RBAC Target Data Model

**Status: APPROVED FOUNDATION MODEL / v0.1 (2026-07-26)**
**Implementation status:** implemented for isolated synthetic migration only;
operating schema comparison, stamp, and mapping remain Human Gates.

## Model overview

```text
accounts ──< family_memberships >── family_groups
                    │        │
                    │        └──< membership_roles >── roles ──< role_permissions >── permissions
                    │
                    └──< membership_service_roles >── service_roles
                                                        │
family_groups ──< service_subscriptions ───────────────┘

accounts ──< sessions
accounts / legacy identities ──< legacy_identity_mappings >── legacy Player/Admin/User identifiers
```

The diagram is target-only. Existing MarkPoint rows continue to reference
`players.id` until an approved adapter/migration step maps them.

## Candidate tables

| Table | Responsibility | Key and relationship | Lifecycle / notes |
| --- | --- | --- | --- |
| `accounts` | canonical login/security subject | internal PK; unique normalized login identifier(s) | active/deleted status, timestamps, security audit; no family role column |
| `family_groups` | family data boundary | PK; referenced by Membership and subscriptions | active/closed status, timestamps, audit; no family resource may omit this boundary |
| `family_memberships` | Account membership and relationship | PK; `account_id → accounts`, `family_group_id → family_groups` | invitation/active/left/suspended status, relationship, timestamps, soft delete/audit policy |
| `roles` | named role bundle | PK; scope and code | active status; code unique within approved scope |
| `permissions` | stable permission registry | PK; global permission code | registry data; never inferred from relationship |
| `membership_roles` | multi-role assignment | `membership_id → family_memberships`, `role_id → roles` | assignment audit; unique pair |
| `role_permissions` | role-to-permission mapping | `role_id → roles`, `permission_id → permissions` | unique pair |
| `service_subscriptions` | Family service enablement | `family_group_id → family_groups`, service code | active/subscribed lifecycle; one active service record per family/service |
| `service_roles` | scoped service-role definition | PK; service code/scope and role code | permission mapping may reuse `role_permissions` or a clearly named equivalent, decided in Foundation |
| `membership_service_roles` | service-role assignment | `membership_id`, `service_role_id` | assignment is effective only for active Membership and subscription |
| `legacy_identity_mappings` | explicit, reviewable legacy identity bridge | target Account/Profile reference plus legacy system/type/id | mapping confidence/status and audit; no heuristic automatic merge |
| `sessions` | future Account-device session control | `account_id → accounts` | token hash, device label/ID, issued/last-seen/revoked; not implemented now |

## Required invariants

| Invariant | Target enforcement |
| --- | --- |
| One Account has at most one active Membership in the same Family Group | partial unique index or equivalent approved DB invariant over active rows |
| A Family Group has at least one active owner | transactional service rule plus DB-safe final-owner protection; exact owner cardinality is a PM Gate |
| Role codes do not collide inside their scope | unique `(scope, code)` |
| Permission codes are global and stable | unique `permissions.code` |
| Same Membership cannot receive same Role twice | unique `(membership_id, role_id)` |
| Same Role cannot contain same Permission twice | unique `(role_id, permission_id)` |
| Same Membership cannot receive same service Role twice | unique `(membership_id, service_role_id)` |
| Service role is usable only in the matching active subscription | server query/guard plus FK/scope validation |
| Legacy identity mappings do not silently collide | unique legacy system/type/id; target-side multiplicity requires explicit mapping status |
| New family-scoped resource references one Family Group | non-null FK in each new family-scoped table |

## Nullable and delete policy

Identity, foreign keys defining security boundaries, codes, lifecycle state, and
audit timestamps are non-null unless a documented lifecycle explicitly requires
otherwise. Relationship may be nullable only during an invitation state; an
active Membership must have a deliberate value. Soft deletion should preserve
audit/migration history, but authorization always excludes deleted/inactive
accounts, memberships, groups, roles, and subscriptions.

Deletion cascades must not silently erase security/audit history. Foundation
chooses restrictive FKs or explicit lifecycle transitions over broad cascading
deletes. Legacy `ON DELETE CASCADE` behavior remains a legacy condition and is
not copied automatically.

## Index candidates

- active Membership resolution by `(account_id, family_group_id, status)`;
- resource-family and active Membership joins;
- unique active Membership invariant;
- role and permission code lookups;
- membership-role and role-permission joins;
- active subscription lookup by `(family_group_id, service_code)`;
- legacy mapping lookup by legacy system/type/id and by target identity;
- session lookup/revoke by `account_id`, token hash, and active status.

Indexes are candidates, not approved DDL. Query plans and actual migration
shape must be measured during Foundation work.

## Role scope alternatives

| Option | Strength | Cost / risk | Recommendation |
| --- | --- | --- | --- |
| A. one `roles` table with `scope` | one registry, simple common mapping tables | scope validation and service linkage require care | **recommended**, subject to PM Gate |
| B. separate family/service role tables | type distinction is explicit | duplicate join/mapping patterns and more migration/UI work | not preferred for v1 |
| C. permission scope only, unscoped roles | flexible bundles | easy to assign a role in the wrong context | reject for v1 |

Recommended A uses an explicit `scope` (`FAMILY`, `MARKPOINT`, `MESSAGING`,
future service code) and validates assignment path: family-role assignment via
`membership_roles`; service-role assignment only via
`membership_service_roles` with matching active subscription.

## Transaction boundaries

The approved target UoW owns one transaction. Membership creation, initial role
assignment, and default service enrollment must be atomic where a workflow
requires all of them. Ownership transfer must atomically prove a successor,
assign/retain the successor owner role, and prevent removal of the final owner.
Routers/services/helpers do not independently commit in new Foundation code.
