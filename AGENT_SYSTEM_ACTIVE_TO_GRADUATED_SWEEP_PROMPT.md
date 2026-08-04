# [Task Prompt] Active → Graduated Sweep (Task Management Utility)

- Task ID pattern: `PHASE0-ACTIVE-TO-GRADUATED-SWEEP-<NNN>` — assign the next
  unused `<NNN>` at invocation time (check `active.md`, `graduated/*.md`, and
  git history for the highest prior sweep number, per `rules.md`
  Invariant 9). This is a **reusable, repeatedly-run utility**, not a
  one-off task like the Integrity Audit prompts — each run gets its own
  fresh Task ID rather than reopening a prior sweep.
- Issued by: PM, 2026-08-04
- Executor: any implementation agent (Claude Code or Codex), following `AGENTS.md`

## Purpose

This is narrower than either half of the Integrity Audit split
(`AGENT_SYSTEM_INTEGRITY_AUDIT_READONLY_PROMPT.md` /
`..._REMEDIATION_PROMPT.md`). It does not discover new discrepancies and it
does not judge whether a task is actually done. It only performs the
**mechanical `active.md` → `graduated/<month>.md` transition** for entries
that are *already, in their own current fields, done* — moving them out of
the open-work register and into the compact completion index, per `rules.md`
Invariant 2 ("`active.md` contains open work only; completed work is
summarized in `graduated/` and detailed in its handoff").

Run this whenever `active.md` has accumulated entries that look finished, to
keep it a true open-work list rather than a growing archive. It is meant to
be cheap and frequent, unlike the full Integrity Audit.

## Read first

`AGENTS.md`, then `agent-system/rules.md` (**Invariants 1, 2, 5, 10** are
the ones this task lives inside), then `agent-system/active.md`, then
`agent-system/relay/current.md`.

## Eligibility — what counts as "already done"

An `active.md` entry is a graduation **candidate** only if, in its own
current text:

1. `Execution` is `SUCCEEDED` (not `RUNNING`, not `FAILED`).
2. `Lifecycle` is a complete-shaped value (`COMPLETE`, or
   `IMPLEMENTED_AWAITING_INDEPENDENT_QA` where the entry's own text already
   discloses its evidence level — self-check-only is graduation-eligible in
   this repository's established convention, see `graduated/2026-08.md`'s
   many "Self-reported only, never independently QA'd" rows; it does not
   need to be independently QA-passed to graduate, only to be honestly
   labeled).
3. Its own `Next Action` does not point at unresolved follow-up work that
   would keep it "open" in spirit (e.g. "awaiting Independent Re-QA" for a
   *different*, still-open follow-up task is fine — that follow-up stays in
   `active.md` under its own Task ID; but "blocked pending X" for the task's
   *own* completion is not eligible).
4. It is not itself marked `REOPENED`, `SUSPENDED`, `HUMAN_GATE`, or
   carrying an explicit unresolved PM decision gate in its own text (e.g.
   the current `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)`
   entry is never eligible while it stays reopened).
5. Its Handoff (and QA Evidence, if any) files exist at their stated paths.

**Do not upgrade, downgrade, or reinterpret any field to make a borderline
entry eligible.** If eligibility is genuinely ambiguous from the entry's own
current text, leave it in `active.md` and list it as a candidate for PM
review instead of moving it — this task has no authority to make that call
(same boundary the Remediation prompt draws for `JUDGEMENT_REQUIRED` rows).

## Method

1. Read `active.md` top to bottom. For each entry, apply the Eligibility
   checklist above using only that entry's own current text — do not
   re-derive Lifecycle/Verification from source code or re-run tests; that
   is the Integrity Audit's job, not this sweep's.
2. For each eligible entry:
   a. Write one new row in the current month's `graduated/<YYYY-MM>.md`
      (create the file from the existing format in `graduated/2026-08.md`
      if the current month has none yet), condensing the entry's own
      Lifecycle/Verification text into the table's `Final conclusion`
      column — do not add new claims, only compress what the entry already
      says. Cite the entry's own git ref if stated, or `(unchanged — no
      commit made)` if none.
   b. If the entry's Handoff is under `handoffs/active/`, move it to
      `handoffs/archive/<YYYY-MM>/` (`git mv`-equivalent; preserve content
      unchanged) and update the new graduated row's `Handoff` column to the
      new path. If the entry's own QA Evidence file serves as its handoff
      (no separate Handoff was ever written — an accepted existing pattern
      in this repository), point the graduated row at that QA Evidence path
      instead and say so, matching the existing `"(QA evidence serves as
      handoff)"` annotation style.
   c. Remove the entry from `active.md` entirely (Invariant 1: one Task ID,
      one location — it must not exist in both places after this step).
3. After processing all entries, confirm `agent-system/relay/current.md`
   does not still point at any task just moved to `graduated/` (per
   Invariant 3, relay reflects only present occupancy) — if it does, remove
   that stale relay section (the relay is a mutable current-state register,
   not history, so this is a plain deletion, not a write-once correction).
4. List every entry considered but judged **not** eligible, with the
   specific reason (which checklist item failed), so PM can see what was
   deliberately left open.

## Constraints

- Do not create new top-level or `agent-system/` directories (a new
  `graduated/<month>.md` file under the existing `graduated/` directory is
  not a new directory and is expected).
- Do not rewrite any `graduated/*.md` row once written by a prior sweep —
  append new rows only (Invariant 5's write-once principle extends to this
  file).
- Do not touch `decisions/`, `incidents/`, or any product/test/migration/
  seed file.
- Declare this sweep's own scope in `agent-system/relay/current.md` before
  starting, respecting single-writer ownership of `active.md`.
- No commit/push/merge/rebase/reset/clean/stash — PM commits.

## Acceptance and required evidence

- Every moved entry: old `active.md` location removed, new `graduated/
  <month>.md` row added, Handoff correctly relocated (or QA-evidence-as-
  handoff correctly annotated), `relay/current.md` cleaned of any now-stale
  reference — all in the same pass, so `active.md`/`graduated/` never sit
  inconsistent between two separate commits.
- A short report: N entries moved (listed), M entries considered and left
  open (listed with reason).
- This task follows the Closeout Contract (v1) for its own record: since
  this sweep's own work is itself a completed, mechanical pass, it may
  self-graduate its own Task ID in the same run once its report is written
  — this is the one case where a task recording its own graduation is
  appropriate, because the "judgement" is inherent to the sweep's own
  narrow, already-approved mandate, not a new completion claim about
  someone else's work.

## Human Gate / rollback

Do not push. If any entry's eligibility is ambiguous, leave it in
`active.md` and report it for PM review rather than guessing — this sweep
trades speed for zero judgement calls, by design.
