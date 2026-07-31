# MONGLE_LEGACY_TO_TARGET_MAPPING

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis A -> Axis B)

Every legacy element (table, auth mechanism, role model, route family) is classified into exactly one of: `REFERENCE_ONLY`, `KEEP_AS_IS`, `REUSE_LOGIC_ONLY`, `MIGRATE_DATA`, `TRANSFORM`, `REPLACE`, `DEPRECATE`, `DELETE_CANDIDATE`, `UNDECIDED`. `KEEP_AS_IS` is used only where direct evidence supports it, per PM's instruction.

## Legacy tables

| Table | Classification | Reasoning | Evidence |
|---|---|---|---|
| `players` | `MIGRATE_DATA` (identity records) + `REFERENCE_ONLY` (as an identity *model*) | The rows (names, existing children/parents) represent real people worth carrying into Account/Membership; the *table's own structure* (flat, single-role, no Group concept) is not the target identity model and is not `KEEP_AS_IS` | `player/models.py` |
| `player_auth` | `DEPRECATE` (once a Mongle-native Auth exists) | PIN-based auth is a legacy convenience mechanism, not designed for Account/Session; may survive short-term as a *bridge* only via `LegacyIdentityMapping`, not as MarkPoint's or Mongle's target credential | `auth/models.py:6-21` |
| `admin_auth` | `DEPRECATE` (superseded by Account-native Auth once built) — but its **pattern** (username/password_hash) is `REUSE_LOGIC_ONLY` as a candidate shape for the target Account credential (see PM_DECISION_REQUIRED option (a) in the Business Glossary) | | `auth/models.py:24-34` |
| `missions` | `TRANSFORM` | Ownership FK change only; see MarkPoint-on-Mongle Contract | `mission/models.py` |
| `mission_templates` | `TRANSFORM` | same | `mission_template/models.py` |
| `level_tiers` | `KEEP_AS_IS` | Not player-owned at all today (keyed by `job_code`); no identity-model change needed | `level_tier/models.py` |
| `cheer_messages` | `TRANSFORM` | Needs a `family_group_id` scope column it currently lacks entirely | `cheer/models.py` |
| `feedbacks` | `TRANSFORM` | Ownership FK change | `feedback/models.py` |
| `feedback_replies` | `KEEP_AS_IS` | Already scoped transitively via `feedback_id`, no direct identity FK to change | `feedback/models.py:15-23` |
| `chat_messages` | `DEPRECATE` | Superseded by 와글와글/Doran's DIRECT room type, which the Doran model's own docstring explicitly declines to build on top of this table ("deliberately do not reuse legacy chat_messages") | `chat/models.py:1-4` |
| `deductions` | `TRANSFORM` | Ownership FK change | `deduction/models.py` |
| `daily_points` | `TRANSFORM` | Ownership FK change | `daily_point/models.py` |
| `notifications` | `TRANSFORM` | Ownership FK change (nullable, unchanged nullability) | `notification/models.py` |
| `app_configs` | `KEEP_AS_IS` (mechanism) + `UNDECIDED` (whether config becomes Group-scoped, e.g. per-Group `point_cycle`) | Generic key-value mechanism is identity-agnostic already; whether it needs a Group dimension is a product question | `config/models.py` |
| `login_logs` | `REFERENCE_ONLY` | An audit log of legacy PIN attempts; a Session/Auth audit log is the target-axis equivalent, not a direct carry-over of this table | `login_log/models.py` |
| `admin_auth`-referencing `players.role='admin'` path | `DELETE_CANDIDATE` | The CHECK constraint structurally allows `role='admin'` on a `players` row, but no seed data or current code path actually creates one this way (the real admin path is exclusively `admin_auth`) — this is dead schema surface area, not a used pattern, and does not need to survive into the target model at all | `database/init.sql:8-9`, confirmed by seed data (`init.sql:219-224`, all 4 seeded players are `role='player'`) |

## Legacy auth/session mechanism

| Element | Classification | Reasoning |
|---|---|---|
| PIN-based player login flow (A1's profile-select + PIN entry UX) | `REFERENCE_ONLY` (UX pattern) | The *interaction pattern* (pick a face, enter a short PIN) is valuable, familiar UX worth preserving as a *quick-unlock* layer on top of a real Account Session (see Business Glossary PM_DECISION_REQUIRED #2 option (b)) — but the PIN itself is not proposed as Mongle's Account credential |
| Admin username/password login | `REUSE_LOGIC_ONLY` (as a credential-shape candidate) | See `admin_auth` row above |
| JWT shape (`sub`=legacy id, `role`=player/admin) | `REPLACE` | A Mongle-native Session must carry Account/Membership identity, not legacy Player/Admin identity directly |
| `LegacyIdentityMapping` bridge itself | `KEEP_AS_IS`, scoped as **migration-era infrastructure** | Necessary exactly as long as legacy identities and Mongle Accounts coexist; not a permanent Auth mechanism (see Domain Boundary Map) |
| Two `get_current_user` functions (naming conflict, see Naming Contract G4) | `REPLACE` (both) | Neither is the target Auth dependency; a new Session-based dependency replaces both once built |

## Legacy routes

| Route family | Classification | Reasoning |
|---|---|---|
| `/api/auth/login`, `/api/auth/admin/login`, `/api/auth/logout` | `REPLACE` (once Mongle Auth exists) | See above |
| `/api/players/*` | `REFERENCE_ONLY` (UX pattern for A1's profile list) + eventual `REPLACE` at the API level | The *need* (a pre-login list of who-can-log-in) is real UX; the specific unauthenticated `GET /api/players` mechanism is legacy-shaped and would be replaced by a Group-membership-aware equivalent once Account/Session exists |
| `/api/missions/*` and the other 7 MarkPoint route families | `TRANSFORM` (auth dependency only) | See MarkPoint-on-Mongle Contract |
| `/api/admin/*` (31 routes) | `TRANSFORM` (auth dependency; route delegation structure itself is `KEEP_AS_IS` as a Thin-Controller pattern) | See Target API Inventory |
| `/api/families/*`, `/api/account-context` | `KEEP_AS_IS` | Already Mongle-native |
| `/api/families/{family_id}/doran/*` | `KEEP_AS_IS` | Already Mongle-native |
| `/api/chat/*` | `DEPRECATE` | See `chat_messages` row above |
| `/api/configs/*`, `/api/login-logs/*` | `KEEP_AS_IS`/`REFERENCE_ONLY` respectively | See table rows above |

## Legacy business rules (not tables/routes — the actual domain logic)

Per `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`'s full inventory: mission state machine, point-sync arithmetic, level/tier calculation, cycle-range math, lazy-expiry, and the Outbox-emission bridge are all `REUSE_LOGIC_ONLY` — none require rewriting, only re-pointing at a new ownership FK.

## Summary count

| Classification | Count (tables) |
|---|---|
| KEEP_AS_IS | 3 (`level_tiers`, `feedback_replies`, `app_configs` mechanism) |
| TRANSFORM | 7 (`missions`, `mission_templates`, `daily_points`, `deductions`, `feedbacks`, `notifications`, `cheer_messages`) |
| MIGRATE_DATA | 1 (`players`, as data — see row above for the split reasoning) |
| DEPRECATE | 3 (`player_auth`, `admin_auth`, `chat_messages`) |
| DELETE_CANDIDATE | 1 (the unused `players.role='admin'` path specifically, not the whole `players` table) |
| REFERENCE_ONLY | 1 (`login_logs`) |
| UNDECIDED | (config Group-scoping question — not a table classification of its own) |
