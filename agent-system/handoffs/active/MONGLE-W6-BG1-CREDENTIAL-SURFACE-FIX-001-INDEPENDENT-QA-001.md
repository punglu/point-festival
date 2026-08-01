# MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001

- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001
- Lifecycle: BLOCKED
- Decision: DESIGN_APPROVED
- Verification: BLOCKED
- Execution: SUCCEEDED
- Closeout Contract: v1

Independent QA found `resolve_account_from_session_claim` raises an unhandled
`ValueError` for a non-numeric Account-token `sid`. See the QA evidence for
fresh DB reproduction and the required repair/regression test.

## Closeout Synchronization

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: BLOCKED
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
