# [Task Prompt] Agent System Record Integrity Audit — Phase A (Read-Only)

- Task ID: `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-READONLY-003`
- Issued by: PM, 2026-08-04
- Executor: any implementation agent (Claude Code or Codex), following `AGENTS.md`
- Supersedes-for-future-runs: the combined audit-and-fix method in
  `AGENT_SYSTEM_INTEGRITY_AUDIT_PROMPT.md` (still valid as historical context
  for why this audit exists; its Method section is the source this Phase A
  brief narrows to read-only). Prior runs `-001`/`-002` are not reopened by
  this split — see `rules.md` Invariant 10.

## Why this is now split from remediation

`AGENT_SYSTEM_INTEGRITY_AUDIT_PROMPT.md`'s own Acceptance section already
separated "safe, factual fixes" from "judgement-call fixes left for PM", but
both categories were produced inside one pass. Given the corpus size this
audit must reconcile — at last measurement, 1.1MB of `agent-system/`
markdown, 148 handoff/QA files, ~249 Task-ID-shaped strings to cross-
reference, and 57 product commits to check against agent-system records —
running discovery and remediation in the same context risks either the
session running out of budget mid-audit (leaving a half-applied, harder-to-
trust state) or edits happening before the full findings picture is in.
Phase A produces findings only. **No fix, however "safe," is applied in
Phase A.** `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-REMEDIATION-003`
(separate brief) consumes Phase A's own findings list and applies only what
that findings list itself already classified as safe.

## Read first

`AGENTS.md`, then `agent-system/rules.md`, then `agent-system/active.md`,
then `agent-system/relay/current.md`. This prompt does not replace them — it
is a task brief to be picked up under that system, not a new authority.

## Goal

Produce one findings document making every claim in `agent-system/` (and the
one pointer in `CLAUDE.md`) either confirmed-consistent with measured
repository state or flagged as a discrepancy — with no silent gaps. Do not
just re-read documents and cross-reference them against each other; a
document can be internally consistent and still be wrong about the
repository. Verify against the repository itself (git history, files on
disk, actual test/QA runs where the finding depends on one).

## Method — verify recursively, not just active.md

1. **Enumerate every Task ID that appears anywhere**, not just in
   `active.md`: `grep -rhoE '[A-Z][A-Z0-9-]*-[0-9]{3}(-R[0-9]+)?' agent-system/
   --include='*.md'` (adjust pattern as needed), plus Task IDs mentioned in
   commit messages (`git log --oneline --all | grep -iE 'phase[0-9]|task'`)
   and PR merge titles.
2. For each Task ID, locate **every** place it appears: `active.md`,
   `graduated/*.md`, `handoffs/active/`, `handoffs/archive/*/`, `qa/`,
   `decisions/`, `incidents/`. Apply Invariant #1: it must resolve to exactly
   one open location (`active.md`) or exactly one closed location
   (`graduated/<month>.md`, with its handoff correctly moved to
   `handoffs/archive/<month>/`) — never both, never neither, never a handoff
   left in `handoffs/active/` after graduation.
3. For each `active.md` entry, confirm its Lifecycle/Decision/
   Verification/Execution fields match what its linked Handoff and QA
   Evidence files actually say, and that those files exist at the stated
   paths.
4. For each `graduated/*.md` row, confirm the cited git ref exists
   (`git cat-file -e <ref>`) and its diff plausibly matches the stated
   conclusion, and that the archived handoff file is actually present under
   `handoffs/archive/`.
5. For tasks whose Execution is `SUCCEEDED` or `RUNNING`, confirm the files
   they declare as touched actually exist in the current tree at those paths
   (a task can claim code that was later reverted, moved, or never merged).
6. **Find untracked implementation work**: walk `git log` for commits/PRs
   touching `backend/`, `frontend/`, `database/`, or `engineering/phase*/`
   and check whether each one also touched something under `agent-system/`.
   A product-code commit with no corresponding agent-system change is a
   candidate for a missing task record — list every one found. Do not assume
   the two previously-found instances (`0393971`, `91eb98e`) are the only
   ones; check the full range, including commits before the current
   agent-system existed, which may be legitimately out of scope — use
   judgement and say so in the findings, do not silently exclude them.
7. Confirm `agent-system/relay/current.md` still points at genuinely open,
   in-progress tasks listed in `active.md` (not a finished or abandoned one).
8. Confirm `CLAUDE.md` has not re-accumulated duplicated state since its
   thin-pointer rewrite (it should stay a thin pointer; if someone has added
   detail back to it, that is itself a finding).

## Classify every discrepancy found

For each finding, record: Task ID (if any), location(s), the discrepancy
itself, the measured evidence (git ref, file path, command output — not
inference), and a proposed classification:

- `SAFE_REGISTRATION_FIX` — a factual, judgement-free correction (e.g. a
  missing `active.md` entry for an already-committed, undisputed task; a
  graduated handoff still sitting in `handoffs/active/`; a dead git ref).
  Phase B may apply these without further PM review.
- `JUDGEMENT_REQUIRED` — anything that would reclassify a task's Lifecycle/
  Decision/Verification/Execution to something more (or less) complete than
  its own evidence currently states, or that requires deciding whether
  untracked work is in-scope/legitimate/should be backfilled. Left
  unapplied; PM decides.
- `NO_ACTION` — investigated and confirmed not a real discrepancy (record
  why, so a future audit doesn't re-open it without cause per Invariant 10).

## Constraints — this phase is strictly read-only

- **No file under this repository is edited, moved, or created by Phase A
  except this task's own findings document, its own Handoff, and the
  required relay/active registration entries for this task itself.**
- Do not self-award independent QA PASS for anything found incomplete.
- Do not fabricate handoff or QA evidence content for any untracked commit
  to make it look retroactively compliant — record what the diff actually
  shows and classify it, nothing more.
- Do not create new top-level or `agent-system/` directories.
- Declare this task's own scope in `agent-system/relay/current.md` before
  starting, per the normal working contract, and respect single-writer
  ownership of `active.md` if another task is concurrently claiming it.
- No commit/push/merge/rebase/reset/clean/stash.

## Acceptance and required evidence

- One findings document (use the existing `agent-system/qa/` or
  `agent-system/incidents/` template shape, not a new ad hoc format), every
  row carrying Task ID, location(s), discrepancy, measured evidence, and
  classification (`SAFE_REGISTRATION_FIX` / `JUDGEMENT_REQUIRED` /
  `NO_ACTION`).
- This task itself follows the Closeout Contract (v1): before reporting
  done, synchronize `ACTIVE`, `HANDOFF`, `QA EVIDENCE`, and `COVERAGE MAP`
  per `rules.md` — `COVERAGE MAP` will almost always be
  `NO_CHANGE_REQUIRED` here, since a read-only audit does not change test
  behavior.

## Human Gate / rollback

Do not push. Report the findings document to the PM for review. Phase B
(`PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-REMEDIATION-003`) does not
start until this findings document exists and PM has reviewed at least the
`JUDGEMENT_REQUIRED` rows.
