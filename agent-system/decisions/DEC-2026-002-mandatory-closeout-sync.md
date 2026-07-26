# Mandatory task closeout synchronization

- Decision ID: `DEC-2026-002-mandatory-closeout-sync`
- Title: `Mandatory task closeout synchronization`
- Status: `DESIGN_APPROVED`
- Created at: `2026-07-26`
- Author: `PM-approved Task CLOSEOUT-GATE-001`
- Git ref: `7d31e99c25579cc2760c379f13a6361dc439cee2` (implementation commit)
- Environment: `repository policy`
- Evidence: `CLOSEOUT-GATE-001 implementation evidence and report-only static checker`
- Supersedes: `DEC-2026-001-agent-system-v0.1`
- secrets_redacted: `true`

## Decision

1. Every new task uses Closeout Contract v1 and reviews active, handoff, QA
   evidence, and Coverage Map before its normal end report.
2. Coverage Map review is mandatory; its file changes only for a real coverage
   impact. A no-change result records a specific reason.
3. A missing or blocked contract area prevents a normal completion report.
4. Implementation self-check does not replace independent QA.
5. Historical records are not batch-rewritten. Open work adopts the contract on
   its next modification.
6. Git remains the implementation SSOT. Drive remains a snapshot and
   cross-review layer.
