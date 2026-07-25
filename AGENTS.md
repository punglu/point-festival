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
- Do not place credentials, tokens, personal data, or raw secret-bearing logs in
  repository or Drive artifacts.
- The PM performs `git push`. Agents may commit only when the task authorizes it.

Detailed rules: `agent-system/rules.md`.
