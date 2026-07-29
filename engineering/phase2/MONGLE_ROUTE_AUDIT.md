# MONGLE_ROUTE_AUDIT

TASK ID: MONGLE-FE-ROUTE-ALIGNMENT-001 — Wave 2
**No product code was modified in this wave.** Every row below traces to a specific file/line read directly this session.

> **Namespace rename note (MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001, added after this document was written):** `NaranAppShell` → `MongleAppShell` (component/file/CSS module/`data-testid`), and `tests/e2e/specs-naran/` → `tests/e2e/specs-mongle/`, `playwright.naran.config.ts` → `playwright.mongle.config.ts`. Citations below are as-observed at write time and not retroactively updated — see `MONGLE_TECHNICAL_NAMESPACE_ALIGNMENT_REPORT.md`. Route strings (`/naran/doran`, `/naran/family`) are unaffected and remain accurate.

## 1. Current route tree (top-level, `frontend/src/App.tsx`)

```
/                    → AuthPage (no shell wrap, no guard)
/dashboard           → ProtectedRoute → NaranAppShell → UserDashboard
/admin/*             → AdminProtectedRoute → NaranAppShell → AdminDashboard
                         ├─ (index)        → DashboardView
                         ├─ missions       → MissionView
                         ├─ points         → PointView
                         ├─ players        → PlayerView
                         ├─ chat           → ChatView (legacy ChatModal, embedded)
                         ├─ notifications  → NotificationView
                         ├─ config         → ConfigView
                         └─ *              → Navigate to /admin (replace)
/naran/doran         → ProtectedRoute → NaranAppShell → DoranLanding (Room List + Conversation)
/naran/family        → ProtectedRoute → NaranAppShell → AccessBoundary(family.read) → FamilyLanding
```

**No top-level wildcard/404 route exists.** Any path outside the five registered top-level routes (e.g. `/foo`, `/naran/points`) renders a blank page — React Router v6 matches nothing and renders `null`. This is a genuine gap, not assumed: verified by reading the full `<Routes>` block in `App.tsx`, which contains no `path="*"`.

## 2. Full findings table

| Source file | Line/Component | Current path | Trigger | Destination | User visible | Status | Evidence | Required action |
|---|---|---|---|---|---|---|---|---|
| `App.tsx` | Route `/` | `/` | direct nav | `AuthPage` | Yes (login screen) | ACTIVE_USER_ROUTE | read directly | none |
| `App.tsx` | Route `/dashboard` | `/dashboard` | direct nav / post-login | `NaranAppShell`→`UserDashboard` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `App.tsx` | Route `/admin/*` | `/admin/*` | direct nav / post-admin-login | `NaranAppShell`→`AdminDashboard` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `App.tsx` | Route `/naran/doran` | `/naran/doran` | Dock/nav click | `NaranAppShell`→`DoranLanding` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `App.tsx` | Route `/naran/family` | `/naran/family` | Dock/nav click | `NaranAppShell`→`AccessBoundary`→`FamilyLanding` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `App.tsx` | (absent) | any unmatched path | direct nav / typo / stale link | blank page (no match) | Yes (blank screen) | **BROKEN_TARGET (systemic — no catch-all)** | no `path="*"` in Routes | add a 404/fallback route (Wave 4 candidate) |
| `AdminDashboard/index.tsx` | nested Routes | `/admin` (index) | — | `DashboardView` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `AdminDashboard/index.tsx` | nested Routes | `/admin/missions` | Dock/link | `MissionView` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `AdminDashboard/index.tsx` | nested Routes | `/admin/points` | Dock/link | `PointView` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `AdminDashboard/index.tsx` | nested Routes | `/admin/players` | link (Sidebar/Drawer) | `PlayerView` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `AdminDashboard/index.tsx` | nested Routes | `/admin/chat` | `MobileHeader` button | `ChatView` (legacy `ChatModal`, embedded) | Yes | ACTIVE_USER_ROUTE | read directly | see §5, two parallel chat systems |
| `AdminDashboard/index.tsx` | nested Routes | `/admin/notifications` | bell icon | `NotificationView` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `AdminDashboard/index.tsx` | nested Routes | `/admin/config` | Sidebar/Drawer link | `ConfigView` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `AdminDashboard/index.tsx` | nested `*` | any unmatched `/admin/*` | — | `Navigate to /admin` | Yes | REDIRECT_ALIAS (correct, already handled) | read directly | none |
| `pages/Auth/components/PinInputView.tsx:58` | `navigate(...)` | login submit | PIN success | `res.is_admin ? '/admin' : '/dashboard'` | Yes | ACTIVE_USER_ROUTE | read directly | none — matches registered routes |
| `pages/Auth/components/AdminLoginView.tsx:37` | `navigate(...)` | admin login submit | success | `/admin` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `NaranAppShell.tsx:106` | `<Link>` | brand logo | click | `/dashboard` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `NaranAppShell.tsx:117` | `<NavLink>` desktop nav (5 items) | `/dashboard`, `/naran/doran`, `/naran/family`, `/admin/missions`, `/admin/points` | click, filtered by `visible`/permission | matches registered routes | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `NaranAppShell.tsx:143-151` | mobile Dock (3 items, hardcoded array) | `/dashboard`, `/naran/doran`, `/naran/family` | tap | matches registered routes | Yes | ACTIVE_USER_ROUTE + **DOCK_TARGET note** | read directly, own code comment cites `PM_DECISION_REQUIRED_BOTTOM_DOCK_ROUTE` | see §4 |
| `NaranAppShell.tsx:60,97` / `UserDashboard/index.tsx:87` / `MobileHeader.tsx:21` / `Sidebar.tsx:45` / `MobileDrawer.tsx:36` | `navigate('/')` | logout / session-expired | logout | `/` | Yes | ACTIVE_USER_ROUTE | read directly, consistent across 5 call sites | none |
| `MobileHeader.tsx:56` / `Sidebar.tsx:57` | `navigate('/admin')` | brand click (admin surface) | click | `/admin` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `MobileHeader.tsx:61` | `navigate('/admin/chat')` | 채팅 button | click | `/admin/chat` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `AdminLayout.tsx:28` | `navigate('/admin/notifications')` | bell click | click | `/admin/notifications` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `NotificationItem.tsx:35` | `navigate(...)` | notification row click | click | `` /admin/missions?date=${date} `` | Yes | ACTIVE_USER_ROUTE | read directly | none — query param used correctly |
| `DashboardView.tsx:53`, `PendingMissionCard.tsx:31` | `navigate('/admin/missions')` | button click | click | `/admin/missions` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `RecentAlerts.tsx:48` | `navigate('/admin/notifications')` | button click | click | `/admin/notifications` | Yes | ACTIVE_USER_ROUTE | read directly | none |
| `RecentAlerts.tsx:61` | `navigate(inferRoute(n))` | alert row click | click | dynamic, derived from notification type | Yes | **UNKNOWN_REQUIRES_EVIDENCE** | `inferRoute()` helper not yet read in this pass | out of this wave's scope (not user-visible-naming or Dock-related); flag for Wave 4 if it touches Doran/Room targets |
| `DoranLanding.tsx:170-186` | `setSearchParams`/`navigate(-1)` | room select / back | in-page state | `?room=<id>` query param on `/naran/doran` | Yes | ACTIVE_USER_ROUTE (query-param sub-state, not a new route) | read directly | Room List → Room transition confirmed working via query param, not a separate path |
| `httpClient.ts:35` | `window.location.href = '/'` | 401 response interceptor | any API 401 | `/` | Yes (forced reload) | ACTIVE_USER_ROUTE | read directly | none |
| `nginx.conf` | `location / { try_files $uri $uri/ /index.html; }` | any path, direct access/refresh | server | serves `index.html` (SPA) | N/A (infra) | ACTIVE_INTERNAL_ROUTE (SPA fallback, correct) | read directly | none — but see §1, FE itself has no route-level 404 once index.html loads |
| `nginx.conf` | `location ~ ^/api/families/[^/]+/doran/service/actions$` | — | backend proxy | `backend:8000` | No | API_PATH_NOT_FE_ROUTE, INTERNAL_IDENTIFIER_NOT_USER_VISIBLE | read directly | none — internal `doran` API path, not renamed per PM directive |
| `vite.config.ts` | dev proxy `/api` | — | dev only | `VITE_DEV_PROXY_TARGET` or `localhost:8000` | No | API_PATH_NOT_FE_ROUTE | read directly | none |
| `tests/e2e/specs-naran/01-shell.spec.ts` | multiple | `/`, `/naran/doran`, `/naran/family` | E2E navigation | matches registered routes | test-only | ACTIVE_INTERNAL_ROUTE (test) | read directly | one assertion (`heading name: '와글와글'`) is naming-sensitive — see Wave 3 |

## 3. Required distinctions (per task instruction)

1. **User screen URL**: `/`, `/dashboard`, `/admin`, `/admin/missions`, `/admin/points`, `/admin/players`, `/admin/chat`, `/admin/notifications`, `/admin/config`, `/naran/doran` (+`?room=`), `/naran/family`. All 11 confirmed live and reachable.
2. **Frontend internal route/component name**: `AuthPage`, `UserDashboard`, `AdminDashboard`, `DoranLanding`, `FamilyLanding`, `NaranAppShell`, `AccessBoundary` — none of these names are ever rendered to a user.
3. **API endpoint**: `/api/auth/login`, `/api/chat/unread`, `/api/families/{id}/doran/service/actions`, `/api/account-context`, etc. — distinct namespace from FE routes, not touched.
4. **Backend domain name**: `doran` (Python package `backend/app/domains/doran/`) — internal only.
5. **File/module path**: `platform/pages/DoranLanding.tsx`, `platform/doran/**` — internal only.
6. **Dock service key**: `service_code === 'doran'` (checked in `useFamilyContextStore.serviceStatus`) — internal only, drives the `disabled` empty-state on `/naran/doran`, not a display string.
7. **Screen design ID** (from the reference package, e.g. `1d`, `2u`): a design-tracking label only — confirmed nowhere in the codebase is a screen ID used as a route path, prop, or key. No accidental conflation found.

## 4. Dock current destinations (verbatim from code)

| Dock slot (current, hardcoded 3-item array, `NaranAppShell.tsx:143-151`) | Label shown | Destination |
|---|---|---|
| 1 | 마크포인트 | `/dashboard` |
| 2 | 와글와글 | `/naran/doran` |
| 3 | 가족 | `/naran/family` |

The shell's own code comment (lines 132-141) explicitly documents that this is a **known, PM-flagged gap**: the approved mockup's 4-slot Dock (홈/포인트잔치/대화/나) has no corresponding routes today, and the team deliberately did not invent new routes/icons for 홈 or 나 (tagged `PM_DECISION_REQUIRED_BOTTOM_DOCK_ROUTE` in-code, matching the prior session's `DOCK_EXISTING_CONTRACT_AUDIT.md` finding that no per-user Dock configuration backend exists either). **This audit does not resolve that gap** — it is carried forward to Wave 4 as a known, pre-existing, PM-level open item, not something this Wave decides.

## 5. Two parallel, non-unified chat/messaging systems (significant finding)

This session found the product currently ships **two structurally separate messaging implementations**, not one:

| | Legacy chat | New Doran/Room-List chat |
|---|---|---|
| Entry points | `/dashboard`'s header 💬 button (`UserDashboard/index.tsx:108`); `/admin/chat` (`ChatView.tsx`) | Dock "와글와글" item → `/naran/doran` (`DoranLanding.tsx`) |
| Component | `shared/components/ChatModal` (overlay on `/dashboard`, embedded on `/admin/chat`) | `DoranLanding` (Room List + Conversation), `platform/doran/components/*` |
| Data source | **Real API** — `GET /api/chat/unread`, per `CLAUDE.md`'s documented `P-FEATURE-CHAT-001` (`chat_messages` table) | **Fixture only** — `doranPreviewRooms`/`doranPreviewMessagesByRoom` from `platform/doran/preview/`; the page itself renders `"UX Gate 미리보기 · 실제 API 연결 전 화면입니다."` in dev mode (`DoranLanding.tsx:250-252`), confirming no live API wiring yet despite the backend's `doran` domain (rooms/messages/participants) existing per `all_models.py` |
| Room concept | None (1:1 player↔player/admin only, no GROUP/DIRECT/SERVICE distinction) | GROUP/DIRECT/SERVICE room kinds, Room List → Conversation flow |

**This is not something this wave resolves or unifies** — Wave 4's PM directive is explicit that "가족 홈의 '몽글' 진입은 Room List를 향한다" and "Dock의 대화 서비스도 Room List를 향한다," which already point to the **new** Doran/Room-List system as the intended target, not the legacy `ChatModal`. This audit flags the coexistence as a fact, not a defect to fix in this task.

## 6. Direct-access / refresh / broken-link results

- **Direct URL access**: works for all 5 top-level routes (SPA fallback via nginx `try_files`, confirmed in config) — reaching `AuthPage`/`ProtectedRoute` guards correctly (redirect to `/` if not logged in, per `ProtectedRoute`/`AdminProtectedRoute`).
- **Browser refresh**: same mechanism — nginx serves `index.html` regardless of path, React Router then re-resolves client-side. No server-side session loss beyond normal `sessionStorage`/store rehydration (not audited further — out of this wave's route-focused scope).
- **Broken/orphan internal links**: **0 found.** Every `navigate()`/`<Link>`/`<NavLink>` target inspected in §2 resolves to a route actually registered in `App.tsx` or `AdminDashboard/index.tsx`. This is a positive finding, not assumed — every target was cross-checked against the registered route list.
- **Unmatched-path behavior**: confirmed blank page (see §1) — this is the one genuine gap found.
- **Relative vs. absolute paths**: all `navigate()`/`to=` values found use absolute paths (leading `/`); no relative-path bugs found.
- **URL/internal-domain-name coupling**: none found — no code constructs a route path by concatenating a domain name or the internal `doran` identifier into something user-visible.

## 7. Test impact of any future route change

- `tests/e2e/specs-naran/01-shell.spec.ts` navigates to `/`, `/naran/doran`, `/naran/family` directly and asserts on `page.getByRole('heading', { name: '와글와글' })` and `getByRole('navigation', { name: /몽글 (서비스 탐색|모바일 탐색)/ })`. Any Wave 3/4 change to the "와글와글" display text (see naming inventory) or to the `/naran/doran` path itself would require updating this spec — flagged for Wave 3/4, not changed in this wave.
- No other E2E spec files exist under `tests/e2e/specs-naran/` (only this one file).

## 8. nginx/Vite impact of any future route change

- `nginx.conf`'s SPA fallback (`location /`) is path-agnostic — adding, renaming, or aliasing a client-side route requires **no nginx change** as long as the new path still falls under `/`. Only a change to the API proxy paths (`/api/...`, including the `doran`-specific rate-limit block) would need an nginx edit, and this task does not touch API paths.
- `vite.config.ts` has no `base` override (defaults to `/`) and no route-related config — unaffected by any FE-only route change.

## 9. Wave 2 Gate

- Route definitions: fully enumerated (top-level + nested admin routes).
- Route call sites: fully enumerated (`navigate`, `Link`, `NavLink`, `window.location`, form-submit redirects).
- Dock destinations: enumerated and cross-referenced against the pre-existing PM-flagged gap.
- Broken/orphan/duplicate classification: 0 broken, 0 orphan, 0 duplicate found among registered-route targets; 1 systemic gap (no top-level 404) found and classified.
- API path vs. FE path: separated throughout (see §3).
- Product code modified: **0 files.**
- `MONGLE_ROUTE_AUDIT.md` written: this file.

**Verdict: PASS** (one non-blocking systemic gap — missing top-level 404/fallback route — carried to Wave 4 as a candidate minimal fix, not a blocker for proceeding to Wave 3).
