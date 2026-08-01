# MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001

- Task ID: `MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001`
- Predecessor: `MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9 (no host port, removed at teardown); frontend checks in `mongle-frontend-toolchain`; clean production build in a throwaway workspace with container-only `node_modules`
- evidence: `agent-system/qa/MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001.md`
- secrets_redacted: `true`
- Lifecycle: `IMPLEMENTED_AWAITING_INDEPENDENT_QA`
- Decision: `DESIGN_APPROVED` (PM directive, 2026-08-01 — released both allowlist keeps)
- Verification: `PASS` (self-check only)
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- End HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Origin

The predecessor task left `naran` alive in two PM-approved keeps. PM has now
released both: `/naran/*` routes are removed outright (no redirect, alias or
fallback — old bookmarks 404 by explicit cutover decision), and the persisted
`naran.activeFamily.*` key is migrated one-time to `mongle.activeFamily.*`.
This closes the frontend naming campaign on both the platform (Naran) and
messaging (Doran) axes.

## Worktree and changed files

- New: `frontend/src/shared/storage/activeFamilyStorageMigration.ts` — the sole location of the retired key name, and only as a migration source.
- Modified: `frontend/src/App.tsx` (both `/naran/*` routes + `LegacyRouteRedirect` + unused `useLocation` import removed), `platform/shell/MongleAppShell.tsx` (comment), `shared/stores/useFamilyContextStore.ts` (delegates to the migration module), `generated/openapi.d.ts` (regenerated from live schema, not text-substituted), `tests/e2e/specs-mongle/01-shell.spec.ts` (route + storage contracts rewritten), `backend/scripts/phase1_seed_synthetic.py` (comment only).
- Docs: `engineering/phase2/MONGLE_NARAN_REMAINING_ALLOWLIST.md` closed (`ACTIVE_NARAN_ALLOWLIST: EMPTY`).
- Existing Dirty State: the Wave 2/4 bundle's uncommitted work was present at start and is untouched. Nothing was reset, restored, checked out, cleaned or stashed.

## Commands and outcomes

```
tsc --noEmit (toolchain)              -> EXIT=0
npm run lint (toolchain)              -> clean
tsc --noEmit (clean workspace)        -> EXIT=0
eslint (clean workspace)              -> clean
tokenContract (clean workspace)       -> 29 pass / 0 fail
npm ci + npm run build (clean)        -> PASS, ✓ built in 1.05s
OpenAPI regeneration                  -> doran 0, naran 0, wagle 11, markpoint 9
pytest --collect-only                 -> 173 collected
pytest -q (full backend)              -> 173 passed, 0 failed
git diff --check                      -> clean
```

Naran Zero Gate — all `0`: active runtime identifier, route, file path, import,
component, type, storage key, CSS, API reference, test expectation, backend, and
current-Target document.

Counted separately and **not** claimed as zero:
`STORAGE_MIGRATION_SOURCE_NARAN_COUNT: 2` (+1 constant-folded in the bundle),
`PROHIBITION_OR_BEFORE_VALUE_NARAN_COUNT: 3`,
`HISTORICAL_ARCHIVE_NARAN_COUNT: 37 files`.

Doran regression gate — all `0`, including the built bundle.

- Tests Run: frontend typecheck/lint/token contract in two environments; clean production build; full backend suite including the 3 frontend service-code contract tests.
- Tests Not Run: **Playwright E2E execution** — the specs were rewritten to the new route/storage contract but need the full isolated Compose runtime, which this task did not stand up. Frontend component tests — no such framework exists in this repo.

## Completed / remaining

- **Predecessor blocker resolved:** `PRODUCTION_BUILD` was
  `BLOCKED_BY_PRE_EXISTING_ENVIRONMENT` (container `linux-arm64` musl vs
  bind-mounted `rollup-darwin-arm64`). Built here by copying source +
  `package-lock.json` into a throwaway workspace and running `npm ci` for a
  container-only tree. The host's `node_modules` was never deleted or
  overwritten.
- Known Gaps:
  - **The rewritten Playwright specs have not been executed.** Largest residual risk.
  - **Independent QA has not run** on this task or its predecessor.
  - Old `/naran/*` bookmarks now 404 — intended, but user-visible.
  - The one-time migration only runs when a user loads the app; a browser that never returns keeps its retired key locally.
- Not Measured / Estimated: none.
- QA Status: self-check only.
- Coverage Map Review: `UPDATED` — one new source-backed row.

## Risks and Human Gate

- The retired namespace is assembled as `'na' + 'ran'` in both the migration module and the E2E spec. **Do not "clean this up" into a literal** — a repository-wide sweep would then rewrite it into the canonical key, turning the migration into a no-op that silently discards every user's selected Family. Two sweep-induced inversions have already occurred in this effort.
- The migration copies the value forward *before* deleting the retired key. Reordering or dropping the copy is a user-data loss.
- Mid-task, a grep for `<Route path=` appeared to show every canonical route deleted; reading `App.tsx` disproved it (the canonical routes are multi-line). Verify against the file, not that grep.
- No commit or push was made. Branch and HEAD unchanged.

## Next agent first action

Combined independent QA of this task and
`MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001`: stand up the isolated E2E
runtime and **actually run** `tests/e2e/specs-mongle/01-shell.spec.ts` (the
route-not-registered, storage-migration, malformed-value and idempotency
assertions), re-derive the Naran and Doran zero gates independently, read the
diff for historical-context damage rather than trusting metrics, and confirm the
built bundle's single `naran` occurrence is the migration source and nothing
else.

## Forbidden Scope

Reintroducing any `/naran/*` route, alias, redirect or fallback; making the
retired storage key a permanent fallback or dual-write; renaming Naran to Wagle
(the platform axis maps to **Mongle**); rewriting historical/archived documents
to remove the retired names; Wagle/Markpoint backend product code; Wave 3
realtime/Push/PIN; Markpoint Mission/Ledger; graduating any task in this bundle;
and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: one new source-backed row for the storage-migration and route-retirement contract.
- CLOSEOUT GATE: `PASS`
