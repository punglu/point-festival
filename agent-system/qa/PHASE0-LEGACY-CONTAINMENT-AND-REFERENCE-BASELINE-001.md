# PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001 Implementation Evidence

- Task ID: `PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001`
- author/agent: `Codex`
- observed_at: `2026-07-26`
- git_ref: `773fb92c49f67e4136019362f67d6b6d405f8ba5`
- environment: `local macOS workspace; isolated mc_phase0 runtime (PostgreSQL 15432, API 18000, frontend 13000)`
- secrets_redacted: `true`
- Verification: `QA_PENDING`
- Self-check only: `true`
- Independent QA: `complete — PASS`
- Git repository is SSOT.

## Scope reviewed

Legacy API containment in the current player/admin model, complete route security
classification, regression tests for authorization and rejected-request DB
invariants, and legacy-reference documentation. No family tenant, new role model,
schema change, calculation rewrite, or API-contract retrofit is in scope.

## Commands, exit codes, and results

- Isolated `mc_phase0` Compose build/start: exit 0; separate PostgreSQL 15432, API 18000, frontend 13000; existing `outlook-hub` containers untouched.
- Python compile and `cd backend && python3 -m pytest -q`: exit 0; 6 passed.
- Frontend lint/build under Volta Node 20.19.0/npm 10.8.2: exit 0.
- `tests/api/test_weekly_api.sh`: exit 0; 6/6 passed.
- `tests/api/legacy_auth_boundary_test.py`: exit 0. It proves anonymous/cross-user rejection, administrator cross-user success, rejected-request DB invariants, and A/B versus C chat-pair isolation.
- `tests/api/e2e_scenario_test_v2.py`: exit 0; 87/87 passed after management actions moved to administrator routes.
- `tests/e2e npm test`: exit 0; 9 passed.

## Findings

The predecessor task measured high-severity unauthenticated and cross-user
mission/point/notification exposure. This implementation adds common
current-player/self-ID guards, closes legacy management aliases to administrators,
scopes notification reads/writes to their current player, and records all observed
OpenAPI operations in the security matrix. No schema, tenant, point/level
calculation, or API-response retrofit was made.

## Final QA verdict

Independent read-only security QA completed with `PASS` on the committed
implementation/test candidate. It measured 91 OpenAPI operations and 91 matrix
entries with no mismatch; 87 protected operations had OpenAPI security metadata,
four explicit public operations did not, and no sensitive anonymous operation
returned an unexpected 2xx. It independently verified A-to-B mission/point/
notification denial, administrator preservation, chat pair isolation, rejected
request DB invariants, dirty preservation, and all required regression suites.

## Independent QA result

- Verdict: `PASS`
- QA mode: independent, read-only, isolated `mc_phase0` runtime
- Reviewed candidate: implementation `5a6ac98582f4da045878006724cd2eb35677ec0b`, tests `773fb92c49f67e4136019362f67d6b6d405f8ba5`, documentation baseline `a27327db78ebe489184c47f78b62426d0caa06d3`
- Corrections: none required
- Existing dirty SHA-256: preserved at `eae6f749b838eedb02780242c71d6cc285f97335f39d0728669f593877cbdf5f`

## Closeout review

- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED`
- QA EVIDENCE: `UPDATED`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: `new executable ownership/DB-invariant suite and route classification were added`
- CLOSEOUT GATE: `PASS`
