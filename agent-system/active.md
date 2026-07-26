# Active Tasks

Only open tasks belong here. Lifecycle, decision, verification, and execution
are separate axes.

## PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001

- Task ID: PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_REQUIRED
- Handoff: agent-system/handoffs/active/PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001.md
- QA Evidence: agent-system/qa/PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001.md
- Independent QA: not_applicable — contract design; Foundation implementation requires independent QA
- Next Action: PM review of five bounded Phase 1 architecture gates before Foundation implementation

## PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001

- Task ID: PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: PASS
- Execution: SUCCEEDED
- Phase Note: PHASE0 LEGACY CONTAINMENT COMPLETE / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001.md
- QA Evidence: agent-system/qa/PHASE0-LEGACY-CONTAINMENT-AND-REFERENCE-BASELINE-001.md
- Independent QA: complete — PASS (independent read-only security QA)
- Next Action: Phase 0 automated baseline is ready for PM closeout confirmation; push is authorized by this task's passing conditions

## PHASE0-AUTOMATED-GAP-CLOSEOUT-001

- Task ID: PHASE0-AUTOMATED-GAP-CLOSEOUT-001
- Lifecycle: SUSPENDED
- Decision: DESIGN_APPROVED
- Verification: BLOCKED
- Execution: FAILED
- Phase Note: BLOCKED / CORE DEFECT — CURRENT USER OWNERSHIP AND MUTATION AUTHORIZATION
- Handoff: agent-system/handoffs/active/PHASE0-AUTOMATED-GAP-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/PHASE0-AUTOMATED-GAP-CLOSEOUT-001.md
- Independent QA: required for a follow-up core authorization/ownership fix
- Next Action: PM triage and a bounded core authorization/ownership repair task; do not resume automated closeout or push first

## PHASE0-DEV-RUNTIME-RECOVERY-001

- Task ID: PHASE0-DEV-RUNTIME-RECOVERY-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / SELF_CHECKED
- Handoff: agent-system/handoffs/active/PHASE0-DEV-RUNTIME-RECOVERY-001.md
- QA Evidence: agent-system/qa/PHASE0-DEV-RUNTIME-RECOVERY-001.md
- Independent QA: not_applicable — tooling and isolated runtime self-check
- Next Action: PM review; retain the isolated runtime volume only if follow-up regression work needs it

## PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001

- Task ID: PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: IMPLEMENTED / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001.md
- QA Evidence: agent-system/qa/PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001.md
- Independent QA: not_applicable — documentation localization; PM review required
- Next Action: PM review of localized engineering contracts and five bounded gates

## PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001

- Task ID: PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: NOT_TESTED
- Execution: SUCCEEDED
- Phase Note: PHASE0 AUTOMATED BASELINE COMPLETE / PM_REVIEW_PENDING
- Handoff: agent-system/handoffs/active/PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001.md
- QA Evidence: agent-system/qa/PHASE0-ENGINEERING-BASELINE-CLOSEOUT-001.md
- Independent QA: not_applicable — implementation changed docs, tooling, generated API types, and tests only; no core code or contract behavior changed
- Next Action: PM review, then PHASE0-DEVICE-AND-OPERATIONS-GATE-001 for physical-device and operating-DB rehearsal gates
