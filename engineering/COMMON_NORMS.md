# Common Engineering Norms

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

## PM_GATE / DEFERRED

- **PM_GATE-01:** canonical async transaction boundary.
- **PM_GATE-02:** API response-envelope strategy.
- **PM_GATE-03:** `database/init.sql` and Alembic/migration SSOT.
- **PM_GATE-04:** OpenAPI/generated types versus a contracts package.
- **PM_GATE-05:** scope for rules/guards in core transitions.

The five gates are deliberately capped; their evidence and options are in [Provenance and PM gates](PROVENANCE_AND_PM_GATES.md).
