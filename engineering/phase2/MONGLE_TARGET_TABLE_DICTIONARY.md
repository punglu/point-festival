# MONGLE_TARGET_TABLE_DICTIONARY

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

Every table below is classified `KEEP_AS_IS` (already target-shaped, evidence-confirmed), `TRANSFORM` (exists, needs an ownership/FK change to fit the target identity model), or `UNDECIDED` (does not exist yet, blocked on a PM_DECISION_REQUIRED item from `MONGLE_TARGET_BUSINESS_GLOSSARY.md`). No `REPLACE`/`DELETE_CANDIDATE` table designs are invented here without PM naming/scope approval — where a new table would be needed, its columns are only sketched provisionally for discussion, not finalized.

## Platform layer (Mongle) — all KEEP_AS_IS

| Target table | Classification | Reasoning | Evidence |
|---|---|---|---|
| `accounts` | KEEP_AS_IS | Already Account-shaped, Group-independent identity | `family/models.py:6-11` |
| `family_groups` | KEEP_AS_IS, pending PM_DECISION_REQUIRED #1 (Business Glossary) on whether "Group" stays Family-specific | Already Group-shaped; a rename to a generic `groups` table is a live open question, not assumed here | `family/models.py:14-19` |
| `family_memberships` | KEEP_AS_IS (same caveat) | | `family/models.py:22-35` |
| `roles` | KEEP_AS_IS | | `family/models.py:38-51` |
| `permissions` | KEEP_AS_IS | | `family/models.py:54-58` |
| `role_permissions` | KEEP_AS_IS | | `family/models.py:62-65` |
| `membership_role_assignments` | KEEP_AS_IS | | `family/models.py:68-75` |
| `service_subscriptions` | KEEP_AS_IS | | `family/models.py:78-89` |
| `legacy_identity_mappings` | KEEP_AS_IS as a **migration-era bridge only** — not a permanent Auth mechanism; its lifecycle ends once legacy data migration/cutover completes (see Migration/Cutover Gap Report) | | `family/models.py:92-106` |
| `service_outbox_events` | KEEP_AS_IS | Owner-agnostic, already platform-shaped | `service_outbox/models.py` |
| **`sessions` (or equivalent)** | **UNDECIDED** | Does not exist. Blocked on PM_DECISION_REQUIRED #2 (Auth/Session model). A provisional sketch, not a proposal: `id, account_id FK, issued_at, expires_at, revoked_at, device_label?` — not finalized | none |
| **Account credential table** (name/shape depends on PM_DECISION_REQUIRED #2's option a/b/c) | **UNDECIDED** | If option (a): could extend/generalize `admin_auth`'s shape (`username`/`password_hash`) onto `accounts` directly or a new `account_credentials` table. If option (b): would need `email`/`phone` + password columns, or no local table at all if a pure external IdP is chosen. Not decided here | none |

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

Every table below currently owns its rows via `player_id -> players.id` (a legacy identity). The recommended target ownership FK is `family_membership_id -> family_memberships.id`, for one specific, evidence-based reason: this is exactly the pattern the already-approved Doran domain uses for its own Group-scoped ownership (`doran_participants.family_membership_id`, `doran_messages` via participant), so adopting the same pattern for MarkPoint keeps one consistent ownership model across both Services on the Mongle platform, rather than inventing a second, different convention. This is a recommendation, not a PM-confirmed decision — flagged as `PM_DECISION_REQUIRED` at the top of `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`.

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

`players`, `player_auth`, `admin_auth`, `login_logs`, `chat_messages`: not reproduced here since their target-axis classification (REFERENCE_ONLY / MIGRATE_DATA / DEPRECATE_CANDIDATE, per-table) is the specific subject of the Legacy-to-Target Mapping document, not this one.
