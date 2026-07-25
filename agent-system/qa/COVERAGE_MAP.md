# Coverage Map v0.1

`Git Ref` is the commit whose source paths were inspected; it is not a test
execution result. Observed from source on `2026-07-26`; no listed test was run for this policy
addition. Three executable API scripts were relocated from `docs/` to
`tests/api/`; only invocation-path comments and trailing whitespace changed.
This map is an index, not a backlog.

| Journey ID | User or system behavior | Tier | Test Path | Evidence Level | Last Verified | Git Ref | Known Gap |
|---|---|---|---|---|---|---|---|
| `BE-WEEK-001` | Week range and same-week classification | `TIER 1 UNIT` | `backend/tests/test_weekly.py` | `SOURCE_VERIFIED` | `NOT_RUN_IN_THIS_TASK` | `e2a6f08` | Runner/dependency setup unverified. |
| `API-WEEKLY-001` | Weekly APIs, authorization, and response shape | `TIER 2 INTEGRATION` | `tests/api/test_weekly_api.sh` | `SOURCE_VERIFIED` | `NOT_RUN_IN_THIS_TASK` | `e2a6f08` | Local API, seeded credentials, and mutable endpoint access required. |
| `API-SCENARIO-001` | Mission, proposal, deduction, notification, and related API flows | `TIER 3 JOURNEY` | `tests/api/e2e_scenario_test.py`; `tests/api/e2e_scenario_test_v2.py` | `SOURCE_VERIFIED` | `NOT_RUN_IN_THIS_TASK` | `e2a6f08` | Local API, seeded data/credentials, and cleanup effects require controlled runtime. |
| `E2E-LOGIN-001` | Player selection and PIN dashboard transition | `TIER 3 JOURNEY` | `tests/e2e/specs/01-login.spec.ts` | `SOURCE_VERIFIED` | `NOT_RUN_IN_THIS_TASK` | `e2a6f08` | Docker-backed runtime and credentials not run. |
| `E2E-MISSION-001` | Logged-in mission list and proposal control visibility | `TIER 3 JOURNEY` | `tests/e2e/specs/02-mission.spec.ts` | `SOURCE_VERIFIED` | `NOT_RUN_IN_THIS_TASK` | `e2a6f08` | Docker-backed runtime and credentials not run. |
| `E2E-ADMIN-001` | Admin entry form and post-login route | `TIER 3 JOURNEY` | `tests/e2e/specs/03-admin.spec.ts` | `SOURCE_VERIFIED` | `NOT_RUN_IN_THIS_TASK` | `e2a6f08` | Docker-backed runtime and credentials not run. |
| `E2E-FLOW-001` | Player logout and administrator access workflow | `TIER 3 JOURNEY` | `tests/e2e/specs/04-flow.spec.ts` | `SOURCE_VERIFIED` | `NOT_RUN_IN_THIS_TASK` | `e2a6f08` | Docker-backed runtime and credentials not run. |

Add rows bottom-up when a real test is added or verified. Keep per-task commands
and raw results in Task QA evidence, not here.
