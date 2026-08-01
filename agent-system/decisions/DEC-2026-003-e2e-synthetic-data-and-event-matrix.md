# E2E synthetic-data boundary and event-matrix contract

- Decision ID: `DEC-2026-003-e2e-synthetic-data-and-event-matrix`
- Title: `E2E synthetic-data boundary and event-matrix contract`
- Status: `DESIGN_APPROVED`
- Created at: `2026-07-31`
- Author: `PM decision`
- Git ref: `6c633679c6708a21920f0e4b306bc1e36a2ea72d` (decision baseline)
- Environment: `repository policy; no account or fixture provisioned`
- Evidence: `PM direction in MONGLE-E2E-DATA-BOUNDARY-AND-EVENT-MATRIX-001`
- Supersedes: `NONE`
- secrets_redacted: `true`

## Decision

1. `e2e_tester` is reserved as the logical identity for synthetic E2E testing;
   it is not an operating user, credential, fixture row, or permission grant.
   Creation, roles, fixture shape, and cleanup are deferred until DATA-A
   contract review and a separately approved implementation task.
2. Automated tests use only isolated synthetic data. They must not create,
   read as fixtures, alter, or delete operating business data, an operating DB,
   or NAS data. Without an isolated environment and approved fixture lifecycle,
   the scenario is `UNSAFE_ON_SHARED_DB`.
3. Before implementing a feature with a user or system event, the feature task
   records an event-branch matrix in its handoff or approved feature contract.
   Every row identifies event, precondition/actor, API expectation, durable
   state expectation where applicable, UI expectation where applicable, test
   level/evidence, and cleanup requirement.
4. A filter or selector matrix includes every supported value and approved
   combination plus initial/default state, reset, empty result, invalid input
   where accepted by the API, and authorization-dependent result where
   applicable. API expectations are the backend source of truth; UI assertions
   verify their faithful presentation.
5. The matrix is a design and selection aid, not permission to expand tests.
   At completion, follow the existing-test-first and minimum-new-test policy.
   The independent Test Agent checks the matrix against diff, source, selected
   tests, and actual execution evidence.

## Non-decisions

- This decision creates no user account, secret, DB row, fixture framework,
  script, CI workflow, or production access.
- It does not define unmeasured product filters, roles, event branches, or
  expected values; those are feature-contract facts.
