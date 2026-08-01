# Regression Candidates

This is a backlog of repeatable defect classes, not a bug log and not evidence
that a candidate has a test. Policy and final Coverage Map state remain in
[`agent-system/qa/TEST_POLICY.md`](../../agent-system/qa/TEST_POLICY.md) and
[`agent-system/qa/COVERAGE_MAP.md`](../../agent-system/qa/COVERAGE_MAP.md).

| ID | Pattern | Product Area | Status | First Observed | Last Observed | Root Cause | Detection Evidence | Recommended Guard | Related Tests | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `REG-001` | Seed-time-dependent visual delta in otherwise identical isolated browser captures | E2E harness | `CANDIDATE` | 2026-07-31 | 2026-07-31 | `Mission` model timestamp default was identified in the recorded Foundation closeout; no new root-cause audit performed here | `agent-system/qa/COVERAGE_MAP.md` row `E2E-MONGLE-WAVE6-1-001` | Compare stable UI signals and explicitly classify seeded timestamps; do not weaken visual assertions | `tests/e2e/specs-mongle/01-shell.spec.ts` | `HIGH_CONFIDENCE_INFERENCE`; candidate only, no new test authorized by this task. |
