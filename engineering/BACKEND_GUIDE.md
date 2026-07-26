# Backend Development Guide

## CURRENT CONTRACT — platform and layout

- FastAPI assembles routers in `backend/app/main.py`; the application uses an async lifespan and imports domain routers directly.
- Database access uses SQLAlchemy async engine/session factory in `backend/app/database.py` (`AsyncSessionLocal`, `AsyncSession`).
- Configuration uses `pydantic-settings` in `backend/app/config.py`; the current file still uses nested `class Config`, so do not claim a completed ConfigDict migration.
- Backend capabilities are under `backend/app/domains/`, including `auth`, `player`, `mission`, `daily_point`, `chat`, `admin`, and `mission_template`. Models are also imported through `backend/app/models/all_models.py`.

## CURRENT CONTRACT — audited samples

| Area | Read paths | Observed contract |
| --- | --- | --- |
| Auth/account | `domains/auth/router.py`, `service.py`, `models.py`, `schema.py` | Async queries, bcrypt/JWT, soft-delete filters, service-owned commits in login paths. |
| Mission | `domains/mission/router.py`, `service.py`, models/schema | Route/service split; role transition mapping and `total_earned` synchronization; both flush and service commits occur. |
| Daily points/levels | `domains/daily_point/service.py`, `domains/level_tier/` | Point adjustments use async service calls and commits; level configuration is a separate domain. |
| Chat | `domains/chat/router.py`, `service.py` | Router commits after service operations; service flushes. |
| Admin/repeated mission | `domains/admin/router.py`, `domains/mission_template/router.py`, `service.py` | Admin dependency guards exist; template writes are committed at router boundary and propagate related mission/point changes. |

Do not infer universal ownership checks or response envelopes from one route. Several mission endpoints expose raw Pydantic/list/dict responses, while auth has typed responses; this is an observed compatibility condition.

## CURRENT CONTRACT — DB and schema

- `database/init.sql` initializes the local PostgreSQL schema and synthetic development data. It is mounted by Compose for a new volume.
- `backend/requirements.txt` includes Alembic, but this audit did not find a canonical project Alembic configuration/version chain. Therefore an Alembic workflow is not a current contract.
- Soft deletion appears in models and query filters such as `deleted_at.is_(None)` in auth/mission code. Treat it as an entity-specific compatibility behavior until a retention policy is approved.

## TARGET CONTRACT — router, service, and transaction discipline

1. Router code should parse/validate inputs, obtain dependencies, call a use case, and serialize a declared response. Keep cross-domain write logic out of new routers.
2. Services should coordinate business writes and cross-domain effects. A core operation must expose one understandable transaction boundary and avoid loop-level commits.
3. Use a pure helper/rules unit only for complex state eligibility (mission approval, point/level changes, role changes, subscription or chat membership). Do not create rules/guards files for simple CRUD.
4. Backend must enforce RBAC and resource ownership; frontend visibility is not an authorization decision. Dynamic SQL values/order keys must be bound or whitelisted.
5. For core writes, transitions, aggregate/ledger updates, migrations/backfills, and expensive queries, keep concise Intent/Query/Audit evidence close to the code. Do not impose Outlook's mandatory SQL comment on trivial pass-throughs.

Sources: family-platform Backend draft (adapted), Outlook BE guide (thin controller/security/query lessons), Viblot BE DRAFT (service/rules boundaries).

## LEGACY CONDITION — transaction and response variation

- Commits occur in both routers and services: examples include `domains/chat/router.py`, `domains/mission_template/router.py`, `domains/auth/service.py`, `domains/daily_point/service.py`, and `domains/mission/service.py`.
- Some routers include domain calculations or direct persistence calls, for example `domains/mission/router.py` and `domains/admin/router.py`.
- Pydantic settings still use `class Config` in `backend/app/config.py`.

Do not mechanically normalize these patterns in unrelated changes. Any behavioral refactor must be separately scoped and independently QAed.

## APPROVED DECISION-01 — async transaction boundary

**Evidence:** current async code commits in both layers; Outlook's current guide prefers router one-commit, while Viblot's DRAFT prefers service-owned transactions.

**Approved:** a top-level use-case Unit of Work opens the transaction, commits
once on success, and rolls back on error. Router/service/helper code is
no-commit; services may `add()`/`flush()`. Existing mixed commits remain LEGACY
until the relevant domain is deliberately migrated.

## APPROVED DECISION-02 — API response contract

Current endpoints return typed models, lists, and dictionaries; no repository-wide envelope exists. Preserve them. New singleton endpoints return typed bodies; new lists prefer `{items,total,cursor?}`. Standard error bodies (`code`, `message`, `details`, optional `trace_id`) are a TARGET and are not a global retrofit.

## APPROVED DECISION-03 — schema/migration SSOT

`database/init.sql` remains the new-DB bootstrap baseline. After baseline freeze,
Alembic is the incremental migration SSOT; ORM changes and revisions travel
together. Operating DB work requires schema comparison, backup, and restore
rehearsal before a first stamp.

## APPROVED DECISION-04 — OpenAPI type contract

Pydantic/OpenAPI are the Phase 0–1 wire source. Generate types at the API
boundary, never edit generated output, and map to feature/view types internally.
Reconsider a contracts package only for independently versioned WebSocket or
multi-runtime contracts.

## Backend verification minimums

For core API changes, verify normal, validation, unauthenticated, permission or ownership, not-found, forbidden transition, and invariant/rollback outcomes against an isolated synthetic DB. Existing executable evidence is indexed in `agent-system/qa/COVERAGE_MAP.md`; do not describe unrun scenarios as PASS.
