# Family Platform Engineering Guides

## Status and authority

**Status: APPROVED_WITH_DECISIONS / v0.1 (2026-07-26).** The five previously
bounded PM gates are approved decisions; their implementation rollout remains
subject to the CURRENT/TARGET/LEGACY labels below.

These guides localize the directly reviewed Outlook Hub and Viblot materials for this repository. They are a repository-local development reference, not a replacement for source, runtime evidence, PM decisions, or Agent System rules.

Authority order is: PM decision, measured repository/runtime evidence, this guide, then external source guidance. `docs/` is user-managed; this `engineering/` directory is the canonical local location for these guides.

Every rule is marked as one of:

- **CURRENT CONTRACT** — observed in the current repository.
- **TARGET CONTRACT** — required for new or materially changed code after PM review where the current implementation is inconsistent.
- **LEGACY CONDITION** — observed, retained for compatibility, and not a model for new code.
- **PM_GATE** — a decision that cannot be made by documentation alone.
- **DEFERRED** — useful direction with no approved implementation time.

## Guide index

| Guide | Purpose |
| --- | --- |
| [Common norms](COMMON_NORMS.md) | authority, boundaries, server authority, QA, and change safety |
| [Backend guide](BACKEND_GUIDE.md) | FastAPI/async SQLAlchemy domain practices and API/DB gates |
| [Frontend guide](FRONTEND_GUIDE.md) | React/Vite page structure, transport, state, UI, PWA, and journeys |
| [Testing guide](TESTING_GUIDE.md) | test tiers, isolated runtime, evidence, and device work |
| [Operating DB backup and migration plan](OPERATING_DB_BACKUP_MIGRATION_PLAN.md) | approval-bound backup, restore, and initial Alembic adoption plan |
| [Provenance and PM gates](PROVENANCE_AND_PM_GATES.md) | adoption record and unresolved architectural choices |

## Direct source set

The following Drive documents were read directly on 2026-07-26 before this localization. They remain external reference material, not local SSOT.

| Family | Documents |
| --- | --- |
| Outlook Hub originals | Backend development guide; Frontend development guide |
| Viblot originals | Cross-Cutting Norms DRAFT; Backend Guide DRAFT; Frontend Guide DRAFT |
| Family-platform drafts | Integrated README; Common Norms; Backend; Frontend; Testing & QA; Provenance & PM Gates |

The concrete source-document IDs and the adoption decisions are retained in [Provenance and PM gates](PROVENANCE_AND_PM_GATES.md).

## How to use a guide

1. Inspect the affected source paths and tests first.
2. Apply a **CURRENT CONTRACT** without reinterpreting it.
3. Do not turn a **TARGET CONTRACT**, **DEFERRED** item, or **PM_GATE** into an implementation decision without its required approval.
4. Record actual commands, HEAD, environment, and unrun checks in task evidence.
5. Update this guide only when a source-backed contract or PM decision changes; do not use it as a task log.

## Current repository anchors

- Backend application/router assembly: `backend/app/main.py`
- Async session factory: `backend/app/database.py`
- Bootstrap schema and synthetic seed: `database/init.sql`
- Frontend routes: `frontend/src/App.tsx`
- Shared HTTP client and session-expiry behavior: `frontend/src/shared/api/httpClient.ts`
- Existing test policy and evidence map: `agent-system/qa/TEST_POLICY.md` and `agent-system/qa/COVERAGE_MAP.md`

## Legacy implementation status

The current MarkPoint implementation is **LEGACY REFERENCE / NOT FULLY
VALIDATED**. It is useful for workflow, vocabulary, data-meaning, and migration
research, but it is not a source of truth for authorization, API, transaction,
ownership, state-transition, idempotency, error-handling, or frontend type
contracts. See [Legacy reference baseline](LEGACY_MARKPOINT_REFERENCE.md) and
[Legacy API security matrix](LEGACY_API_SECURITY_MATRIX.md).

## Deliberately not decided here

The approved decisions choose a UoW direction, compatibility-first responses,
`init.sql` bootstrap plus future Alembic increments, OpenAPI-generated boundary
types, and scoped rules/guards. They do not retroactively rewrite current code.
