# DEC-2026-001-agent-system-v0.1

- Decision ID: `DEC-2026-001-agent-system-v0.1`
- Title: `Agent System v0.1 foundation`
- Status: `DESIGN_APPROVED`
- Created at: `2026-07-26`
- Author: `PM-approved implementation task`
- Git ref: `b85efedb9be8b1d8f75361cac9f96aea00a3b8ff` (adoption baseline)
- Environment: `repository policy`
- Evidence: `Task AGENT-SYSTEM-V0.1-IMPLEMENT-001; FAMILY_PLATFORM_AGENT_SYSTEM_FREEZE_v0.1`
- Supersedes: `none`
- secrets_redacted: `true`

## Decision

1. The Agent System parent path is `agent-system/`; the root contains only the
   thin, engine-neutral `AGENTS.md` bootstrap.
2. `docs/` remains user-managed and is excluded from Agent System SSOT.
3. Existing `CLAUDE.md` is not changed by this task.
4. Claude Code and Codex are equal implementation agents. Codex is the primary
   independent QA role.
5. Gemini is limited to explicitly scoped, structured cross-checks.
6. Git is the implementation SSOT. Google Drive is an exchange and evidence
   layer, never a replacement for repository state.
7. The PM performs `git push`.
8. Changes to this decision require a new decision record that references this
   ID through `Supersedes`; this record is not rewritten for semantic changes.
