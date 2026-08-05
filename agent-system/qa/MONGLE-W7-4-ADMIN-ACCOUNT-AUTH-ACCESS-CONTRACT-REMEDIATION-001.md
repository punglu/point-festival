# QA Evidence — MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001

- Task ID: MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001
- Role: Developer self-check (Invariant 6: this session implemented the
  fix, so this is disclosed self-verification, not Independent QA).
- Independent from implementer: false
- Scope: DEFECT-001 and DEFECT-002 only, as raised by
  `MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001`.

## 1. Authority readback (before any edit)

`/admin`'s real backend surface (`/api/admin/*`, plus `require_admin`-gated
routes in `mission`/`deduction`/`config`/`cheer`/`daily_point`) recognizes
only a legacy `role=="admin"` JWT. There is no family-scoped RBAC concept
involved for this console at all — `useAdminData`/`adminApi.ts` call
exclusively `/api/admin/*`, 0 family-scoped/Account-native calls anywhere
in `AdminDashboard`'s own data layer. "Account-native user with real Admin
authority" can only mean: the same real person as an existing `admin_auth`
identity, now signed in through the newer Account-native login —
resolvable only via the existing `LegacyIdentityMapping` bridge
(`resolve_current_account` already uses it for `/api/account-context` and
Wagle). Not a new authority source; not family-admin treated as
service-admin.

`admin_auth` SSOT table (measured, not assumed):

| Login Type | Identity Source | Account Context Source | Admin Authority Source | Guard (before fix) | Guard (after fix) |
|---|---|---|---|---|---|
| Legacy Admin, valid `player_id` | `admin_auth` row via JWT `sub` | N/A (JWT `role=="admin"` decoded client-side) | `admin_auth` row itself | `require_admin`/`get_current_admin`: `role=="admin"` → pass | unchanged, same branch |
| Legacy Admin, null `player_id` | `admin_auth` row via JWT `sub` | `/api/account-context` crashed (DEFECT-002) | `admin_auth` row itself | `require_admin`/`get_current_admin`: same as above (unaffected by DEFECT-002, that bug was only in `_legacy_identity`) | unchanged for `/admin`; `/api/account-context` now returns clean 403 instead of crashing |
| Account-native, linked to an `admin_auth` row via `LegacyIdentityMapping` | `accounts` row + `legacy_identity_mappings` | `/api/account-context` (`is_admin` field, new) | the linked `admin_auth` row, resolved via the bridge | `require_admin`/`get_current_admin`: `role=="account"` always rejected (DEFECT-001) | `role=="account"` → resolve link → pass if linked |
| Account-native, family-owner only, 0 admin link | `accounts` row | `/api/account-context` (`is_admin: false`) | none | rejected (correctly) | rejected (still correctly — `is_admin: false`) |
| Account-native, unlinked, no family | `accounts` row | `/api/account-context` (`is_admin: false`) | none | rejected (correctly) | rejected (still correctly) |

## 2. Fresh reproduction (before any edit)

**DEFECT-002**: disposable `admin_auth` row, `player_id=NULL`. Token →
`GET /api/account-context` → `401 "유효하지 않은 레거시 인증입니다"`.
Matches the QA task's finding exactly. Root cause confirmed by code read:
`_legacy_identity`'s `if "player_id" in user:` tests key *presence*, and
`authenticate_admin` always includes the key (even as `None`), so
`int(str(None))` raises.

**DEFECT-001**: disposable Account-native account, linked via a new
`legacy_identity_mappings` row to a disposable `admin_auth` row. Real
`accountLogin()` (the only real login path) always sets `isAdmin: false`
in `useAuthStore`; `AdminProtectedRoute` gated on that flag alone →
`/admin` → `/` → `/dashboard` (which 404s for an Account-native session,
no `player` object). Matches the QA task's finding exactly.

## 3. Fixes applied

- `backend/app/domains/family/service.py`: `_legacy_identity` reordered —
  `role=="admin"` checked before the `player_id`-presence test. New
  `resolve_linked_admin_auth`/`is_account_linked_to_admin` helpers resolve
  an Account-native token to a linked `admin_auth` row via the existing
  bridge.
- `backend/app/dependencies.py`: `require_admin` widened to accept a
  linked Account-native token.
- `backend/app/domains/auth/dependencies.py`: `get_current_admin` (the
  **actual** guard on `/api/admin/*` — discovered mid-task to be a second,
  independently-duplicated legacy-only check, never routed through
  `require_admin` at all) widened the same way.
- `backend/app/domains/family/schema.py` + `router.py`:
  `AccountContextResponse.is_admin` (additive field), computed the same
  way, populated in the response.
- `frontend/src/App.tsx`: `AdminProtectedRoute` now accepts legacy
  `isAdmin` OR the new Account-native `is_admin` signal (with a real
  loading state while context resolves — no admin-content flash); non-admin
  Account session redirect fixed `/dashboard` (404-prone) → `/family`;
  `AuthPage`'s own `isLoggedIn` redirect corrected the same way. Legacy
  non-admin player sessions unchanged.
- `frontend/src/generated/openapi.d.ts`: regenerated (`pnpm run
  generate:api`), 5-line additive diff only (`is_admin` field).
- `frontend/src/shared/api/httpClient.ts` — **discovered necessary only
  once the route guard was reachable and testable**: `AdminDashboard`'s
  `MobileHeader` unconditionally polls `/api/chat/unread` (legacy-only,
  needs `player_id`), and the global 401-interceptor read that 401 as
  session-expired, force-logging-out an otherwise-correctly-authorized
  Account-native Admin (and, separately, a null-`player_id` legacy Admin —
  `get_current_chat_user` also 401s when `player_id` is absent) within
  ~1s of arriving at `/admin`. Fixed with a 1-line addition to the
  existing `OPTIONAL_ACCOUNT_ENDPOINTS` array (same precedented mechanism
  already used for `/api/me/wagle/` — a 401 from a decorative/optional
  feature must not end an otherwise-valid session). No new mechanism
  introduced.

## 4. Runtime verification — 5 required scenarios (real UI login)

All via real browser login through the actual forms (`/login` for
Account-native, `/` → "관리자 로그인" → username/password form for legacy),
not token injection, using disposable accounts:

- **A — Account-native Admin, linked** (`qa.remediation.account`, linked
  via `legacy_identity_mappings` to a disposable `admin_auth` row):
  login → `/family` (correct real home) → navigate `/admin` → reaches and
  stays (`is_admin: true` from `/api/account-context`, `/api/admin/players`
  etc. all 200) → deep-link `/admin/players` → holds → `page.reload()`
  (session restore) → holds → logout → token cleared, lands `/`. **PASS.**
- **B — legacy Admin, valid `player_id`** (`qa.remediation.validplayer`):
  login → `/admin` directly (unchanged legacy `isAdmin` branch) → reload
  → holds → logout → token cleared, lands `/`. Core access: 0 regression.
  (See §5 for the one pre-existing, unrelated data-loading gap found here.)
  **PASS.**
- **C — legacy Admin, null `player_id`** (`qa.remediation.nullplayer`):
  login → `/admin` → reaches and **stays** (previously would have hit the
  `chat/unread` forced-logout; now doesn't) → reload → holds.
  `/api/account-context` correctly returns `403 "계정 매핑이 필요합니다"`
  (clean categorization, not a crash, no fake identity assigned). **PASS.**

  **Endpoint-by-endpoint disambiguation (added after PM review flagged the
  401→403 text next to "reaches and stays" as reading like a contradiction
  — re-verified fresh with a new disposable null-`player_id` row,
  `id=8`, deleted immediately after; same result reproduced)**:
  `/api/account-context` final status = **403** (`계정 매핑이 필요합니다`
  — this admin_auth row has no `legacy_identity_mappings` link, a correct
  answer, not a bug); `/api/admin/players`, `/api/admin/notifications`,
  `/api/admin/missions` final status = **200** (all three, confirmed both
  via the page's own requests and a direct `fetch` issued in the browser
  context); `/admin` UI final entry = **reached and held**, both 2s after
  login and after a full `page.reload()`; the 403's target and reason =
  `/api/account-context` only, fired by `FamilyContextLoader` (mounted
  globally for *every* logged-in session, legacy Admin included) — it is
  not part of the `/admin` access gate at all, which for a legacy Admin is
  the client-decoded JWT `role=="admin"` claim (`useAuthStore.isAdmin`),
  entirely independent of `/api/account-context`; Admin session
  persistence = **held**, `sessionStorage.accessToken` present
  immediately after login, after a 2s settle window, and after reload —
  no forced logout at any point. Root cause of why these coexist without
  conflict: `/admin` route access and `/api/admin/*` data access for a
  legacy Admin never depend on `/api/account-context` at all — that call
  is an unrelated, incidental, globally-fired probe for an Account-native-
  only feature (family context) that this legacy identity was never
  expected to have, and returning 403 for it is the *correct*,
  DEFECT-002-fixed behavior, not evidence of a blocked session.

  **Scenario C supplemental verification (second PM review pass, a further
  disposable row, `id=9`, created for verification only and deleted
  immediately after — final residue 0)**:
  - `/api/account-context`: HTTP 403; expected `mapping_required` state
    (per `useFamilyContextStore`'s own status enum); no exception
    propagation; no retry loop; no crash.
  - Session behavior: access token present immediately after login;
    present at T+1.5s; present at T+5s; `mc_session_expired`
    (`sessionStorage`) remains `null` throughout; URL remains `/admin`
    throughout; `page.reload()` preserves both `/admin` and the token.
  - Admin APIs (all via the live token, both through the page's own
    requests and a direct in-page `fetch`): `players` 200, `notifications`
    200, `missions` 200, `login-logs` 200, `deductions` 200,
    `daily-points` (single endpoint) 200. `daily-points/range` is a
    separate, already-tracked open GAP
    (`API-W7-4-ADMIN-DASHBOARD-DAILY-POINTS-RANGE-PLAYER-ONLY-GAP-001`),
    not re-tested here.
  - Structural evidence (code, not just observed behavior): the global
    logout interceptor (`httpClient.ts`) reacts only to HTTP 401
    (`if (err.response?.status === 401)` — 403 never enters that branch);
    `FamilyContextLoader`'s own store (`useFamilyContextStore`) classifies
    HTTP 403 as `mapping_required`, a defined member of its own status
    enum, not an unhandled error; `/api/account-context`'s 403 is
    structurally independent of Admin authorization (different
    dependency, different router, different purpose).

  **Status**:
  - DEFECT-002: `FIXED` / `FOCUSED_RUNTIME_REVERIFIED` /
    `INDEPENDENT_QA_PENDING`.
  - `/api/account-context` 403 (for a legacy Admin with no
    `legacy_identity_mappings` link): `EXPECTED_NON_MAPPED_ACCOUNT_STATE`
    / `NOT_AN_ADMIN_ACCESS_FAILURE` / `NOT_A_SESSION_EXPIRY_TRIGGER`.
- **D — authenticated non-Admin** (`qa.remediation.familyadmin`: real
  family-owner role, 0 admin link, 0 markpoint roles): login → `/family`
  → navigate `/admin` → correctly denied, lands `/family`, 0 console
  errors. **PASS.**
- **E — unauthenticated**: direct navigation to `/admin` → correctly
  denied, lands `/`. Only 2 benign pre-login 401s from
  `/api/configs/level.thresholds` (`ProfileSelectorContainer` probes this
  regardless of auth state; self-redirects to the page already showing;
  confirmed unrelated to this task, present identically for any
  unauthenticated visit to `/`). **PASS.**

## 5. New defect found, explicitly NOT fixed (out of scope)

`GET /api/daily-points/range` (`get_current_player`/`require_self_player_id`,
requires `role=="player"` literally) returns `403` for **every** Admin
session — legacy valid-`player_id`, legacy null-`player_id`, and
Account-native alike, confirmed identical before and after this task's
changes (the endpoint and its dependencies were untouched). Caught by
`useAdminData.ts`'s own `try/catch` (console-logged, not fatal) — does not
block `/admin` access, does not force logout (403, not 401) — but the
Admin dashboard's weekly point-chart widget is permanently empty for any
Admin today. Pre-existing, unrelated to DEFECT-001/002's identity-
resolution/route-guard scope; fixing it would mean redesigning how the
Admin dashboard is authorized to read player data — out of proportion for
this "minimal, non-RBAC-redesigning" remediation. Tracked as
`API-W7-4-ADMIN-DASHBOARD-DAILY-POINTS-RANGE-PLAYER-ONLY-GAP-001` in the
Coverage Map. Recommends a dedicated follow-up task.

## 6. Security checks

- Client-state tampering: `isAdmin` alone is no longer sufficient for an
  Account-native session (it's always `false` for `accountLogin`); the
  real signal (`is_admin` from `/api/account-context`) is server-computed,
  not settable from the client. A family-owner-only Account-native session
  (Scenario D) was confirmed denied both server-side (`/api/admin/players`
  → 401 via curl) and client-side.
- URL-only entry: unauthenticated direct navigation to `/admin/players`
  redirects to `/` (Scenario E-equivalent deep-link check).
- family-admin ≠ service-admin: confirmed via curl — a real family-owner
  role (Scenario D's account) gets `is_admin: false` and `401` from
  `/api/admin/players`, despite holding real family-scoped permissions.
- Pre-context-load flash-of-admin-UI: `AdminProtectedRoute` shows an
  explicit loading state (`aria-busy`) while `contextStatus` is
  `idle`/`loading`, never renders Admin content before the server
  confirms `is_admin`.
- Backend API authorization sample-verified directly (not just the FE
  guard): `/api/admin/players` returns `401` for both an unlinked
  Account-native session and a family-owner-only Account-native session,
  `200` only for the linked one — confirmed via curl with real tokens for
  all three.

## 7. Validation run

- `pnpm run lint`: clean.
- `pnpm run build` (`tsc -b && vite build`): clean.
- `git diff --check`: clean (exit 0).
- `python3 agent-system/tools/check_all.py`: clean (report-only mode, 0
  new warnings under this Task ID).
- 3-viewport check (390×844, 820×1180, 1180×820) on `/admin`: 0 horizontal
  overflow, 0 page errors, content renders, at all 3.
- Regression smoke (`/login`, `/`, `/family`, `/markpoint`, `/wagle`,
  `/admin`, unauthenticated baseline): all correctly bounce to `/`, 0 page
  errors.
- Backend pytest: **BLOCKED**. This WSL session has no Docker installed
  (`docker: command not found`); the isolated test DB
  (`docker-compose.phase2.yml`, `127.0.0.1:15435`) required by
  `tests/conftest.py` is unreachable. Pre-existing environment constraint
  (confirmed via prior-session memory: the main dev environment is
  Mac/OrbStack, not this WSL session), not something introduced or
  fixable within this task's scope. Substituted with the extensive
  live-curl verification in §1, §4, §6 above, run against the actual
  running dev backend (`uvicorn`, `:8000`) with real disposable accounts
  covering every identity permutation.

## 8. DB safety / cleanup

Disposable rows created (all additive, exact PKs recorded): `admin_auth`
ids 4/5/6, `legacy_identity_mappings` id 2, `players` id 6, `accounts` ids
8/9/10 + their `family_groups` (7/8), `family_memberships`,
`membership_role_assignments`, `account_credentials`, `account_sessions`,
1 `service_subscriptions` row. All deleted via ID-scoped `DELETE` in
FK-safe order after verification completed. Final state independently
re-queried and confirmed to match the true pre-task baseline: `admin_auth`
= only `dad`/`mom` (ids 1/2); `players` = only ids 1-4; `accounts` = 0
rows; `family_groups` = 0 rows; `legacy_identity_mappings` = 0 rows. No
destructive seed script used (`phase1_seed_synthetic.py` never touched).
All disposable `*.local.py` (backend) / `*.local.mjs` (`tests/e2e/`)
scripts removed; confirmed via a final `git status` showing 0 stray files.

## 9. Verdict

**Developer self-check: PASS**, within this task's declared minimal
scope. Both DEFECT-001 and DEFECT-002 reproduced fresh, fixed, and
runtime-verified across all 5 required scenarios plus logout/deep-link/
session-restore/3-viewport/regression-smoke. One new, pre-existing,
out-of-scope defect found and disclosed, not fixed
(`API-W7-4-ADMIN-DASHBOARD-DAILY-POINTS-RANGE-PLAYER-ONLY-GAP-001`).
Backend pytest BLOCKED by a pre-existing environment constraint, not this
task's own regression — substituted with live-API verification.

Per Invariant 6, this session cannot self-award Independent QA PASS. This
verdict is `DEVELOPER_SELF_CHECK_COMPLETE` /
`FOCUSED_RUNTIME_VERIFICATION_COMPLETE` /
`READY_FOR_FOCUSED_INDEPENDENT_QA` only — explicitly NOT
`INDEPENDENT_QA_PASS`, `W7_4_CLOSED`, or `W7_6_READY`.
