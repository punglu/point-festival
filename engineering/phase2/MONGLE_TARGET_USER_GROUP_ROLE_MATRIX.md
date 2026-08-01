# MONGLE_TARGET_USER_GROUP_ROLE_MATRIX

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

Per PM instruction, no user-group name, role name, or permission is confirmed here beyond what an already-approved migration seeded (`PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001`). This matrix presents the current approved baseline as-is and flags every place a fresh Mongle-framing decision is genuinely open.

## Group scope

| scope_type | service_code | Meaning | Evidence |
|---|---|---|---|
| `FAMILY` | (none) | A permission that applies across the whole Group, not tied to any one Service | `roles.scope_type` CHECK — `family/models.py:38-51` |
| `SERVICE` | `markpoint` | A permission scoped to the MarkPoint service within one Group | same |
| `SERVICE` | `doran` | A permission scoped to the 와글와글 (Doran) service within one Group | same |

**RESOLVED by approved D1:** 몽글 is a family platform and the Family-specific vocabulary is retained. `FAMILY` stays; renaming it to a generic `GROUP` scope_type is **rejected**, not pending. The former open question is `STALE_CONFLICT_REMOVED`.

**Still open, `REQUIRES_PM_REVIEW` / `NON_BLOCKING`:** whether the specific seeded role code strings are final. D4 approves the *structure* — FamilyAdmin and ServiceAdmin are separate FamilyMembership-scoped roles, service work authority requires explicit ServiceAdmin assignment, default deny, last-admin protection and audit — but does not re-confirm the code strings themselves. The Wave 1 scoped-RBAC task confirms them at its Start Gate; changing one is a real migration.

**D4 mapping note:** in the approved vocabulary, `FamilyAdmin` is the FAMILY-scope administrative role and `ServiceAdmin` is a `SERVICE`-scope role per `service_code`. Holding a FAMILY-scope admin role **never** implies Markpoint work authority; that requires an explicit `SERVICE`-scope assignment. A FamilyAdmin may assign that role to themselves, but the assignment must exist.

## Role matrix (current approved baseline)

| Role code | scope_type | service_code | Name (Korean, from seed) | Grants (via `role_permissions`, per migration seed) | Evidence |
|---|---|---|---|---|---|
| `owner` | FAMILY | — | Owner | ALL current FAMILY-scope permissions (cross-joined to every permission at seed time — see caveat below) | `0001_account_family_rbac_foundation.py:132-148` |
| `admin` | FAMILY | — | Admin | `family.read`, `family.members.read`, `family.members.invite`, `family.members.manage`, `family.services.manage`, `markpoint.missions.manage`, `markpoint.points.adjust` | same file, lines 149-157 |
| `member` | FAMILY | — | Member | `family.read`, `family.members.read`, `markpoint.own.read` | lines 158-164 |
| `restricted_member` | FAMILY | — | Restricted member | `markpoint.own.read` only | lines 165-170 |
| `participant` | SERVICE | `markpoint` | MarkPoint participant | `markpoint.own.read` | lines 171-179 |
| `mission_manager` | SERVICE | `markpoint` | Mission manager | `markpoint.missions.manage` | same |
| `point_admin` | SERVICE | `markpoint` | Point administrator | `markpoint.points.adjust` | same |
| `participant` | SERVICE | `doran` | Doran participant | `doran.messages.read`, `doran.messages.send` | `0002_doran_messaging_foundation.py:39-40` |
| `room_admin` | SERVICE | `doran` | Doran room admin | above + `doran.rooms.create`, `doran.rooms.manage`, `doran.participants.manage` | same, line 41 |

**Caveat on `owner`**: the seed migration's `owner` grant is a cross-join of *every currently-seeded permission at migration-apply time* (`SELECT r.id, p.id FROM roles r CROSS JOIN permissions p WHERE r.scope_type='FAMILY' AND r.code='owner'`), not an explicit, auditable list like every other role gets. This means `owner`'s actual permission set silently grows every time a future migration adds a new FAMILY-scope permission (via its own seed statement) unless that migration also explicitly re-grants it, or shrinks/stays fixed if a later migration doesn't touch it. This is a real, evidence-confirmed implicit-scope-growth risk worth PM awareness, not an invented concern.

## Permission list (current approved baseline)

| Permission code | Description (from seed) | Scope family |
|---|---|---|
| `family.read` | Read the active family context | Group-wide |
| `family.members.read` | Read family memberships | Group-wide |
| `family.members.invite` | Create a membership for an existing account | Group-wide |
| `family.members.manage` | Update membership lifecycle or relationship | Group-wide |
| `family.roles.assign` | Assign or revoke membership roles | Group-wide |
| `family.ownership.manage` | Manage owner assignments and transfer | Group-wide (declared, no current API route found for it — see `MONGLE_TARGET_API_INVENTORY.md`) |
| `family.services.manage` | Manage family service subscriptions | Group-wide |
| `markpoint.own.read` | Read own mapped MarkPoint data | MarkPoint service |
| `markpoint.missions.manage` | Manage MarkPoint missions | MarkPoint service |
| `markpoint.points.adjust` | Adjust MarkPoint points | MarkPoint service |
| `doran.rooms.create` | Create Doran rooms | 와글와글 service |
| `doran.rooms.manage` | Manage own Doran rooms | 와글와글 service |
| `doran.participants.manage` | Manage Doran participants | 와글와글 service |
| `doran.messages.read` | Read Doran messages | 와글와글 service |
| `doran.messages.send` | Send Doran messages | 와글와글 service |

## Wave 1 changes to the seeded registry (implemented, measured)

1. **Added `family.members.provision`** — "Provision an independent Account and
   initial credential for a family member". Granted to the FAMILY-scope `owner`
   and `admin` roles only. It exists separately rather than overloading
   `family.members.invite`, whose `0001` seed description is specifically
   "Create a membership for an *existing* account". Migration `0005`.

2. **Removed `markpoint.missions.manage` and `markpoint.points.adjust` from
   every FAMILY-scope role.** The `0001` seed had granted both to `admin`
   directly and to `owner` via a `CROSS JOIN` over all permissions, so a
   FamilyAdmin automatically held Markpoint *service administration* authority —
   which D4/D5 prohibit ("ServiceAdmin authority exists only where explicitly
   assigned"). Because they hung off FAMILY-scope roles they also bypassed the
   Markpoint `ServiceSubscription` gate, which `effective_permissions()` applies
   only to SERVICE-scope roles. Found by
   `MONGLE-W1-SCOPED-RBAC-001`'s own separation test. Migration `0006`.

   Current impact was verified to be nil rather than assumed: no product code
   references either permission code today — every `/api/missions/*`,
   `/api/daily-points/*` etc. route still authorizes through the legacy
   `require_admin`/`get_current_player` dependencies. The defect would have
   become a live privilege escalation at the Wave 4/5 Markpoint authorization
   TRANSFORM. Markpoint administration remains reachable only through the
   SERVICE-scope `markpoint` roles (`mission_manager`, `point_admin`) that
   `0001` already seeds and that `assign_role()` gates behind an active
   subscription.

   **Left in place, flagged for Wave 4:** `markpoint.own.read` is still granted
   to the FAMILY `member`/`restricted_member` roles. That is self-read rather
   than service administration, and whether a family role should carry it at all
   is a D5-B "default access" question this Wave does not decide.

## What is genuinely undecided (per PM instruction, not invented here)

- Whether any *new* Role/Permission is needed once MarkPoint is actually re-hosted on Membership (today's `markpoint.own.read` etc. exist as permission codes but are not enforced by any current MarkPoint route — every `/api/missions/*` etc. route checks legacy `PLAYER_ONLY`/`ADMIN_ONLY`, never a Group Role/Permission at all; see `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`).
- Whether `family.ownership.manage` needs a real API route (none found today — `PM_DECISION_REQUIRED`, or `UNDECIDED` pending confirmation this permission is still wanted).
- Any user-facing display name/label for these roles in Korean UI copy beyond the seed migration's own `name` column (e.g. whether "Owner"/"Admin"/"Member"/"Restricted member" are the actual product-facing labels, or placeholders) — not decided here, flagged `PM_DECISION_REQUIRED` if product copy is needed.
