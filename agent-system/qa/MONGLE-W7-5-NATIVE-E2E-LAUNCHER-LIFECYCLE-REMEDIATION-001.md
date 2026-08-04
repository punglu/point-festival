# Task QA Evidence — MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001

- Task ID: MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001

```text
Parent:  MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001
Finding: E2E-RUNTIME-F-001 (native launcher lifecycle defect, not a
         product/backend/Playwright/browser defect)
Status:  DEVELOPER_SELF_CHECK_COMPLETE -- NOT an Independent QA PASS
         declaration. A follow-up focused Independent Re-QA is expected.
```

Full narrative (root cause, exact script content, per-test evidence,
cleanup/git integrity detail) is in this task's own handoff:
`agent-system/handoffs/active/MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001.md`.

## Root cause

```text
E2E_NATIVE_LAUNCHER_LIFECYCLE_DEFECT (prior task's own launcher, now removed)
```

The prior launcher's own source is unavailable for direct diff-based
diagnosis (already cleaned up by its own author). Most plausible mechanism,
given this environment: the full lifecycle (DB + migrations + seed + backend
+ frontend readiness, measured close to a minute on its own in this task's
run) was most likely driven as a single **foreground** command inside a tool
whose default execution timeout (120s in this environment) would kill the
whole process tree — including its own backgrounded Backend/Vite — right
around when Playwright was starting, producing exactly the observed
"readiness passed, then 10/10 connection-refused" shape.

## Fix

```text
New file: tests/e2e/scripts/run-w75-full-spec-native.sh
```

Reuses `run-w75-full-spec.sh`'s own already-proven `( cd dir && exec ... ) &
PID=$!` construct verbatim (top-level scope; never inside `$(...)` command
substitution or a function whose return would end the backgrounding
subshell) for starting Backend/Vite, with `trap cleanup EXIT` registered
once at top level so it fires exactly once, after Playwright's own
foreground invocation returns. Adds beyond the existing pattern: a `kill -0`
liveness check inside each readiness-polling loop (not HTTP-only), a second
`kill -0` re-check for both PIDs immediately before Playwright starts, and a
post-Playwright liveness log for both PIDs. Invoked as a **background**
shell command this run, specifically to avoid the foreground-timeout failure
mode identified above. No product code, backend API, migration, seed,
Playwright spec, assertion, timeout, retry, or skip changed.

## Verification

```text
Lifecycle smoke (standalone, backend+frontend only, no Playwright):
  held 24s, 3 liveness+HTTP checks at ~8s intervals, all PASS, 0 premature exit

Full-stack native E2E (background invocation, unchanged spec):
  Both PIDs confirmed alive immediately before Playwright start
  10 passed, 0 failed, 0 skipped, 53.9s
  Both PIDs confirmed still alive immediately after Playwright finished

Cleanup: QA DB removed, both PIDs killed and confirmed dead, QA ports
  (18096/5195) confirmed free, runtime log directory auto-removed (exit 0),
  persistent dev stack (8000/5174) confirmed unaffected before and after.

Static checks: frontend lint PASS, frontend build PASS (pre-existing
  chunk-size warning only), bash -n syntax PASS, git diff --check clean,
  check_all.py 0 warnings for this task's own lineage.

git integrity: this task's own changes are additive only (1 new script,
  1 documentation section, its own handoff/QA/active/relay/Coverage Map
  records) -- 0 product/test/migration/seed/other-task files touched,
  confirmed via git status/diff before and after.
```

## 5-Gate Self-Check

- **Hallucination Guard**: the root cause is explicitly labeled a
  reconstruction, not a literal diagnosis, since the original launcher no
  longer exists to inspect -- this is disclosed rather than presented as
  measured fact. The 10/10 result is this task's own freshly executed run,
  not carried forward from the parent finding's own numbers.
- **Omission Guard**: this is a single run, not a repeat-run stability
  check -- disclosed as a "not independently measured" item in the handoff
  rather than silently generalized to "always passes."
- **Miswork Guard**: `git diff --check` clean; the QA database, both
  service PIDs, and the runtime log directory were all confirmed removed;
  the persistent dev stack was confirmed unaffected; no product/test file
  was touched.
- **Axis Alignment**: this closes `E2E-RUNTIME-F-001`'s own lifecycle-defect
  scope only. It does not declare
  `MONGLE_W7_5_MARKPOINT_CONDITIONAL_CLOSEOUT_INDEPENDENT_RE_QA_PASS`,
  `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`, W7.4 live-consumer-
  integration completion, or W7.6 readiness.
- **Freshness/Evidence Consistency**: every number above came from a
  command run in this session against current HEAD, using a database
  created fresh in this session and dropped at the end, not carried forward
  from any prior task's own report.

## Final Declaration

```text
E2E_RUNTIME_F_001_ROOT_CAUSE_IDENTIFIED (reconstructed, original script unavailable)
BACKEND_LIFECYCLE_HELD_UNTIL_PLAYWRIGHT_END
VITE_LIFECYCLE_HELD_UNTIL_PLAYWRIGHT_END
CLEANUP_EXECUTED_AFTER_PLAYWRIGHT
PLAYWRIGHT_EXIT_CODE_PRESERVED (0)

NODE_20_PASS
PLAYWRIGHT_1_58_2_PASS
CHROMIUM_V1208_PASS
NATIVE_ISOLATED_POSTGRESQL_PASS
CURRENT_BACKEND_PASS
CURRENT_VITE_PASS

E2E_10_PASSED
E2E_0_FAILED
E2E_0_SKIPPED

MOCK_API_ZERO
PERSISTENT_DEV_STACK_IMPACT_ZERO
QA_RESOURCE_RESIDUE_ZERO
RUNTIME_GIT_DIRTY_ZERO
EXISTING_DIRTY_DAMAGE_ZERO

MONGLE_W7_5_NATIVE_E2E_LAUNCHER_LIFECYCLE_REMEDIATION_COMPLETE
NATIVE_FULL_STACK_SERVICE_LIFECYCLE_SELF_CHECK_PASS
NON_DOCKER_FULL_STACK_E2E_DEVELOPER_SELF_CHECK_10_OF_10_PASS
RUNTIME_AND_CLEANUP_SELF_CHECK_PASS
READY_FOR_FINAL_W7_5_E2E_INDEPENDENT_QA
```

Not declared (per this task's own Section 17 restriction):
`MONGLE_W7_5_MARKPOINT_CONDITIONAL_CLOSEOUT_INDEPENDENT_RE_QA_PASS`,
`W7_5_CODE_DEFECT_HARDENING_SCOPE_CLOSED`,
`MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`,
`W7_4_LIVE_CONSUMER_INTEGRATION_PASS`,
`READY_FOR_W7_6_COMMON_COMPONENT_EXTRACTION`.

```text
W7.5: CONDITIONAL / HUMAN_GATE
W7.4: REOPENED / AUDIT PENDING
W7.6: BLOCKED
```

No commit, push, merge, or rebase was performed by this task.
