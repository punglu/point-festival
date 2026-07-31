# MONGLE_CURRENT_COLUMN_DICTIONARY

> **AXIS: LEGACY_CURRENT_STATE (A).** Factual current-column record only. See
> `MONGLE_TARGET_COLUMN_DICTIONARY.md` for the target schema.

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001

Evidence: every column below is read directly from its ORM model (`backend/app/domains/<domain>/models.py`) and cross-checked against the live isolated-DB introspection described in `MONGLE_CURRENT_TABLE_DICTIONARY.md`. `sensitive_data` flags anything that must never appear in logs/Drive artifacts per `agent-system/rules.md`. `source_of_truth` marks columns that are themselves derived/computed elsewhere so a reader does not treat them as independently authoritative.

## `players`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | sensitive_data | source_of_truth | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer (SERIAL) | no | autoincrement | PK | — | — | | no | yes | `player/models.py:12` |
| name | 이름 | String(50) | no | — | — | — | — | | no (display name, not legally sensitive but still a minor's name) | yes | `player/models.py:13` |
| role | 역할 | String(10) | no | `'player'` | CHECK IN (player,admin) | — | enum-like (2 values) | | no | yes | `player/models.py:14-19,27-29` |
| photo | 사진 | Text | yes | — | — | — | — | Base64 or data-URI, not a filesystem path | possibly (a child's photo) | yes | `player/models.py:20` |
| status_msg | 상태 메시지 | String(200) | yes | — | — | — | — | | no | yes | `player/models.py:21` |
| last_login | 마지막 로그인 | BigInteger | yes | — | — | — | — | epoch **milliseconds**, not seconds — confirmed by `auth/service.py:65` (`int(time.time() * 1000)`) | no | yes | `player/models.py:22` |
| total_earned | 누적 획득 포인트 | Integer | no | 0 | — | — | — | Lifetime, monotonic (only ever incremented by mission completion, decremented only by an admin revert); leveling input, **not** the current spendable balance | no | yes (but see `daily_points.balance` for the different "current balance" figure) | `player/models.py:23` |
| is_locked | 잠금 여부 | Boolean | no | false | — | — | — | Admin-imposed permanent lock, distinct from `player_auth.lock_until`'s temporary rate-limit lock — both are OR'd together at read time (`player/service.py:58`) | no | yes | `player/models.py:24` |
| is_dashboard_visible | 대시보드 노출 여부 | Boolean | no | true | — | — | — | | no | yes | `player/models.py:25` |
| created_at / updated_at | 생성/수정일 | TimestampMixin | no | now() | — | — | — | | no | yes | `models/base.py` |
| deleted_at | 삭제일 | SoftDeleteMixin | yes | null | — | — | — | | no | yes | `models/base.py` |

## `player_auth`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | sensitive_data | source_of_truth | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | no | yes | |
| player_id | 플레이어 ID | Integer | no | — | UNIQUE, FK CASCADE | `players.id` | | 1:1 with players | no | yes | `auth/models.py:12-17` |
| pin_hash | PIN 해시 | String(128) | no | — | — | — | | bcrypt hash | **yes** — never log/expose | yes | `auth/models.py:18` |
| login_attempts | 로그인 시도 횟수 | Integer | no | 0 | — | — | | resets to 0 on success | no | yes | `auth/models.py:19` |
| lock_until | 잠금 해제 시각 | BigInteger | yes | — | — | — | | epoch **milliseconds** | no | yes | `auth/models.py:20` |
| is_admin | 관리자 여부 | Boolean | no | false | — | — | | present on the model but the live admin path is exclusively via `admin_auth`, not this flag — status: likely vestigial, `UNKNOWN` whether any code path still reads it (not found in grep of routers/services during this task) | no | yes | `auth/models.py:21` |

## `admin_auth`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | sensitive_data | source_of_truth | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | no | yes | |
| username | 아이디 | String(50) | no | UNIQUE | — | — | | | no (a login identifier, low sensitivity) | yes | `auth/models.py:29` |
| password | 비밀번호 해시 | String(255) | no | — | — | — | | bcrypt hash despite the column name "password" (misleading name — it is never plaintext) | **yes** | yes | `auth/models.py:30` |
| display_name | 표시 이름 | String(50) | no | — | — | — | | | no | yes | `auth/models.py:31` |
| player_id | 연결된 플레이어 | Integer | yes | — | FK (no ondelete specified) | `players.id` | | optional display association only | no | yes | `auth/models.py:32` |
| created_at/updated_at | 생성/수정일 | DateTime (naive, `func.now()`) | no | now() | — | — | | **not** `TimestampMixin` — hand-rolled, naive (non-timezone-aware) `DateTime`, inconsistent with every other table's `DateTime(timezone=True)` | no | yes | `auth/models.py:33-34` |
| deleted_at | 삭제일 | SoftDeleteMixin | yes | null | — | — | | | no | yes | |

## `missions`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| player_id | 플레이어 ID | Integer | no | — | FK CASCADE | `players.id` | | | `mission/models.py:9` |
| date | 날짜 | Date | no | — | — | — | | which day's mission this is; drives cycle/weekly aggregation | `mission/models.py:10` |
| text | 내용 | String(500) | no | — | — | — | | | |
| point | 포인트 | Integer | no | 0 | — | — | | awarded on completion | |
| status | 상태 | String(20) | no | `'active'` | CHECK (init.sql): active/completed/failed/pending_approval/proposed/rejected | — | enum (CHECK-constrained, 6 values in DB) | **Gap**: application code (`mission/service.py` `ROLE_TRANSITIONS`) also references a `cancelled` status for admin-only `completed -> cancelled` transitions, but `cancelled` is **absent from the `init.sql` CHECK constraint** — a live write of `status='cancelled'` would violate the DB constraint. Not verified further in this task (would require a live write attempt, out of scope: no product/DB mutation permitted); flagged in Gap Report as `MIGRATION_REQUIRED` or a code-only fix. | `database/init.sql:41-43`, `mission/service.py:146-160` |
| sender | 발신자 | String(20) | yes | — | — | — | | free string, e.g. "아빠"/"엄마" — not an FK to any parent identity table | |
| msg | 메모 | Text | yes | — | — | — | | | |
| proposed_by | 제안자 | String(20) | yes | — | — | — | | free string | |
| proposal_reason | 제안 사유 | Text | yes | — | — | — | | | |
| rejection_reason | 반려 사유 | Text | yes | — | — | — | | | |
| sort_order | 정렬 순서 | Integer | no | 0 | — | — | | | |
| group_id | 그룹 ID | String(36) | yes | — | index (partial, `WHERE group_id IS NOT NULL`) | — | | UUID-shaped free string linking mass-created/mass-deleted sibling missions (e.g. clone-selected, delete-by-group); **not** a real FK to any table | `database/init.sql:50,57` |
| template_id | 템플릿 ID | Integer | yes | — | FK SET NULL | `mission_templates.id` | | | `database/init.sql:77-81` |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `mission_templates`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| player_id | 플레이어 ID | Integer | no | — | FK CASCADE | `players.id` | | | |
| text | 내용 | String(500) | no | — | — | — | | | |
| point | 포인트 | Integer | no | 0 | — | — | | | |
| day_of_week | 요일 비트마스크 | Integer | no | 127 | — | — | bitmask (1=월…64=일, 127=매일) | | `database/init.sql:75` (COMMENT) |
| is_active | 활성 여부 | Boolean | no | true | — | — | | | |
| last_generated_date | 마지막 생성일 | Date | yes | — | — | — | | | |
| group_id | 그룹 ID | String(36) | yes | — | — | — | | same free-string convention as `missions.group_id` | |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `level_tiers`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| job_code | 직업 코드 | String(20) | no | `'COMMON'` | UNIQUE with `level` | — | | forward-looking job-branch key; every seeded row today uses `COMMON` | |
| level | 레벨 | Integer | no | — | UNIQUE with `job_code` | — | | | |
| title | 칭호 | String(100) | no | — | — | — | | Korean rank name, e.g. "새싹 모험가" | |
| required_points | 필요 포인트 | Integer | no | 0 | — | — | | threshold compared against `players.total_earned`, **not** `daily_points.balance` | `level_tier/service.py:197-214` |
| icon_path | 아이콘 경로 | String(300) | yes | — | — | — | | not confirmed wired to any current FE render path in this task's scope | |
| milestone_type | 마일스톤 유형 | String(30) | yes | — | — | — | | `UNKNOWN` — no consumer found in this task's grep of frontend/backend for this field beyond passthrough in schema | |
| milestone_data | 마일스톤 데이터 | JSONB | yes | — | — | — | | same `UNKNOWN` consumer status as `milestone_type` | |
| created_at/updated_at | | Mixins (no `deleted_at` — physical delete only) | | | | | | | `level_tier/service.py:63-74` |

## `cheer_messages`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| date | 날짜 | Date | no | — | index | — | | one row expected per day (not DB-enforced unique, only convention — `upsert_cheer` is PUT-by-date at the router level) | `cheer/router.py` |
| sender | 발신자 | String(20) | no | — | — | — | free string ('dad'/'mom' by convention, not CHECK-enforced) | | |
| message | 메시지 | Text | no | — | — | — | | | |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `feedbacks`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| player_id | 플레이어 ID | Integer | no | — | FK CASCADE | `players.id` | | | |
| date | 날짜 | Date | no | — | — | — | | | |
| msg | 내용 | Text | no | — | — | — | | | |
| recipient | 수신 대상 | String(50) | yes | null | — | — | free string | | |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `feedback_replies`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| feedback_id | 피드백 ID | Integer | no | — | FK CASCADE | `feedbacks.id` | | | |
| sender | 발신자 | String(20) | no | — | — | — | free string | | |
| text | 내용 | Text | no | — | — | — | | | |
| created_at | 생성일 | DateTime(tz) | no | now() | — | — | | no `updated_at` (explicit, per code comment) | `feedback/models.py:16` |
| deleted_at | 삭제일 | SoftDeleteMixin | yes | null | — | — | | | |

## `chat_messages`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| sender_id | 발신자 ID | Integer | no | — | FK CASCADE | `players.id` | | | |
| receiver_id | 수신자 ID | Integer | no | — | FK CASCADE | `players.id` | | | |
| message | 메시지 | Text | no | — | — | — | | | |
| is_read | 읽음 여부 | Boolean | no | false | — | — | | | |
| created_at | 생성일 | DateTime(tz) | no | now() | — | — | | no `updated_at` | |
| deleted_at | 삭제일 | SoftDeleteMixin | yes | null | — | — | | | |

## `deductions`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| player_id | 플레이어 ID | Integer | no | — | FK CASCADE | `players.id` | | | |
| date | 날짜 | Date | no | — | — | — | | | |
| reason | 사유 | String(300) | no | — | — | — | | | |
| amount | 차감량 | Integer | no | — | — | — | | positive integer expected by schema (`Field(gt=0)`) though the DB column itself has no CHECK constraint enforcing positivity | `deduction/schema.py:10` |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `daily_points`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| player_id | 플레이어 ID | Integer | no | — | FK CASCADE | `players.id` | | | |
| date | 날짜 | Date | no | — | UNIQUE with `player_id` | — | | one row per player per day | `database/init.sql:169` |
| earned | 획득 | Integer | no | 0 | — | — | | | |
| spent | 소비 | Integer | no | 0 | — | — | | no code path found in this task writing a nonzero `spent` (no "spend points" feature located in routers/services) — `UNKNOWN` whether this is a planned-but-unbuilt feature or dead column | |
| balance | 잔액 | Integer | no | 0 | — | — | | **This is the authoritative "current point total"** — `SUM(balance)` across all rows is what `PlayerListItem.total_points` returns | `player/service.py:31-38` |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `notifications`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| type | 유형 | String(30) | no | — | — | — | free string (e.g. `approval_request`, `proposal` — seen in `mission/service.py:444-450,498-502`) | not CHECK-constrained; no enum table backs it | |
| player_id | 대상 플레이어 | Integer | yes | — | FK SET NULL | `players.id` | | | |
| title | 제목 | String(200) | no | — | — | — | | | |
| body | 본문 | Text | yes | — | — | — | | | |
| is_read | 읽음 여부 | Boolean | no | false | — | — | | | |
| created_at | 생성일 | TIMESTAMP(tz) | no | now() | — | — | | no `updated_at`/`deleted_at` at all (init.sql comment confirms) | `notification/models.py:5` |

## `app_configs`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| key | 키 | String(100) | no | UNIQUE | — | — | | free string key, e.g. `point_cycle`, `photos.dad`, `cheer.senders` — **no `level.thresholds` key exists in any seed** | `database/init.sql:238-243` |
| value | 값 | Text | yes | — | — | — | | free-text, sometimes JSON-encoded by convention (`cheer.senders`) but not schema-validated as JSON | |
| created_at/updated_at | | Mixins (no `deleted_at`) | | | | | | | `config/models.py:4` |

## `login_logs`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | autoincrement | PK | — | | | |
| player_id | 플레이어 ID | Integer | no | — | FK CASCADE | `players.id` | | | |
| success | 성공 여부 | Boolean | no | — | — | — | | | |
| ip_address | IP 주소 | String(45) | yes | — | — | — | | v4/v6-sized; possibly sensitive (PII-adjacent) | mark for handling per `agent-system/rules.md` masking rule |
| date | 날짜 | Date | no | — | — | — | | | |
| created_at | 생성일 | TIMESTAMP(tz) | no | now() | — | — | | no `updated_at`/`deleted_at` (audit log, append-only) | `login_log/models.py:5` |

## `accounts`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| display_name | 표시 이름 | String(100) | no | — | — | — | | | |
| status | 상태 | String(20) | no | `'active'` | CHECK (active/suspended/deleted) | — | enum | note: has both a `status='deleted'` value **and** a `deleted_at` soft-delete column — same dual-representation-of-gone pattern noted for `doran_rooms` | `family/models.py:6-11` |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `family_groups`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| name | 이름 | String(100) | no | — | — | — | | | |
| status | 상태 | String(20) | no | `'active'` | CHECK (active/suspended/closed) | — | enum | same dual `status`+`deleted_at` pattern as `accounts` | |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `family_memberships`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| family_group_id | 가족 ID | Integer | no | — | FK RESTRICT | `family_groups.id` | | see naming note (`family_id` vs `family_group_id`) in Naming Contract | `family/models.py:25` |
| account_id | 계정 ID | Integer | no | — | FK RESTRICT | `accounts.id` | | | |
| relationship | 관계 | String(30) | no | `'unknown'` | CHECK (mother/father/child/guardian/grandparent/other/unknown) | — | enum | | |
| status | 상태 | String(20) | no | `'invited'` | CHECK (invited/active/suspended/left/removed) | — | enum | | |
| joined_at | 가입일 | DateTime(tz) | yes | — | — | — | | null until `status` becomes `active` | `family/service.py:169-175` |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

Composite: `UNIQUE(account_id, family_group_id)` — one Membership per Account per Family. Also `UNIQUE(id, family_group_id)` (`uq_family_memberships_id_family`) — exists solely to let Doran tables declare composite FKs `(x_id, family_group_id) -> (family_memberships.id, family_memberships.family_group_id)`, cross-table-verifying family scope at the DB level, not just in application code.

## `roles`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| scope_type | 범위 유형 | String(20) | no | — | CHECK (FAMILY/SERVICE) | — | enum | | |
| service_code | 서비스 코드 | String(50) | yes | — | CHECK: NULL iff scope_type=FAMILY, NOT NULL iff scope_type=SERVICE | — | free string (`markpoint`/`doran` observed) | | |
| code | 코드 | String(80) | no | — | part of composite unique index | — | free string (`owner`/`admin`/`member`/`restricted_member`/`participant`/`mission_manager`/`point_admin`/`room_admin`) | | |
| name | 이름 | String(100) | no | — | — | — | | | |
| description | 설명 | Text | yes | — | — | — | | | |
| is_system | 시스템 역할 여부 | Boolean | no | true | — | — | | | |
| is_active | 활성 여부 | Boolean | no | true | — | — | | | |
| created_at/updated_at | | Mixin (no `deleted_at`) | | | | | | | |

Unique index `uq_roles_scope_service_code` on `(scope_type, COALESCE(service_code,''), code)` — a functional index working around SQL's `NULL != NULL` so that a `(FAMILY, NULL, 'owner')` role can't be duplicated even though a naive unique constraint on nullable `service_code` would not catch it.

## `permissions`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| code | 코드 | String(120) | no | UNIQUE | — | — | free string, dotted namespace (`family.read`, `markpoint.own.read`, `doran.messages.send`, etc.) | | |
| description | 설명 | Text | yes | — | — | — | | | |
| created_at | 생성일 | DateTime(tz) | no | now() | — | — | | no `updated_at`/`deleted_at` (registry table) | |

## `role_permissions`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | evidence |
|---|---|---|---|---|---|---|---|
| role_id | 역할 ID | Integer | no | — | PK part, FK RESTRICT | `roles.id` | |
| permission_id | 권한 ID | Integer | no | — | PK part, FK RESTRICT | `permissions.id` | |

Pure join table, composite PK, no surrogate id, no timestamps — a deliberately minimal registry-relationship table.

## `membership_role_assignments`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| membership_id | 구성원 ID | Integer | no | — | FK RESTRICT | `family_memberships.id` | | | |
| role_id | 역할 ID | Integer | no | — | FK RESTRICT | `roles.id` | | | |
| assigned_by_account_id | 부여자 계정 ID | Integer | yes | — | FK RESTRICT | `accounts.id` | | | |
| assigned_at | 부여일 | DateTime(tz) | no | now() | — | — | | | |
| revoked_at | 회수일 | DateTime(tz) | yes | — | — | — | | doubles as the "is this grant still active" flag | |

Partial unique index `uq_active_membership_role` on `(membership_id, role_id) WHERE revoked_at IS NULL` — allows re-granting the same Role after a prior revocation, but never two simultaneously-active grants.

## `service_subscriptions`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| family_group_id | 가족 ID | Integer | no | — | FK RESTRICT, UNIQUE with `service_code` | `family_groups.id` | | | |
| service_code | 서비스 코드 | String(50) | no | — | UNIQUE with `family_group_id` | — | free string | | |
| status | 상태 | String(20) | no | `'active'` | CHECK (active/suspended/cancelled) | — | enum | | |
| started_at / ended_at | 시작/종료일 | DateTime(tz) | yes | — | — | — | | | |
| created_at/updated_at | | Mixin (no `deleted_at` — status covers lifecycle) | | | | | | | |

## `legacy_identity_mappings`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| account_id | 계정 ID | Integer | yes | — | FK RESTRICT | `accounts.id` | | null until reviewed/linked | |
| legacy_system | 레거시 시스템 | String(50) | no | — | part of composite unique | — | free string (`markpoint` observed) | | |
| legacy_identity_type | 레거시 신원 유형 | String(50) | no | — | part of composite unique | — | free string (`player_auth`/`admin_auth` observed) | | |
| legacy_identity_id | 레거시 신원 ID | String(100) | no | — | part of composite unique | — | stringified legacy PK | | |
| mapping_status | 매핑 상태 | String(20) | no | `'candidate'` | CHECK (candidate/reviewed/linked/rejected/ambiguous) | — | enum | only `linked` grants Account resolution | `family/service.py:71-86` |
| reviewed_by_account_id | 검토자 계정 ID | Integer | yes | — | FK RESTRICT | `accounts.id` | | | |
| reviewed_at | 검토일 | DateTime(tz) | yes | — | — | — | | | |
| created_at | 생성일 | DateTime(tz) | no | now() | — | — | | no `updated_at` | |

Composite unique `(legacy_system, legacy_identity_type, legacy_identity_id)` — one mapping row per legacy identity, ever.

## `doran_rooms`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | UUID | no | `gen_random_uuid()` | PK | — | | | |
| family_group_id | 가족 ID | Integer | no | — | FK RESTRICT, part of `uq_doran_rooms_id_family` | `family_groups.id` | | | |
| room_type | 방 유형 | String(20) | no | — | CHECK (DIRECT/GROUP/SERVICE) | — | enum | | |
| title | 제목 | String(200) | yes | — | — | — | | required by schema validator when `room_type=GROUP`, but not DB-CHECK-enforced (application-level only) | `doran/schemas.py:30-31` |
| status | 상태 | String(20) | no | `'active'` | CHECK (active/read_only/closed/deleted) | — | enum | | |
| created_by_actor_type | 생성자 유형 | String(20) | no | — | CHECK (ACCOUNT/SERVICE/SYSTEM) | — | enum | | |
| created_by_account_id | 생성자 계정 ID | Integer | yes | — | FK RESTRICT | `accounts.id` | | null when `created_by_actor_type != ACCOUNT` | |
| next_message_sequence | 다음 메시지 순번 | BigInteger | no | 0 | — | — | | atomically incremented per send (`UPDATE ... RETURNING`) — the room's own monotonic counter | `doran/service.py:128,482` |
| version | 버전 | Integer | no | 1 | — | — | | `UNKNOWN` — declared on the model/migration but no read/write site found in the service layer during this task (optimistic-lock field not yet wired to any UPDATE's WHERE clause) | |
| closed_at | 종료일 | DateTime(tz) | yes | — | — | — | | | |
| created_at/updated_at/deleted_at | | Mixins | | | | | | | |

## `doran_direct_pairs`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | evidence |
|---|---|---|---|---|---|---|---|
| room_id | 방 ID | UUID | no | — | PK, FK RESTRICT | `doran_rooms.id` | |
| family_group_id | 가족 ID | Integer | no | — | FK RESTRICT | `family_groups.id` | |
| membership_low_id / membership_high_id | 낮은/높은 구성원 ID | Integer | no | — | composite FK RESTRICT to `(family_memberships.id, family_memberships.family_group_id)` each; CHECK `low < high` | `family_memberships.id` | canonical ordering trick so an unordered pair has one deterministic row, see `doran/rules.py:5-8` |
| is_active | 활성 여부 | Boolean | no | true | — | — | |
| created_at | 생성일 | DateTime(tz) | no | now() | — | — | no `updated_at` |

Partial unique index `uq_doran_active_direct_pair` on `(family_group_id, membership_low_id, membership_high_id) WHERE is_active` — allows a DIRECT room to be recreated after being "closed" without a permanent unique-constraint conflict, since only one row can be `is_active=true` at a time per pair.

## `doran_participants`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | UUID | no | `gen_random_uuid()` | PK | — | | | |
| family_group_id | 가족 ID | Integer | no | — | part of composite FKs | — | | denormalized copy, not its own FK — enforced only transitively via the composite FKs on `room_id`/`family_membership_id` | `doran/models.py:49,60-61` |
| room_id | 방 ID | UUID | no | — | composite FK RESTRICT | `doran_rooms.(id,family_group_id)` | | | |
| family_membership_id | 구성원 ID | Integer | no | — | composite FK RESTRICT | `family_memberships.(id,family_group_id)` | | note the name here is `family_membership_id` (matches DB), vs. `family/schema.py`'s own `membership_id` for the same referent — see Naming Contract | |
| room_role | 방 내 역할 | String(20) | no | `'member'` | CHECK (room_admin/member) | — | enum | | |
| status | 상태 | String(20) | no | `'active'` | CHECK (active/left/removed); CHECK `left_sequence IS NULL OR left_sequence >= joined_sequence` | — | enum | | |
| joined_sequence / left_sequence | 참여/이탈 순번 | BigInteger | no/yes | — | — | — | | defines the message-visibility window (`doran/rules.py:visible_range`) | |
| joined_at / left_at / removed_at | 참여/이탈/제거일 | DateTime(tz) | no/yes/yes | now()/—/— | — | — | | | |
| created_at/updated_at | | Mixin (no `deleted_at` — `status` covers it) | | | | | | | |

## `doran_messages`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | UUID | no | `gen_random_uuid()` | PK | — | | | |
| family_group_id | 가족 ID | Integer | no | — | denormalized (see participants note) | — | | | |
| room_id | 방 ID | UUID | no | — | composite FK RESTRICT, UNIQUE with `sequence` | `doran_rooms.(id,family_group_id)` | | | |
| sequence | 순번 | BigInteger | no | — | UNIQUE with `room_id` | — | | assigned atomically from `doran_rooms.next_message_sequence` | |
| sender_participant_id | 발신 참여자 ID | UUID | yes | — | FK RESTRICT | `doran_participants.id` | | null iff `message_type=SERVICE_ACTION` (CHECK-enforced) | |
| message_type | 메시지 유형 | String(20) | no | `'TEXT'` | CHECK (TEXT/SYSTEM/SERVICE_ACTION); CHECK: TEXT requires 1-4000 char body | — | enum | | |
| client_message_id | 클라이언트 메시지 ID | String(64) | yes | — | UNIQUE with `(sender_participant_id, room_id)` | — | | client-supplied idempotency key for human sends | |
| body | 본문 | Text | yes | — | CHECK: required+bounded iff TEXT | — | | | |
| reply_to_message_id | 답장 대상 메시지 | UUID | yes | — | **no FK** declared at either DB or ORM level (`UNKNOWN`/possible gap — a dangling reference is structurally possible) | — | | | `doran/models.py:96` |
| service_code | 서비스 코드 | String(50) | yes | — | CHECK: required iff SERVICE_ACTION | — | | | |
| service_payload_version | 페이로드 버전 | Integer | yes | — | — | — | | | |
| service_payload | 페이로드 | JSONB | yes | — | — | — | | display-minimum snapshot only, per code docstring — never a business-decision payload | `doran/service.py:1` |
| service_principal_id | 서비스 주체 ID | Integer | yes | — | FK RESTRICT; CHECK: required iff SERVICE_ACTION, forbidden otherwise | `service_principals.id` | | mutually exclusive with `sender_participant_id` by CHECK | `migration 0003...:48-54` |
| source / source_event_id | 출처/출처 이벤트 ID | String(100)/String(128) | yes | — | UNIQUE `(service_principal_id, source, source_event_id)` partial, `WHERE message_type='SERVICE_ACTION'` | — | | idempotency key for service-published events | migration `0003...:55-61` |
| created_at | 생성일 | DateTime(tz) | no | now() | — | — | | no `updated_at` (messages are immutable except for the tombstone fields below) | |
| deleted_at / deleted_by_account_id | 삭제일/삭제자 | DateTime(tz)/Integer | yes | — | FK RESTRICT on the latter | `accounts.id` | | tombstone pattern — row retained, `deleted:true` still returned in API response | `doran/schemas.py:88-90` |

## `doran_participant_read_states`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | evidence |
|---|---|---|---|---|---|---|---|
| participant_id | 참여자 ID | UUID | no | — | PK, FK RESTRICT | `doran_participants.id` | 1:1 |
| last_read_sequence | 마지막 읽음 순번 | BigInteger | no | 0 | CHECK >= 0 | — | |
| updated_at | 수정일 | DateTime(tz) | no | now(), onupdate | — | — | no `created_at` — this row's creation time is not separately tracked, only its last update |

## `service_principals`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| service_code | 서비스 코드 | String(50) | no | — | — | — | free string | | |
| display_name | 표시 이름 | String(100) | no | — | — | — | | | |
| credential_id | 자격 증명 ID | String(64) | no | UNIQUE | — | — | | public half of the Bearer credential | **yes** (identifier, not secret itself, but should still be treated carefully) |
| credential_hash | 자격 증명 해시 | String(255) | no | — | — | — | | bcrypt hash of the secret half; secret itself is returned exactly once at issuance and never persisted | **yes — never log** |
| status | 상태 | String(20) | no | `'active'` | CHECK (active/revoked) | — | enum | | |
| revoked_at | 회수일 | DateTime(tz) | yes | — | — | — | | | |
| created_at/updated_at | | Mixin (no `deleted_at`) | | | | | | | |

## `doran_service_bindings`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | Integer | no | — | PK | — | | | |
| service_principal_id | 서비스 주체 ID | Integer | no | — | FK RESTRICT, UNIQUE with `room_id`, UNIQUE with `family_group_id` | `service_principals.id` | | the family_group_id unique constraint enforces "at most one Binding per (Principal, Family)" — added later in migration 0004, not 0003 | migration `0004...:42-46` |
| family_group_id | 가족 ID | Integer | no | — | FK RESTRICT | `family_groups.id` | | | |
| room_id | 방 ID | UUID | no | — | composite FK RESTRICT | `doran_rooms.(id,family_group_id)` | | additionally guarded by a live DB trigger requiring the referenced room's `room_type='SERVICE'` | migration `0004...:52-80` |
| allowed_actions | 허용 액션 목록 | JSONB | no | — | — | — | | list of `{action_type, schema_version}` allow-list entries checked at publish time | `doran/service.py:457-464` |
| status | 상태 | String(20) | no | `'active'` | CHECK (active/inactive) | — | enum | | |
| created_at/updated_at | | Mixin (no `deleted_at`) | | | | | | | |

## `doran_service_audit_log`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | BigInteger | no | autoincrement | PK | — | | | |
| event_type | 이벤트 유형 | String(40) | no | — | CHECK (9 named values, see Table Dictionary) | — | enum | | |
| service_principal_id | 서비스 주체 ID | Integer | yes | — | FK RESTRICT | `service_principals.id` | | | |
| family_group_id | 가족 ID | Integer | yes | — | **no FK** (deliberate — see Table Dictionary purpose note) | — | | | |
| room_id | 방 ID | UUID | yes | — | **no FK** (same reason) | — | | | |
| result_code | 결과 코드 | String(20) | no | — | not CHECK-constrained | — | free string (`success`/`denied`/`conflict`/`idempotent` observed) | | |
| detail | 상세 | String(200) | yes | — | — | — | | never a credential/token/message body, per code docstring | `doran/models.py:169-172` |
| created_at | 생성일 | DateTime(tz) | no | now() | — | — | | append-only, no `updated_at` | |

## `service_outbox_events`

| column | logical_name_ko | data_type | nullable | default | constraint | reference | enum_or_status | definition | evidence |
|---|---|---|---|---|---|---|---|---|---|
| id | ID | BigInteger | no | autoincrement | PK | — | | | |
| owner_service | 소유 서비스 | String(50) | no | UNIQUE with `source_event_id` | — | — | free string (`mark-point` observed) | | |
| event_type | 이벤트 유형 | String(60) | no | — | — | — | free string (`mission.completed` observed) | | |
| event_version | 이벤트 버전 | Integer | no | — | — | — | | | |
| aggregate_type / aggregate_id | 대상 유형/ID | String(50)/String(64) | no | — | — | — | | `aggregate_type="mission"`, `aggregate_id=str(mission.id)` observed | `mission/service.py:339,359` |
| source_event_id | 출처 이벤트 ID | String(128) | no | UNIQUE with `owner_service` | — | | includes a timestamp component so a re-completion after revert produces a distinct id | `mission/service.py:352` |
| family_id | 가족 ID | Integer | no | — | **no FK** (owner-agnostic table, deliberately decoupled) | — | | note: this table uses `family_id`, not `family_group_id` — yet another instance of the naming split noted in the Naming Contract | |
| payload | 페이로드 | JSONB | no | — | — | — | | display-minimum event snapshot | |
| status | 상태 | String(20) | no | `'PENDING'` | CHECK (PENDING/PROCESSING/PUBLISHED/DEAD) | — | enum | **No worker/consumer was found in this task's scope that ever transitions a row out of `PENDING`** — see Gap Report | grep of `backend/app` for a Doran-side outbox consumer/worker returned no match |
| attempt_count | 시도 횟수 | Integer | no | 0 | — | — | | | |
| next_attempt_at | 다음 시도 시각 | DateTime(tz) | no | now() | — | — | | | |
| locked_until | 잠금 해제 시각 | DateTime(tz) | yes | — | — | — | | the one `*_until` timestamp column in the whole schema that does not follow the `*_at` convention — a worker-claim lock field, not a user-facing lock | |
| published_at | 발행일 | DateTime(tz) | yes | — | — | — | | | |
| last_error_code | 마지막 오류 코드 | String(60) | yes | — | — | — | | | |
| created_at/updated_at | | Mixin | | | | | | | |
