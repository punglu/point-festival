# MONGLE_TARGET_TABLE_DICTIONARY

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

Frozen against `MONGLE_TARGET_DECISION_FREEZE.md` (D1–D8 `APPROVED`, 2026-08-01).

Every table below is classified `KEEP_AS_IS` (already target-shaped, evidence-confirmed), `TRANSFORM` (exists, needs an ownership/FK change to fit the target identity model), or `NOT_IMPLEMENTED` (approved by contract, no table exists yet). No table design is invented here — where a new table would be needed, its columns are only sketched provisionally, and a sketch is never an approved schema. Physical schema design happens in the owning implementation task.

## Platform layer (Mongle) — all KEEP_AS_IS

| Target table | Classification | Reasoning | Evidence |
|---|---|---|---|
| `accounts` | KEEP_AS_IS | Already Account-shaped, Group-independent identity | `family/models.py:6-11` |
| `family_groups` | KEEP_AS_IS | **D1 approved:** the Family-specific physical name is retained. A rename to a generic `groups` table is rejected, not open | `family/models.py:14-19` |
| `family_memberships` | KEEP_AS_IS | **D1 approved**, same as above. One Account may hold multiple rows here | `family/models.py:22-35` |
| `roles` | KEEP_AS_IS | | `family/models.py:38-51` |
| `permissions` | KEEP_AS_IS | | `family/models.py:54-58` |
| `role_permissions` | KEEP_AS_IS | | `family/models.py:62-65` |
| `membership_role_assignments` | KEEP_AS_IS | | `family/models.py:68-75` |
| `service_subscriptions` | KEEP_AS_IS | | `family/models.py:78-89` |
| `legacy_identity_mappings` | `CURRENT_STATE_EVIDENCE_NOT_TARGET_CONTRACT` | The table exists in code today. Under **D8 RESET** it is not a Target Auth mechanism, not a required cutover bridge, and not a prerequisite for creating new Accounts. Its retirement follows the PM-gated Legacy retirement sequence, not a data-migration completion | `family/models.py:92-106` |
| `service_outbox_events` | KEEP_AS_IS | Owner-agnostic, already platform-shaped. **D6** requires its write to share a Transaction boundary with message persistence — verify before accepting reuse | `service_outbox/models.py` |
| `account_sessions` | **IMPLEMENTED (Wave 1)** | **D3.** Account-scoped persistent Session; the `AuthorizedFamilySet` is derived per request from ACTIVE memberships rather than stored on the row, so ending one membership never invalidates the Session. Refresh tokens are stored only as SHA-256 hashes; rotation revokes the presented row and issues a new one, so replaying a rotated token is rejected. `device_id` is a plain column, not a separate Device aggregate — device unlink is a bulk revoke over `(account_id, device_id)`, which keeps a future `account_devices` table (Wagle PIN, Push subscriptions) possible without reshaping this one | `family/models.py` (`AccountSession`), migration `0005` |
| `account_credentials` | **IMPLEMENTED (Wave 1)** | **D2.** `아이디 + 플랫폼 비밀번호`; email/phone are absent by design, not merely optional. One live credential per Account and one live username globally, both via partial unique indexes on `deleted_at IS NULL` so a revoked username cannot be re-registered by someone else. Carries credential status, initial-credential/`is_password_change_required` state, failed-attempt count with `locked_until`, `issued_by_account_id` for issuer audit, and `password_changed_at`. No legacy credential row is read or converted (D8 RESET) | `family/models.py` (`AccountCredential`), migration `0005` |
| **Wagle PIN store** — see below | **NOT_IMPLEMENTED** | Unchanged; Wave 3. The Wave 1 Session contract deliberately keeps `device_id` as a first-class column so an `Account + Device` PIN can attach later | none |
| **Wagle PIN store** | **NOT_IMPLEMENTED** | **D3-PIN-SCOPE approved** an optional `Account + Device` local screen lock. Reset-not-recovery, never readable by FamilyAdmin, no shared/per-family PIN. Whether any of it is server-side at all is Wave 3 design | none |
| **Push subscription store** | **NOT_IMPLEMENTED** | **D6 approved** PWA Web Push bound to Account and Device/PWA installation, revoked on logout, Account suspension, Session revoke, device unlink or Account switch | none |

## Realtime messaging layer (와글와글) — all KEEP_AS_IS

| Target table | Classification | Evidence |
|---|---|---|
| `doran_rooms` | KEEP_AS_IS | `doran/models.py:11-28` |
| `doran_direct_pairs` | KEEP_AS_IS | `doran/models.py:31-43` |
| `doran_participants` | KEEP_AS_IS | `doran/models.py:46-65` |
| `doran_messages` | KEEP_AS_IS | `doran/models.py:86-121` |
| `doran_participant_read_states` | KEEP_AS_IS | `doran/models.py:124-129` |
| `service_principals` | KEEP_AS_IS | `doran/models.py:132-146` |
| `doran_service_bindings` | KEEP_AS_IS | `doran/models.py:149-165` |
| `doran_service_audit_log` | KEEP_AS_IS | `doran/models.py:168-188` |

No renaming (e.g. a `doran_*` -> `wagle_*` physical rename to match the Korean product name) is proposed here — the current prefix is an internal codename, not user-facing, and this task treats a purely cosmetic internal rename as out of scope unless PM explicitly wants it (flagged, not assumed).

## MarkPoint-on-Mongle layer — TRANSFORM (ownership FK change), business logic REUSE_LOGIC_ONLY

Every table below currently owns its rows via `player_id -> players.id` (a legacy identity). **D5-B approves** `FamilyMembership` as Markpoint's human identity and `FamilyGroup` as owner, which matches the pattern the Doran domain already uses (`doran_participants.family_membership_id`, `doran_messages` via participant) and keeps one consistent ownership model across the platform.

**This is not an instruction to rewrite legacy rows.** Under **D8 RESET** the Target ownership shape applies to **newly created** Markpoint records only. No `player_id` value is converted to `family_membership_id`, and no legacy mission, point, ledger, level or reward row is imported or backfilled. The legacy tables below are `ARCHIVE_ONLY` reference; whether the Target reuses these table names or creates new ones is Wave 5 physical design.

| Current table | Target table (name unchanged unless noted) | Classification | Current FK | Proposed target FK | Reasoning |
|---|---|---|---|---|---|
| `missions` | `missions` | TRANSFORM | `player_id` | `family_membership_id` | Mirrors Doran's ownership pattern; a mission is a Membership-scoped concept (one child's task within one Family) |
| `mission_templates` | `mission_templates` | TRANSFORM | `player_id` | `family_membership_id` | same |
| `level_tiers` | `level_tiers` | KEEP_AS_IS (structurally) | none (global config table, not player-owned) | none | This table is not player-scoped at all today (keyed by `job_code`, not `player_id`) — no transform needed regardless of identity model |
| `daily_points` | `daily_points` | TRANSFORM | `player_id` | `family_membership_id` | same reasoning |
| `deductions` | `deductions` | TRANSFORM | `player_id` | `family_membership_id` | same |
| `cheer_messages` | `cheer_messages` | TRANSFORM (scope clarification, not an FK add) | none (date-keyed only) | `family_group_id` (a cheer message is a whole-Group broadcast, not a Membership-owned row — currently has no scope column at all, meaning in a **multi-Group** target world, today's schema cannot tell which Group a cheer message belongs to) | Currently only works because there is exactly one implicit "family" in the legacy single-tenant system; a real multi-Group Mongle needs this scoped |
| `feedbacks` | `feedbacks` | TRANSFORM | `player_id` | `family_membership_id` | same reasoning as missions |
| `feedback_replies` | `feedback_replies` | KEEP_AS_IS | `feedback_id` (already scoped via parent) | none | Already scoped transitively through `feedbacks` |
| `notifications` | `notifications` | TRANSFORM | `player_id` (nullable) | `family_membership_id` (nullable) | same reasoning |

**Explicitly not proposed as part of this transform**: renaming any of these tables' physical names, or merging them into fewer/different tables. The transform is scoped strictly to "which identity owns this row," per PM's own instruction not to conflate a Gap/legacy-difference finding with an invented redesign beyond what's needed.

## Legacy identity tables — see `MONGLE_LEGACY_TO_TARGET_MAPPING.md` for full classification

`players`, `player_auth`, `admin_auth`, `login_logs`, `chat_messages`: not reproduced here since their target-axis classification is the subject of the Legacy-to-Target Mapping document. Under **D8 RESET** their current disposition is `ARCHIVE_ONLY` / `REFERENCE_ONLY` / `DEPRECATE` — the historical `MIGRATE_DATA` label is no longer a current Target action.
