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

## UNDECIDED — provisional sketches only, not proposals

These are offered strictly to make the open PM decision concrete, not as a recommendation to build either shape as-is.

### If PM selects Auth option (a) — generalize `admin_auth`'s credential pattern onto Account

| column | data_type | nullable | notes |
|---|---|---|---|
| `account_id` | Integer | no | FK -> `accounts.id`, UNIQUE (1:1) |
| `username` or `email` | String | no | UNIQUE — exact field TBD by PM |
| `password_hash` | String(255) | no | bcrypt, same convention as legacy `admin_auth.password`/`player_auth.pin_hash` |
| `created_at`/`updated_at` | Timestamp | no | `TimestampMixin` |

### Session table, any Auth option

| column | data_type | nullable | notes |
|---|---|---|---|
| `id` | UUID or Integer | no | PK |
| `account_id` | Integer | no | FK -> `accounts.id` |
| `issued_at` | Timestamp(tz) | no | |
| `expires_at` | Timestamp(tz) | no | |
| `revoked_at` | Timestamp(tz) | yes | explicit revocation, mirroring `service_principals.revoked_at`'s existing convention |

Neither sketch above is final. Both are blocked on `MONGLE_TARGET_BUSINESS_GLOSSARY.md`'s PM_DECISION_REQUIRED #2.
