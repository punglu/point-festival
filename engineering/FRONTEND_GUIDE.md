# Frontend Development Guide

**Status: APPROVED_WITH_DECISIONS / v0.1 (2026-07-26).**

## CURRENT CONTRACT — stack and entry points

- React 18, TypeScript, Vite, CSS Modules, Axios, and Zustand are declared in `frontend/package.json`.
- The canonical toolchain pin is package-local Volta/engines: Node 20.19.0 and npm 10.8.2. Source: `frontend/package.json`.
- Routes are in `frontend/src/App.tsx`: `/`, `/dashboard`, and `/admin/*`. `ProtectedRoute` and `AdminProtectedRoute` are UX route guards.
- Shared HTTP transport is `frontend/src/shared/api/httpClient.ts`, including bearer-token injection and expiry cleanup. Authentication state is the shared Zustand store at `frontend/src/shared/stores/useAuthStore.ts`.
- Page-oriented colocation is current: `pages/Auth`, `pages/UserDashboard`, and `pages/AdminDashboard`, with page APIs/hooks/components and CSS Modules.

## CURRENT CONTRACT — audited samples

| Surface | Read paths | Observed contract |
| --- | --- | --- |
| Auth | `pages/Auth/index.tsx`, `api/authApi.ts`, components | API mapping lives with page; token is written to session storage and shared auth state. |
| User dashboard | `pages/UserDashboard/index.tsx`, `hooks/useDashboard.ts`, `api/dashboardApi.ts` | Page hook owns data/UI state and aborts several requests; it has fallback/config handling. |
| Admin dashboard | `pages/AdminDashboard/index.tsx`, `hooks/useAdminData.ts`, `api/adminApi.ts`, views/components | Admin surface is composed from views and shared/local components; some fetch errors are logged or intentionally absorbed. |
| Mission flow | User/admin dashboard APIs and mission views | Endpoint calls are page-local; server responses drive reloads after approval actions. |
| Chat | `shared/components/ChatModal/`, Admin `ChatView` | Chat UI is shared/view-oriented; backend remains authority for persisted messages. |

## TARGET CONTRACT — placement and state

| Concern | Preferred home |
| --- | --- |
| Route composition and guard wiring | page/route |
| Page/capability endpoint mapping and server-state coordination | nearest page/feature API and hook |
| Common transport, auth header, global expiry behavior | `shared/api` |
| Capability-local ephemeral state | component or page-local hook/store |
| Genuine cross-surface state (session/auth, common toast) | `shared/stores` |
| Pure UX visibility/availability decision | local pure selector/view-rule |

- Keep a new capability local-first; consider shared promotion only after a second actual consumer. Do not reorganize all pages into a new feature tree merely to match Viblot's DRAFT layout.
- UI permissions, button visibility, and route guards improve UX but never replace backend RBAC/ownership enforcement.
- Core mutations (points, approval, roles, subscriptions, message membership) must not be treated as successful before server confirmation.
- Keep API wire changes compatible with actual backend responses. Phase 0–1 uses
  OpenAPI-generated types at the API boundary; generated files are not edited
  and page/view types remain local mappings.
- Use CSS Modules and the existing shared component/token surfaces. Respect safe-area, keyboard, mobile/tablet, and desktop requirements when a surface is affected; do not import Outlook's desktop visual tokens or layout rules.

## LEGACY CONDITION

- Current code is page-centered rather than capability-module centered.
- Some dashboard hooks intentionally swallow request errors or use local fallback values (for example `useDashboard.ts`); new work should make relevant loading/empty/error/retry state explicit rather than copying silent failure handling.
- UI types are currently handwritten near their consumers. They are not proof of a contracts package or DB-field naming policy.

## TARGET CONTRACT — PWA and multi-device

PWA/mobile behavior is a family-platform requirement, but runtime/device confirmation is separate from source inspection. Keep `/dashboard` compatible, preserve safe-area and keyboard usability, and test iPhone, iPad, Android tablet, and desktop journeys when relevant. Push/device-token/multi-device session policy requires server contract evidence before implementation.

## Playwright selector and journey rules

Prefer role plus accessible name, then labels, then stable test IDs; avoid CSS module hash/DOM-depth selectors. Existing test configuration is `tests/e2e/playwright.config.ts`, using the isolated `mc_phase0` Compose project and port 13000. Do not remove assertions, skip defects, or increase retries to mask a product failure.

## DEFERRED

- Feature-level view-rules directories may be introduced only where complex, pure UX gating truly exists.
- OpenAPI type generation/boundary checks wait for PM_GATE-04.
- PWA update, push, and real-device contracts remain device/runtime work, not documentation completion.
