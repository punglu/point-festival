# MONGLE_CURRENT_TABLE_DICTIONARY

> **AXIS: LEGACY_CURRENT_STATE (A).** This is the factual current-schema
> record (34 relations, live-verified), not the target schema. The
> `canonical_proposed_name`/`rename_classification` columns below only ever
> proposed renames *within* the legacy structure and must not be read as
> Mongle's target table design. See `MONGLE_TARGET_TABLE_DICTIONARY.md` for
> the target schema and `MONGLE_LEGACY_TO_TARGET_MAPPING.md` for each
> legacy table's disposition.

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001

Evidence method: every row below was cross-checked against (1) the ORM model source, (2) the Alembic migration or `database/init.sql` that creates it, and (3) a live introspection of an isolated PostgreSQL 16.9 instance created by stamping `0000_legacy_schema_baseline` onto a freshly-applied `database/init.sql`, then running `alembic upgrade head` to `0004_doran_reliable_slice` — `\dt` on that instance returned exactly 34 relations (33 application tables + `alembic_version`), matching this dictionary's row count exactly.

## Legacy tables (created by `database/init.sql`, no Alembic revision owns them)

| domain | logical_name_ko | current_physical_name | canonical_proposed_name | purpose | primary_key | parent_or_owner | lifecycle | soft_delete | status column | rename_classification | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| player | 플레이어 | `players` | `players` (no change proposed) | Child/player roster; also structurally allows `role='admin'` but that path is unused in practice | `id` | none (root) | active | yes | none (uses `is_locked`/`is_dashboard_visible` instead) | KEEP | `database/init.sql:5-19`, `backend/app/domains/player/models.py` |
| auth | 플레이어 인증 | `player_auth` | `player_auth` | PIN hash + login-attempt/lock state, 1:1 with `players` | `id` | `players` (1:1 via unique `player_id`) | active | yes | none | KEEP | `database/init.sql:22-32` |
| auth | 관리자 인증 | `admin_auth` | `admin_auth` | Username/password admin identity, optionally linked to a `players` row for display purposes | `id` | optionally `players` | active | yes | none | KEEP | `database/init.sql:205-214` |
| mission | 미션 | `missions` | `missions` | One dated, point-bearing task instance | `id` | `players`; optionally `mission_templates` | active | yes | `status` (CHECK: active/completed/failed/pending_approval/proposed/rejected — note: model+init.sql do not list `cancelled` in the CHECK constraint despite `ROLE_TRANSITIONS` in code allowing a `completed -> cancelled` transition, see Gap Report) | KEEP | `database/init.sql:35-57`, `backend/app/domains/mission/models.py` |
| mission_template | 반복 미션 템플릿 | `mission_templates` | `mission_templates` | Recurring mission generator definition | `id` | `players` | active | yes | `is_active` (boolean, not a string status) | KEEP | `database/init.sql:60-75` |
| level_tier | 레벨 구간 | `level_tiers` | `level_tiers` | Point-threshold-to-title rank ladder, keyed by `job_code` for future job branching | `id` | none (global config-like table, not owned per-player) | active | no (physical delete only — explicit design choice, see `level_tier/service.py:63-74` docstring) | none | KEEP | `database/init.sql:84-96` |
| cheer | 응원 메시지 | `cheer_messages` | `cheer_messages` | One parent's daily cheer/encouragement message | `id` | none (keyed by `date`, not a player FK — a single shared message per day, not per-player) | active | yes | none | KEEP | `database/init.sql:99-108` |
| feedback | 피드백 | `feedbacks` | `feedbacks` | Player-submitted feedback entry | `id` | `players` | active | yes | none | KEEP | `database/init.sql:111-120` |
| feedback | 피드백 답변 | `feedback_replies` | `feedback_replies` | Admin reply to a Feedback | `id` | `feedbacks` | active | yes (no `updated_at`) | none | KEEP | `database/init.sql:123-130` |
| chat | (레거시) 1:1 채팅 메시지 | `chat_messages` | `chat_messages` | Direct sender/receiver message, pre-Doran | `id` | `players` (both `sender_id`/`receiver_id`) | active, superseded in intent by Doran but still the only live 1:1 UI path | yes (no `updated_at`) | none (`is_read` boolean instead) | KEEP | `database/init.sql:133-143` |
| deduction | 포인트 차감 | `deductions` | `deductions` | Manual point deduction record | `id` | `players` | active | yes | none | KEEP | `database/init.sql:146-156` |
| daily_point | 일별 포인트 | `daily_points` | `daily_points` | Per-player-per-day earned/spent/balance ledger row; `SUM(balance)` is the authoritative current point total | `id` | `players` | active | yes | none | KEEP | `database/init.sql:159-170` |
| notification | 알림 | `notifications` | `notifications` | In-app notification feed entry | `id` | optionally `players` (`ON DELETE SET NULL`) | active | yes (no `updated_at`) | none (`is_read` boolean) | KEEP | `database/init.sql:173-182` |
| config | 앱 설정 | `app_configs` | `app_configs` | Generic key-value app setting | `id` | none | active | no | none | KEEP | `database/init.sql:185-191` |
| login_log | 로그인 로그 | `login_logs` | `login_logs` | Login attempt audit row | `id` | `players` | active | no (no `updated_at`/`deleted_at` — audit log, append-only by nature) | none (`success` boolean) | KEEP | `database/init.sql:194-201` |

## Foundation tables (created by `0001_account_family_rbac_foundation.py`, revision id `0001_account_family_rbac`)

| domain | logical_name_ko | current_physical_name | canonical_proposed_name | purpose | primary_key | parent_or_owner | lifecycle | soft_delete | status column | rename_classification | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| family | 계정 | `accounts` | `accounts` | Foundation-layer human identity, independent of legacy system | `id` | none (root) | active | yes | `status` (active/suspended/deleted) | KEEP | migration `0001...`:20-28, `family/models.py:6-11` |
| family | 가족 | `family_groups` | `family_groups` | Tenant/household boundary | `id` | none (root) | active | yes | `status` (active/suspended/closed) | KEEP | migration `0001...`:29-37 |
| family | 가족 구성원 | `family_memberships` | `family_memberships` | Account's membership in one FamilyGroup | `id` | `accounts` + `family_groups` | active | yes | `status` (invited/active/suspended/left/removed) | KEEP | migration `0001...`:38-52 |
| family | 역할 | `roles` | `roles` | Named permission bundle, FAMILY- or SERVICE-scoped | `id` | none (registry table, seeded by migration) | active | no | no `status`; uses `is_active`/`is_system` booleans instead | KEEP | migration `0001...`:53-67 |
| family | 권한 | `permissions` | `permissions` | Individual permission code + description | `id` | none (registry) | active | no | none | KEEP | migration `0001...`:69-75 |
| family | 역할-권한 매핑 | `role_permissions` | `role_permissions` | Pure many-to-many join, composite PK, no surrogate id | `(role_id, permission_id)` | `roles` + `permissions` | active | no | none | KEEP | migration `0001...`:76-80 |
| family | 구성원-역할 부여 | `membership_role_assignments` | `membership_role_assignments` | One Membership's grant of one Role, revocable (not deletable) | `id` | `family_memberships` + `roles` | active | no `deleted_at`; uses `revoked_at` instead (append-only history of grants, not a mutable current-state row) | `revoked_at` (nullable timestamp doubles as a status) | KEEP | migration `0001...`:81-90 |
| family | 서비스 구독 | `service_subscriptions` | `service_subscriptions` | A Family's enablement of a named service | `id` | `family_groups` | active | no | `status` (active/suspended/cancelled) | KEEP | migration `0001...`:91-102 |
| family | 레거시 신원 매핑 | `legacy_identity_mappings` | `legacy_identity_mappings` | Bridge from legacy `player_auth`/`admin_auth` identity to a Foundation Account, gated by explicit review | `id` | optionally `accounts` (nullable until review links it) | active | no | `mapping_status` (candidate/reviewed/linked/rejected/ambiguous) | KEEP | migration `0001...`:103-116 |

## Doran messaging tables (`0002_doran_messaging_foundation.py`, `0003_doran_service_binding.py`, `0004_doran_reliable_slice.py` — `0004`'s revision id is `0004_doran_reliable_slice`, filename says `_service_slice`, a minor filename/revision-id mismatch noted here as evidence, not corrected)

| domain | logical_name_ko | current_physical_name | canonical_proposed_name | purpose | primary_key | parent_or_owner | lifecycle | soft_delete | status column | rename_classification | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| doran | 방 | `doran_rooms` | `doran_rooms` | Conversation container: DIRECT/GROUP/SERVICE | `id` (UUID) | `family_groups` | active | yes | `status` (active/read_only/closed/deleted — note the *table itself* also has a `deleted_at` soft-delete column in addition to a `status='deleted'` string value; two ways to represent "gone", see Gap Report) | KEEP, flag the dual delete-representation for future cleanup | migration `0002...`:15-26 |
| doran | DIRECT 방 고유쌍 | `doran_direct_pairs` | `doran_direct_pairs` | Enforces exactly one active DIRECT room per unordered Membership pair per Family | `room_id` | `doran_rooms`, `family_memberships` (both low/high) | active | no (`is_active` boolean instead) | `is_active` | KEEP | migration `0002...`:27-29 |
| doran | 방 참여자 | `doran_participants` | `doran_participants` | A Membership's join/participation record in one Room | `id` (UUID) | `doran_rooms`, `family_memberships` | active | no (uses `status`+`left_at`/`removed_at` instead of `deleted_at`) | `status` (active/left/removed) | KEEP | migration `0002...`:30-33 |
| doran | 메시지 | `doran_messages` | `doran_messages` | One Room message (TEXT/SYSTEM/SERVICE_ACTION) | `id` (UUID) | `doran_rooms`; optionally `doran_participants` (sender) or `service_principals` (service actor) | active | yes (tombstone pattern: row retained, `deleted_at`+`deleted_by_account_id` set, response still returned with `deleted: true`) | `message_type` (not a lifecycle status; TEXT/SYSTEM/SERVICE_ACTION classify the message's *kind*, not its state) | KEEP | migration `0002...`:34-36, `0003...`:45-54 (adds `service_principal_id`/`source`/`source_event_id` columns) |
| doran | 참여자 읽음 상태 | `doran_participant_read_states` | `doran_participant_read_states` | One watermark row per Participant | `participant_id` | `doran_participants` (1:1) | active | no | none | KEEP | migration `0002...`:37 |
| doran | 첨부 서비스 신원 | `service_principals` | `service_principals` | Non-human, credentialed actor identity | `id` | none (root) | active | no (`revoked_at`+`status='revoked'`) | `status` (active/revoked) | KEEP | migration `0003...`:15-27 |
| doran | 서비스-방 결합 | `doran_service_bindings` | `doran_service_bindings` | Sole (principal, family) publish-authority record; also enforced by a DB trigger (`fn_doran_service_binding_room_guard`) that the bound room is actually `room_type='SERVICE'` in the same family | `id` | `service_principals`, `family_groups`; FK-pair to `doran_rooms` | active | no | `status` (active/inactive) | KEEP | migration `0003...`:29-43, `0004...`:39-79 (trigger + `uq_doran_service_binding_principal_family` unique constraint) |
| doran | 서비스 감사 로그 | `doran_service_audit_log` | `doran_service_audit_log` | Append-only audit trail of every service-ingress attempt (allowed or denied); `family_group_id`/`room_id` deliberately **not** FKs so a denied attempt against a nonexistent Family/Room can still be recorded | `id` (bigint) | none (audit log; loosely references `service_principals`) | active | no (append-only, never mutated) | `result_code` (free string, not CHECK-constrained; `event_type` is the CHECK-constrained classifier) | KEEP | migration `0003...`:63-78 |
| service_outbox | 아웃박스 이벤트 | `service_outbox_events` | `service_outbox_events` | Generic transactional outbox row, one per business event awaiting delivery | `id` (bigint) | none (owner-agnostic; `owner_service` is a free string, not an FK) | active | no | `status` (PENDING/PROCESSING/PUBLISHED/DEAD) | KEEP | migration `0004...`:14-35 |

## Table naming-family alignment check (§6.2 of the task prompt)

Sorting all 33 table names alphabetically groups every real family correctly with zero manual intervention needed: `accounts`, `admin_auth`, `app_configs`, `cheer_messages`, `chat_messages`, `daily_points`, `deductions`, `doran_direct_pairs`, `doran_messages`, `doran_participant_read_states`, `doran_participants`, `doran_rooms`, `doran_service_audit_log`, `doran_service_bindings`, `family_groups`, `family_memberships`, `feedback_replies`, `feedbacks`, `legacy_identity_mappings`, `level_tiers`, `login_logs`, `membership_role_assignments`, `mission_templates`, `missions`, `notifications`, `permissions`, `player_auth`, `players`, `role_permissions`, `roles`, `service_outbox_events`, `service_principals`, `service_subscriptions`. All seven `doran_*` tables sort contiguously; both `family_*` tables sort contiguously; `feedback`/`feedbacks` sort contiguously; the three `service_*` tables (`service_outbox_events`, `service_principals`, `service_subscriptions`) sort contiguously. No `RENAME_CANDIDATE`, `MERGE_CANDIDATE`, or `SPLIT_CANDIDATE` was found — every table already carries a real, single-Aggregate, correctly-prefixed name. This is a materially different (better) result than a green-field naming audit would expect to find, and is recorded as a genuine, evidence-based finding, not an assumption.

## UNKNOWN / not classified

None. All 33 application tables were read directly from ORM source, cross-checked against their creating migration or `init.sql`, and confirmed present in a live `\dt` introspection. No table's purpose, ownership, or lifecycle required inference from a name alone.
