# CLAUDE.md

This file is intentionally thin. It is not the SSOT for this repository and
does not restate current state, stack, structure, or phase status — those
drift, and duplicating them here is exactly what caused this file to go
stale for months after the project pivoted.

## Read this first, not this file

Start with **`AGENTS.md`** in the repository root. It is the actual session
bootstrap and lists what to read, in order, before doing anything:

1. `AGENTS.md`
2. `agent-system/rules.md`
3. `agent-system/active.md`
4. `agent-system/relay/current.md`
5. The active task handoff, when one is declared

Current architecture and development contracts live in
[`engineering/README.md`](engineering/README.md) and its linked guides
(`COMMON_NORMS.md`, `BACKEND_GUIDE.md`, `FRONTEND_GUIDE.md`,
`TESTING_GUIDE.md`). Legacy (pre-pivot "MarkPoint"/point-festival)
implementation reference is in
[`engineering/LEGACY_MARKPOINT_REFERENCE.md`](engineering/LEGACY_MARKPOINT_REFERENCE.md)
— it is background only, not a platform contract.

## Standing rule

Do not create new top-level or ad hoc directories without PM approval and
without declaring them in `agent-system/relay/current.md` first. Repeated
undeclared directory creation is what broke source control tracking here
before (see `docs/temp/` incident, fixed in commit `f9da663`).
