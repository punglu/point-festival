# Agent System Bootstrap

This repository uses the Git worktree as the implementation SSOT. Agent memory,
Google Drive, and chat history are supporting evidence only.

## Read at every session

1. `AGENTS.md`
2. `agent-system/rules.md`
3. `agent-system/active.md`
4. `agent-system/relay/current.md`
5. The active task handoff, when one is declared

Read task-specific decisions, QA evidence, incidents, and integration guidance
only when the active task requires them.

QA policy, Coverage Map, and Task QA evidence are respectively located at
`agent-system/qa/TEST_POLICY.md`, `agent-system/qa/COVERAGE_MAP.md`, and
`agent-system/qa/<TASK-ID>.md`.

For feature work, comply with the applicable
[`engineering/FRONTEND_GUIDE.md`](engineering/FRONTEND_GUIDE.md) or
[`engineering/BACKEND_GUIDE.md`](engineering/BACKEND_GUIDE.md), then apply the
feature-completion safety net in
[`agent-system/qa/TEST_POLICY.md`](agent-system/qa/TEST_POLICY.md). Detailed
commands and artifact handling are in [`tests/README.md`](tests/README.md).
Before feature implementation, comply with the mandatory
[first-development enforcement sequence](agent-system/decisions/DEC-2026-004-first-development-enforcement-sequence.md)
and the linked synthetic-data/event-matrix decision; do not bypass their
preconditions inside a feature task.

## Working contract

- Declare intended files in `agent-system/relay/current.md` before editing.
- `agent-system/active.md` is the only active-task register. Keep only open work.
- Put detailed transfer context in `agent-system/handoffs/`; keep relay current-only.
- The implementer does not issue their own final QA PASS. Codex is the primary
  independent QA role; Gemini performs only explicitly scoped, structured checks.
- Treat compose, deployment, migrations, common agent state, and central
  configuration as high-risk: one writer at a time.
- Measure branch, HEAD, worktree, runtime, database, and test state; never infer
  them from stale documents.
- `docs/` is user-managed and is not an Agent System SSOT.
- Keep all agent-created project files, documentation, artifacts, temporary
  work directories, and copies inside the Git worktree. Creating, writing, or
  moving project material to any path outside the worktree—including `/tmp`,
  repository-adjacent folders, and external worktrees—is absolutely prohibited.
  Existing historical external paths are not authorization to recreate them.
- Do not place credentials, tokens, personal data, or raw secret-bearing logs in
  repository or Drive artifacts.
- The PM performs `git push`. Agents may commit only when the task authorizes it.
- Before ending any task, complete mandatory closeout synchronization for active,
  handoff, QA evidence, and Coverage Map. A task cannot report completion when
  its Closeout Contract is missing or blocked.

Detailed rules: `agent-system/rules.md`.

Canonical development guides: [`engineering/README.md`](engineering/README.md).
