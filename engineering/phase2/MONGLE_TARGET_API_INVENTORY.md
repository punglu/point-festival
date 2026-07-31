# MONGLE_TARGET_API_INVENTORY

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

This inventories what changes, what stays, and what is net-new in the API surface under the corrected Mongle framing. `MONGLE_BACKEND_API_CONTRACT_INVENTORY.md` (Axis A) remains the authoritative list of exact current routes/schemas; this document does not repeat every field, only the disposition per route group.

## Platform layer (Mongle) — KEEP_AS_IS, one net-new group

| Route group | Classification | Notes |
|---|---|---|
| `/api/account-context`, `/api/families/*` (13 routes) | KEEP_AS_IS | Already Group/Membership/Role-shaped; auth today runs through the legacy `get_current_user` (app.dependencies) only to resolve *which* Account is calling — the Group-scoped permission checks (`family.service.require_permission`) are already Mongle-native, not legacy. Only the outer JWT-verification step is legacy (see next section). |
| **Auth/Session** (login, refresh, logout, credential management) | **UNDECIDED — net-new** | Does not exist for Account today. Every current login route (`/api/auth/login`, `/api/auth/admin/login`) issues a JWT shaped around legacy identity (`sub`=player_id/admin_id, `role`=player/admin), never around Account/Membership. A Mongle-native login must exist before `/api/account-context` and friends can be reached without going through the legacy bridge first. Exact routes depend on PM_DECISION_REQUIRED #2 (Business Glossary) — not designed here. |

## Realtime messaging layer (와글와글) — KEEP_AS_IS, frontend wiring is the only real gap

All 16 Doran routes (`/api/families/{family_id}/doran/*`) are already Group/Membership-scoped, tested, and require no schema or contract change under the corrected framing — see `MONGLE_BACKEND_API_CONTRACT_INVENTORY.md`'s Doran section for the full list. The only gap is what was already found before this correction: zero frontend consumers, and no batch room-list-with-preview endpoint. Both remain valid Gaps under the *target* framing too (they are not legacy-vs-target disagreements — 와글와글 genuinely needs this wiring regardless of axis). Restated in `MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md`.

## MarkPoint-on-Mongle layer — auth dependency TRANSFORM, business endpoints REUSE_LOGIC_ONLY

Every current MarkPoint route (`/api/missions/*`, `/api/mission-templates/*`, `/api/level-tiers/*`, `/api/daily-points/*`, `/api/deductions/*`, `/api/cheers/*`, `/api/feedbacks/*`, `/api/notifications/*`, `/api/admin/*`) authorizes via legacy `PLAYER_ONLY`/`ADMIN_ONLY`/`ADMIN_JWT` dependencies (`app/dependencies.py` or `app/domains/auth/dependencies.py`) — never via a Group Role/Permission check. Under the target architecture, these need the same authorization pattern Doran already uses (`family.service.require_permission` against `markpoint.*` permission codes, which already exist in the seeded Role/Permission table — see Target User/Group/Role Matrix). This is a **TRANSFORM of the auth dependency only** — the route path, request/response schema, and underlying business logic (mission state machine, point ledger math, level calculation, cycle-range logic) are all `REUSE_LOGIC_ONLY`, unchanged.

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
