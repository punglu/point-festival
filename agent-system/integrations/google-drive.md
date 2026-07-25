# Google Drive Exchange Contract

## Role and priority

Google Drive is an exchange, review, and evidence layer. Git repository source,
Git ref, and measured execution results remain authoritative for implementation.
Drive snapshots are never evidence that a newer local checkout is equivalent.

## Exchange root

- Root: `new_markp / 마크포인트잔치 개선 - Agent Exchange`
- Exchange folder ID: `1httyoER5XIvKhjnCz-1Y8zEEcMl1Frxn`
- Read order: validate supplied file/folder ID; inspect metadata/parents; read
  content; compare its Task ID and Git ref to the local task before relying on it.

| Purpose | Folder ID | Publication owner |
|---|---|---|
| Frozen baselines | `18TECF5jipG8kggPfl_fyN99IK-qxGWcv` | PM-managed baseline |
| Active task snapshots | `1Pd4OozYY1aIEBa5cR9KjoZwOn3C7-8OF` | task implementer |
| Handoffs | `18UCKwy6WG8uoukRnu4Pu5gZpdI6gfKVU` | task implementer |
| QA evidence | `1t3vKGU4FeIfFnHmK7P6fX6XcNL05VtEg` | independent QA |
| Codex results | `1ckr2NdhqcJIykMUrjj857YNlFYV-I97F` | Codex |
| Claude Code results | `1Qn5Nz5iT6JE68a-oMOqKuN03ObpNBe6Q` | Claude Code |
| GPT Web results | `1Puq2i559P4Dx6miWfBQEiMcumK_xu9xu` | GPT Web |
| Decision snapshots | `1tpBh-WfsAzbK9CRgCZwhX7Cl7ZG8AsVl` | decision author |
| Incidents | `1Ip7SpAPn1Jz1OEkh95WpW2RCoZSKyW9z` | incident author |
| Archive | `1Mlcdp2W7AlZ-gzU2WeRUcD7a5ULCXQNN` | PM-approved archival flow |

## Publication contract

- Filename: `<TASK-ID>_<ARTIFACT>.md`; include `Task ID`, `git_ref`,
  `observed_at`, `agent`, `environment`, `evidence`, and `secrets_redacted`.
- Never upload source trees, credentials, OAuth material, tokens, or personal
  data. Summaries and evidence pointers only.
- Before a write, verify destination folder ID. After a write, read back the
  created item and record the observed file ID/URL in the local handoff.
- On duplicate/conflict, do not overwrite another agent's result. Publish a
  distinct Task-ID artifact and note the conflict in handoff.
- A Drive item is stale when its declared Git ref differs from the active local
  Task ref or lacks `observed_at`/Task ID. Mark it stale; do not silently edit it.

## MCP connection

Use only a Drive connector surfaced by the current client. Do not add packages,
invent server names, or store connector configuration/credentials in this repo.
For a task that needs Drive, first list the current client tools, then read the
destination folder by its supplied ID and fetch the source/baseline by ID. For a
write, upload only a metadata-bearing summary, then fetch the returned file ID
and compare the expected Task ID and Git ref. Record the connector outcome and
file IDs in the task handoff, not as a permanent claim in this contract.

The installed client command surfaces are evidence only: `codex --help` exposes
`mcp`/`mcp-server`, and `claude --help` exposes `mcp`, `--mcp-config`, and
`--strict-mcp-config`. They do not prove a reusable configuration schema or a
connected Claude Code Drive client; those are `UNVERIFIED` unless measured in
that client session.

If the connector cannot access a required item, record `ENVIRONMENT_REQUIRED` in
the handoff with the measured failure and requested user action.
