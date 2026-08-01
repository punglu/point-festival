# MONGLE_TARGET_API_INVENTORY

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

This inventories what changes, what stays, and what is net-new in the API surface under the corrected Mongle framing. `MONGLE_BACKEND_API_CONTRACT_INVENTORY.md` (Axis A) remains the authoritative list of exact current routes/schemas; this document does not repeat every field, only the disposition per route group.

## Platform layer (Mongle) — KEEP_AS_IS, one net-new group

| Route group | Classification | Notes |
|---|---|---|
| `/api/account-context`, `/api/families/*` (13 routes) | KEEP_AS_IS | Already Group/Membership/Role-shaped; auth today runs through the legacy `get_current_user` (app.dependencies) only to resolve *which* Account is calling — the Group-scoped permission checks (`family.service.require_permission`) are already Mongle-native, not legacy. Only the outer JWT-verification step is legacy (see next section). |
| **Auth/Session** | **IMPLEMENTED (Wave 1)** | Shipped as the routes below. Account-level per D7, so they do not sit under `/families/{familyId}/...`. None of them consults `LegacyIdentityMapping`; the legacy `/api/auth/login` and `/api/auth/admin/login` routes are untouched and remain legacy-only. |

### Account-native Auth/Session routes (Wave 1)

Implemented in `backend/app/domains/family/router.py`; authorization
dependencies in `backend/app/domains/family/dependencies.py`. Access tokens
carry `role="account"`, a value the legacy player/admin dependencies do not
accept and which the Account dependency requires — so neither token type can be
used against the other's routes.

| Route | Method | Actor | Scope | Notes |
|---|---|---|---|---|
| `/api/auth/account/login` | POST | anonymous | account | 아이디 + 플랫폼 비밀번호. Returns access + refresh token, `is_password_change_required`. Unknown-username and wrong-password responses are byte-identical to prevent user enumeration. Lockout after `ACCOUNT_MAX_LOGIN_ATTEMPTS` |
| `/api/auth/account/refresh` | POST | refresh-token bearer | account | Rotates: the presented row is revoked and a new one issued in one transaction, so replay of the old token is rejected |
| `/api/auth/account/logout` | POST | account | account | Revokes only the calling Session; other devices stay signed in |
| `/api/me` | GET | account | account | Current Account plus the server-derived `AuthorizedFamilySet`, each entry with its roles and effective permissions |
| `/api/me/password` | POST | account | account | Self-service change; revokes every Session including the caller's |
| `/api/me/sessions` | GET | account | account | Live sessions for the calling Account |
| `/api/me/devices/{device_id}` | DELETE | account | account | Device unlink — revokes every live Session for that device |
| `/api/families/{family_id}/member-accounts` | POST | FamilyAdmin | family | Provisions an independent Account + Membership + initial credential in one transaction. Requires `family.members.provision` **in the path family**, so cross-family attempts are denied before the handler body runs. Returns the initial password exactly once |

A revoked Session is rejected immediately even while its access token is still
within its TTL, because the dependency validates the Session row on every
request rather than trusting the JWT alone.

## Realtime messaging layer (와글와글) — KEEP_AS_IS, frontend wiring is the only real gap

All 16 Wagle routes (`/api/families/{family_id}/wagle/*`) are already Group/Membership-scoped, tested, and require no schema or contract change under the corrected framing — see `MONGLE_BACKEND_API_CONTRACT_INVENTORY.md`'s Wagle (historically Doran) section for the full list. The only gap is what was already found before this correction: zero frontend consumers, and no batch room-list-with-preview endpoint. Both remain valid Gaps under the *target* framing too (they are not legacy-vs-target disagreements — 와글와글 genuinely needs this wiring regardless of axis). Restated in `MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md`.

### Wave 2 additions (2026-08-01, `MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001`)

| Route | Method | Actor | Scope | Notes |
|---|---|---|---|---|
| `/api/families/{family_id}/wagle/room-summaries` | GET | family member (`wagle.messages.read`) | family | Batch room list: each room with its last visible message preview and the caller's unread count, in one round trip. Closes the "no batch room-list-with-preview endpoint" gap noted above. Added **alongside** `/rooms` rather than replacing it, so existing callers that only need room identity are unaffected. A deleted last message keeps its list slot but surrenders its body, matching the per-message tombstone rule. |

`POST /rooms/{room_id}/messages` is unchanged in request/response shape, but its
transaction now also appends a `service_outbox_events` row
(`owner_service="wagle"`, `event_type="wagle.message.created"`,
`aggregate_type="wagle_message"`, v1) so a persisted message always has its
delivery event. **Consuming** that event — WebSocket broadcast, Web Push —
remains Wave 3 and is not implemented. No user-facing `DELIVERED` state was
introduced.

Naming: the whole runtime is Wagle as of migration `0007` — route prefix
`/api/families/{familyId}/wagle/...`, permission codes `wagle.*`, service code
`wagle`, tables `wagle_*`. The historical `/doran/` prefix is no longer served
and returns 404; no alias or fallback was kept.

## MarkPoint-on-Mongle layer — auth dependency TRANSFORM, business endpoints REUSE_LOGIC_ONLY

Every current MarkPoint route (`/api/missions/*`, `/api/mission-templates/*`, `/api/level-tiers/*`, `/api/daily-points/*`, `/api/deductions/*`, `/api/cheers/*`, `/api/feedbacks/*`, `/api/notifications/*`, `/api/admin/*`) authorizes via legacy `PLAYER_ONLY`/`ADMIN_ONLY`/`ADMIN_JWT` dependencies (`app/dependencies.py` or `app/domains/auth/dependencies.py`) — never via a Group Role/Permission check. Under the target architecture, these need the same authorization pattern Wagle already uses (`family.service.require_permission` against `markpoint.*` permission codes, which already exist in the seeded Role/Permission table — see Target User/Group/Role Matrix). This is a **TRANSFORM of the auth dependency only** — the route path, request/response schema, and underlying business logic (mission state machine, point ledger math, level calculation, cycle-range logic) are all `REUSE_LOGIC_ONLY`, unchanged.

| Current route group | Business logic classification | Auth dependency classification | Evidence |
|---|---|---|---|
| `/api/missions/*` (9 routes) | REUSE_LOGIC_ONLY | TRANSFORM (`PLAYER_ONLY`/`ADMIN_ONLY` -> `markpoint.missions.manage`/`markpoint.own.read` permission check) | `mission/router.py` |
| `/api/mission-templates/*` (8 routes) | REUSE_LOGIC_ONLY | TRANSFORM | `mission_template/router.py` |
| `/api/level-tiers/*` (6 routes) | REUSE_LOGIC_ONLY (the hybrid auto-extension calculation is pure, identity-agnostic math) | TRANSFORM | `level_tier/router.py` |
| `/api/daily-points/*` (5 routes) | REUSE_LOGIC_ONLY | TRANSFORM | `daily_point/router.py` |
| `/api/deductions/*` (4 routes) | REUSE_LOGIC_ONLY | TRANSFORM | `deduction/router.py` |
| `/api/cheers/*` (2 routes) + `/api/admin/cheers/{date}` | REUSE_LOGIC_ONLY, plus the Table Dictionary's `family_group_id` scope addition | TRANSFORM | `cheer/router.py` |
| `/api/feedbacks/*` (3 routes) | REUSE_LOGIC_ONLY | TRANSFORM | `feedback/router.py` |
| `/api/notifications/*` (4 routes) | REUSE_LOGIC_ONLY | TRANSFORM | `notification/router.py` |
| `/api/admin/*` (31 routes, all delegate to the above domains' services) | REUSE_LOGIC_ONLY | TRANSFORM (today: blanket `ADMIN_JWT`; target: presumably `mission_manager`/`point_admin`-class permission checks per sub-route, mirroring the Group model rather than a single global admin flag) — **exact target permission-per-route mapping is `PM_DECISION_REQUIRED`, not invented here** | `admin/router.py` |
| `/api/configs/*` | REUSE_LOGIC_ONLY (generic key-value mechanism, identity-agnostic already) | UNDECIDED — likely stays legacy-shaped or becomes Group-scoped config (e.g. per-Group `point_cycle`); not decided | `config/router.py` |
| `/api/login-logs/*` | REFERENCE_ONLY (an audit log of legacy PIN attempts specifically — its target-axis equivalent would be a Session/Auth audit log once that exists, not a direct carry-over) | n/a | `login_log/router.py` |
| `/api/chat/*` (legacy 1:1) | DEPRECATE_CANDIDATE (superseded by 와글와글/Doran's DIRECT room type) | n/a | `chat/router.py` |
| `/api/players/*`, `/api/auth/*` | REFERENCE_ONLY for UX (see Legacy-to-Target Mapping) | n/a — superseded by Account/Auth once built | `player/router.py`, `auth/router.py` |

**Not decided here**: the exact new route paths/prefixes for a re-hosted MarkPoint API (e.g. whether `/api/missions` stays as-is with a changed auth dependency, or moves under `/api/families/{family_id}/markpoint/missions` to match Doran's own URL-scoping convention). Both are structurally reasonable; PM should decide which convention MarkPoint follows before any TRANSFORM work starts, since this affects every route path, not just auth.
