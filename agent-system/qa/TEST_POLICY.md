# Bottom-up Test Policy v0.1

## Boundary

This is a small operating policy, not a test inventory or task log. Start from
tests that actually exist in the repository; do not claim future coverage.
Task-specific commands, raw output, and screenshots belong in
`agent-system/qa/<TASK-ID>.md`, which references this policy.

Implementation completion and test PASS are separate states. Where practical,
the implementer and independent QA are separate. Do not mark an unrun test as
PASS or make a test pass by deleting it, skipping it, or weakening assertions.
A regression fix needs a reproducible test where scope and environment permit.

Each executed result records command, exit code, environment, Git HEAD, and an
evidence location. Update `COVERAGE_MAP.md` when an actual test changes. Update
this policy only for a repeated operating problem or a new verification layer.

## Tiers

| Tier | Meaning |
|---|---|
| `TIER 0 STATIC` | Formatting, type, lint, build, or source-static checks. |
| `TIER 1 UNIT` | Isolated logic behavior. |
| `TIER 2 INTEGRATION` | Multiple application components or boundaries. |
| `TIER 3 JOURNEY` | User/system workflow across screens or services. |
| `TIER 4 RUNTIME_DEVICE` | Real runtime, device, browser, network, or install behavior. |

An absent or unexecuted tier is not PASS. If a required device or runtime is
unavailable, record `ENVIRONMENT_REQUIRED` with the missing environment.

## Result classification

| Result | Use when |
|---|---|
| `PASS` | Declared command succeeded with recorded evidence. |
| `PRODUCT_DEFECT` | Product behavior violates an intended assertion. |
| `TEST_DEFECT` | Test is invalid, stale, or incorrectly asserted. |
| `ENVIRONMENT_REQUIRED` | Required runtime, device, service, credential, or tool is unavailable. |
| `KNOWN_CONDITION` | Accepted condition affects the result; retain evidence. |
| `BLOCKED` | A concrete dependency prevents meaningful execution. |
| `HUMAN_GATE` | PM/owner decision is needed before proceeding. |

## Evidence and map rules

`COVERAGE_MAP.md` is a compact source-backed index, never a completion history.
Task QA evidence does not overwrite it; only real verification updates its
`Evidence Level`, `Last Verified`, or `Git Ref`. Do not copy raw task logs into
this policy or map. This policy is engine-neutral.
