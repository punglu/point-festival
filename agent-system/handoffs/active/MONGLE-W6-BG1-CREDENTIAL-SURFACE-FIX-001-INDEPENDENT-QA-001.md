# MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001

- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001
- Lifecycle: IN_PROGRESS
- Decision: DESIGN_APPROVED
- Verification: CONDITIONAL
- Execution: SUCCEEDED
- Closeout Contract: v1

Initial independent QA found `resolve_account_from_session_claim` raised an
unhandled `ValueError` for a non-numeric Account-token `sid`. The repair was
then independently rechecked: six targeted HTTP tests passed twice on two
fresh disposable DBs and malformed claim probes returned 401. A complete
independent backend-suite run is still required; its attempted run was stopped
after 32 tests without a final result.

## Closeout Synchronization

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: BLOCKED
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001.md
