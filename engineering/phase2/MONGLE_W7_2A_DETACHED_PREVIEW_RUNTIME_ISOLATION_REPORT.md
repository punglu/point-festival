# MONGLE W7.2A Detached Preview Runtime Isolation

## Verdict

`MONGLE_W7_2A_DETACHED_PREVIEW_RUNTIME_ISOLATION_PASS`

## Root cause and correction

`FamilyContextLoader` originally wrapped the complete router, so detached `/__wave6/*` routes inherited product loader activity. `App.tsx` now uses `ProductContext` only for `/`, `/dashboard`, `/admin/*`, `/login`, and the catch-all; all detached routes render outside it.

## Evidence

- Detached routes: 63/63 DOM marker smoke passed; actual endpoint request criterion is `new URL(request.url()).pathname.startsWith('/api/')`; result 0.
- Initial 315 count was a classification error: Vite source-module URLs such as `src/**/api/*.ts` are not backend endpoints.
- Responsive structural: 28 × 3 representative viewports = 84/84 passed; blank roots 0; horizontal overflow 0.
- Console/page errors: 0/0. New Screen-local API/store/router/storage/WebSocket dependency: 0.
- Product branch source remains inside `ProductContext → FamilyContextLoader`. Browser `/` and guarded product routes issued the pre-existing loader endpoint family `/api/configs/level.thresholds`, `/api/players`; backend was unavailable, producing expected proxy refusal noise.

## Validation

`npm run lint`, `npm run build`, and `git diff --check` passed after composition change.

## Boundaries

Product integration, Shared extraction, API wiring, and visual-fidelity closeout remain out of scope. W7.3 is the next visual-fidelity task; independent QA remains pending.
