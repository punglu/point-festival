# PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001

- Task ID: `PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001`
- Closeout Contract: `v1`
- Branch: `dev`
- Start HEAD: `83aad8198610fe3c3a442e9d51320f34a395142e`
- End HEAD: `pending — final baseline evidence commit`
- Final Commit: `pending — final baseline evidence commit`
- Existing Dirty State: `CLAUDE.md` modified; root prompt and `docs/` deletions. User-owned and excluded.
- Decision: PM-approved development-guide decisions 01–05.

## Scope

Apply the approved guide decisions, revalidate existing Node/ESLint and isolated runtime work, build reproducible synthetic API/DB baseline fixtures where the existing API supports them, add OpenAPI type-generation foundation, run existing and relevant tests, capture safe synthetic runtime evidence, and write a no-access operating DB rehearsal plan.

## Forbidden scope

Production/NAS/operating DB access; schema or migration changes; existing Docker project/volume changes; core backend business logic/RBAC/API compatibility changes; user dirty-state cleanup; and push.

## Implemented baseline

- Recorded the five PM-approved engineering decisions in local guides and added an operating DB backup/migration rehearsal plan.
- Reused isolated Compose project `mc_phase0` (ports 15432/18000/13000, volume `phase0_pg_data`, network `mc_phase0_network`) without touching `outlook-hub`.
- Added `openapi-typescript` as a pinned frontend development dependency, `generate:api`, generated OpenAPI definitions, and a compile-time admin-login boundary check. Generated code carries a no-direct-edit header.
- Made API scripts default to `PHASE0_API_BASE_URL=http://localhost:18000`; updated the v2 scenario to use synthetic admin credentials and source-backed transition/config expectations.
- Added level-tier and chat-access checks to the synthetic scenario.
- Captured login, user dashboard, and administrator dashboard at Desktop, iPhone 390, iPad 1024, Android-tablet portrait, and Android-tablet landscape. Fifteen PNGs are preserved outside the repository at `/tmp/phase0-screen-captures`.

## Executed commands and results

- `docker compose -p mc_phase0 --env-file .env.phase0.example -f docker-compose.phase0.yml up -d --build`: exit 0; health, OpenAPI (71 paths), and frontend HTTP 200.
- `PHASE0_API_BASE_URL=http://localhost:18000 bash tests/api/test_weekly_api.sh`: exit 0; 6/6 PASS.
- `PHASE0_API_BASE_URL=http://localhost:18000 python3 tests/api/e2e_scenario_test_v2.py`: exit 0; 87/87 PASS.
- `cd frontend && volta run --node 20.19.0 --npm 10.8.2 -- npm run lint`: exit 0.
- `cd frontend && volta run --node 20.19.0 --npm 10.8.2 -- npm run build`: exit 0.
- `cd frontend && OPENAPI_URL=http://localhost:18000/openapi.json volta run --node 20.19.0 --npm 10.8.2 -- npm run generate:api`: exit 0; generated output stable.
- `cd backend && python3 -m pytest -q`: exit 0; 6 passed.
- `docker compose ... exec backend python -c 'import app.main'`: exit 0.
- `cd tests/e2e && volta run --node 20.19.0 --npm 10.8.2 -- npm test`: exit 0; 9 passed.

## Findings

- Host-side backend import without environment variables is `ENVIRONMENT_REQUIRED`; the isolated container import succeeds.
- API script execution emits a host Python LibreSSL/urllib3 warning but completes all checks; it is not a product failure.
- Automated viewport captures are not physical-device, standalone-PWA, keyboard, or Push evidence.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001.md`
- Independent QA: `not_applicable — no core backend/RBAC/schema/API behavior changed`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: API integration/journey execution and viewport evidence changed from source-only to measured isolated-runtime evidence.
- CLOSEOUT GATE: `PASS`
