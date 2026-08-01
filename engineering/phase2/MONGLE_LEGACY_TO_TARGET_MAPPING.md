# MONGLE_LEGACY_TO_TARGET_MAPPING

> **D8 RESET override:** no Legacy operational data is migrated, transformed, backfilled, or used as Target fallback. Legacy records are `ARCHIVE_ONLY`/reference until separately PM-approved retirement. The historical classifications below remain source-inventory context only, not Target migration instructions.

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis A -> Axis B)

For D8 current Target disposition, Legacy operational records are `ARCHIVE_ONLY`; `REFERENCE_ONLY` and `REUSE_LOGIC_ONLY` describe source/reference value only. Historical `MIGRATE_DATA`/`TRANSFORM` labels are no longer current Target actions.

## Legacy tables

| Table | Classification | Reasoning | Evidence |
|---|---|---|---|
| `players` | `ARCHIVE_ONLY` (data) + `REFERENCE_ONLY` (identity model) | D8 prohibits Account/Membership conversion; retained only for Legacy reference/audit | `player/models.py` |
| `player_auth` | `DEPRECATE` (once a Mongle-native Auth exists) | PIN-based auth is a legacy convenience mechanism, not designed for Account/Session; may survive short-term as a *bridge* only via `LegacyIdentityMapping`, not as MarkPoint's or Mongle's target credential | `auth/models.py:6-21` |
| `admin_auth` | `DEPRECATE` (superseded by the approved D2 Account credential) — its **pattern** (`username`/`password_hash`) is `REUSE_LOGIC_ONLY` reference for the D2-approved `아이디 + 플랫폼 비밀번호` shape. Reusing the *shape* is not reusing the *rows*: no legacy credential is converted (D8) | | `auth/models.py:24-34` |
| `missions` | `ARCHIVE_ONLY` | D8 prohibits Target import; new Markpoint begins with new records | `mission/models.py` |
| `mission_templates` | `ARCHIVE_ONLY` | no Target import under D8 RESET | `mission_template/models.py` |
| `level_tiers` | `REFERENCE_ONLY` | Existing rules may inform a new implementation; rows are not imported | `level_tier/models.py` |
| `cheer_messages` | `ARCHIVE_ONLY` | no Target message import under D8 RESET | `cheer/models.py` |
| `feedbacks` | `ARCHIVE_ONLY` | no Target import under D8 RESET | `feedback/models.py` |
| `feedback_replies` | `ARCHIVE_ONLY` | retained only with Legacy feedback history | `feedback/models.py:15-23` |
| `chat_messages` | `DEPRECATE` | Superseded by 와글와글/Doran's DIRECT room type, which the Doran model's own docstring explicitly declines to build on top of this table ("deliberately do not reuse legacy chat_messages") | `chat/models.py:1-4` |
| `deductions` | `ARCHIVE_ONLY` | no Target import under D8 RESET | `deduction/models.py` |
| `daily_points` | `ARCHIVE_ONLY` | no Target opening balance or point import | `daily_point/models.py` |
| `notifications` | `ARCHIVE_ONLY` | no Target notification import | `notification/models.py` |
| `app_configs` | `KEEP_AS_IS` (mechanism) + `UNDECIDED` (whether config becomes Group-scoped, e.g. per-Group `point_cycle`) | Generic key-value mechanism is identity-agnostic already; whether it needs a Group dimension is a product question | `config/models.py` |
| `login_logs` | `REFERENCE_ONLY` | An audit log of legacy PIN attempts; a Session/Auth audit log is the target-axis equivalent, not a direct carry-over of this table | `login_log/models.py` |
| `admin_auth`-referencing `players.role='admin'` path | `DELETE_CANDIDATE` | The CHECK constraint structurally allows `role='admin'` on a `players` row, but no seed data or current code path actually creates one this way (the real admin path is exclusively `admin_auth`) — this is dead schema surface area, not a used pattern, and does not need to survive into the target model at all | `database/init.sql:8-9`, confirmed by seed data (`init.sql:219-224`, all 4 seeded players are `role='player'`) |

## Legacy auth/session mechanism

| Element | Classification | Reasoning |
|---|---|---|
| PIN-based player login flow (A1's profile-select + PIN entry UX) | `REFERENCE_ONLY` (UX pattern) | The *interaction pattern* (pick a face, enter a short PIN) is familiar UX. Under approved D3 the Target equivalent is the **optional `Account + Device` Wagle PIN screen lock**, which is not authentication, not a platform-password substitute, and not a per-family or shared PIN. No legacy PIN value is ever converted into it (D8) |
| Admin username/password login | `REUSE_LOGIC_ONLY` (as a credential-shape candidate) | See `admin_auth` row above |
| JWT shape (`sub`=legacy id, `role`=player/admin) | `REPLACE` | A Mongle-native Session must carry Account/Membership identity, not legacy Player/Admin identity directly |
| `LegacyIdentityMapping` bridge itself | `REFERENCE_ONLY` / `DEPRECATE` for Target | D8 RESET forbids Legacy-to-Account migration; it is not Target Auth or a required cutover bridge |
| Two `get_current_user` functions (naming conflict, see Naming Contract G4) | `REPLACE` (both) | Neither is the target Auth dependency; a new Session-based dependency replaces both once built |

## Legacy routes

| Route family | Classification | Reasoning |
|---|---|---|
| `/api/auth/login`, `/api/auth/admin/login`, `/api/auth/logout` | `REPLACE` (once Mongle Auth exists) | See above |
| `/api/players/*` | `REFERENCE_ONLY` (UX pattern for A1's profile list) + eventual `REPLACE` at the API level | The *need* (a pre-login list of who-can-log-in) is real UX; the specific unauthenticated `GET /api/players` mechanism is legacy-shaped and would be replaced by a Group-membership-aware equivalent once Account/Session exists |
| `/api/missions/*` and the other 7 MarkPoint route families | `REFERENCE_ONLY` / eventual `DEPRECATE` | D8 does not require compatibility; D7 Target routes are newly implemented Family-scoped APIs |
| `/api/admin/*` (31 routes) | `REFERENCE_ONLY` / eventual `DEPRECATE` | Legacy operational surface is not a Target compatibility requirement; controller pattern may be reference only |
| `/api/families/*`, `/api/account-context` | `KEEP_AS_IS` | Already Mongle-native |
| `/api/families/{family_id}/doran/*` | `KEEP_AS_IS` | Already Mongle-native |
| `/api/chat/*` | `DEPRECATE` | See `chat_messages` row above |
| `/api/configs/*`, `/api/login-logs/*` | `KEEP_AS_IS`/`REFERENCE_ONLY` respectively | See table rows above |

## Legacy business rules (not tables/routes — the actual domain logic)

Per `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`: pure point/level/cycle arithmetic is `REUSE_LOGIC_ONLY` candidate material; mission transitions, approvals, ledger/balance, expiry and event bridges require target actor/scope/transaction/idempotency review. None is authorized for a simple Player-to-Membership or Player-to-ServicePrincipal rewrite.

## Summary count

| Current D8 disposition | Count / scope |
|---|---|
| ARCHIVE_ONLY | Legacy identity, auth, family, Markpoint, message and notification records — no Target import |
| REFERENCE_ONLY | legacy UX, routes, schema and audit material retained for reference only |
| REUSE_LOGIC_ONLY | selected identity-independent business-rule ideas, subject to new Target contract verification |
| RETIREMENT_PENDING | Legacy operational system; read-only retention and destructive retirement require PM gate |
