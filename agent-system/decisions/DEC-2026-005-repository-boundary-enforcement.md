# Repository-boundary enforcement

- Decision ID: `DEC-2026-005-repository-boundary-enforcement`
- Title: `Repository-boundary enforcement`
- Status: `DESIGN_APPROVED`
- Created at: `2026-07-31`
- Author: `PM decision`
- Git ref: `6c633679c6708a21920f0e4b306bc1e36a2ea72d` (decision baseline)
- Environment: `repository policy`
- Evidence: `PM direction in MONGLE-REPOSITORY-BOUNDARY-ENFORCEMENT-001`
- Supersedes: `NONE`
- secrets_redacted: `true`

## Decision

Agents create, write, retain, and move project material only inside the Git
worktree. Project material includes source, tests, documents, task records,
artifacts, temporary work directories, generated reports, and copied worktrees.
Creation or use of `/tmp` project artifacts, repository-adjacent directories,
or external worktrees is prohibited. Existing historical references to such
locations are records only and never authorize recreation.

If a tool requires an opaque system-managed runtime cache, agents do not treat
that cache as a project workspace and must not place project material there.
When a required workflow cannot operate within the worktree, stop and request a
PM decision; do not create an exception.
