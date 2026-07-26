# PHASE0-AUTOMATED-GAP-CLOSEOUT-001 Implementation Evidence

- Task ID: `PHASE0-AUTOMATED-GAP-CLOSEOUT-001`
- author/agent: `Codex`
- observed_at: `2026-07-26`
- git_ref: `163d577f103dc31ea7baaa3caba2a705ed9834b8`
- environment: `local macOS workspace; isolated mc_phase0 synthetic runtime (PostgreSQL 15432, API 18000, frontend 13000)`
- secrets_redacted: `true`
- Verification: `QA_PENDING`
- Self-check only: `true`
- Independent QA: `not_applicable unless a core product fix is required`
- Git repository is SSOT.

## Scope reviewed

Current user ownership, role boundaries, chat 1:1 boundary, duplicate-request
characterization, point/level/repeating-mission aggregates, existing Playwright
journeys, and safe synthetic capture evidence. `PHASE1 FAMILY TENANT — NOT YET
DEFINED` is outside this evidence.

## Commands, exit codes, and results

- `docker compose -p mc_phase0 --env-file .env.phase0.example -f docker-compose.phase0.yml up -d --build`: exit 0. The Phase 0 backend, frontend, and database became healthy without changing `outlook-hub` containers.
- `curl -fsS http://localhost:18000/api/health`, `curl -fsS http://localhost:18000/openapi.json`, and `curl -fsS http://localhost:13000/`: exit 0. (The initial non-canonical `/health` probe returned 404; source defines `/api/health`.)
- Synthetic ownership requests against `http://localhost:18000`:
  - unauthenticated Player B mission list: 200 and four Player B rows;
  - Player A bearer token reading Player B mission list: 200 and four Player B rows;
  - Player A bearer token creating a Player B mission: 201;
  - unauthenticated deletion of that newly-created synthetic mission: 204;
  - unauthenticated Player B point summary: 200, including Player B aggregate fields;
  - unauthenticated notification list: 200.
- Current protected comparisons:
  - unauthenticated and Player A access to admin-only mission-template list: 401;
  - unauthenticated chat partners: 401;
  - authenticated Player A chat partners: 200;
  - Player A-to-B synthetic 1:1 send: 201; Player B pair history for A: 200 with one matching message.

All mutations were confined to the disposable synthetic Phase 0 database. The created mission was soft-deleted by the measured unauthenticated endpoint; the sent 1:1 probe message remains inside only that isolated database volume.

## Findings

1. **HIGH — PRODUCT_DEFECT — CURRENT USER OWNERSHIP / IDOR.** Mission and daily-point read routes accept a caller-controlled `player_id` without authentication or ownership validation. Reproduce with the requests above; both anonymous callers and Player A received Player B data. Impact: direct disclosure of another current user's mission and aggregate point data.
2. **HIGH — PRODUCT_DEFECT — CURRENT ROLE BOUNDARY / unauthorized mutation.** `POST /api/missions/` accepts Player A's token and a body targeting Player B, and `DELETE /api/missions/{id}` accepts no bearer token. Impact: unauthorized creation and soft deletion of another current user's mission.
3. **HIGH — PRODUCT_DEFECT — notification exposure.** `GET /api/notifications/` returns 200 without authentication. Impact: notification data is not scoped to an authenticated current user.
4. **PASS (limited) — CURRENT CHAT PARTICIPANT BOUNDARY.** The existing chat router requires a bearer token and its history query is restricted to the authenticated user and requested partner. This does not establish a room/participant model; `PHASE2 ROOM PARTICIPANT MODEL — DEFERRED` remains unchanged.

The first three findings meet the task's core-defect stop condition. No product code, schema, authentication, RBAC, or API contract was changed. Push is not authorized by the task conditions.

## Final QA verdict

`BLOCKED / CORE DEFECT`. This implementation evidence is not independent QA and cannot declare PASS. A bounded authorization/ownership repair followed by independent QA is required before Phase 0 automated closeout can resume.

## Closeout review

- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED`
- QA EVIDENCE: `UPDATED`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: `measured isolated-runtime ownership/role findings were recorded; no incomplete capture or regression expansion is represented as covered`
- CLOSEOUT GATE: `BLOCKED`
