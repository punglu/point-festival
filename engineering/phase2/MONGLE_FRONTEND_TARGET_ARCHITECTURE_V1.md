# MONGLE Frontend Target Architecture v1

Task: `MONGLE-W6-FRONTEND-TARGET-ARCHITECTURE-DESIGN-001`

## Scope and Design Inputs

This is a design-only contract grounded in the measured active router, 420 relative static import edges, zero static cycles, and one confirmed `shared -> pages` reverse dependency. No frontend directory, route, import, package, or product code is created or changed by this document.

Observed conflict to resolve incrementally: the active App router owns `/`, `/dashboard`, `/admin/*`, `/login`, `/__wave6/1c`, and `*`, while the shell links `/family`, `/wagle`, `/markpoint`, and `/markpoint/admin` without registrations. FamilyLanding, WagleLanding, MarkpointUser and MarkpointAdmin are not active route entries.

## Target Layers and Responsibilities

| Layer | Responsibility | Must not contain |
| --- | --- | --- |
| `app` | router/provider composition, registry composition, flags, global errors/runtime config | domain UI or service rules |
| `pages` | one route-screen entry, screen composition, page-local UI/state/style/fixtures | direct imports from another page internals |
| `platform` | cross-service family capabilities: auth, account, family, membership, profile, access, shell, navigation, notifications, service-catalog, settings, contracts | service mission, conversation, calendar, album, ledger models |
| `services` | independently added family-service capability implementation | direct dependency on another service |
| `shared` | domain-neutral UI, hooks, lib, types, config, assets, styles | family/service/page semantics or imports upward |

## Dependency Contract

```text
app -> pages, platform, services, shared
pages -> platform, services, shared
services -> platform/contracts, shared
platform -> shared
shared -> external packages only
```

Forbidden: `shared -> pages/platform/services`; `platform -> pages`; `platform -> service implementation`; `service A -> service B`; `page A -> page B internals`; `api -> page component`; and `store -> page-local API`.

## Target Tree: Status-Aware Contract

```text
frontend/src/
  app/          (CREATE_LATER: route/registry authority decision)
  pages/        (KEEP_CURRENT: already present; use one entry per approved screen)
  platform/     (KEEP_CURRENT: existing transitional capability location)
  services/     (CREATE_LATER: service authority, route and API decisions)
  shared/       (KEEP_CURRENT: domain-neutral only after reverse-dependency repair)
```

Candidate subpaths are contracts, not scaffold authorization: `app/{routing,providers,registry,config,errors}`, `platform/{auth,account,family,membership,profile,access,shell,navigation,notifications,service-catalog,settings,contracts}`, `services/{markpoint,doran,calendar,tasks,family-album,household-ledger}`, and `shared/{ui,hooks,lib,types,config,assets,styles}`. No empty directory is implied.

## Page Contract

An approved route screen receives one `pages/<PageName>/index.tsx` entry. It may contain only needed `components`, `hooks`, `api`, `types`, `fixtures`, and `<PageName>.module.css` children. `index.tsx` assembles the screen; page-only UI and presentation fixtures stay page-local. A page must not import another page's internals. Service API adapters are added only after service/API authority is approved.

## Service and Platform Contracts

A service may expose `api` (transport/mapping), `components` (reused by multiple pages in that service), `hooks` (domain/query orchestration), `model` (pure rules/transitions), `types`, `assets`, and `contracts` (minimum interface to app/platform). Barrel exports are permitted only after a public contract is approved.

Platform publishes only cross-service contracts. Auth, active family context, membership/role/capability checks, shell/navigation and service availability belong there when genuinely cross-service. A Markpoint mission, Wagle room/message, calendar event, task, album item, or ledger transaction remains service-owned.

## Shared Promotion Rule

Promote an item to `shared` only after at least two actual consumers have the same meaning and contract. Anticipated reuse is insufficient. Shared cannot own service names, family-role rules, mission/room/transaction/event models, or page API types.

## Registry, Router and Navigation Contract

The future registry owner is `app/registry`; it composes service declarations but does not implement services. A declaration has `serviceId`, `displayName`, `status`, `entryRoute`, `iconKey`, `allowedRoles`, `requiredCapabilities`, `featureFlag`, `navigationPlacement`, `supportedFormFactors`, `offlinePolicy`, and `notificationPolicy`.

Router composition derives approved enabled routes from this declaration; platform navigation derives visible items from the same declaration after access evaluation. Feature flags are applied in app composition before route/nav exposure. Platform access evaluates roles/capabilities against the active family context; services re-check server authorization. The contract must make a shell-visible service route either registered and reachable or intentionally absent, and must support a static consistency check.

## Reverse Dependency Recommendation

Selected direction: move the auth store with its auth contracts to `platform/auth` (candidate C), and expose only domain-neutral transport primitives in `shared`. The existing store is consumed by App, shell, FamilyContextLoader, Auth and legacy dashboard, so it is a platform identity/session capability rather than page-local state. Candidate A (move only types to platform/auth/contracts) reduces the direct violation but leaves the store's ownership ambiguous. Candidate B (move types to shared) would incorrectly make Auth semantics generic. Implementation is deferred until an authority-approved incremental migration task.

## Incremental Migration and Preview Rule

Keep current active routes and implementations until route/API/product authority is decided. New approved screens use the target Page contract first. Migrate one approved authority at a time; never move files merely to match the tree. `platform/preview/PointFestivalPreview.*` is `PREVIEW_TASK_OWNED`; its final Page location is decided only after the 1c GPT Visual Gate in a separate task.

## Future Service Procedure

For calendar (가족 일정), tasks (가족 할 일), family-album (가족 앨범), and household-ledger (가족 가계부), status remains planned, route unassigned, backend contract unassigned. Before scaffolding any one service: approve product/domain name and authority, backend contract, entry route, access/capability policy, registry declaration, page scope, and first actual shared-consumer evidence. Household-ledger is a PM-requested planned example, not a confirmed implementation.
