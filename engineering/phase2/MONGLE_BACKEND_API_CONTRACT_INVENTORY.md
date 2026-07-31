# MONGLE_BACKEND_API_CONTRACT_INVENTORY

> **AXIS: LEGACY_CURRENT_STATE (A).** This inventories the API surface as it
> exists today, including legacy PIN/admin-JWT routes that are explicitly
> **not** assumed preserved in the target architecture. The Family/Doran
> routes documented here, however, are largely already Axis-B-shaped (see
> `MONGLE_LEGACY_TO_TARGET_MAPPING.md` — most are KEEP_AS_IS or TRANSFORM,
> not REPLACE). See `MONGLE_TARGET_API_INVENTORY.md` for the target surface.

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001

Method: every route below was extracted by grepping `@router.(get|post|put|patch|delete)` across all 16 domain routers, then cross-checked against each router's actual `APIRouter(prefix=...)` declaration and `app/main.py`'s `include_router` calls for the final mounted path. Auth dependency was read directly from each route's own `Depends(...)` parameter, not inferred. `consumer` was checked by grepping the frontend for the literal route string or its known API-client wrapper function; "NONE FOUND" means a real grep returned zero matches, not an assumption.

Total: 88 distinct operations across 16 domain routers + 1 root health check.

## Auth dependency legend

| Short code | Actual dependency | Module | Behavior |
|---|---|---|---|
| `PLAYER_OR_ADMIN` | `get_current_user` | `app/dependencies.py` | HTTPBearer; accepts JWT `role` of `player` or `admin`; returns raw payload dict |
| `PLAYER_ONLY` | `get_current_player` | `app/dependencies.py` | wraps `PLAYER_OR_ADMIN`, 403s if `role != player`, normalizes `player_id` |
| `ADMIN_ONLY` | `require_admin` | `app/dependencies.py` | wraps `PLAYER_OR_ADMIN`, 403s if `role != admin` |
| `PLAYER_JWT_ONLY` | `get_current_user` | `app/domains/auth/dependencies.py` | **different function, same name** — OAuth2PasswordBearer, accepts only `role=player`, returns normalized `{player_id, is_admin}` |
| `ADMIN_JWT` | `get_current_admin` | `app/domains/auth/dependencies.py` | OAuth2PasswordBearer, `role=admin`, loads and returns the real `AdminAuth` ORM row |
| `CHAT_USER` | `get_current_chat_user` | `app/domains/auth/dependencies.py` | accepts either player or admin token, normalizes to `{player_id}` |
| `SERVICE_PRINCIPAL` | `get_current_service_principal` | `app/domains/doran/service_actor.py` | HTTPBearer, `<credential_id>.<secret>` shape, never a user JWT |
| `NONE` | — | — | no auth dependency present |

## `/api/auth` (auth domain)

| screen | method | route | request | response | authorization | family_scope | service | tables | test | consumer | status | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | POST | `/api/auth/login` | `LoginRequest{player_id,pin,remember_me}` | `LoginResponse` | NONE (this IS the login) | n/a | `auth/service.py::authenticate_player` | `player_auth`,`players` | `tests/api/legacy_auth_boundary_test.py` (indirect, via login flow) | `frontend/src/pages/Auth/api/authApi.ts::authApi.login` | LIVE | `auth/router.py:12-16` |
| A1 | POST | `/api/auth/admin/login` | `AdminLoginRequest{username,password}` | `AdminLoginResponse` | NONE | n/a | `auth/service.py::authenticate_admin` | `admin_auth` | same | `authApi.ts::adminLogin` | LIVE | `auth/router.py:18-27` |
| A1 | POST | `/api/auth/logout` | none | 200 (no body model declared) | `PLAYER_OR_ADMIN` | n/a | n/a (stateless JWT — likely a no-op/client-side token discard; not verified further in this task) | none | none found | `authApi.ts::authApi.logout` | LIVE (thin) | `auth/router.py:29-32` |

## `/api/players` (player domain)

| screen | method | route | request | response | authorization | family_scope | service | tables | test | consumer | status | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | GET | `/api/players` | — | `list[PlayerListItem]` | NONE (!) — no `Depends` present on this specific route despite the domain having auth deps available | n/a | `get_player_list` | `players`,`player_auth`,`daily_points` (subquery sum) | `tests/api/legacy_auth_boundary_test.py` (asserts something about unauthenticated player listing — not re-verified line-by-line this task) | `authApi.ts::authApi.getPlayers` (called pre-login on A1) | LIVE, **flagged**: this is the one player-roster-exposing route with zero auth requirement, confirmed by direct source read (`player/router.py:15-19` has no `Depends` param) — matches the observed A1 behavior of successfully listing players before any login | `player/router.py:15-19` |
| A3 | GET | `/api/players/me` | — | `PlayerListItem` | `PLAYER_ONLY` | n/a | `get_player_by_id(self)` | `players` | not verified this task | not confirmed — no direct grep match for this exact path in frontend | UNKNOWN (exists server-side, FE consumer not located) | `player/router.py:21-28` |
| n/a | POST | `/api/players` | `PlayerCreate` | `PlayerListItem`, 201 | `ADMIN_ONLY` | n/a | `create_player` | `players`,`player_auth` | not verified | not located in FE grep (likely an as-yet-unbuilt admin "add player" screen) | LIVE server-side, FE consumer UNKNOWN | `player/router.py:30-38` |
| A5 | PATCH | `/api/players/{player_id}` | `PlayerUpdate` | `PlayerListItem` | `PLAYER_ONLY` (self only, via `require_self_player_id`) | n/a | `update_player` | `players` | not verified | not located | LIVE server-side, FE consumer UNKNOWN | `player/router.py:40-49` |
| A5 | DELETE | `/api/players/{player_id}` | — | 204 | `ADMIN_ONLY` | n/a | `soft_delete_player` | `players` | not verified | not located | LIVE server-side, FE consumer UNKNOWN | `player/router.py:51-56` |

## `/api/missions` (mission domain)

| screen | method | route | request | response | authorization | family_scope | service | tables | test | consumer | status | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A3 | GET | `/api/missions` | query: player_id? | `list[MissionResponse]` | `PLAYER_ONLY` | n/a | `get_missions_by_player_date`/list variant | `missions` | not verified | `dashboardApi.ts` (assumed, not individually confirmed by literal-string grep in this pass) | LIVE | `mission/router.py:21-35` |
| A3 | POST | `/api/missions` | `MissionCreate` | `MissionResponse`, 201 | `ADMIN_ONLY` | n/a | `create_mission` | `missions` | not verified | AdminDashboard | LIVE | `mission/router.py:37-45` |
| A3 | PATCH | `/api/missions/{id}` | `MissionUpdate` | `MissionResponse` | `PLAYER_ONLY` | n/a (role-gated transition logic, not family-gated) | `update_mission(role=player)` | `missions`,`daily_points`,`players`,`service_outbox_events` (on completion) | not verified | dashboard | LIVE | `mission/router.py:47-61` |
| A3 | DELETE | `/api/missions/{id}` | — | 204 | `ADMIN_ONLY` | n/a | `soft_delete_mission` | `missions` | not verified | admin | LIVE | `mission/router.py:63-71` |
| A3 | POST | `/api/missions/propose` | `MissionPropose` | `MissionResponse`, 201 | `PLAYER_ONLY` | n/a | `propose_mission` | `missions`,`notifications` | not verified | dashboard | LIVE | `mission/router.py:73-83` |
| n/a | POST | `/api/missions/copy` | — | `list[MissionResponse]`, 201 | `PLAYER_ONLY` | n/a | `batch_copy_missions` | `missions` | not verified | not located | LIVE server-side, FE consumer UNKNOWN | `mission/router.py:85-95` |
| n/a | POST | `/api/missions/batch-copy` | — | `list[MissionResponse]`, 201 | `PLAYER_ONLY` | n/a | `batch_copy_missions` | `missions` | not verified | not located | LIVE server-side, FE consumer UNKNOWN | `mission/router.py:97-107` |
| A3 | GET | `/api/missions/weekly` | — | ad hoc dict (no `response_model`) | `PLAYER_ONLY` | n/a | `get_missions_by_range` | `missions` | `backend/tests/test_weekly.py` | dashboard | LIVE | `mission/router.py:109-122` |
| A3 | GET | `/api/missions/weekly-remaining` | — | ad hoc dict | `PLAYER_ONLY` | n/a | (not read in full this task) | `missions` | not verified | dashboard | LIVE | `mission/router.py:124` |

## `/api/admin` (admin domain — aggregating router, no own models/schema)

This entire router requires `ADMIN_JWT` (`get_current_admin`) on every single one of its 31 operations, with zero exceptions found. All 31 routes delegate to another domain's own service functions (Thin Controller, confirmed by the router's own docstring and import list). Screen: A5 for all rows below unless noted.

| method | route | delegates to (service) | tables touched | consumer | status | evidence |
|---|---|---|---|---|---|---|
| GET | `/api/admin/players` | `player.service.get_player_list` | `players`,`player_auth`,`daily_points` | `adminApi.ts` | LIVE | `admin/router.py:80-85` |
| GET | `/api/admin/missions` | `mission.service.get_missions_admin` (+ lazy-expiry side effect via `expire_stale_missions`) | `missions` | admin | LIVE | `admin/router.py:89-104` |
| POST | `/api/admin/missions` | `mission.service.create_mission` | `missions` | admin | LIVE | `admin/router.py:107-113` |
| PATCH | `/api/admin/missions/{id}/status` | `mission.service.update_mission_status(role=admin)` | `missions`,+point sync | admin | LIVE | `admin/router.py:116-125` |
| PATCH | `/api/admin/missions/{id}` | `mission.service.update_mission(role=admin)` | `missions`,+point sync | admin | LIVE | `admin/router.py:128-135` |
| POST | `/api/admin/missions/{id}/revert` | `mission.service.admin_revert_mission` | `missions`,`daily_points`,`players` | admin | LIVE | `admin/router.py:138-147` |
| DELETE | `/api/admin/missions/by-group/{group_id}` | inline (not delegated — direct `sql_update` in the router itself, the one exception to Thin Controller in this router) | `missions` | admin | LIVE (architecture exception noted) | `admin/router.py:150-165` |
| DELETE | `/api/admin/missions/{id}` | `mission.service.soft_delete_mission` | `missions` | admin | LIVE | `admin/router.py:168-174` |
| POST | `/api/admin/missions/clone` | `mission.service.clone_missions` | `missions` | admin | LIVE | `admin/router.py:177-183` |
| POST | `/api/admin/missions/clone-selected` | `mission.service.clone_selected_missions` | `missions` | admin | LIVE | `admin/router.py:186-193` |
| GET | `/api/admin/deductions` | `deduction.service.get_deductions_admin` | `deductions` | admin | LIVE | `admin/router.py:197-204` |
| POST | `/api/admin/deductions` | `deduction.service.create_deduction` | `deductions` | admin | LIVE | `admin/router.py:207-213` |
| PATCH | `/api/admin/deductions/{id}` | `deduction.service.update_deduction` | `deductions` | admin | LIVE | `admin/router.py:216-223` |
| DELETE | `/api/admin/deductions/{id}` | `deduction.service.soft_delete_deduction` | `deductions` | admin | LIVE | `admin/router.py:226-232` |
| GET | `/api/admin/daily-points` | `daily_point.service.get_daily_points_admin` | `daily_points` | admin | LIVE | `admin/router.py:236-243` |
| POST | `/api/admin/daily-points/adjust` | `daily_point.service.adjust_daily_point` | `daily_points` | admin | LIVE | `admin/router.py:246-252` |
| PUT | `/api/admin/cheers/{target_date}` | `cheer.service.upsert_cheer` | `cheer_messages` | admin | LIVE | `admin/router.py:256-263` |
| PATCH | `/api/admin/players/{id}` | `player.service.update_player_admin` | `players` | admin | LIVE | `admin/router.py:267-274` |
| PATCH | `/api/admin/players/{id}/pin` | `player.service.change_player_pin` | `player_auth` | admin | LIVE | `admin/router.py:277-284` |
| PATCH | `/api/admin/players/{id}/lock` | `player.service.lock_player` | `players` | admin | LIVE | `admin/router.py:287-294` |
| PATCH | `/api/admin/players/{id}/visibility` | `player.service.set_player_visibility` | `players` | admin | LIVE | `admin/router.py:297-304` |
| GET | `/api/admin/notifications` | `notification.service.get_all_notifications` | `notifications` | admin | LIVE | `admin/router.py:308-313` |
| POST | `/api/admin/notifications` | `notification.service.create_notification` | `notifications` | admin | LIVE | `admin/router.py:316-322` |
| PATCH | `/api/admin/notifications/read-all` | `notification.service.mark_all_as_read` | `notifications` | admin | LIVE | `admin/router.py:325-330` |
| PATCH | `/api/admin/notifications/{id}/read` | `notification.service.mark_as_read` | `notifications` | admin | LIVE | `admin/router.py:333-339` |
| GET | `/api/admin/feedbacks` | `feedback.service.get_feedbacks_by_player` | `feedbacks`,`feedback_replies` | admin | LIVE | `admin/router.py:343-350` |
| POST | `/api/admin/feedbacks/{id}/replies` | `feedback.service.add_reply` | `feedback_replies` | admin | LIVE | `admin/router.py:353-360` |
| GET | `/api/admin/cycle-progress` | `mission.service.get_cycle_mission_progress` | `missions` | admin | LIVE | `admin/router.py:364-375` |
| GET | `/api/admin/weekly-summary` | inline (calls `player.service.get_player_list` + `mission.service.get_missions_by_range` and aggregates) | `players`,`missions` | admin | LIVE (architecture exception, same as delete-by-group) | `admin/router.py:379-423` |
| POST | `/api/admin/missions/bulk-approve` | `mission.service.bulk_approve_missions` | `missions`,`players` | admin | LIVE | `admin/router.py:426-436` |
| GET | `/api/admin/login-logs` | `login_log.service.get_all_login_logs` | `login_logs` | admin | LIVE | `admin/router.py:440-447` |
| GET | `/api/admin/configs` | `config.service.get_all_configs` | `app_configs` | admin | LIVE | `admin/router.py:451-456` |
| PUT | `/api/admin/configs/{key}` | `config.service.upsert_config` | `app_configs` | admin | LIVE | `admin/router.py:459-466` |

## `/api/cheers`, `/api/configs`, `/api/deductions`, `/api/daily-points`, `/api/notifications`, `/api/login-logs`, `/api/level-tiers`, `/api/feedbacks`, `/api/chat` (non-admin player-facing player + household domains)

| screen | method | route | authorization | service | tables | consumer | status | evidence |
|---|---|---|---|---|---|---|---|---|
| A3 | GET | `/api/cheers/` | `PLAYER_OR_ADMIN` | `list_cheers` (not read in full) | `cheer_messages` | dashboard | LIVE | `cheer/router.py:14-22` |
| n/a | POST | `/api/cheers/` | `ADMIN_ONLY` | `create_cheer` | `cheer_messages` | admin (superseded in practice by `/api/admin/cheers/{date}` PUT) | LIVE, likely-redundant path | `cheer/router.py:24-32` |
| A1 (pre-login, see Gap Report) / A5 | GET | `/api/configs/` | `PLAYER_OR_ADMIN` | `get_all_configs` | `app_configs` | admin configs screen | LIVE | `config/router.py:12-18` |
| A1 (pre-login, see Gap Report) | GET | `/api/configs/{key}` | `PLAYER_OR_ADMIN` | `get_config_by_key` | `app_configs` | `PlayerSelectView.tsx` fetches `level.thresholds` **before login**, so this call 401s in practice today | LIVE server-side, **broken in the one place it's called** | `config/router.py:21-28`, confirmed by direct A1 empirical test (401 observed) |
| n/a | PUT | `/api/configs/{key}` | `ADMIN_ONLY` | `upsert_config` | `app_configs` | admin (superseded in practice by `/api/admin/configs/{key}` PUT) | LIVE, likely-redundant path | `config/router.py:31-39` |
| A3/A5 | GET/POST/PATCH/DELETE `/api/deductions/*` | `PLAYER_ONLY` (GET) / `ADMIN_ONLY` (write) | `deduction.service.*` | `deductions` | dashboard/admin (superseded in practice by `/api/admin/deductions/*` for writes) | LIVE, likely-redundant write paths | `deduction/router.py` |
| A3 | GET `/api/daily-points/` `/range` `/summary` `/total-earned`; POST `/api/daily-points/` | `PLAYER_ONLY` (GET) / `ADMIN_ONLY` (POST) | `daily_point.service.*` | `daily_points` | dashboard | LIVE | `daily_point/router.py` |
| A3 | GET/POST/PATCH `/api/notifications/*` | `PLAYER_ONLY` (GET/PATCH) / `ADMIN_ONLY` (POST) | `notification.service.*` | `notifications` | dashboard | LIVE | `notification/router.py` |
| A5 | GET `/api/login-logs/` | `ADMIN_ONLY` | `login_log.service.get_all_login_logs` | `login_logs` | admin | LIVE | `login_log/router.py` |
| A3/A5 | GET/POST/PATCH/DELETE/PUT `/api/level-tiers*` | `PLAYER_ONLY` (GET) / `ADMIN_ONLY` (write) | `level_tier.service.*` | `level_tiers`,`players` | **NONE FOUND** — no frontend grep match for `level-tiers` at all, anywhere. This is the real, authoritative level API and it appears to have **zero frontend consumers today** | LIVE server-side, **FE consumer confirmed absent** | `level_tier/router.py`, grep of `frontend/src` for `level-tiers` returned zero matches |
| A3 | GET/POST `/api/feedbacks/*`, POST `/api/feedbacks/replies` | `PLAYER_OR_ADMIN` (GET/reply) / `PLAYER_ONLY` (create) | `feedback.service.*` | `feedbacks`,`feedback_replies` | dashboard | LIVE | `feedback/router.py` |
| n/a (legacy 1:1, not A4) | GET/POST `/api/chat/*` | `CHAT_USER` | (chat service, not read in full this task) | `chat_messages` | dashboard's existing 1:1 chat UI (pre-Doran, still live, separate from A4/와글와글) | LIVE | `chat/router.py` |

## `/api/families/*` and `/api/account-context` (family domain — no router-level prefix; each route's full path is hand-written)

| screen | method | route | request | response | authorization | family_scope | service | tables | consumer | status | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A2 | GET | `/api/account-context` | — | `AccountContextResponse` | `PLAYER_OR_ADMIN` | resolves caller's own Account, lists all their Families | `family.service.resolve_current_account` + per-family summary | `accounts`,`family_memberships`,`family_groups`,`legacy_identity_mappings` | `familyApi.ts::getAccountFamilyContext` | LIVE | `family/router.py:51-59` |
| n/a | POST | `/api/families` | `FamilyCreate{name}` | `FamilyResponse`, 201 | `PLAYER_OR_ADMIN` | creates a brand-new Family, caller becomes Owner | `family.service.create_family` | `family_groups`,`family_memberships`,`membership_role_assignments` | not located by literal-string grep this task | LIVE server-side, FE consumer UNKNOWN | `family/router.py:61-65` |
| A2 | GET | `/api/families` | — | `list[FamilyResponse]` | `PLAYER_OR_ADMIN` | lists caller's Families (not scoped to one) | `family.service` (list) | `family_groups`,`family_memberships` | not located | LIVE server-side, FE consumer UNKNOWN (A2's own family-summary needs may be served entirely by `/api/account-context` instead — see Screen Data Contract Matrix) | `family/router.py:67-74` |
| A2 | GET | `/api/families/{family_id}` | — | `FamilyResponse` | `PLAYER_OR_ADMIN`, family-membership-checked inside the service call | one Family | `family.service.get_family` | `family_groups` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:76-80` |
| A2/A5 | PATCH | `/api/families/{family_id}` | `FamilyUpdate` | `FamilyResponse` | requires `family.members.manage` permission | yes | inline (not delegated to a single named service function; permission-gated directly in the router) | `family_groups` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:82-98` |
| A2 | GET | `/api/families/{family_id}/members` | — | `list[MembershipSummary]` | requires `family.members.read` | yes | inline | `family_memberships`,`membership_role_assignments`,`roles` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:100-105` |
| A2/A5 | POST | `/api/families/{family_id}/members` | `MembershipCreate` | `MembershipSummary`, 201 | requires `family.members.invite` | yes | `family.service.add_membership` | `family_memberships` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:107-113` |
| A2/A5 | PATCH | `/api/families/{family_id}/members/{membership_id}` | `MembershipUpdate` | `MembershipSummary` | requires `family.members.manage` | yes | `family.service.update_membership` | `family_memberships` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:115-123` |
| A2/A5 | GET | `.../members/{membership_id}/roles` | — | `list[RoleAssignmentResponse]` | requires `family.members.read` | yes | `family.service.family_roles` | `membership_role_assignments`,`roles` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:125-131` |
| A2/A5 | POST | `.../members/{membership_id}/roles` | `RoleAssignmentCreate` | `RoleAssignmentResponse`, 201 | requires `family.roles.assign` | yes | `family.service.assign_role` | `membership_role_assignments` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:133-142` |
| A2/A5 | DELETE | `.../roles/{assignment_id}` | — | 204 | requires `family.roles.assign` | yes | `family.service.revoke_assignment` | `membership_role_assignments` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:144-151` |
| A2/A5 | GET | `/api/families/{family_id}/services` | — | `list[SubscriptionResponse]` | requires `family.services.manage` | yes | `family.service.list_subscriptions` | `service_subscriptions` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:152-157` |
| A2/A5 | POST | `.../services/{service_code}` | `ServiceSubscriptionCreate` | `SubscriptionResponse`, 201 | requires `family.services.manage` | yes | `family.service.set_subscription` | `service_subscriptions` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:158-163` |
| A2/A5 | PATCH | `.../services/{service_code}` | `ServiceSubscriptionUpdate` | `SubscriptionResponse` | requires `family.services.manage` | yes | `family.service.set_subscription` | `service_subscriptions` | not located | LIVE server-side, FE consumer UNKNOWN | `family/router.py:164-171` |

**Family API consumer summary**: only `GET /api/account-context` has a confirmed frontend caller (`familyApi.ts`). All 13 remaining Family-domain routes are fully built, tested-at-the-model-layer (via `backend/tests/`), and reachable, but **no frontend consumer was located** for any of them in this task's grep pass — Family membership management, role assignment, and service-subscription management all currently have no UI.

## `/api/families/{family_id}/doran/*` (doran domain)

| screen | method | route | request | response | authorization | family_scope | service | tables | test | consumer | status | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A4 | GET | `.../doran/rooms` | — | `list[RoomResponse]` | `PLAYER_OR_ADMIN` + `doran.messages.read` permission | yes | `doran.service.list_rooms` | `doran_rooms`,`doran_participants` | `backend/tests/test_doran_integration.py` | **NONE — DoranLanding.tsx uses static preview fixtures, not this endpoint** | LIVE server-side, **zero frontend consumer**, see Gap Report | `doran/router.py:27-29`, `frontend/src/platform/pages/DoranLanding.tsx` imports only from `../doran/preview` |
| A4 | POST | `.../doran/rooms` | `RoomCreate` | `RoomResponse`, 201 | `doran.rooms.create` | yes | `doran.service.create_room` | `doran_rooms`,`doran_direct_pairs`,`doran_participants` | same test file | NONE FOUND | same | `doran/router.py:31-34` |
| A4 | GET | `.../doran/rooms/{id}` | — | `RoomResponse` | read permission | yes | `_room` helper (inline) | `doran_rooms` | same | NONE FOUND | same | `doran/router.py:36-42` |
| A4 | PATCH | `.../doran/rooms/{id}` | `RoomUpdate` | `RoomResponse` | `doran.rooms.manage` | yes | `doran.service.update_room` | `doran_rooms` | same | NONE FOUND | same | `doran/router.py:44-46` |
| A4 | GET | `.../rooms/{id}/participants` | — | `list[ParticipantResponse]` | read permission | yes | (not individually read this task, delegates within doran.service) | `doran_participants` | same | NONE FOUND | same | `doran/router.py:48-53` |
| A4 | POST | `.../rooms/{id}/participants` | `ParticipantCreate` | `ParticipantResponse`, 201 | `doran.participants.manage` | yes | `doran.service.add_participant` | `doran_participants` | same | NONE FOUND | same | `doran/router.py:55-57` |
| A4 | DELETE | `.../participants/{id}` | — | `ParticipantResponse` | `doran.participants.manage` (or self, if voluntary) | yes | `doran.service.remove_participant` | `doran_participants` | same | NONE FOUND | same | `doran/router.py:59-61` |
| A4 | POST | `.../rooms/{id}/leave` | — | `ParticipantResponse` | any active participant (self) | yes | `doran.service.remove_participant(voluntary=True)` | `doran_participants` | same | NONE FOUND | same | `doran/router.py:63-66` |
| A4 | GET | `.../rooms/{id}/messages` | query: after/before_sequence, limit | `MessageListResponse` | read permission | yes | `doran.service.list_messages` | `doran_messages` | same | NONE FOUND | same | `doran/router.py:68-71` |
| A4 | POST | `.../rooms/{id}/messages` | `MessageCreate` | `MessageResponse`, 201 | send permission | yes | `doran.service.send_message` | `doran_messages`,`doran_rooms` | same | NONE FOUND | same | `doran/router.py:73-75` |
| A4 | DELETE | `.../rooms/{id}/messages/{msg_id}` | — | `MessageResponse` (tombstoned) | sender-only | yes | `doran.service.delete_message` | `doran_messages` | same | NONE FOUND | same | `doran/router.py:77-79` |
| A4 | GET | `.../rooms/{id}/read-state` | — | `ReadStateResponse` | read permission | yes | `doran.service.read_state` | `doran_participant_read_states` | same | NONE FOUND | same | `doran/router.py:81-84` |
| A4 | PUT | `.../rooms/{id}/read-state` | `ReadStateUpdate` | `ReadStateResponse` | read permission | yes | `doran.service.read_state` (with `requested`) | `doran_participant_read_states` | same | NONE FOUND | same | `doran/router.py:86-89` |
| n/a (no HTTP UI at all) | POST | `.../doran/service/actions` | `ServiceActionPublish` | `MessageResponse`, 201 | `SERVICE_PRINCIPAL` (not a user at all) | yes | `doran.service.publish_service_action` | `doran_messages`,`doran_service_bindings`,`doran_service_audit_log` | `backend/tests/test_doran_service_binding.py`, `test_doran_reliable_service_slice.py` | n/a — service-to-service, never called from a browser | LIVE, correctly not user-facing | `doran/router.py:91-98` |
| A4 (self-onboard on first visit) | POST | `.../doran/services/{service_code}/room` | — | `ServiceRoomOnboardResponse`, 200 | `doran.service.onboard_self_into_service_room`'s own read-permission check | yes | same | `doran_participants`,`doran_rooms`,`doran_service_bindings` | not individually confirmed | NONE FOUND | same as above | `doran/router.py:100-103` |

**Doran API consumer summary**: all 16 Doran HTTP operations are implemented, migration-backed, and covered by `backend/tests/test_doran_*.py` (71 tests passed against a freshly-migrated isolated DB, confirmed this task). **Zero of them have a frontend consumer.** The entire live A4/와글와글 UI (`DoranLanding.tsx` and its `platform/doran/components/*`) renders exclusively from `platform/doran/preview/*.ts` static fixture data. This is the single largest Gap in this reconciliation — see `MONGLE_DB_BACKEND_GAP_REPORT.md`.

## Root

| method | route | auth | evidence |
|---|---|---|---|
| GET | `/api/health` | NONE | `main.py:74-76` |
