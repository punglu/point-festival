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

The report-only `agent-system/tools/check_closeout.py` checks v1 task records.
Its warnings are evidence for correction, not an automatic state transition or
blocking CI gate. Keep Coverage Map entries bottom-up and source-backed.

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
