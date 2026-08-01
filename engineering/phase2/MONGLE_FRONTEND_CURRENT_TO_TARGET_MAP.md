# MONGLE Frontend Current-to-Target Map

Task: `MONGLE-W6-FRONTEND-TARGET-ARCHITECTURE-DESIGN-001`

| Current path | Current classification | Route reachability / consumers | Target path | Target classification | Timing | Prerequisite | Risk / decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `src/App.tsx` | ACTIVE_STABLE composition | all top-level routes | `src/app/*` candidate | MIGRATE_AFTER_ROUTE_DECISION | later | registry/router authority | do not split while active links/routes disagree |
| `src/pages/Auth` | KEEP_CURRENT_ACTIVE | `/`; Auth flow | `pages/A1AccountLogin` or platform auth consumer, unassigned | KEEP_UNTIL_AUTHORITY_DECISION | later | login authority and auth contract | A1 is separate current route |
| `src/pages/UserDashboard` | LEGACY_REACHABLE; DUPLICATE_CANDIDATE | guarded `/dashboard` | legacy retained; possible `services/markpoint` consumers unassigned | MIGRATE_AFTER_AUTHORITY_DECISION | later | Markpoint product authority | must not declare final authority here |
| `src/pages/AdminDashboard` | LEGACY_REACHABLE | `/admin/*` plus nested routes | legacy retained | KEEP_CURRENT_ACTIVE | later | admin product/route authority | wide active surface |
| `src/pages/A1AccountLogin` | ACTIVE_ROUTE_ENTRY | `/login` | `pages/A1AccountLogin` | KEEP_CURRENT | after A1 ownership allows | A1 protection | no source change in this task |
| `src/platform/markpoint/MarkpointUser` | NOT_IMPORTED | none | `services/markpoint/*` plus page entry, candidate | MIGRATE_AFTER_ROUTE_DECISION | later | Markpoint authority/API/route | duplicates UserDashboard |
| `src/platform/markpoint/MarkpointAdmin` | NOT_IMPORTED | none | `services/markpoint/*` plus page entry, candidate | MIGRATE_AFTER_ROUTE_DECISION | later | admin authority/API/route | duplicates legacy admin intent |
| `src/platform/pages/FamilyLanding` | NOT_IMPORTED | shell links `/family` | `pages/FamilyLanding` with platform/family dependencies, candidate | MIGRATE_AFTER_ROUTE_DECISION | later | registered route/access contract | current dead link |
| `src/platform/pages/WagleLanding` | NOT_IMPORTED | shell link `/wagle` | `pages/WagleLanding` using `services/doran`, candidate | MIGRATE_AFTER_ROUTE_DECISION | later | service name/route/API decision | current dead link; Wagle naming decision |
| `src/platform/wagle/*` | TRANSITIONAL / unreachable entry | imported under WagleLanding | `services/doran/*` candidate | MIGRATE_AFTER_AUTHORITY_DECISION | later | Doran/Wagle authority, route/API | do not rename/move speculatively |
| `src/platform/shell` | ACTIVE_TRANSITIONAL | wraps dashboard/admin; emits service links | `platform/shell` | KEEP_CURRENT | incremental | registry/navigation contract | navigation/router mismatch |
| `src/platform/access` | IMPORTED_BUT_UNREACHABLE | MarkpointUser only | `platform/access` | KEEP_UNTIL_AUTHORITY_DECISION | later | cross-service access contract | preserve server re-check rule |
| `src/shared/family` and stores | ACTIVE_TRANSITIONAL | App/shell/platform consumers | `platform/family`, `platform/auth` candidates | MIGRATE_AFTER_AUTHORITY_DECISION | later | auth/family contracts | shared owns domain state today |
| `src/shared/stores/useAuthStore.ts` | REVERSE_DEPENDENCY_CONFIRMED | App, shell, Auth, dashboards | `platform/auth/store` candidate | MIGRATE_AFTER_AUTHORITY_DECISION | later | approved auth migration | direct type import to page API |
| `src/shared/api/httpClient.ts` | ACTIVE_STABLE | pages/platform APIs | `shared/lib` or shared transport retained, candidate | KEEP_CURRENT | only if no contract change | transport must stay domain-neutral |
| `src/platform/preview/PointFestivalPreview.*` | PREVIEW_TASK_OWNED | `/__wave6/1c` | final page UNASSIGNED | MIGRATE_AFTER_VISUAL_GATE | later | GPT Visual Gate + product route authority | 1c owner protection |

Counts: keep-current active 4; migrate-later/after decision 10; legacy candidates 2; preview-owned 1; unresolved target authority decisions 7. These are planning classifications, not file-move authorization.
