# [Task Prompt] Agent System Record Integrity Audit — Phase B (Remediation)

- Task ID: `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-REMEDIATION-003`
- Issued by: PM, 2026-08-04
- Executor: any implementation agent (Claude Code or Codex), following `AGENTS.md`
- Precondition: `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-READONLY-003`'s
  own findings document exists and has been reviewed by PM. Do not start
  this task from a partial or in-progress Phase A run.

## Read first

`AGENTS.md`, then `agent-system/rules.md`, then `agent-system/active.md`,
then `agent-system/relay/current.md`, then Phase A's own findings document
in full (its path is recorded in Phase A's `active.md`/QA Evidence entry).

## Goal

Apply every `SAFE_REGISTRATION_FIX`-classified row from Phase A's findings
document, and only those rows. Leave every `JUDGEMENT_REQUIRED` row
untouched — this task does not make the judgement calls Phase A deferred;
it applies what Phase A already determined needs no judgement.

## Method

1. Read Phase A's findings document. Build a worklist of only the rows
   classified `SAFE_REGISTRATION_FIX`.
2. For each: re-verify its own cited evidence still holds (git ref, file
   path, current repository state may have moved since Phase A ran — do not
   trust a stale finding blindly, per `rules.md`'s Authority and evidence
   ordering: current measured environment outranks a prior report).
3. Apply the fix using the existing `agent-system/{active.md,graduated/,
   handoffs/,qa/,decisions/,incidents/,relay/}` structure and its existing
   templates. Typical shapes, per Phase A's own `SAFE_REGISTRATION_FIX`
   examples:
   - Add a missing `active.md` entry for an already-committed, undisputed
     task (with real Lifecycle/Decision/Verification/Execution values taken
     from what its own Handoff/QA Evidence actually say — never invented).
   - Move a handoff still in `handoffs/active/` to `handoffs/archive/
     <month>/` for a task already correctly graduated, and confirm the
     `graduated/<month>.md` row's path reference is updated to match.
   - Correct a dead or mismatched git ref citation in a `graduated/*.md` row
     to the actual correct ref, with the correction visible (append/annotate
     per Invariant 5's write-once principle — do not silently overwrite a
     wrong ref with no trace that it was wrong).
4. If applying a fix surfaces a new discrepancy Phase A did not catch (e.g.
   fixing a path reveals a second, related inconsistency), do not silently
   also fix that one under this task's own `SAFE_REGISTRATION_FIX` label
   unless it is unambiguously the same shape and equally judgement-free —
   otherwise record it as a new finding for a future Phase A/B cycle rather
   than absorbing scope.

## Constraints

- Apply only `SAFE_REGISTRATION_FIX` rows. A row not clearly one of Phase
  A's worked examples (missing registration, mis-shelved handoff, dead ref)
  is `JUDGEMENT_REQUIRED` by default even if it looks easy — do not
  downgrade a classification to get it done in this pass.
- Do not reclassify any task's Lifecycle/Decision/Verification/Execution to
  something more (or less) complete than its own Handoff/QA Evidence
  already states. That is exactly the class of change Phase A reserved for
  PM.
- Do not self-award independent QA PASS for anything.
- Do not create new top-level or `agent-system/` directories.
- Declare this task's own scope in `agent-system/relay/current.md` before
  starting, respecting single-writer ownership of `active.md`.
- No commit/push/merge/rebase/reset/clean/stash — PM commits.

## Acceptance and required evidence

- Every `SAFE_REGISTRATION_FIX` row from Phase A applied, with the specific
  git ref / file / command evidence re-verified at application time (not
  merely copied from Phase A's own report).
- Every row Phase A left `JUDGEMENT_REQUIRED` restated as-is in this task's
  own closing report, still unapplied, still awaiting PM.
- This task follows the Closeout Contract (v1): synchronize `ACTIVE`,
  `HANDOFF`, `QA EVIDENCE`, and `COVERAGE MAP` before reporting done.

## Human Gate / rollback

Do not push. Report applied fixes and the still-open `JUDGEMENT_REQUIRED`
list to PM for review before any further action.
