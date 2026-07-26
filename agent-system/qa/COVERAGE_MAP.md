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
| `AGENT-CLOSEOUT-001` | Detect missing or inconsistent mandatory Task closeout synchronization, including an empty `NO_CHANGE_REQUIRED` reason without cross-line value capture | `TIER 0 STATIC` | `agent-system/tools/check_closeout.py`; `agent-system/tests/test_check_closeout.py` | `SELF_CHECKED` | `2026-07-26` | `35ff2afac81d2886ba3d8797eb2d503ff280e40e` | Independent QA pending; report-only checker does not transition task state. The former empty-reason cross-line parsing defect is covered by a permanent stdlib regression test. |
| `AGENT-CLOSEOUT-002` | Distinguish OPEN Task closeout records from ARCHIVED handoff/graduated records; detect mixed, missing, duplicate, and stale-relay lifecycle artifacts without treating archived QA evidence as active work | `TIER 0 STATIC` | `agent-system/tools/check_closeout.py`; `agent-system/tests/test_check_closeout.py` | `SELF_CHECKED` | `2026-07-26` | `f399088e010c9db1a2e03abd382680e6d64c99db` | Independent QA pending; report-only checker validates archive lifecycle records but does not archive, graduate, or transition Task state. |
| `AGENT-CLOSEOUT-003` | Reproduce a source-backed Closeout Contract v1 regression matrix for OPEN/ARCHIVED artifact selection, invalid lifecycle combinations, report-only behavior, and current-repository warning-free execution | `TIER 0 STATIC` | `agent-system/tools/check_closeout.py`; `agent-system/tests/test_check_closeout.py` | `SELF_CHECKED` | `2026-07-26` | `e1ee71061606a20b94d175caeef2ed06386c7381` | Independent QA pending. Historical `23/23` was repository-external evidence; its full fixture definitions were not committed. The permanent matrix has its own measured case count. Follow-up candidate: internal-ID bucketing in `documents_by_task()` may make a mismatch-only branch unreachable for selected malformed artifacts. |

Add rows bottom-up when a real test is added or verified. Keep per-task commands
and raw results in Task QA evidence, not here.
