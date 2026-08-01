# Agent System Rules v0.1

## Authority and evidence

Authority order is: latest PM approval; repository source and execution results;
current measured environment; approved decisions; active task contract; rules and
guides; derived summaries; agent memory. Git is the implementation SSOT. Google
Drive is an exchange, review, and evidence layer only.

Use `UNVERIFIED` or `ENVIRONMENT_REQUIRED` when a fact cannot be measured.
Volatile facts must identify `observed_at`, `git_ref`, `environment`, and
`evidence`. Mask secrets and personal data.

## State model

Keep these axes separate:

| Axis | Values |
|---|---|
| Lifecycle | `PLANNED`, `IN_PROGRESS`, `SUSPENDED`, `COMPLETED`, `ARCHIVED` |
| Decision | `NOT_REVIEWED`, `DESIGN_APPROVED`, `HUMAN_GATE`, `REJECTED` |
| Verification | `NOT_TESTED`, `PASS`, `CONDITIONAL`, `BLOCKED`, `ENVIRONMENT_REQUIRED` |
| Execution | `NOT_STARTED`, `RUNNING`, `FAILED`, `SUCCEEDED` |

`COMPLETED`, `PASS`, `DESIGN_APPROVED`, and `SUCCEEDED` are not interchangeable.

## Invariants

1. One Task ID has one active location in `active.md`.
2. `active.md` contains open work only; completed work is summarized in
   `graduated/` and detailed in its handoff.
3. `relay/current.md` contains only present file occupancy, not history.
4. Handoffs are Task-ID-specific and contain measured context, commands, results,
   scope, and next action.
5. Decisions are write-once. A changed decision creates a new decision with a
   `Supersedes` reference; it does not rewrite the old record.
   New records use `Supersedes: NONE` when there is no predecessor. The decision
   checker accepts legacy empty forms (`N/A`, `NA`, `NOT_APPLICABLE`, `-`, `—`,
   or blank) for compatibility.
6. QA PASS requires actual execution evidence. The implementation session cannot
   award its own final QA PASS.
7. Do not manually edit both an SSOT and its mirror. Generated mirrors require a
   source, regeneration method, and drift check.
8. Repeated incident patterns may be promoted to rules only after human review.
9. Before opening a new Task ID, check in order: an existing open entry in
   `active.md` covering the same scope; a prior closed entry in
   `graduated/*.md`; known aliases/renames of the same task; recent `git log`
   for commits that may already implement it; the current code directly. Open
   a new Task ID only if none of these already cover it. A prior incident
   re-proposed already-completed work as new debt because this check was
   skipped.
10. A `graduated` task may be reopened only on a measured regression or
    recurrence of the defect it closed, a changed precondition that
    invalidates its closure, or an explicit new PM decision. Rereading old
    documents, or a general improvement suggestion, is not sufficient grounds
    to reopen — open a new Task ID and reference the old one instead.
11. Never reconstruct the current content of `active.md`, a handoff, QA
    evidence, or a `graduated/*.md` file from memory or an earlier summary.
    Read the file immediately before editing it, every time, even within the
    same session.

## Documentation change routing

Classify a repository or Agent System record change before touching any file,
and touch only what the tier requires. When a change could plausibly be two
tiers, use the higher one — under-classifying to save effort is itself a
staleness defect. `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2` and two follow-up
commits went unregistered for days because implementation work was effectively
routed to `NO-DOC` by omission instead of `FULL-SYNC`; see the findings under
`PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-001` for the full case.

| Tier | Trigger | Required touch |
|---|---|---|
| `NO-DOC` | No repository-visible behavior or state change. | Nothing under `agent-system/`. |
| `LOG-ONLY` | Worth recording but not a new unit of work (a diagnostic command, an observation). | Append to the current task's handoff "Commands and outcomes"; no new Task ID. |
| `LOCAL-STATE` | An already-open task's own progress or scope changed. | That task's `active.md` fields and its own handoff only. |
| `LOCAL-FIX` | A bounded correction to existing records: a missing registration, a broken link, a graduated task whose handoff was never archived. | Only the specific `active.md` entr(y/ies) and handoff/QA files involved. |
| `FULL-SYNC` | New task creation, task graduation, or any Decision/Verification/Execution change other tasks or the Coverage Map may depend on. | Full Closeout Contract v1 cycle: ACTIVE, HANDOFF, QA EVIDENCE, COVERAGE MAP all reviewed. |

## Coordination

- Before edits, declare scope, forbidden paths, and high-risk files in relay.
- High-risk files have a single writer: common agent state, compose/deploy files,
  migrations, registry/manifest, authority seed, and shared configuration.
- Claude Code and Codex are equal implementation agents. Codex is QA-centered.
- Gemini may only provide designated, structured cross-check output and may not
  change common SSOT or make a final completion decision.
- `docs/` remains user-managed and outside this system.

## Mandatory closeout synchronization (Closeout Contract v1)

New tasks must declare `Closeout Contract: v1` and, before their normal end
report, record a Closeout Synchronization block in the task handoff. The block
must review `ACTIVE`, `HANDOFF`, `QA EVIDENCE`, and `COVERAGE MAP`. Existing
historical tasks are not retroactively rewritten; an existing open task adopts
the contract on its next modification.

- `ACTIVE`, `HANDOFF`, and `QA EVIDENCE` must be `UPDATED` for a normal
  closeout report and point to the current task-specific records.
- `COVERAGE MAP` is reviewed for every task. It is `UPDATED` when a test path,
  behavior, tier, journey, execution evidence, known gap, environment status,
  or Agent System static check changes. Otherwise it is
  `NO_CHANGE_REQUIRED` with a non-empty, specific reason; do not touch the map
  merely to satisfy the contract.
- A `BLOCKED` area makes `CLOSEOUT GATE` `BLOCKED`. A `PASS` gate is invalid
  unless ACTIVE, HANDOFF, and QA EVIDENCE are all `UPDATED`.
- `CLOSEOUT GATE: PASS` means only that the four documentation obligations are
  synchronized. It does not mean `Lifecycle: COMPLETED`, independent QA PASS,
  PM approval, graduation, or push approval. An implementation task may retain
  `Verification: NOT_TESTED` and `QA_PENDING`; the implementer's self-check
  never substitutes for independent QA.

A normal closeout report must include an explicit list of values or claims
that were not independently measured or verified during the task, marked as
estimates. Presenting an unverified value as measured is the single largest
cause of documentation staleness; when a fact cannot be measured, write
`UNVERIFIED` or `ENVIRONMENT_REQUIRED` per Authority and evidence above rather
than a plausible-looking number.

The report-only `agent-system/tools/check_closeout.py` checks v1 task records.
Its warnings are evidence for correction, not an automatic state transition or
blocking CI gate. Keep Coverage Map entries bottom-up and source-backed.
Structural self-checks it does not yet perform (leftover completion wording
such as "완료"/`COMPLETED`/`Closed` in a section that should not have it, a
table whose pipe count broke after a row edit, a stale "last updated" date)
remain a writer's manual responsibility; extending the tool to catch them is
a deferred tooling improvement, not a current guarantee.

## Document grades

| Grade | Location | Rule |
|---|---|---|
| Bootstrap | `AGENTS.md` | thin, stable, no current state or history |
| Rule | `rules.md` | approved invariant and operating contract |
| Active | `active.md` / `relay/current.md` | mutable current state only |
| Decision | `decisions/` | write-once record with stable ID |
| Evidence | `qa/`, `handoffs/`, `incidents/` | task/incident-scoped, measured metadata |
| Graduate | `graduated/` | compact completion index, no raw logs |

## Human Gate

Stop for PM direction before broadening scope, changing product architecture,
altering existing documentation, enabling CI/hooks, changing database/migrations,
changing deployment, resolving another owner's dirty worktree, or publishing
secrets/sensitive material.

## Prohibited actions

- Do not create a new top-level or `agent-system/` directory without PM
  approval and a declared scope in `relay/current.md` first.
- Do not create, write, or move project files, documentation, artifacts,
  temporary work directories, or copies outside the Git worktree. `/tmp`,
  repository-adjacent directories, and external worktrees are prohibited for
  project material; historical external artifacts do not create an exception.
- Do not self-award independent QA PASS; the implementing session's own check
  is evidence, not the verdict (Invariant 6).
- Do not rewrite `graduated/` or `decisions/` history in place; append or
  supersede only (Invariant 5).
- Do not create a second `active.md`/`graduated/` location for a Task ID that
  already has one (Invariant 1).
- Do not reopen a graduated task without a qualifying condition
  (Invariant 10).
- Do not under-classify a new task or completion claim to a lower
  Documentation change routing tier to avoid registering it.
- Do not leave a handoff file in `handoffs/active/` after its task graduates
  to `graduated/`.
- Do not present an unmeasured or remembered value as a measured one in a
  closeout report.
