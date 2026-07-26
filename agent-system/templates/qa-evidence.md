# QA Evidence Template

- Task ID: ``
- author/agent: ``
- observed_at: ``
- git_ref: ``
- environment: ``
- evidence: ``
- secrets_redacted: `true`
- Verification: `NOT_TESTED`
- Closeout Contract: `v1`
- Independent from implementer: `false`
- Independent QA: `pending`

## Scope reviewed

## Commands, exit codes, and results

## Findings

## Final QA verdict

Implementation evidence records self-check only and uses `Verification:
QA_PENDING`; it cannot award final QA PASS. Independent QA records whether it
is independent and a verdict (`PASS`, `CONDITIONAL`, `BLOCKED`, or
`HUMAN_GATE`). Git is the SSOT; redact secrets.

## Closeout review

- ACTIVE: `UPDATED | BLOCKED`
- HANDOFF: `UPDATED | BLOCKED`
- QA EVIDENCE: `UPDATED | BLOCKED`
- COVERAGE MAP: `UPDATED | NO_CHANGE_REQUIRED | BLOCKED`
- COVERAGE MAP Reason:
- CLOSEOUT GATE: `PASS | BLOCKED`
