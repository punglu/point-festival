# First-development enforcement sequence

- Decision ID: `DEC-2026-004-first-development-enforcement-sequence`
- Title: `First-development enforcement sequence`
- Status: `DESIGN_APPROVED`
- Created at: `2026-07-31`
- Author: `PM decision`
- Git ref: `6c633679c6708a21920f0e4b306bc1e36a2ea72d` (decision baseline)
- Environment: `repository policy; no CI, lint guard, or fixture provisioned`
- Evidence: `PM direction in MONGLE-DEVELOPMENT-ENFORCEMENT-PLAN-001`
- Supersedes: `NONE`
- secrets_redacted: `true`

## Decision

The current project sequence remains unchanged: receive DATA-A, then review
the A1/DATA contracts. No implementation task below starts before that review.
After it, agents must execute the following approved task plans before relying
on the affected capability in feature delivery:

| Priority | Reserved Task ID | Required result | Start condition |
| --- | --- | --- | --- |
| 1 | `MONGLE-CI-BASELINE-GATES-001` | A first-PR blocking CI gate using measured non-destructive smoke commands; exactly one Alembic head; Python service-slice dotted-call static guard. | DATA-A/A1 contract review complete and commands/config scope approved. |
| 2 | `MONGLE-TEST-SPEC-NAMING-CONVENTION-001` | A new-spec-only naming convention and migration-free adoption rule. | Before creating a new test spec; existing specs are not renamed. |
| 3 | `MONGLE-E2E-SYNTHETIC-FIXTURE-PROVISIONING-001` | Provisioned `e2e_tester` synthetic identity, isolated fixture lifecycle, marker/PK cleanup, and repeat-safe evidence. | DATA-A determines account/role/data contract and PM approves DB/fixture implementation. |

The CI task checks Alembic's single-head invariant on every migration change;
if heads diverge, a merge revision is required immediately. The static guard
applies to Python decomposed service slices; do not substitute a frontend-only
ESLint rule for it. The CI task must use actual repository commands and may not
claim Tier A automation until those commands are measured.

Golden Journeys and final Tier labels remain deferred until sufficient real
specs and workflows exist. Feature tasks still follow the event-matrix and
synthetic-data contract in
[`DEC-2026-003-e2e-synthetic-data-and-event-matrix.md`](DEC-2026-003-e2e-synthetic-data-and-event-matrix.md).

## Enforcement

Agents must not silently bypass these preconditions, create an operating-data
fixture, introduce a new spec before the naming decision, or treat a migration
branch as acceptable. Missing prerequisites are reported as `HUMAN_GATE`,
`ENVIRONMENT_REQUIRED`, or the applicable Test Policy BLOCKED category—not
worked around in a feature task.
