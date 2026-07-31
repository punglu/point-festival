# [Task Prompt] Agent System Record Integrity Audit

- Task ID: `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001`
- Issued by: PM, 2026-07-31
- Executor: any implementation agent (Claude Code or Codex), following `AGENTS.md`

## Read first

`AGENTS.md`, then `agent-system/rules.md`, then `agent-system/active.md`, then
`agent-system/relay/current.md`. This prompt does not replace them — it is a
task brief to be picked up under that system, not a new authority.

## Why this task exists

Two staleness/registration defects were found and partially fixed on
2026-07-31:

1. `CLAUDE.md` had been frozen since 2026-04-05 (the pre-pivot "point-festival"
   project) and still claimed to be the session SSOT, while the repository had
   already moved to the current family-platform product and to
   `AGENTS.md`/`agent-system/` governance since 2026-07-26. Fixed by reducing
   `CLAUDE.md` to a thin pointer (commit `4963649`).
2. `agent-system/handoffs/active/PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2.md`
   and its QA evidence file existed (committed since `a1575e0`, 2026-07-26) but
   the task was **never registered in `agent-system/active.md`** — a direct
   violation of Invariant #1 in `rules.md` ("One Task ID has one active
   location in `active.md`"). Registration was added back retroactively as a
   documentation-only fix. While investigating it, two later commits,
   `0393971` ("add service principal and room binding") and `91eb98e` ("add
   reliable service event delivery"), were found to have added real product
   code under `backend/app/domains/doran/` with **zero agent-system files
   touched** — no task record, no handoff, no QA evidence at all.

Both defects share a shape: real repository state (code, product direction)
moved forward while the record system either duplicated authority (CLAUDE.md)
or silently failed to track it (untracked commits). Since directory/file
sprawl and lost git tracking have already been traced back to this kind of
drift, this audit exists to find every other instance of the same shape
before it causes another incident, not just to fix the two found so far.

## Goal

Make every claim in `agent-system/` (and the one pointer in `CLAUDE.md`)
consistent with measured repository state — actual git history, actual files
on disk, actual test/QA runs — with no silent gaps. Do not just re-read the
documents and cross-reference them against each other; a document can be
internally consistent and still be wrong about the repository. Verify against
the repository itself.

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
   candidate for a missing task record — list every one found (start from
   `0393971` and `91eb98e`, but do not assume those are the only two; check
   the full range, including commits before the current agent-system existed,
   which may be legitimately out of scope — use judgement and say so).
7. Confirm `agent-system/relay/current.md` still points at a genuinely open,
   in-progress task listed in `active.md` (not a finished or abandoned one).
8. Confirm `CLAUDE.md` has not re-accumulated duplicated state since the
   2026-07-31 rewrite (it should stay a thin pointer; if someone has added
   detail back to it, that is itself a finding).

## Constraints

- Do not self-award independent QA PASS for anything found incomplete.
  `rules.md`: "The implementation session cannot award its own final QA
  PASS." Fixing a *registration* gap (adding a missing `active.md` entry,
  moving an already-graduated handoff to `archive/`) is a documentation
  correction and is in scope. Declaring new work `COMPLETED`/`PASS` is not —
  flag it for PM/QA instead.
- Do not fabricate handoff or QA evidence content for the untracked commits
  (`0393971`, `91eb98e`, and any others found) to make them look
  retroactively compliant. Register them honestly as
  `Verification: NOT_TESTED`, note what the diff actually shows, and leave
  the real QA/testing as a Next Action.
- Do not create new directories. All fixes live inside the existing
  `agent-system/{active.md,graduated/,handoffs/,qa/,decisions/,incidents/,
  relay/}` structure and its existing templates in `agent-system/templates/`.
- Follow `rules.md` Human Gate: stop for PM direction before changing
  product architecture, database/migrations, deployment, or before resolving
  another owner's dirty worktree. Pure record-consistency fixes do not
  require stopping; reclassifying a task's Lifecycle/Decision/Verification/
  Execution to something more complete than its evidence supports does.
- Declare this task's own scope in `agent-system/relay/current.md` before
  editing, per the normal working contract, and respect single-writer
  ownership of `active.md` if another task is concurrently claiming it.

## Acceptance and required evidence

- A findings list: every Task-ID/registration/graduation/untracked-commit
  discrepancy found, using the existing `agent-system/qa/` or
  `agent-system/incidents/` templates — not a new ad hoc report format.
- Every safe, factual registration/consistency fix applied directly (with
  git refs as evidence).
- Every fix that would require judgement calls beyond registration (deciding
  something is complete, discarding a task, rewriting Decision state) left
  unapplied and listed as a PM decision item instead.
- This task itself follows the Closeout Contract (v1): before reporting done,
  synchronize `ACTIVE`, `HANDOFF`, `QA EVIDENCE`, and `COVERAGE MAP` per
  `rules.md`.

## Human Gate / rollback

Do not push. Report findings and applied fixes to the PM for review before
any further action is taken on the untracked-commit gaps.
