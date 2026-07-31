# PHASE0-DOC-STALENESS-PREVENTION-001

- Task ID: `PHASE0-DOC-STALENESS-PREVENTION-001`
- author/agent: Claude Code
- created_at: 2026-07-31
- git_ref: `8739008` (repository state this task started from)
- environment: local worktree, no runtime/DB involved
- evidence: `agent-system/rules.md`, `agent-system/templates/handoff.md`
- secrets_redacted: `true`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `8739008`
- End HEAD: `PENDING_METADATA_COMMIT` (this handoff is committed together with
  its own content in the same commit)
- Final Commit: `PENDING_METADATA_COMMIT`

## Goal

PM shared a doc-update-staleness-prevention prompt from a sibling project
(Outlook Hub) and asked to absorb its generalizable principles into this
repository's own record system, so that the kind of registration gap found
in `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2` (real work landing with zero
agent-system tracking) is structurally harder to repeat, not just fixed once.

## Worktree and changed files

- Changed Files: `agent-system/rules.md` (new "Documentation change routing"
  section, Invariants 9-11, Closeout Contract "not measured/estimated"
  requirement, new "Prohibited actions" section), `agent-system/templates/
  handoff.md` (new "Not Measured / Estimated" field).
- Existing Dirty State: two unrelated untracked files were present
  (`engineering/phase2/MONGLE_W6_1_E2E_HARNESS_PROVENANCE.md`,
  `engineering/phase2/MONGLE_W6_1_E2E_HARNESS_RECOVERY_REPORT.md`); not
  touched, not staged, not part of this task.

## Commands and outcomes

- Tests Run: none (documentation/process change; no product code, DB, or auth
  touched).
- Tests Not Run: n/a — see COMMON_NORMS.md risk-based QA (doc/metadata work
  uses self-check unless it reveals a product-risk defect).
- Self-check performed: read the full amended `rules.md` back after editing
  to confirm table pipe counts, section structure, and Invariant numbering
  are intact (dogfooding the "structural self-check" principle this task
  itself adds).

## Completed / remaining

- Known Gaps: the Outlook Hub source template also included an automated
  structural-validation script (line count, stale-date grep, leftover
  completion-wording grep, table pipe-count check). That script itself was
  not ported — only the written rule requiring the check was. Porting the
  actual tool into `agent-system/tools/` is left as a Next Action, not done
  here.
- Not Measured / Estimated: none — this task's only claims are about the
  content of the two files it edited, which were read directly before and
  after editing.
- QA Status: self-check only; `Independent QA: not_applicable` per
  COMMON_NORMS.md (documentation/lifecycle-only work).
- Drive Evidence: none.
- Coverage Map Review: `NO_CHANGE_REQUIRED` — no test path, behavior, tier,
  journey, execution evidence, or environment status changed; this is a
  process-rule addition, not a product or test change.

## Risks and Human Gate

This alters an existing Rule-grade document (`rules.md`), which
`rules.md`'s own Human Gate section flags as requiring PM direction before
altering existing documentation. The PM directed this change directly in the
current session, which satisfies that gate; it is recorded here rather than
in `relay/current.md` because this was a live PM-directed edit outside the
normal declare-before-edit task flow, not a background task pickup — noted
as a deliberate, disclosed deviation rather than a silent skip.

## Next agent first action

Consider porting the source template's structural-validation script (see
Known Gaps) into `agent-system/tools/`, and using the new Documentation
change routing tiers when triaging `AGENT_SYSTEM_INTEGRITY_AUDIT_PROMPT.md`'s
findings.

## Forbidden Scope

Product code, database/migrations, deployment config — none of which this
task touched.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md` entry for this Task ID
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/PHASE0-DOC-STALENESS-PREVENTION-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE0-DOC-STALENESS-PREVENTION-001.md`
- Independent QA: `not_applicable`
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: process/rule-document change only; no test or product
  surface changed.
- CLOSEOUT GATE: `PASS`

Closeout Gate PASS means only that the four documentation obligations above
are synchronized — it is not independent QA PASS or graduation; graduation is
a PM decision.
