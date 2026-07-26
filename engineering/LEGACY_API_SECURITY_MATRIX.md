# Legacy API Security Matrix

**Observed:** 2026-07-26 against source and isolated `mc_phase0` OpenAPI
(91 business routes plus framework documentation endpoints). **Status:** current
containment baseline, not proof of complete legacy correctness.

## Classification rules

| Method / path set | Current auth | Target class | Ownership rule | Role rule | Source file | Test | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `GET /api/health` | none | `PUBLIC` | none | none | `backend/app/main.py` | health probe | contained | service health only |
| `POST /api/auth/login`, `POST /api/auth/admin/login` | none | `PUBLIC` | supplied credentials only | login flow | `domains/auth/router.py` | legacy auth suite | contained | explicit login endpoints |
| `GET /api/players` | none | `PUBLIC` | no per-user data beyond selector projection | none | `domains/player/router.py` | Playwright login | contained | login player selector compatibility |
| `POST /api/auth/logout` | JWT | `AUTHENTICATED_SELF` | current session only | player or admin | `domains/auth/router.py` | route sweep | contained | no target resource |
| `GET /api/missions/`, `/weekly`, `/weekly-remaining`; `PATCH /api/missions/{mission_id}`; `POST /api/missions/propose` | player JWT | `AUTHENTICATED_SELF` | token `sub` must match requested/body/resource player | player | `domains/mission/router.py` | auth boundary suite + 87 scenario | contained | proposal body player ID is forced to authenticated actor |
| `POST /api/missions/`, `/copy`, `/batch-copy`; `DELETE /api/missions/{mission_id}` | JWT | `ADMIN_ONLY` | target may be cross-user | admin | `domains/mission/router.py` | auth boundary suite | contained | legacy direct management aliases retained but closed |
| all `GET`, `POST`, `PATCH`, `DELETE`, `PUT /api/admin/*` routes | admin JWT | `ADMIN_ONLY` | administrator may specify managed target | admin | `domains/admin/router.py` | auth boundary suite, weekly API, 87 scenario | contained | includes mission, deduction, point, notification, feedback, player, config, cheer, summary, cycle, and login-log management |
| `GET /api/daily-points/`, `/range`, `/summary`, `/total-earned` | player JWT | `AUTHENTICATED_SELF` | token `sub` must match query player ID | player | `domains/daily_point/router.py` | auth boundary suite | contained | user aggregate reads only |
| `POST /api/daily-points/` | JWT | `ADMIN_ONLY` | target in admin body | admin | `domains/daily_point/router.py` | route sweep | contained | adjustments remain legacy calculation implementation |
| `GET /api/deductions/` | player JWT | `AUTHENTICATED_SELF` | token `sub` must match query player ID | player | `domains/deduction/router.py` | 87 scenario | contained | own history only |
| `POST /api/deductions/`; `PATCH`, `DELETE /api/deductions/{deduction_id}` | JWT | `ADMIN_ONLY` | target in admin body/resource | admin | `domains/deduction/router.py` | 87 scenario | contained | legacy direct management aliases retained but closed |
| `GET /api/notifications/`; `PATCH /api/notifications/{notification_id}/read`; `PATCH /api/notifications/read-all` | player JWT | `AUTHENTICATED_SELF` | service filters `notification.player_id` | player | `domains/notification/router.py`, `service.py` | auth boundary suite | contained | cross-user read returns not-found and leaves row unchanged |
| `POST /api/notifications/` | JWT | `ADMIN_ONLY` | target in admin body | admin | `domains/notification/router.py` | route sweep | contained | server/admin creation only |
| all `/api/chat/*` routes | JWT | `AUTHENTICATED_SELF` | sender derives from token; history query is current-user/pair filtered | player or legacy admin-chat actor | `domains/chat/router.py`, `service.py` | auth boundary suite | contained | current 1:1 model only; no room policy claimed |
| `GET /api/feedbacks/`; `POST /api/feedbacks/`; `POST /api/feedbacks/replies` | JWT | `AUTHENTICATED_SELF` | player reads/writes own feedback; reply verifies feedback owner | player; existing admin read/reply compatibility | `domains/feedback/router.py` | 87 scenario | contained | admin cross-user behavior is also available under `/api/admin/*` |
| `GET /api/cheers/` | JWT | `AUTHENTICATED_SELF` | date-only shared family display | player or admin | `domains/cheer/router.py` | 87 scenario | contained | no caller-selected player data |
| `POST /api/cheers/` | JWT | `ADMIN_ONLY` | shared message write | admin | `domains/cheer/router.py` | route sweep | contained | `/api/admin/cheers/{date}` is canonical admin UI route |
| `GET /api/configs/`, `GET /api/configs/{key}` | JWT | `AUTHENTICATED_SELF` | authenticated shared configuration read | player or admin | `domains/config/router.py` | Playwright + 87 scenario | contained | public selector must not rely on config reads |
| `PUT /api/configs/{key}` | JWT | `ADMIN_ONLY` | key is managed configuration | admin | `domains/config/router.py` | 87 scenario | contained | `/api/admin/configs/{key}` is canonical admin UI route |
| `GET /api/level-tiers`; `GET /api/level-tiers/player/{player_id}` | player JWT | `AUTHENTICATED_SELF` | player-level target must equal token `sub` | player | `domains/level_tier/router.py` | 87 scenario | contained | tier list is authenticated compatibility data |
| `POST /api/level-tiers`; `PATCH`, `DELETE /api/level-tiers/{tier_id}`; `PUT /api/level-tiers/bulk` | JWT | `ADMIN_ONLY` | managed tier target | admin | `domains/level_tier/router.py` | route sweep | contained | no tier calculation rewrite |
| `GET /api/login-logs/` | JWT | `ADMIN_ONLY` | query target is managed player | admin | `domains/login_log/router.py` | route sweep | contained | `/api/admin/login-logs` is canonical admin UI route |
| all `/api/mission-templates/*` routes | admin JWT | `ADMIN_ONLY` | managed template/group target | admin | `domains/mission_template/router.py` | auth boundary suite + Playwright | contained | repeating lifecycle is otherwise legacy/unvalidated |
| FastAPI `/docs`, `/redoc`, `/openapi.json` | framework default | `INTERNAL_OR_DISABLED` for production policy | no business data | deployment policy | `backend/app/main.py` | isolated OpenAPI inspection | deferred | enabled for local development; production exposure is not approved by this matrix |

## OpenAPI path inventory

The following path families enumerate the 91 observed business routes. Each
member inherits the matching rule above; an unlisted future route is
`INTERNAL_OR_DISABLED` until classified and tested.

- `/api/admin/*`: 34 administrator management routes (players, missions,
  deductions, daily points, notifications, feedback, configuration, cheers,
  cycle/weekly summaries, login logs, clone/revert/bulk actions).
- `/api/auth/*`: three routes — player login, administrator login, logout.
- `/api/chat/*`: four routes — partners, history, send, unread.
- `/api/cheers/*`: read and legacy write.
- `/api/configs/*`: list, read-key, legacy write-key.
- `/api/daily-points/*`: point, range, summary, total-earned, legacy adjust.
- `/api/deductions/*`: list, create, update, delete.
- `/api/feedbacks/*`: list, create, reply.
- `/api/health`: health probe.
- `/api/level-tiers*`: list, current player level, create, update, delete, bulk.
- `/api/login-logs/*`: legacy administrator log list.
- `/api/mission-templates/*`: list, create, update, delete, batch delete,
  preview, and generation.
- `/api/missions/*`: list, create, update, delete, proposal, copy/batch-copy,
  weekly and weekly-remaining.
- `/api/notifications/*`: list, create, single-read, all-read.
- `/api/players*`: public selector, self read, create, update, delete.

### Per-operation crosswalk

This is the complete 91-operation OpenAPI crosswalk captured on 2026-07-26.
The path-set rules above supply detailed ownership and role notes; the crosswalk
prevents a new or unclassified operation from being silently treated as public.

| Method | Path | Current auth | Target class | Ownership rule | Source file | Test | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
+| `DELETE` | `/api/admin/deductions/{deduction_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `DELETE` | `/api/admin/missions/by-group/{group_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `DELETE` | `/api/admin/missions/{mission_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `DELETE` | `/api/deductions/{deduction_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/deduction/router.py` | matrix/suite | contained |
| `DELETE` | `/api/level-tiers/{tier_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/level_tier/router.py` | matrix/suite | contained |
| `DELETE` | `/api/mission-templates/by-group/{group_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission_template/router.py` | matrix/suite | contained |
| `DELETE` | `/api/mission-templates/{template_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission_template/router.py` | matrix/suite | contained |
| `DELETE` | `/api/missions/{mission_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission/router.py` | matrix/suite | contained |
| `DELETE` | `/api/players/{player_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/player/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/configs` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/cycle-progress` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/daily-points` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/deductions` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/feedbacks` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/login-logs` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/missions` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/notifications` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/players` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/admin/weekly-summary` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `GET` | `/api/chat/history/{partner_id}` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/chat/router.py` | matrix/suite | contained |
| `GET` | `/api/chat/partners` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/chat/router.py` | matrix/suite | contained |
| `GET` | `/api/chat/unread` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/chat/router.py` | matrix/suite | contained |
| `GET` | `/api/cheers/` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/cheer/router.py` | matrix/suite | contained |
| `GET` | `/api/configs/` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/config/router.py` | matrix/suite | contained |
| `GET` | `/api/configs/{key}` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/config/router.py` | matrix/suite | contained |
| `GET` | `/api/daily-points/` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/daily_point/router.py` | matrix/suite | contained |
| `GET` | `/api/daily-points/range` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/daily_point/router.py` | matrix/suite | contained |
| `GET` | `/api/daily-points/summary` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/daily_point/router.py` | matrix/suite | contained |
| `GET` | `/api/daily-points/total-earned` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/daily_point/router.py` | matrix/suite | contained |
| `GET` | `/api/deductions/` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/deduction/router.py` | matrix/suite | contained |
| `GET` | `/api/feedbacks/` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/feedback/router.py` | matrix/suite | contained |
| `GET` | `/api/health` | none | `PUBLIC` | n/a | `app/main.py` | matrix/suite | contained |
| `GET` | `/api/level-tiers` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/level_tier/router.py` | matrix/suite | contained |
| `GET` | `/api/level-tiers/player/{player_id}` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/level_tier/router.py` | matrix/suite | contained |
| `GET` | `/api/login-logs/` | admin JWT | `ADMIN_ONLY` | managed target | `domains/login_log/router.py` | matrix/suite | contained |
| `GET` | `/api/mission-templates` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission_template/router.py` | matrix/suite | contained |
| `GET` | `/api/missions/` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/mission/router.py` | matrix/suite | contained |
| `GET` | `/api/missions/weekly` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/mission/router.py` | matrix/suite | contained |
| `GET` | `/api/missions/weekly-remaining` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/mission/router.py` | matrix/suite | contained |
| `GET` | `/api/notifications/` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/notification/router.py` | matrix/suite | contained |
| `GET` | `/api/players` | none | `PUBLIC` | n/a | `domains/player/router.py` | matrix/suite | contained |
| `GET` | `/api/players/me` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/player/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/deductions/{deduction_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/missions/{mission_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/missions/{mission_id}/status` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/notifications/read-all` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/notifications/{notification_id}/read` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/players/{player_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/players/{player_id}/lock` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/players/{player_id}/pin` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/admin/players/{player_id}/visibility` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PATCH` | `/api/deductions/{deduction_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/deduction/router.py` | matrix/suite | contained |
| `PATCH` | `/api/level-tiers/{tier_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/level_tier/router.py` | matrix/suite | contained |
| `PATCH` | `/api/mission-templates/{template_id}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission_template/router.py` | matrix/suite | contained |
| `PATCH` | `/api/missions/{mission_id}` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/mission/router.py` | matrix/suite | contained |
| `PATCH` | `/api/notifications/read-all` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/notification/router.py` | matrix/suite | contained |
| `PATCH` | `/api/notifications/{notification_id}/read` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/notification/router.py` | matrix/suite | contained |
| `PATCH` | `/api/players/{player_id}` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/player/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/daily-points/adjust` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/deductions` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/feedbacks/{feedback_id}/replies` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/missions` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/missions/bulk-approve` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/missions/clone` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/missions/clone-selected` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/missions/{mission_id}/revert` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/admin/notifications` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `POST` | `/api/auth/admin/login` | none | `PUBLIC` | n/a | `domains/auth/router.py` | matrix/suite | contained |
| `POST` | `/api/auth/login` | none | `PUBLIC` | n/a | `domains/auth/router.py` | matrix/suite | contained |
| `POST` | `/api/auth/logout` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/auth/router.py` | matrix/suite | contained |
| `POST` | `/api/chat/send` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/chat/router.py` | matrix/suite | contained |
| `POST` | `/api/cheers/` | admin JWT | `ADMIN_ONLY` | managed target | `domains/cheer/router.py` | matrix/suite | contained |
| `POST` | `/api/daily-points/` | admin JWT | `ADMIN_ONLY` | managed target | `domains/daily_point/router.py` | matrix/suite | contained |
| `POST` | `/api/deductions/` | admin JWT | `ADMIN_ONLY` | managed target | `domains/deduction/router.py` | matrix/suite | contained |
| `POST` | `/api/feedbacks/` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/feedback/router.py` | matrix/suite | contained |
| `POST` | `/api/feedbacks/replies` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/feedback/router.py` | matrix/suite | contained |
| `POST` | `/api/level-tiers` | admin JWT | `ADMIN_ONLY` | managed target | `domains/level_tier/router.py` | matrix/suite | contained |
| `POST` | `/api/mission-templates` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission_template/router.py` | matrix/suite | contained |
| `POST` | `/api/mission-templates/batch-delete` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission_template/router.py` | matrix/suite | contained |
| `POST` | `/api/mission-templates/batch-delete/preview` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission_template/router.py` | matrix/suite | contained |
| `POST` | `/api/mission-templates/generate` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission_template/router.py` | matrix/suite | contained |
| `POST` | `/api/missions/` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission/router.py` | matrix/suite | contained |
| `POST` | `/api/missions/batch-copy` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission/router.py` | matrix/suite | contained |
| `POST` | `/api/missions/copy` | admin JWT | `ADMIN_ONLY` | managed target | `domains/mission/router.py` | matrix/suite | contained |
| `POST` | `/api/missions/propose` | JWT | `AUTHENTICATED_SELF` | current actor | `domains/mission/router.py` | matrix/suite | contained |
| `POST` | `/api/notifications/` | admin JWT | `ADMIN_ONLY` | managed target | `domains/notification/router.py` | matrix/suite | contained |
| `POST` | `/api/players` | admin JWT | `ADMIN_ONLY` | managed target | `domains/player/router.py` | matrix/suite | contained |
| `PUT` | `/api/admin/cheers/{target_date}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PUT` | `/api/admin/configs/{key}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/admin/router.py` | matrix/suite | contained |
| `PUT` | `/api/configs/{key}` | admin JWT | `ADMIN_ONLY` | managed target | `domains/config/router.py` | matrix/suite | contained |
| `PUT` | `/api/level-tiers/bulk` | admin JWT | `ADMIN_ONLY` | managed target | `domains/level_tier/router.py` | matrix/suite | contained |

## Verification boundary

`tests/api/legacy_auth_boundary_test.py` proves the measured sensitive-route
subset: anonymous rejection, player A-to-B read/write rejection, administrator
cross-user success, chat pair filtering, and rejected-request DB invariants.
The 87-scenario synthetic suite and Playwright smoke suite protect existing
workflow compatibility. This matrix does **not** validate a family tenant model;
`PHASE1 FAMILY TENANT — NOT YET DEFINED` remains outside the current schema.
