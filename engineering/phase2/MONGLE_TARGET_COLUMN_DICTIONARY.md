# MONGLE_TARGET_COLUMN_DICTIONARY

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

For every table classified `KEEP_AS_IS` in `MONGLE_TARGET_TABLE_DICTIONARY.md` (all platform-layer and 와글와글-layer tables), the full column-level definition already exists in `MONGLE_CURRENT_COLUMN_DICTIONARY.md` and is not repeated here — those columns do not change under the target architecture. This document covers only the columns that actually change (the `TRANSFORM`ed MarkPoint tables) and provisional sketches for `UNDECIDED` new tables.

## TRANSFORM deltas — MarkPoint-on-Mongle ownership column

Each row below replaces exactly one column; every other column of the named table is unchanged from `MONGLE_CURRENT_COLUMN_DICTIONARY.md`.

| Table | Removed column | Added column | data_type | nullable | constraint | reference | evidence for the change reasoning |
|---|---|---|---|---|---|---|---|
| `missions` | `player_id` (Integer, FK->`players.id` CASCADE) | `family_membership_id` | Integer | no | FK RESTRICT (matches Doran's own ondelete convention for Membership references, not CASCADE — a Membership going away should not silently mass-delete a mission history) | `family_memberships.id` | `MONGLE_TARGET_TABLE_DICTIONARY.md` |
| `mission_templates` | `player_id` | `family_membership_id` | Integer | no | FK RESTRICT | `family_memberships.id` | same |
| `daily_points` | `player_id` | `family_membership_id` | Integer | no | FK RESTRICT; UNIQUE with `date` (unchanged shape, new referent) | `family_memberships.id` | same |
| `deductions` | `player_id` | `family_membership_id` | Integer | no | FK RESTRICT | `family_memberships.id` | same |
| `feedbacks` | `player_id` | `family_membership_id` | Integer | no | FK RESTRICT | `family_memberships.id` | same |
| `notifications` | `player_id` (nullable, FK->`players.id` SET NULL) | `family_membership_id` | Integer | yes | FK SET NULL (unchanged nullability semantics) | `family_memberships.id` | same |
| `cheer_messages` | (no column existed) | `family_group_id` | Integer | no (new column, would need a backfill default at migration time given today's implicit single-tenant assumption) | FK RESTRICT | `family_groups.id` | see Table Dictionary reasoning — today's schema cannot express "which Group" a cheer belongs to |

**Not changed by this transform**: `missions.sender`/`proposed_by` (free strings, e.g. "아빠"/"엄마" — these remain free-text labels under the target model too; whether they should become a real reference to the *other* Membership in the Group, e.g. "who sent this," is a separate, `UNDECIDED` product question this task does not resolve), every mission-lifecycle column (`date`,`text`,`point`,`status`,`msg`,`sort_order`,`group_id`,`template_id`), every `level_tiers` column (table itself is `KEEP_AS_IS`, see Table Dictionary), `feedback_replies`'s columns (scoped transitively, unchanged).

## `level_tiers` leveling input, post-transform

Today `level_tier/service.py::calculate_level` reads `players.total_earned` directly. Once mission ownership moves to `family_membership_id`, the natural target home for a "lifetime earned points" counter is on `family_memberships` (a per-Membership running total), not on the legacy `players` table. This is a **new column on an existing target table**, not a new table:

| Table | New column | data_type | nullable | default | evidence for reasoning |
|---|---|---|---|---|---|
| `family_memberships` | `total_earned` (name matches the legacy column being superseded, for continuity) | Integer | no | 0 | Mirrors `players.total_earned`'s exact current role (`mission/service.py::_sync_total_earned`), just re-homed to the Membership that a target-shaped `missions` row would actually reference |

`daily_points`'s own `balance` column (the authoritative *current spendable* total, distinct from lifetime `total_earned` — see Naming Contract G3) needs the same re-homing treatment implicitly, since it's already being moved to `family_membership_id` ownership above; no separate new column is needed for it beyond the FK change already listed.

## IMPLEMENTED (Wave 1) — Account-native credential and Session

The historical sketches that previously occupied this section were
`VALID_HISTORICAL_REFERENCE` and are superseded by the shipped schema below.
They were missing three things the approved D3 contract requires — refresh
mechanics, a per-device identity for device unlink, and a revocation reason —
which is why Wave 1 designed the real schema rather than adopting them.

Source of truth: `backend/app/domains/family/models.py`, migration
`0005_account_credential_session`, plus `0006_family_service_separation` for the
RBAC seed correction. Every parameter (hashing cost, lockout threshold, lock
duration, token TTLs, initial-password length) lives in `backend/app/config.py`
as a single SSOT and is not duplicated as a literal in domain code.

### `account_credentials` (D2)

| column | data_type | nullable | notes |
|---|---|---|---|
| `id` | Integer | no | PK |
| `account_id` | Integer | no | FK -> `accounts.id` RESTRICT. Partial UNIQUE on `deleted_at IS NULL` — one live credential per Account |
| `username` | String(150) | no | Normalized lower/trimmed at write and lookup so `Alice` and `alice` cannot become two accounts. Partial UNIQUE on `deleted_at IS NULL`, so a revoked username stays reserved rather than becoming re-registrable |
| `password_hash` | String(255) | no | bcrypt. No reversible form of the password exists anywhere in the system |
| `status` | String(20) | no | CHECK `active`/`disabled`/`revoked` |
| `is_initial_credential` | Boolean | no | Admin-issued first credential not yet replaced by the member |
| `is_password_change_required` | Boolean | no | Set with the initial credential; cleared on self-service password change |
| `password_changed_at` | Timestamp(tz) | yes | |
| `failed_attempt_count` | Integer | no | CHECK `>= 0`; reset on success |
| `locked_until` | Timestamp(tz) | yes | Deadline, not an event — the documented `*_at` naming exception (Naming Contract §3) |
| `issued_by_account_id` | Integer | yes | FK -> `accounts.id` RESTRICT. Issuer audit for the FamilyAdmin provisioning flow |
| `last_login_at` | Timestamp(tz) | yes | |
| `revoked_at` | Timestamp(tz) | yes | |
| `created_at`/`updated_at` | Timestamp(tz) | no | `TimestampMixin` |
| `deleted_at` | Timestamp(tz) | yes | `SoftDeleteMixin` |

### `account_sessions` (D3)

| column | data_type | nullable | notes |
|---|---|---|---|
| `id` | Integer | no | PK |
| `account_id` | Integer | no | FK -> `accounts.id` RESTRICT. Account-scoped, never scoped to one FamilyGroup |
| `refresh_token_hash` | String(64) | no | SHA-256 hex. Globally UNIQUE across live and revoked rows so a replayed token resolves to its revoked row and is rejected rather than silently missing |
| `device_id` | String(64) | no | Stable client-install id. Indexed with `account_id` for per-device listing and unlink |
| `device_label` | String(100) | yes | Display only |
| `issued_at` | Timestamp(tz) | no | |
| `expires_at` | Timestamp(tz) | no | D3 requires expiry; a persistent Session is not indefinite authentication |
| `last_seen_at` | Timestamp(tz) | yes | |
| `revoked_at` | Timestamp(tz) | yes | |
| `revoked_reason` | String(30) | yes | CHECK `logout`/`refresh_rotation`/`device_unlink`/`credential_reset`/`password_change`/`admin_revoke` |
| `rotated_from_session_id` | Integer | yes | Self-FK SET NULL. Makes a rotation chain auditable, so a replay is traceable and not only denied |
| `created_at`/`updated_at` | Timestamp(tz) | no | `TimestampMixin` |

No soft delete: a Session is revoked, never soft-deleted, matching
`service_principals`' existing `revoked_at` convention.

### ActiveFamilyContext — deliberately not a column anywhere

`ActiveFamilyContext` has **no** database representation and no
`session.active_family_id` column. It is client/tab-local UX state. The family a
request acts on comes from the route path and is authorized on its own merits
every time (D7), so a client-selected "current family" is never an input to an
authorization decision and one tab's switch cannot affect another's. The
`AuthorizedFamilySet` is likewise a query over ACTIVE memberships, not stored
state.
