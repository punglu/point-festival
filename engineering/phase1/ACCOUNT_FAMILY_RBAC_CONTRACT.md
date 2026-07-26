# Account, Family, and Multirole RBAC Contract

**Status: APPROVED DECISIONS / v0.1 (2026-07-26)**
**Authority:** PM decision `PM-DECISION-RBAC-MULTIROLE-001` (Drive ID
`12J43Bd7BEdxPxLupJv9vsQlKf133kWicaka8tkLKVO4`), directly reviewed for
this contract. Git remains the implementation SSOT.

## Purpose and boundary

This is the target authorization contract for the Naran platform. It is not an
implemented schema, migration, JWT payload, API change, or retrofit of the
contained MarkPoint application. The current MarkPoint implementation remains
**LEGACY REFERENCE / NOT FULLY VALIDATED**.

## Approved Foundation decisions

1. Multiple active Owners are allowed; each Family keeps at least one active
   Owner, and Owner is a Membership Role rather than a `family_groups.owner_id`.
2. `roles` is a unified registry with `scope_type` (`FAMILY` or `SERVICE`) and
   nullable `service_code`; its scoped code is unique.
3. Family-scoped APIs use `/api/families/{family_id}/...`; JWT identifies only
   the Account, and server-side Membership/resource checks establish authority.
4. v1 uses Role-Permission unions only. Explicit grants and denies are absent;
   default deny applies.
5. Legacy bootstrap creates one reviewed Family candidate per installation only
   with an explicit Owner mapping. Relationships default to `unknown`/`other`,
   and identity ambiguity blocks operating activation.

The contract separates four things that are currently conflated in legacy code:

| Concept | Target responsibility | Must not be used as |
| --- | --- | --- |
| Account | login identity, credential, security state, sessions, account audit | family-specific role container |
| Profile / service participant | display and service-specific data; MarkPoint participant mapping | platform login identity by default |
| Family Group | durable family data boundary | a global account role |
| Family Membership | Account-to-Family relation, relationship, lifecycle, and roles | a credential or session |

## Current model measured, not adopted

- `players` has a legacy `role` constrained to `player`/`admin`, profile fields,
  lock/visibility fields, and `total_earned`.
- `player_auth` is one-to-one with a Player and contains a PIN hash and lock
  counters. `admin_auth` has its own username/password credential and may point
  to a Player.
- Current JWTs encode a global `role` and `sub`; the frontend restores that
  role from session storage and routes to `/dashboard` or `/admin`.
- Mission, daily-point, deduction, feedback, notification, and chat rows refer
  to `players.id`. There is no family-group foreign key, membership, or
  permission registry.

These facts explain the migration need; they are not the new-platform contract.

## Account and service profile

An **Account** is the canonical platform authentication subject. It owns an
immutable internal ID, login identifiers/credentials, active/deleted state,
security/session metadata, and account-level audit fields. A single Account may
join more than one Family Group.

A platform Profile is optional display/person data associated with an Account.
A MarkPoint Player is a **service participant/profile**. It is linked through
an explicit legacy or service mapping; renaming the existing `players` table to
`accounts` would lose the distinction and is prohibited.

## Family Group and Membership

Every new family-scoped resource belongs to exactly one active Family Group.
Personal account data and system-wide registry data are the only alternatives.
New family data without a Family Group is invalid.

A **Family Membership** links one Account to one Family Group. It carries:

- membership lifecycle (`invited`, `active`, `left`, `suspended` as target
  states; exact transition policy is implementation work);
- a display Relationship;
- zero or more family roles;
- optional service-role assignments; and
- timestamps/audit fields and, when needed, a default Profile reference.

An inactive, suspended, or soft-deleted membership has no effective permissions.
An inactive/deleted account has no effective permissions.

## Relationship is not authorization

`mother`, `father`, `child`, `guardian`, `grandparent`, and `other` are display
and family-relationship values. They are not role aliases and are never an API
authorization predicate. For example, a child may have Relationship `child`
and family Role `member` or `restricted_member`; an adult child may have
administrative permissions. Age and legal-guardian policies are deliberately
deferred.

## Roles and permissions

Roles are named Permission bundles. A Membership may hold multiple roles, while
the common case may use one base role. Roles are not stored as an Account array
or a global Account `role` column.

The target family roles are `owner`, `admin`, `member`, and
`restricted_member`. `sub_admin` is not a target role. `owner` includes the
administrative permissions needed to preserve the group and additionally
controls ownership transfer, closure, and top-level settings. Detailed owner
count/lifecycle policy is a PM Gate.

Backend authorization is permission-based and default-deny. Frontend checks are
only UX gates. A new API must follow this order:

```text
authenticate Account
→ resolve active Membership for resource Family Group
→ calculate effective permissions server-side
→ require permission and resource ownership/family boundary
→ execute service under its use-case transaction
```

No caller-provided account, player, membership, or family ID is authorization
proof. A supplied family context is a selection hint only and must be cross
checked with Membership and the resource's Family Group.

The initial registry is intentionally bounded. Family governance starts with
`family.read`, `family.members.invite`, `family.members.remove`,
`family.roles.assign`, and `family.ownership.transfer`; MarkPoint starts with
`markpoint.own_missions.read`, `markpoint.missions.manage`,
`markpoint.own_points.read`, and `markpoint.points.adjust`; messaging starts
with `messaging.participate` and later explicit room-management permissions.
The complete initial decision matrix is [Permission Matrix](PERMISSION_MATRIX.md).

## Effective Permission calculation

```text
Effective Permissions
= active Family Membership Roles
+ active service-specific Membership Roles for an active subscription
```

The result is a set union: duplicate permissions have no extra effect. Version
1 intentionally does **not** introduce explicit per-membership grant or deny
rows. They remain a future extension only if a demonstrated policy cannot be
represented by scoped roles. Service unsubscription removes access even when a
service role row exists; disabled/deleted roles are ignored.

## Family roles and service roles

The recommended model is **common family roles plus optional service roles**.
Family roles cover group governance and baseline participation. Service roles
are added only when service-specific delegation is required:

- MarkPoint: `mission_manager`, `point_admin`, `participant`.
- Doran: `room_admin`, `participant`.

This avoids making a family `admin` automatically an unrestricted administrator
of every future service. A Family Role may grant baseline service permission
where explicitly mapped; a service-specific assignment grants only its scoped
permission bundle.

## Family context and sessions

JWT identifies the Account, not a permanently selected Family Group or a
frozen permission set. The server resolves current Membership and permissions on
each request so role/membership changes take effect without trusting stale token
claims. A family context is selected per request through an API shape to be
approved in Foundation design; it must be resource-checked server-side.

Sessions belong to Accounts, not Memberships. Future session records may include
device ID/label, token hash, issued/last-seen/revoked timestamps, and Push-token
association. This creates a clean extension point for device revoke and for
immediate permission re-evaluation after Membership changes. Multi-device policy
is not decided here.

## Frontend target contract

The authenticated frontend state will eventually include Account session,
available Families, current Family, Membership relationship, and effective
permissions. UI code should ask a capability selector such as
`can("markpoint.missions.manage")`, not compare raw role names. Generated
OpenAPI wire types stay at the API boundary and map to feature/view models.
`/dashboard` remains an adapter surface until its replacement is deliberately
migrated. Backend remains final authority.

## Explicit non-goals

This contract does not create tables, alter legacy credentials/JWTs, decide
invite UX, design Doran rooms, establish idempotency semantics, or prove legacy
calculations. Foundation implementation must independently test schema,
migration, authentication, RBAC, ownership, and cross-family DB invariants.
