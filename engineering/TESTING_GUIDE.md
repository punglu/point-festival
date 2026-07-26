# Testing and QA Guide

**Status: APPROVED_WITH_DECISIONS / v0.1 (2026-07-26).**

## CURRENT CONTRACT — test layers and evidence

The local tier definitions are authoritative in `agent-system/qa/TEST_POLICY.md`:

| Tier | Current local meaning | Current examples |
| --- | --- | --- |
| TIER 0 STATIC | source/build/static checks | Agent System checkers; frontend lint/build |
| TIER 1 UNIT | isolated logic | `backend/tests/test_weekly.py` |
| TIER 2 INTEGRATION | component/boundary checks | API scripts listed in Coverage Map; environment dependent |
| TIER 3 JOURNEY | user flow | `tests/e2e/specs/*.spec.ts` |
| TIER 4 RUNTIME_DEVICE | runtime/browser/device | isolated Compose and future physical-device evidence |

The Coverage Map is a compact index, not a completion log. It currently records six backend unit tests and nine self-checked Playwright tests from the isolated Phase 0 runtime. Read `agent-system/qa/COVERAGE_MAP.md` for command/evidence boundaries; never convert SOURCE_VERIFIED or unrun work into PASS.

## CURRENT CONTRACT — isolated runtime

- `docker-compose.phase0.yml` defines a separate test stack with host ports 15432 (PostgreSQL), 18000 (backend), and 13000 (frontend), volume `phase0_pg_data`, and network `mc_phase0_network`.
- Playwright starts/reuses that isolated project through `tests/e2e/playwright.config.ts`.
- `database/init.sql` is mounted read-only at first database initialization.
- API scenario scripts default to the isolated port through `PHASE0_API_BASE_URL=http://localhost:18000`; they must never default to an unrelated project on port 8000.
- The project must not stop or modify another Compose project, its volume, or an operational DB.

## TARGET CONTRACT — risk-based verification

| Change risk | Required primary evidence |
| --- | --- |
| Schema/migration, auth/RBAC/ownership, API contract, transaction/idempotency, mission/point/level core logic | isolated API + DB assertions and independent QA |
| FE core calculation, permission branching, or state transition | risk-based independent QA plus relevant journey evidence |
| General UI, responsive/layout, navigation, modal/form | relevant Playwright journey and viewport evidence |
| Runtime/PWA/device/push | isolated runtime plus real-device evidence where applicable |
| Docs, links, metadata, lifecycle artifact | self-check and static checks |

For core API actions, assert both the response and durable invariants. Examples: mission approval should include mission state, related point/aggregate effects, and notification/audit effects if those are contractual; a point adjustment should include ledger/aggregate and unchanged data after rejected paths. Use synthetic data only.

## TARGET CONTRACT — execution reporting

Each report must name the command, HEAD, environment, exit code, test/case count, warnings, database scope, generated artifacts, unrun checks, and known gaps. Classify results as PASS, PRODUCT_DEFECT, TEST_DEFECT, ENVIRONMENT_REQUIRED, KNOWN_CONDITION, BLOCKED, HUMAN_GATE, NOT_PRESENT, or NOT_APPLICABLE. An unavailable device/runtime is never PASS.

## Playwright and device matrix

Existing Playwright coverage includes login, mission, admin, and logout/admin flow specs. Future journey coverage should cover user login/dashboard/missions/points-level/notifications/chat/logout and administrator login/dashboard/mission management/approval/point/repeated mission/chat.

| Surface | Required evidence before claiming support |
| --- | --- |
| iPhone | Safari, standalone install, safe area, keyboard, push, reconnect/session |
| iPad | portrait/landscape, Safari/PWA, keyboard, density, split-view consideration |
| Android tablet | Chrome/PWA install, portrait/landscape, system Back, keyboard/composer, push, restart, concurrent phone/tablet login |
| Desktop admin | major admin journeys and responsive controls |

Viewport automation is valuable but does not replace physical device evidence.

## CURRENT baseline commands

```bash
docker compose -p mc_phase0 --env-file .env.phase0.example -f docker-compose.phase0.yml up -d --build
PHASE0_API_BASE_URL=http://localhost:18000 bash tests/api/test_weekly_api.sh
PHASE0_API_BASE_URL=http://localhost:18000 python3 tests/api/e2e_scenario_test_v2.py
cd backend && python3 -m pytest -q
cd tests/e2e && npm test
```

These commands exercise synthetic data only. They neither connect to nor alter the running `outlook-hub` project.

## LEGACY CONDITION / DEFERRED

- API scenario scripts exist but need controlled local credentials/data and cleanup; their current map status is source-verified rather than executed.
- The current backend unit suite is small and does not prove API/DB invariants.
- No operating DB backup/restore rehearsal is evidenced by this guide. A future plan must cover logical schema/data/full backups, roles/extensions/sequences, external files, encrypted retention, restore rehearsal, row counts, and key invariants without using production data as test fixtures.

## QA conduct

Do not delete/skip/weaken assertions to pass. Preserve traces/screenshots/video for failures without secrets or personal data. Do not run writer and independent QA concurrently in one worktree. LOW metadata corrections do not automatically open recursive QA loops.

## APPROVED migration rehearsal direction

`database/init.sql` bootstraps a new database. After baseline freeze, incremental
changes use Alembic and must include a backup/restore rehearsal plan, schema
comparison before initial operating stamp, row-count/invariant checks, and a
rollback point. This is a plan requirement, not authorization to access an
operating database.
