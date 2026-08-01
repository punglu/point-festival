# MONGLE Frontend Scaffold Plan

Task: `MONGLE-W6-FRONTEND-TARGET-ARCHITECTURE-DESIGN-001`

No path in this plan is created by this task. CREATE_NOW means eligible only for a separately authorized Scaffold Task, not an instruction to create now.

| Directory path | Decision | Existing path status | Reason | Collision/runtime risk | Owner |
| --- | --- | --- | --- | --- | --- |
| `src/app/` | CREATE_LATER | absent | router/registry authority is undecided | App is active composition root | app architecture owner |
| `src/app/routing`, `providers`, `registry`, `config`, `errors` | CREATE_LATER | absent | create only with first approved composition migration | route/nav drift if partial | app architecture owner |
| `src/pages/` | KEEP_CURRENT | exists | route-screen root already exists | legacy active routes | page owner |
| `src/platform/` | KEEP_CURRENT | exists | transitional shared family capabilities exist | contains services mixed with platform | platform owner |
| `src/services/` | CREATE_LATER | absent | needs service authority, first route/API contract | premature duplicate trees | service architecture owner |
| `src/services/markpoint` | CREATE_LATER | absent | UserDashboard/Markpoint authority unresolved | duplicate candidate | Markpoint PM/task owner |
| `src/services/doran` | CREATE_LATER | absent | Doran/Wagle name and route/API authority unresolved | Wagle implementation already exists elsewhere | messaging PM/task owner |
| `src/services/calendar`, `tasks`, `family-album`, `household-ledger` | CREATE_LATER | absent | planned services; route/backend contracts unassigned | speculative scaffolding | respective future owner |
| `src/platform/auth` | CREATE_LATER | directory currently present but no measured source contract | await ADR-FE-008 approval | A1/current auth protection | platform auth owner |
| `src/platform/contracts` | CREATE_LATER | absent | create when first cross-service contract is approved | generic-contract dumping ground | platform owner |
| `src/shared/{ui,hooks,lib,types,config,assets,styles}` | DO_NOT_CREATE as a batch | shared root exists with varied current subpaths | only create individual proven-consumer location | premature shared promotion | shared owner |
| final `pages/PointFestival` | CREATE_LATER | absent | 1c Visual Gate and final route authority pending | violates preview ownership | 1c/Markpoint owner |

Prohibited early roots: `services/markpoint`, `services/doran`, final PointFestival page, an actual service registry, and actual route configuration. There are zero CREATE_NOW paths because all absent roots either require authority decisions or would be empty scaffolding.
