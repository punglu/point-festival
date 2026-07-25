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
