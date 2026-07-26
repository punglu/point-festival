# Active Tasks

Only open tasks belong here. Lifecycle, decision, verification, and execution
are separate axes.

## AGENT-SYSTEM-V0.1-IMPLEMENT-001

- Task ID: `AGENT-SYSTEM-V0.1-IMPLEMENT-001`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Implementer: `Codex /root`
- QA: `independent Codex pending`
- Phase note: `IMPLEMENTED / QA_PENDING`
- Handoff: `agent-system/handoffs/active/AGENT-SYSTEM-V0.1-IMPLEMENT-001.md`
- Declared scope: `AGENTS.md` and `agent-system/**` only

## AGENT-SYSTEM-V0.1-FIX-001

- Task ID: `AGENT-SYSTEM-V0.1-FIX-001`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Implementer: `Codex /root`
- QA: `independent Codex pending`
- Phase note: `IMPLEMENTED / QA_PENDING`
- Handoff: `agent-system/handoffs/active/AGENT-SYSTEM-V0.1-FIX-001.md`
- Declared scope: `CLAUDE.md`, `AGENTS.md`, `agent-system/qa/**`, `agent-system/tools/check_decision_ids.py`, active/relay/handoff state only

## AGENT-SYSTEM-V0.1-FIX-002

- Task ID: `AGENT-SYSTEM-V0.1-FIX-002`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Implementer: `Codex /root`
- QA: `independent Codex pending`
- Phase note: `IMPLEMENTED / QA_PENDING`
- Handoff: `agent-system/handoffs/active/AGENT-SYSTEM-V0.1-FIX-002.md`
- Declared scope: `agent-system/tools/check_decision_ids.py`, minimal rules/template updates, FIX-001 metadata supplement, and active/relay/handoff/QA state only

## AGENT-SYSTEM-V0.1-FIX-003

- Task ID: `AGENT-SYSTEM-V0.1-FIX-003`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Implementer: `Codex /root`
- QA: `independent Codex pending`
- Phase note: `IMPLEMENTED / QA_PENDING`
- Handoff: `agent-system/handoffs/active/AGENT-SYSTEM-V0.1-FIX-003.md`
- Declared scope: `FIX-002 local handoff metadata supplement and FIX-003 active/relay/handoff/QA evidence only`

## CLOSEOUT-GATE-001

- Task ID: `CLOSEOUT-GATE-001`
- Lifecycle: `SUSPENDED`
- Decision: `DESIGN_APPROVED`
- Verification: `BLOCKED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Implementer: `Codex /root`
- QA: `independent Codex QA BLOCKED`
- Phase note: `QA BLOCKED / FIX IN PROGRESS`
- Handoff: `agent-system/handoffs/active/CLOSEOUT-GATE-001.md`
- QA Evidence: `agent-system/qa/CLOSEOUT-GATE-001.md`
- Next action: `CLOSEOUT-GATE-FIX-001 must repair same-line field parsing and add a regression test before independent QA reruns`
- Blocking Task: `CLOSEOUT-ARCHIVE-AWARE-FIX-001`
- Declared scope: `Agent System closeout contract, report-only checker, templates, Decision, Coverage Map, and task evidence only`

## CLOSEOUT-GATE-FIX-001

- Task ID: `CLOSEOUT-GATE-FIX-001`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Implementer: `Codex /root`
- QA: `independent Codex pending`
- Phase note: `IMPLEMENTED / QA_PENDING`
- Handoff: `agent-system/handoffs/active/CLOSEOUT-GATE-FIX-001.md`
- QA Evidence: `agent-system/qa/CLOSEOUT-GATE-FIX-001.md`
- Next action: `Independent Codex QA must re-run empty-reason, CRLF, field-absence, parser, and 23-fixture checks plus correction evidence review`
- Declared scope: `Agent System closeout parser, regression test, task evidence, Coverage Map, and active/relay state only`

## CLOSEOUT-ARCHIVE-AWARE-FIX-001

- Task ID: `CLOSEOUT-ARCHIVE-AWARE-FIX-001`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Implementer: `Codex /root`
- QA: `independent Codex pending`
- Phase note: `IMPLEMENTED / QA_PENDING`
- Handoff: `agent-system/handoffs/active/CLOSEOUT-ARCHIVE-AWARE-FIX-001.md`
- QA Evidence: `agent-system/qa/CLOSEOUT-ARCHIVE-AWARE-FIX-001.md`
- Next action: `Independent Codex QA must verify OPEN/ARCHIVED lifecycle classification, parser regression coverage, archive fixtures, and existing dirty-state preservation`
- Declared scope: `agent-system/tools/check_closeout.py`, `agent-system/tests/test_check_closeout.py`, Coverage Map, and task active/relay/handoff/QA evidence only`

## CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001

- Task ID: `CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Implementer: `Codex /root/regression_fixture_persistence_writer`
- QA: `independent Codex pending`
- Phase note: `IMPLEMENTED / QA_PENDING`
- Handoff: `agent-system/handoffs/active/CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001.md`
- QA Evidence: `agent-system/qa/CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001.md`
- Next action: `Independent Codex QA must verify the permanent matrix, historical evidence distinction, Finding 1 record, static checks, and dirty-state preservation`
- Declared scope: `agent-system/tests/test_check_closeout.py`, optional test-only fixtures, Coverage Map, and task active/relay/handoff/QA evidence only`
