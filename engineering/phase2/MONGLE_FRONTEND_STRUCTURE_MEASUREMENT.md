# MONGLE Frontend Structure Measurement

Task: `MONGLE-W6-FRONTEND-SOURCE-STRUCTURE-MEASUREMENT-001`  
Observed at: `2026-08-02T06:01:56Z`  
Git ref: `dev-newmarkp @ 78913b48e1147073f3b1c56b39de9eea28d5d9cf`

This is a read-only source measurement. It neither proposes a target frontend tree nor decides which concurrent implementation is authoritative.

## 1. Executive Summary

`frontend/src/App.tsx` is the active runtime composition root. It eagerly routes legacy Auth, UserDashboard and AdminDashboard, plus A1 login and the task-owned 1c preview. `MongleAppShell` links to `/family`, `/wagle`, `/markpoint`, and `/markpoint/admin`, but none is registered by the current router; each falls through to the catch-all.

FamilyLanding, WagleLanding, MarkpointUser and MarkpointAdmin have no App import/route chain. A shared auth store directly type-imports a page-local Auth API. No static relative-import cycle was found.

## 2. Baseline

| Field | Measured value |
| --- | --- |
| worktree | `/Users/mac/mac_Project/mongle_ui` |
| branch | `dev-newmarkp` |
| HEAD | `78913b48e1147073f3b1c56b39de9eea28d5d9cf` |
| dirty paths | 134 repository paths |
| frontend tracked / worktree | 298 / 314 |
| frontend modified / untracked / deleted | 8 / 14 / 0 |
| frontend manifest SHA-256 | `8b37be767c2dd133362b6bcdd2c0edac740df794c5c2d532c494e8b4880760c5` |
| diff check at measurement | clean (no output) |

The prescribed sorted `git ls-files frontend` plus sorted `find frontend` input, excluding `node_modules` and `dist`, was recomputed and matches the required fingerprint.

## 3. Physical Source Tree

Source-owner file counts: `pages` 157, `platform` 59, `shared` 53, `assets` 13, `generated` 1, and `styles` 2; App, main and declarations are outside those owners. The complete per-file manifest provides path, status, extension, size, SHA-256, owner and candidate layer.

The tree has legacy `pages/{Auth,UserDashboard,AdminDashboard}` beside `platform/{shell,pages,wagle,markpoint,preview,access}`. This is observed coexistence only.

## 4. Active Runtime Routes

14 static route declarations were found: 6 in `App.tsx`, 8 in `pages/AdminDashboard/index.tsx`. Top-level paths are `/`, `/dashboard`, `/admin/*`, `/login`, `/__wave6/1c`, and `*`. There is no `import()`/lazy route under `frontend/src`. `/dashboard` uses ProtectedRoute; `/admin/*` uses AdminProtectedRoute. The matrix records all route entries.

## 5. Link/Route Mismatches

`/family`, `/wagle`, `/markpoint`, and `/markpoint/admin` are explicit shell `LINKED_BUT_UNREGISTERED` targets. `WagleLanding` also has `navigate('/markpoint')`, but that component is itself unreachable. The fallback does not make an intended screen reachable.

## 6. Reachability Classification

| Implementation | Classification | Evidence |
| --- | --- | --- |
| AuthPage | ACTIVE_ROUTE_ENTRY | eager App import; `/` |
| UserDashboard | ACTIVE_ROUTE_ENTRY; LEGACY_REACHABLE | guarded `/dashboard` |
| AdminDashboard | ACTIVE_ROUTE_ENTRY; LEGACY_REACHABLE | admin-guarded `/admin/*` |
| A1AccountLogin | ACTIVE_ROUTE_ENTRY | `/login`; untracked at snapshot |
| PointFestivalPreview | PREVIEW_ROUTE_ENTRY; PREVIEW_TASK_OWNED | `/__wave6/1c` |
| FamilyLanding / WagleLanding | NOT_IMPORTED | no App import or route declaration |
| WagleRoomView | IMPORTED_BUT_UNREACHABLE | imported only by WagleLanding |
| MarkpointUser / MarkpointAdmin | NOT_IMPORTED | no runtime route-chain importer |
| AccessBoundary | IMPORTED_BUT_UNREACHABLE | imported by MarkpointUser only |

## 7. Import Dependency Findings

The static graph extraction found all resolved relative imports under `frontend/src`; counts and the generated edge inventory are in the manifest. Confirmed reverse dependency:

```text
shared/stores/useAuthStore.ts -> pages/Auth/api/authApi.ts
symbol: AdminLoginResponse; direct, type-only; no re-export intermediary
classification: REVERSE_DEPENDENCY_CONFIRMED
```

App, MongleAppShell, FamilyContextLoader, Auth and legacy dashboard code consume this store. Moving/replacing the page-local Auth API therefore changes a shared state boundary. No `shared -> platform` static import and no static relative-import cycle was found.

## 8. Domain Ownership Findings

| Area | Classification | Runtime/import evidence |
| --- | --- | --- |
| application composition | ACTIVE_STABLE | App owns BrowserRouter/top-level imports |
| legacy auth/dashboard | LEGACY_REACHABLE | active Auth, UserDashboard, AdminDashboard routes |
| family platform shell | ACTIVE_TRANSITIONAL | wraps legacy routes; emits unregistered service links |
| family/profile/access | MIXED_RESPONSIBILITY | shared family context; FamilyLanding/AccessBoundary unrouted |
| Markpoint | DUPLICATE_CANDIDATE | legacy dashboard active; Markpoint pages unimported |
| Wagle | ACTIVE_TRANSITIONAL | shell path exists; entry wrapper unrouted |
| shared UI/technical | ACTIVE_STABLE with exception | shared store has page-local type dependency |
| preview | PREVIEW_TASK_OWNED | sole `__wave6/1c` route |

## 9. Duplicate/Collision Candidates

1. UserDashboard is active while MarkpointUser and MarkpointAdmin are same-domain, unregistered implementations.
2. Shell navigation and App routes are separately maintained and disagree on four paths.
3. A legacy Auth API owns `AdminLoginResponse` consumed by shared auth state.
4. Wagle has an unregistered wrapper plus RoomView/realtime subsystem that active navigation cannot reach.

## 10. Future Service Expansion Constraints

| Question | Status | Evidence | Risk |
| --- | --- | --- | --- |
| New route location | CURRENT_SUPPORT | App is sole top-level router | route/shell synchronization needed |
| New service navigation | CURRENT_BLOCKER | hand-authored nav has four missing routes | dead-link recurrence |
| Family context reuse | CURRENT_SUPPORT | App loader and shared store | intended screens not all routed |
| Auth/profile/access reuse | CURRENT_SUPPORT with coupling | auth/family/access primitives exist | page-local API type dependency |
| Service boundary | CURRENT_BLOCKER | no measured registry/import rule | route can diverge from nav |
| Shell service capacity | UNKNOWN_REQUIRES_DECISION | fixed navItems, no registry | scalability cannot be inferred |

## 11. Confirmed Facts

- No product source, package, route, import, relay or directory was modified.
- The supplied starting fingerprint matches the recalculated result.
- The four named service paths are linked and absent from all router declarations.
- Activation is based on import and route chains, not file existence.
- The confirmed reverse dependency is direct and type-only.

## 12. Unknowns Requiring Next-Phase Decision

- Whether legacy dashboard or Markpoint implementations are authoritative.
- Whether unregistered shell links are intended staging or defects.
- Whether router/navigation should share a governed registry.
- The ownership boundary for shared auth types and page-local API code.
- Any target directory structure; none is proposed here.
