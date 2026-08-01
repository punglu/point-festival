# MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001

- Task ID: `MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9 container with no host port published, removed at teardown
- evidence: `agent-system/qa/MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001.md`
- secrets_redacted: `true`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED` (PM integration directive, 2026-08-01)
- Verification: `PASS` (self-check only)
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- End HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Scope completed

1. Doran → Wagle runtime identifier migration (migration `0007`).
2. Track B schema delta (migration `0008`).
3. Markpoint activation request / approve / reject, and per-member restriction / restore.
4. Markpoint → Wagle system-event relay through port → adapter → `wagle.service`.
5. Shared documentation integration for both lanes.
6. Integration tests, self-QA, Zero Gate.

## Worktree and changed files

- Renamed via `git mv`: `app/domains/doran/` → `app/domains/wagle/` (9 files); `test_doran_*` → `test_wagle_*` (4 files).
- New: migrations `0007`/`0008`, `markpoint_access/models.py`, `markpoint_access/wagle_relay_adapter.py`, `tests/test_integration_wagle_markpoint.py`, this handoff and its QA evidence.
- Modified: the Wagle domain, `markpoint_access/{service,router,schema}.py`, `all_models.py`, `main.py`, `mission/service.py`, `service_outbox/*`, `workers/service_outbox.py`, `scripts/phase1_seed_synthetic.py`, `tests/conftest.py`, the renamed test files, six Target documents, `COVERAGE_MAP.md`, `active.md`, `relay/current.md`.
- Existing Dirty State: the tree was clean at HEAD `0d9280c` (both lanes' work already committed). Nothing was reset, restored, checked out, cleaned or stashed; Track B's container and files were untouched.

## Commands and outcomes

```
alembic upgrade head (fresh DB)      -> 8 revisions, head 0008_markpoint_access_control
alembic downgrade -1 (x2) + upgrade  -> full round trip verified, zero residue
pytest tests/test_integration_wagle_markpoint.py -q -> 25 passed
pytest -q                                           -> 170 passed, 0 failed
```

Per-file collection re-derived rather than copied: 33 + 20 + 21 + 25 + 17 + 26 +
19 + 3 + 6 = 170. The earlier 145 equals this minus the 25 new integration tests.

- Tests Run: full backend suite plus migration round trips, all against a database this task created.
- Tests Not Run: frontend lint/build and Playwright (no frontend change; the FE calls no `/doran` API); WebSocket/Push/PIN (Wave 3, absent by contract).

## Completed / remaining

- Known Gaps:
  - Independent QA has not run on either lane or on this integration.
  - Frontend still carries the historical name in fixture-only code (`platform/doran/*`, `DoranLanding.tsx`, generated OpenAPI types) — 127 occurrences, outside this task's Zero-Gate scope, breaking nothing because no FE code calls those routes. Separate FE task.
  - Outbox **consumption** remains Wave 3.
  - The relay has no production caller yet; Markpoint's Wave 5 product code will be the first.
  - Unread count excludes SERVICE_ACTION messages (inherited; `D6-P4` undecided).
  - `docker-compose.phase2.yml` still absent.
- Not Measured / Estimated: none.
- QA Status: self-check only.
- Coverage Map Review: `UPDATED` — three new source-backed rows plus corrected Wave 2 counts.

## Risks and Human Gate

- Migration `0007` renames live schema objects and rewrites permission/service codes. It is reversible and was verified both ways, but it is the highest-risk change in this task and should be re-derived by independent QA from a database that QA creates itself.
- Two defects in this task were invisible in the Alembic log and only visible in the catalog (a trigger-name mismatch here; a `varchar(32)` rollback in a prior session). Independent QA should query `pg_proc`/`pg_trigger`/`permissions` directly rather than trusting migration output.
- No commit or push was made.

## Next agent first action

Independent QA of the parent bundle. Specifically: rebuild a database from
`init.sql` + `alembic upgrade head`, confirm zero historical identifiers in the
catalog and a 404 on the old route prefix, re-run the downgrade/re-upgrade round
trip, and verify the Markpoint→Wagle boundary by inspecting the source rather
than accepting this report's grep. Do not accept 170/170 as the verdict.

## Forbidden Scope

Markpoint mission/ledger product code (Wave 5); Wave 3 realtime/Push/PIN;
frontend source; `database/init.sql`; migrations `0000`–`0006`; legacy data
backfill; any compatibility alias for the historical name; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: three new source-backed rows for real executed tests.
- CLOSEOUT GATE: `PASS`
