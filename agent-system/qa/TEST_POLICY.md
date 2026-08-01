# Test Policy

This is the operating-policy SSOT: when to select, run, classify, and update
tests. The current protection state is only in
[`COVERAGE_MAP.md`](COVERAGE_MAP.md); actual commands, environment, artifacts,
and cleanup are only in [`tests/README.md`](../../tests/README.md). Task-level
raw evidence belongs in `agent-system/qa/<TASK-ID>.md`.

## Feature 완료 후 safety net

Before implementation, apply the mandatory
[E2E synthetic-data boundary and event-matrix contract](../decisions/DEC-2026-003-e2e-synthetic-data-and-event-matrix.md).
It defines safe test identity/data boundaries and the feature event-branch
matrix; this policy remains the SSOT for test selection and coverage updates.

기능 구현 완료 후 COVERAGE_MAP.md와 기존 테스트를 실측한다.

변경 Feature를 보호하는 기존 핵심 Lifecycle 테스트를 우선 실행한다.

보호되지 않는 경우에만 회귀 가치가 명확한 최소 테스트 1건을 추가한다.

실제 실행해 PASS를 확인하고 Coverage Map을 갱신한다.

비차단 발견은 별도 백로그로 분리하며 테스트 확대나 아키텍처 개편으로
작업 범위를 넓히지 않는다.

Completion reporting records: (1) whether a Test Agent was delegated, (2) why
the selected test was relevant, (3) the actual PASS outcome, and (4) any
out-of-scope failure kept separate. Existing tests take priority: reuse them;
make only an evident stale correction; add one minimal core-flow test only when
unprotected; do not expand coverage without separate approval.

## Coverage measurement and confidence

Only the map stores a row's status. Allowed values are `COVERED`, `PARTIAL`,
`MISSING`, and `N/A`.

- `COVERED`: an assertion validates a real state change or meaningful outcome,
  and execution evidence exists.
- `PARTIAL`: entry, rendering, or weak existence protection covers only part of
  the behavior.
- `MISSING`: the feature exists but has no protecting spec/test.
- `N/A`: direct code, UI, or API evidence establishes that the feature does not
  exist; never infer this status.

One row has one status; split a mixed full/partial claim into rows. Every
status or causal explanation has one confidence value: `CONFIRMED`,
`HIGH_CONFIDENCE_INFERENCE`, or `NOT_CONFIRMED`. Do not use speculative wording
or present an unmeasured conclusion as confirmed.

`Measured = COVERED + PARTIAL + MISSING` (exclude `N/A`).

`Full Coverage = COVERED / Measured`.

`Effective Coverage = (COVERED × 1.0 + PARTIAL × 0.5) / Measured`.

These ratios are protection measurements, not targets. Do not add tests just
to increase them.

Lifecycle target is risk-based: `L0` no test; `L1` entry/read; `L2` core
branch; `L3` create/update/state reflection; `L4` error, authorization, and
cleanup. L4 is not universal.

## Golden Journey and execution tiers

A Golden Journey is a business-purpose unit, not a spec file. The current
framework is `GOLDEN_JOURNEY_FRAMEWORK: SKELETON_READY`; only evidence-backed
candidates belong in the map, and no journey count is fixed here.

| Tier | Operating rule |
| --- | --- |
| Tier A | Unauthenticated, non-destructive smoke; eligible for CI automation. |
| Tier B | Authenticated core journey; run locally or in isolated environment. |
| Tier B CONDITIONAL | Synthetic-row or accumulated-state risk; require repeat-run limit and cleanup. |
| Tier C | Dedicated environment, secret, or external system required; do not automate. |

Tier labels describe execution safety and coexist with the historical test-layer
labels (static/unit/integration/journey/device) retained in the map. Scripts
are defined only by their actual package/config source; absent automation is
`SCRIPT_NOT_YET_DEFINED`.

## BLOCKED conditions

`BLOCKED` means execution conditions are unavailable, not that a test failed.

| Category | Definition and example |
| --- | --- |
| `PRODUCT_DECISION_REQUIRED` | A required product choice is unresolved, e.g. expected authorization result has no approved rule. |
| `TEST_DATA_REQUIRED` | Required safe fixture/data is absent, e.g. no synthetic family can exercise a branch. |
| `ENVIRONMENT_REQUIRED` | Required runtime/tool is unavailable, e.g. isolated browser stack cannot start. |
| `EXTERNAL_DEPENDENCY` | A required external service is unavailable, e.g. an approved callback sandbox is down. |
| `PERMISSION_PATH_BROKEN` | The verification actor cannot reach the required authorized path, e.g. fixture role assignment is broken. |
| `PRODUCT_DEFECT` | A known product defect prevents the required state from being verified, e.g. a mutation cannot complete. |
| `LEGACY_OR_DEPRECATED` | The path is retained only for compatibility and is not safe to make an active baseline. |
| `UNSAFE_ON_SHARED_DB` | The scenario would irreversibly affect shared business data without isolated synthetic fixtures. |

## Executed failure classification

Classify every executed non-pass with evidence: `PRODUCT_DEFECT` (product
violates assertion), `TEST_DEFECT` (test is stale/invalid), `FIXTURE_OR_DATA`
(fixture data is wrong or contaminated), `ENVIRONMENT` (runtime/tool/service
failure), `KNOWN_CONDITION` (documented accepted limitation), or
`UNRELATED_FAILURE` (measurably outside selected scope). Never collapse these
into a generic test/environment/flaky statement.

## Data safety and emergency changes

Automation preference is read-only query/filter/toggle, then static options,
then exactly reversible soft-delete/toggle, then irreversible real-data change.
The fourth category is `UNSAFE_ON_SHARED_DB` unless it has isolated synthetic
fixtures. Synthetic writers require a marker, exact PKs, creation scope,
cleanup, business-data separation, and repeat-safe confirmation.

Emergency patches may not delete tests, add skip/disable, weaken assertions or
scope, mask failures with timeout/retry, or report an unrun test as PASS. An
operational correction gets only a clear-value minimal regression test; rerun
the existing baseline. A former PASS that fails blocks completion; an unrun
test records its BLOCKED reason.
