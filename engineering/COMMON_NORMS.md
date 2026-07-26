# Common Engineering Norms

**Status: APPROVED_WITH_DECISIONS / v0.1 (2026-07-26).**

## CURRENT CONTRACT — authority and safety

- Git worktree is implementation SSOT; Drive is a review/evidence layer. Source: `AGENTS.md`, `agent-system/rules.md`.
- Existing user-owned dirty files are never reset, cleaned, staged, or rewritten by an unrelated task. Source: `agent-system/rules.md`.
- `docs/` is user-managed. Canonical engineering policy belongs here, not in `docs/`. Source: `AGENTS.md`.
- Backend is the final authority for authentication, authorization, and durable state. Frontend guards are UX controls. Sources: `backend/app/dependencies.py`, `frontend/src/App.tsx`, and the family-platform Common Norms draft.
- The current app is a modular monolith organized primarily as `backend/app/domains/<domain>` and `frontend/src/pages/<surface>` with shared frontend infrastructure. Sources: `backend/app/main.py`, `frontend/src/pages/`, `frontend/src/shared/`.

## TARGET CONTRACT — responsibility boundary

Use this decision order for new or materially changed code:

| Concern | Home | Constraint |
| --- | --- | --- |
| HTTP parsing, dependencies, response serialization | router | Keep orchestration thin; do not grow domain policy here. |
| use-case coordination, writes, external side effects | service | Keep each operation's transaction boundary explicit. |
| pure transition/eligibility decision | pure helper or `rules` | Use only where state logic is non-trivial; no DB/network side effects. |
| API request/response form | Pydantic schema | Treat changed fields as API-contract changes. |
| durable storage | SQLAlchemy model + approved DB mechanism | Do not change schema without migration-policy approval. |
| shared FE transport/auth state | `frontend/src/shared/` | Feature endpoints remain close to their consuming page/feature. |

This adopts the useful thin-router/service/pure-rule separation from Outlook and Viblot, adapted to the current code rather than imposing their folder trees.

## TARGET CONTRACT — dependency and reuse discipline

- Keep capability code local until a second real use demonstrates a shared abstraction; do not create `_v2`, `new`, or speculative common modules. Source: Viblot drafts, adapted to current `pages/` structure.
- A shared/platform layer must not take a dependency on a specific page/domain.
- Keep transport centralized (`frontend/src/shared/api/httpClient.ts`) and keep capability endpoint mappings near consumers (for example `pages/Auth/api/authApi.ts` and `pages/UserDashboard/api/dashboardApi.ts`).
- Do not duplicate backend authorization or transition enforcement in frontend code. A UI may disable or hide an action, but the server decides.

## CURRENT CONTRACT — task and evidence

- Separate lifecycle, execution, verification, independent QA, PM approval, and push approval. Source: `agent-system/rules.md`.
- New Agent System tasks use Closeout Contract v1 and synchronize active, handoff, QA evidence, and Coverage Map review. A closeout gate is not QA PASS. Source: `agent-system/rules.md`.

## TARGET CONTRACT — risk-based QA

- DB/schema/migration, authentication/RBAC/ownership, transaction/idempotency, core mission/point/level logic, and API contracts require independent QA.
- General UI, responsive behavior, navigation, forms, and user journeys use Playwright as the primary verification layer.
- Documentation, link, metadata, and lifecycle-only work use self-check/static checks unless they reveal a product-risk defect.
- Do not create recursive QA correction loops for LOW metadata findings.
- Writer and QA do not change the same worktree concurrently.

Source: `agent-system/qa/TEST_POLICY.md`, family-platform Testing draft, and approved Agent System policy.

## LEGACY CONDITION — current variation

Existing domain code has different transaction conventions and a mix of route and service responsibilities. It remains compatible behavior, not proof that new work may choose arbitrarily. See the backend guide and PM_GATE-01.

## LEGACY REFERENCE / NOT FULLY VALIDATED

The contained MarkPoint implementation is a reference for journeys, language,
data meaning, and migration candidates only. It must not be copied as a platform
contract for authorization, caller-supplied IDs, API shape, transactions, state
transitions, idempotency, error handling, silent failure behavior, or frontend
types. New-platform contracts take precedence when they differ.

## APPROVED DECISIONS — 2026-07-26

1. **Transaction ownership:** use-case Unit of Work owns one commit/rollback;
   routers, services, and helpers are no-commit. Existing mixed commits are
   LEGACY and migrate only with the modified domain.
2. **API responses:** retain existing response compatibility; new singleton
   endpoints return typed bodies and new lists prefer `{items,total,cursor?}`.
   Standard error shape is a TARGET, not a global retrofit.
3. **Migration SSOT:** `database/init.sql` is bootstrap; after baseline freeze,
   Alembic is the incremental migration SSOT. Backup/restore rehearsal precedes
   operating DB adoption.
4. **Wire types:** Phase 0–1 uses OpenAPI-generated types at API boundaries;
   generated files are never hand-edited and feature/view models remain local.
5. **Rules/guards:** pure rules cover high-risk transitions only; common BE
   guards cover auth, RBAC, ownership, tenant boundaries, and IDOR. FE rules are
   UX-only.

The approval evidence and rollout limits are in [Provenance and PM gates](PROVENANCE_AND_PM_GATES.md).
