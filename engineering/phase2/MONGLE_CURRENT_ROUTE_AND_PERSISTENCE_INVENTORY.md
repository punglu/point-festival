# MONGLE_CURRENT_ROUTE_AND_PERSISTENCE_INVENTORY

TASK ID: MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-DESIGN-001
**READ-ONLY.** No source/config/test modified while producing this document. Every row traces to a file/line read directly this session.

> **Implementation update (MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001):** the `/naran/doran` and `/naran/family` rows in §1 are now superseded for "current state" purposes — canonical `/wagle`/`/family` routes exist and are what internal navigation produces; the two `/naran/*` rows now describe **compatibility alias** behavior (redirect, not direct render). See `MONGLE_ROUTE_AND_STORAGE_COMPATIBILITY_MATRIX.md` for the current mapping. §5's storage contract is similarly superseded: `naran.activeFamily.*` is now read-only (legacy fallback), `mongle.activeFamily.*` is the canonical key. This inventory's original content is left as-is below since it accurately reflects the pre-migration baseline this task started from.

## 1. Route inventory

| current path | route owner | user-visible name | internal domain | entry source | auth requirement | family requirement | redirect behavior | deep-link behavior | refresh behavior | Back behavior | E2E coverage | external dependency | migration risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/` | `App.tsx:46` (`<Route path="/">`) | 로그인/프로필 선택 | `AuthPage` | direct entry, logout targets, 401 interceptor, `<Link>` from 404 page | None (public) | None | If `isLoggedIn`, client-side `<Navigate to={isAdmin?'/admin':'/dashboard'} replace/>` (`pages/Auth/index.tsx:32`) | Works — always resolves via SPA fallback | Works, re-evaluates `isLoggedIn` fresh from `sessionStorage` on mount | Normal (no loop) | `specs-mongle/01-shell.spec.ts` — indirect only, every test's `loginAsFirstPlayer()` helper starts here | nginx SPA fallback, PWA `start_url` | **LOW-MEDIUM** — root path, is the PWA install entry point and every unauthenticated redirect target |
| `/dashboard` | `App.tsx:56` | (no distinct visible title beyond page content — "포인트 잔치" header inside `UserDashboard`) | `UserDashboard` (legacy MarkPoint) | Dock/desktop-nav "마크포인트", `<Link>` brand logo in Shell, post-PIN-login `navigate()`, 5 logout call sites | `ProtectedRoute` (`isLoggedIn`) | None (works with no Family selected) | Unauthenticated → `<Navigate to="/" replace/>` | Works | Works | Normal | `01-shell.spec.ts` (`toHaveURL(/dashboard/)` assertions, 3 tests) | none beyond SPA fallback | **MEDIUM** — `isLegacyDashboard` boolean in Shell (`location.pathname === '/dashboard'`) branches layout/Dock-hiding logic; string is checked, not a route constant |
| `/admin/*` | `App.tsx:66`, nested router in `pages/AdminDashboard/index.tsx` | 관리자 화면 (7 sub-views) | `AdminDashboard` | Dock/desktop-nav "미션 관리"/"포인트 관리", Sidebar/MobileDrawer/MobileHeader nav, several `navigate('/admin/...')` call sites (11+ found) | `AdminProtectedRoute` (`isLoggedIn && isAdmin`) | None | Unauthenticated/non-admin → `<Navigate to="/" replace/>`; unmatched nested path → `<Navigate to="/admin" replace/>` (`AdminDashboard/index.tsx:22`) | Works for all 7 sub-paths | Works | Normal | Not covered by `specs-mongle/01-shell.spec.ts` (that suite doesn't log in as admin) | none beyond SPA fallback | **MEDIUM** — 7 nested sub-paths, `isAdminSurface` boolean (`location.pathname.startsWith('/admin')`) in Shell, `AdminLayout` also reads `location.pathname` for its own Sidebar highlighting |
| `/naran/doran` | `App.tsx:75` | 와글와글 (Room List / Conversation) | `DoranLanding`, `platform/doran/**` | Dock/desktop-nav "와글와글" | `ProtectedRoute` | Implicit — page renders its own "가족을 선택해주세요" state when no Family active, not a route guard | Unauthenticated → `<Navigate to="/" replace/>` | Works; `?room=<id>` query sub-state also survives direct entry | Works, but note: on ≥701px viewport, first `normal`-state load auto-selects the first room via `setSearchParams({room:...}, {replace:true})` — a one-time internal redirect, not a route change | Normal; explicit `navigate(-1)` used for the mobile "back to room list" gesture when the room was reached via a *pushed* history entry (`pushedSelectionRef`) | 2 of the 6 `01-shell.spec.ts` tests, plus 1 test in `MONGLE-E2E-DORAN-SUBSCRIPTION-SEED-ALIGNMENT-001`'s manual verification | `serviceStatus('doran')` reads `naran.activeFamily.*`-selected Family's service list (backend), gates page state | **HIGH** — contains both `naran` and `doran` tokens in one URL; heaviest test/screenshot/doc reference density of any route |
| `/naran/family` | `App.tsx:79` | 가족 (Family details, minimal) | `FamilyLanding`, `AccessBoundary` | Dock/desktop-nav "가족" | `ProtectedRoute` + `AccessBoundary permission="family.read"` | Explicit — `AccessBoundary` blocks with "가족을 선택해주세요"/"권한이 없어요" states | Unauthenticated → `<Navigate to="/" replace/>` | Works | Works | Normal | 2 of the 6 `01-shell.spec.ts` tests (permission-denial + mapping-required paths) | none beyond SPA fallback | **HIGH** — same reasoning as `/naran/doran` (URL literally encodes the old platform name) |
| `*` (catch-all) | `App.tsx:86`, added in `MONGLE-FE-ROUTE-ALIGNMENT-001` | 페이지를 찾을 수 없어요 | `NotFoundPage` (inline in `App.tsx`) | Any unmatched path | None | None | None (terminal) | Works by definition | Works | Normal | 1 test (`shows a safe not-found page...`) | none | **LOW** — newest route, single responsibility, zero other code depends on it |

## 2. Redirect, Back, and deep-link current behavior (consolidated)

| Mechanism | Trigger | Target | Type |
|---|---|---|---|
| `pages/Auth/index.tsx:32` | Already logged in, viewing `/` | `/dashboard` or `/admin` | React Router `<Navigate replace>` (client-side, no full reload) |
| `App.tsx` `ProtectedRoute`/`AdminProtectedRoute` | Not authenticated for a guarded route | `/` | React Router `<Navigate replace>` |
| `AdminDashboard/index.tsx:22` | Unmatched `/admin/*` sub-path | `/admin` | React Router `<Navigate replace>` |
| `shared/api/httpClient.ts:35` | Any API call returns 401 | `/` | **`window.location.href = '/'`** — full page reload, not a React Router navigation. Also sets `sessionStorage.mc_session_expired` first so `pages/Auth/index.tsx` shows a toast after the reload. |
| `MongleAppShell.tsx` logout button, 4 other logout call sites | User-initiated logout | `/` | `navigate('/')` (React Router, no reload) |
| `DoranLanding.tsx` room auto-select | First normal-state load on ≥701px viewport with no room selected | `?room=<firstRoomId>` on the same path | `setSearchParams({..}, {replace:true})` — URL query mutation, not a path change |
| `DoranLanding.tsx` back gesture | Mobile "back to room list", only when room was reached via a pushed (not replaced) history entry | Previous history entry | `navigate(-1)` (real browser history back, not a fixed target) |

**No redirect loop exists today** — confirmed by tracing every target above; none of them point back to a route that would re-trigger the same redirect (e.g. `/` never redirects to itself).

## 3. `/naran` occurrence classification (8-category reclassification, independently re-verified against current code — see §10 in the Options doc's companion allowlist reasoning; full detail in `MONGLE_NARAN_REMAINING_ALLOWLIST.md` from the prior task, re-confirmed here)

| Category | Occurrences | Representative locations |
|---|---|---|
| `FRONTEND_ROUTE_CONTRACT` | ~15 | `/naran/doran`, `/naran/family` strings in `App.tsx`, `MongleAppShell.tsx`, `specs-mongle/01-shell.spec.ts`, `backend/scripts/phase1_seed_synthetic.py` (comment only) |
| `PERSISTED_CLIENT_CONTRACT` | 1 | `` `naran.activeFamily.${accountId}` `` in `useFamilyContextStore.ts:20` |
| `PWA_CONTRACT` | 0 | Confirmed — `manifest.json`, `index.html`'s PWA meta tags contain **zero** `naran` references |
| `INFRA_DEPLOYMENT_CONTRACT` | 0 | Confirmed — `nginx.conf`, `vite.config.ts`, both `docker-compose*.yml` contain **zero** `naran` references |
| `TEST_CONTRACT` | ~10 | `test.describe`/test-title strings and the `/naran/...` `page.goto()` inputs in `specs-mongle/01-shell.spec.ts` (route strings already counted above; test-only prose like "Mongle shell"/"Mongle mobile navigation" comments are already renamed, not residual `naran`) |
| `CURRENT_DOCUMENTATION` | 0 remaining unhandled | The 3 canonical docs (`DORAN_MESSAGING_CONTRACT.md`, `DORAN_PERFORMANCE_AND_SYNC.md`, `ACCOUNT_FAMILY_RBAC_CONTRACT.md`) already had their platform-name references updated in the prior task; zero pending current-doc updates remain |
| `HISTORICAL_RECORD` | ~200+ | Archived handoffs/QA (`PHASE1-NARAN-PLATFORM-SHELL-001.md` ×2), `graduated/2026-07.md`, `COVERAGE_MAP.md`'s Journey ID/prose, `naran-shell-capture-manifest.md`, `DORAN_FOUNDATION_GAP_ANALYSIS.md`'s test-result quote, `FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md`, plus this session's own accumulating prior-task reports (`MONGLE_ROUTE_AUDIT.md`, `MONGLE_NARAN_REMAINING_ALLOWLIST.md`, `MONGLE_TECHNICAL_NAMESPACE_ALIGNMENT_REPORT.md`, etc. — these are now themselves historical records of the completed rename) |
| `UNKNOWN` | **0** | No unclassifiable occurrence found |

**UNKNOWN = 0 confirmed.** No PM Gate required purely on classification grounds (open questions in this task come from genuine design tradeoffs, §16 of the design task, not from unclassified occurrences).

## 4. Persisted client state — full inventory

| Storage | Key | Set at | Read at | Removed at | Schema | Notes |
|---|---|---|---|---|---|---|
| `sessionStorage` | `accessToken` | `useAuthStore.setLogin/adminLogin` (`useAuthStore.ts:39,44`) | `useAuthStore`'s `restoreFromStorage()` on store init (`:17`), `httpClient.ts:10` per-request | `useAuthStore.logout` (`:56`), `httpClient.ts:32` on 401 | JWT string, payload decoded client-side (`role`, `sub`, `name`, `player_id`) | Tab-scoped by design (`sessionStorage`) — a fresh tab requires re-login. Not a migration concern for route/PWA work; unaffected by any route rename. |
| `sessionStorage` | `mc_session_expired` | `httpClient.ts:31`, just before the 401 full-reload redirect | `pages/Auth/index.tsx:24`, once, on `AuthPage` mount | `pages/Auth/index.tsx:25`, immediately after reading | `'1'` flag string | One-shot toast-trigger flag. Not a migration concern. |
| `localStorage` | `` `naran.activeFamily.${accountId}` `` | `useFamilyContextStore.load()` (`:43`), `.selectFamily()` (`:71`) | `useFamilyContextStore.load()` via `storedFamilyId()` (`:24,40`) | `useFamilyContextStore.reset()` (`:88`), only for the currently-active account | Family ID as a numeric string, namespaced per `accountId` | **The one key with real migration implications** — see §5. |
| `localStorage` | `loggedInPlayer` | **Never set anywhere in current source** | Never read anywhere in current source | `useAuthStore.logout` (`:57`), `httpClient.ts:33` | — | Dead/legacy cleanup-only code, presumably a remnant of a pre-JWT auth iteration. Unrelated to this migration; harmless to leave as-is (it does nothing today). |
| `localStorage` | `rememberMe` | **Never set anywhere in current source** | Never read anywhere in current source | `useAuthStore.logout` (`:58`), `httpClient.ts:34` | — | Same as above. |
| IndexedDB | — | — | — | — | — | Confirmed absent — no `indexedDB` reference anywhere in `frontend/src`. |
| Zustand `persist` middleware | — | — | — | — | — | Confirmed absent — neither `useAuthStore` nor `useFamilyContextStore` uses `persist()`; both manage `sessionStorage`/`localStorage` manually inside their own action functions. |
| React Query / cache library | — | — | — | — | — | Confirmed absent — no `@tanstack`/`react-query` dependency in `package.json`. |
| Service Worker Cache API | — | — | — | — | — | Confirmed absent — see §6. |
| URL query/hash state | `?room=<id>` on `/naran/doran` | `DoranLanding.tsx` `selectRoom()`/auto-select effect | `DoranLanding.tsx` on mount via `useSearchParams` | Cleared via `setSearchParams({}, {replace:true})` when returning to Room List | Doran room ID string | Route-local, not persisted across sessions — irrelevant to storage migration, relevant to route migration (must be preserved on any path rename). |

## 5. `naran.activeFamily.${accountId}` — full behavioral contract (per design-task §9 requirement)

1. **작성 위치**: `useFamilyContextStore.ts:43` (after a successful `load()`, if a valid or auto-selected family ID exists) and `:71` (`selectFamily()`, on explicit user selection).
2. **읽기 위치**: `:24` (`storedFamilyId()`), called from `:40` inside `load()`.
3. **삭제 위치**: `:88` (`reset()`) — invoked by `MongleAppShell.tsx`'s `handleLogout` (`reset(); logout(); navigate('/')`), i.e. only on **explicit UI-triggered logout**, not on the 401-interceptor's full-page-reload path (that path calls `window.location.href = '/'` directly without touching this store — meaning after a *session-expiry* redirect, this key is **not** cleared, only after an *intentional* logout).
4. **value schema**: string-encoded integer (a Family ID), one key per `accountId` (`naran.activeFamily.<id>`).
5. **account switching behavior**: Namespaced by `accountId`, so two different accounts on the same browser never collide; but switching away from account A does not clean up account A's key — it simply becomes unreferenced until that account logs in again or explicitly logs out.
6. **family switching behavior**: `selectFamily()` overwrites the value for the *current* account immediately (synchronous localStorage write, then state update).
7. **invalid value handling**: `storedFamilyId()` guards with `Number.isInteger`; a non-numeric or missing value yields `null`. `load()` then cross-checks the stored ID against the account's *current* Family list (`validSavedId`) — a stale ID (e.g. a Family the account lost access to) is silently discarded, not surfaced as an error.
8. **missing value fallback**: If no valid stored ID exists and the account has exactly one Family, that Family is auto-selected (and immediately written back to storage). With 0 or 2+ Families and no valid stored ID, `activeFamilyId` stays `null` → UI shows `family_selection_required`.
9. **logout behavior**: Cleared for the active account only, and only via the explicit logout path (see #3) — not on session-expiry.
10. **테스트 존재 여부**: The Family-switch *UI* interaction is covered (`01-shell.spec.ts`'s first test), but **no test asserts on `localStorage` persistence across a reload/re-login** — this is a real, pre-existing test gap independent of any migration.
11. **키 변경 시 실제 사용자 영향**: Renaming this key without a compatibility read would make every existing multi-Family account's next `load()` find nothing under the new key name — they would see `family_selection_required` again (a one-time, user-visible regression) even though nothing about their actual Family membership changed. Single-Family accounts would be unaffected (auto-select kicks in regardless).
12. **기존 값을 신규 key로 복사할 수 있는지**: Yes, trivially — `load()` already computes `storedFamilyId()` before the Family-context API call resolves; a compatibility read of the legacy key name as a fallback is a small, local, low-risk addition (not implemented in this design task — see the Storage doc for the recommended migration option).
13. **legacy key를 언제 삭제할 수 있는지**: Only after enough time has passed that essentially every returning user has had at least one session under the migration code (so their data has been copied forward) — a PM-gated, calendar-driven decision, not a code-driven one.
14. **다중 탭 충돌 여부**: `localStorage` is synchronously shared across same-origin tabs; two tabs of the same account writing different Family selections will last-write-win with no explicit lock or `storage` event listener today. This is **pre-existing behavior**, not a new risk introduced by any proposed migration option.

## 6. PWA current implementation state (measured, not assumed)

| Item | Status | Evidence |
|---|---|---|
| `manifest.json` exists | **Yes** | `frontend/public/manifest.json` |
| `<link rel="manifest">` | **Yes** | `frontend/index.html:12` |
| `name` / `short_name` | `"몽글 — 가족 플랫폼"` / `"몽글"` | manifest.json |
| `id` | **ABSENT** | Not a key in manifest.json |
| `start_url` | `"/"` | manifest.json |
| `scope` | **ABSENT** (defaults to the manifest's own directory, i.e. `/`) | manifest.json |
| `display` | `"standalone"` | manifest.json |
| `theme_color` / `background_color` | `#5D45A2` / `#f8fafc` | manifest.json, also duplicated as a `<meta name="theme-color">` in `index.html` |
| `icons` | 3 entries (192/512/512-maskable) | manifest.json |
| `shortcuts` | **ABSENT** | — |
| `protocol_handlers` | **ABSENT** | — |
| `share_target` | **ABSENT** | — |
| `related_applications` | **ABSENT** | — |
| Service Worker file | **ABSENT** | No `sw.js`/`service-worker.js` found anywhere in `frontend/public` or `frontend/src` |
| Service Worker registration code | **ABSENT** | `grep -rn "serviceWorker\|registerSW\|workbox"` across `frontend/src` returns 0 matches outside TypeScript's own ambient `lib.dom.d.ts`/`lib.webworker.d.ts` type declarations (not actual usage) |
| PWA build plugin (`vite-plugin-pwa`, workbox) | **ABSENT** | Not in `package.json` dependencies |
| Vite `base` config | Default (`/`) | `vite.config.ts` has no `base` key |
| Production hosting path | Root (`:3000` → nginx `:80`, no subpath prefix) | `docker-compose.prod.yml` |
| Apple/iOS install meta tags | Present | `apple-mobile-web-app-capable`, `apple-mobile-web-app-status-bar-style`, `apple-touch-icon` in `index.html` |
| Currently installed PWA instances (real users) | **NOT VERIFIED** | No analytics/telemetry access from this session; cannot confirm or deny an existing install base |

**Conclusion**: this is a **manifest-only, installable-looking** web app — it can likely surface an "Add to Home Screen" affordance on supporting browsers (HTTPS + manifest + standalone display are the minimum signal most browsers check), but there is **no actual offline capability, no precache, no navigation fallback via Service Worker, and no `PUBLIC_APP_URL`/`mongle.life` wiring anywhere in code**. Any migration design that assumes an existing Service-Worker-driven PWA would be designing for a system that does not exist yet.

## 7. nginx / deployment route current state

- Dev: Vite dev server (`vite.config.ts`), proxies `/api` to `VITE_DEV_PROXY_TARGET` (default `localhost:8000`); no route rewriting for frontend paths.
- Prod: nginx serves the built `dist/` at root, proxies `/api/` (and a body-size-limited sub-location for `/api/families/{id}/doran/service/actions`) to the backend container; SPA fallback via `try_files $uri $uri/ /index.html`; manifest/favicon explicitly no-cache; hashed JS/CSS/image assets cached 1 year.
- No path-prefix stripping, no subpath deployment configured anywhere (`docker-compose.prod.yml` maps host `:3000` directly to container `:80`).
- `CORS_ORIGINS` (backend config) currently lists only `http://localhost:3000,http://localhost:5173` — **no `mongle.life` entry exists in code today**; the domain remains a documentation-only decision from a prior task, not yet wired into any config.

## 8. Test coverage summary

| Suite | Executable this session | Covers |
|---|---|---|
| `tests/e2e/specs-mongle/01-shell.spec.ts` (via `playwright.mongle.config.ts`, isolated `mc_phase1` stack) | **Yes** — 30/30 PASS, cold-start x2 verified in the prior task | Login, Family switch UI, `/naran/doran` active/responsive-nav checks, `/naran/family` permission denial, mapping-required state, 404 fallback |
| `tests/e2e/specs/*.spec.ts` (4 files: login/mission/admin/flow, via `playwright.config.ts`) | **No** — depends on `docker-compose.phase0.yml`, confirmed absent from the repository | Presumably basic `/`, `/dashboard`, `/admin` flows from an earlier phase; cannot currently verify |
| `naran.activeFamily.*` localStorage persistence across reload/re-login | **No dedicated test found** | Gap, independent of this migration |
