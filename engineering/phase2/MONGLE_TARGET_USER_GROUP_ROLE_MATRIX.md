# MONGLE_TARGET_USER_GROUP_ROLE_MATRIX

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

Per PM instruction, no user-group name, role name, or permission is confirmed here beyond what an already-approved migration seeded (`PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001`). This matrix presents the current approved baseline as-is and flags every place a fresh Mongle-framing decision is genuinely open.

## Group scope

| scope_type | service_code | Meaning | Evidence |
|---|---|---|---|
| `FAMILY` | (none) | A permission that applies across the whole Group, not tied to any one Service | `roles.scope_type` CHECK — `family/models.py:38-51` |
| `SERVICE` | `markpoint` | A permission scoped to the MarkPoint service within one Group | same |
| `SERVICE` | `doran` | A permission scoped to the 와글와글 (Doran) service within one Group | same |

**PM_DECISION_REQUIRED**: is `FAMILY`/`SERVICE` the right pair of scope names for the corrected Mongle framing, or should `FAMILY` be renamed to a more generic `GROUP` scope_type now that Mongle's own vocabulary (per PM's latest message) speaks of "Group," not "Family"? This is a live string value in a CHECK constraint and every row of the `roles` table — a rename here is a real `MIGRATION_REQUIRED`, not a documentation nit. Not decided in this task.

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

## What is genuinely undecided (per PM instruction, not invented here)

- Whether any *new* Role/Permission is needed once MarkPoint is actually re-hosted on Membership (today's `markpoint.own.read` etc. exist as permission codes but are not enforced by any current MarkPoint route — every `/api/missions/*` etc. route checks legacy `PLAYER_ONLY`/`ADMIN_ONLY`, never a Group Role/Permission at all; see `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`).
- Whether `family.ownership.manage` needs a real API route (none found today — `PM_DECISION_REQUIRED`, or `UNDECIDED` pending confirmation this permission is still wanted).
- Any user-facing display name/label for these roles in Korean UI copy beyond the seed migration's own `name` column (e.g. whether "Owner"/"Admin"/"Member"/"Restricted member" are the actual product-facing labels, or placeholders) — not decided here, flagged `PM_DECISION_REQUIRED` if product copy is needed.
