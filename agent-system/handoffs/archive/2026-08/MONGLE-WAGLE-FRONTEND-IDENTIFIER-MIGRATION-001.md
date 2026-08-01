# MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001

- Task ID: `MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9 (no host port published, removed at teardown); frontend checks in the existing `mongle-frontend-toolchain` container
- evidence: `agent-system/qa/MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001.md`
- secrets_redacted: `true`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED` (PM directive, 2026-08-01)
- Verification: `PASS` (self-check only)
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245`
- End HEAD: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged — no commit)
- Final Commit: `not applicable — the PM performs commit/push`

## Origin

PM **retracted** the parent independent QA's classification of the ~127 frontend
occurrences as a non-blocking follow-up. The standing decision is that Doran must
not be used in the current product at all, not only in the backend runtime — and
that QA's own need to patch `DoranLanding.tsx` was itself evidence of active
frontend usage.

## Worktree and changed files

- Renamed via `git mv` (history preserved, shown as `R`/`RM` in `git status`): `platform/doran/**` → `platform/wagle/**` (38 files); `DoranLanding.tsx`/`.module.css` → `WagleLanding.*`.
- Modified: `App.tsx`, `MongleAppShell.tsx`, `MongleAppShell.module.css`, `shared/components/Avatar/Avatar.tsx`, `styles/global.css`, `generated/openapi.d.ts` (regenerated, not text-substituted).
- New: `backend/tests/test_frontend_service_code_contract.py`.
- Existing Dirty State: the Wave 2/4 bundle's uncommitted work was present at start and is untouched except where this task's own scope required. Nothing was reset, restored, checked out, cleaned or stashed.

## Commands and outcomes

```
tsc --noEmit                       -> EXIT=0
npm run lint (eslint)              -> clean
grep "from '.*doran'" frontend/src -> 0
node --test tokenContract.test.mjs -> 29 pass / 0 fail
pytest tests/test_frontend_service_code_contract.py -> 3 passed
pytest -q (full backend)           -> 173 passed, 0 failed
git diff --check                   -> clean
npm run build                      -> FAILED (see Known Gaps)
```

Live `/api/account-context` dump against a migrated database:
`service_code='wagle' status='active'` — matching the literals
`MongleAppShell.tsx:90` and `WagleLanding.tsx:136` compare.

- Tests Run: frontend typecheck/lint/token contract; backend full suite plus 3 new contract tests.
- Tests Not Run: production build (environment fault, below); Playwright E2E (its specs navigate the legacy `/naran/doran` path deliberately, which the redirect still serves).

## Completed / remaining

- Known Gaps:
  - **Independent QA has not run** on this task.
  - **`PRODUCTION_BUILD: BLOCKED_BY_PRE_EXISTING_ENVIRONMENT`** — container is `linux-arm64` (musl) but the bind-mounted `node_modules` carries `rollup-darwin-arm64`, so `@rollup/rollup-linux-arm64-musl` is absent and `require('rollup')` fails with no source involved. Fixing it would rewrite the host's mounted `node_modules`, outside this task's scope. Screen behaviour was therefore verified by integration rather than build output, per the directive.
  - **No frontend component-test framework exists** (only `tokenContract.test.mjs`), so the screen is pinned at the API-contract seam rather than by rendering.
  - **`naran` remains** in two approved-keep categories (below).
- Not Measured / Estimated: none.
- QA Status: self-check only.
- Coverage Map Review: `UPDATED` — one new source-backed row.

## Deliberate keeps — reported, not hidden

Three occurrences remain in active frontend source: the `/naran/doran` legacy
redirect (`App.tsx:107`) and its two explaining comments. These are already
classified `ROUTE_CONTRACT_KEEP` by
`engineering/phase2/MONGLE_NARAN_REMAINING_ALLOWLIST.md`, and `App.tsx` carries
the inline rule *"KEEP UNTIL EXPLICIT CLEANUP GATE — do not remove without a
separate, explicit PM-approved cleanup task."*

`naran` is also deprecated (PM raised this mid-task). The same allowlist covers
both remaining categories:

| Occurrence | Class | Why not changed here |
|---|---|---|
| `/naran/*` route strings | `ROUTE_CONTRACT_KEEP` | URL contract; removal 404s live bookmarks |
| `useFamilyContextStore` `naran.activeFamily.*` | `EXTERNAL_OR_PERSISTED_CONTRACT` | Persisted browser storage key — renaming silently resets every user's selected-Family state |

## Risks and Human Gate

- A bulk substitution broke the legacy redirect during this task (rewriting `/naran/doran` → `/naran/wagle`, which would have 404'd the bookmarks it exists to serve) and inverted a historical comment. Both were caught and fixed, but independent QA should re-check the diff for the same failure mode rather than trusting the metrics alone.
- The persisted storage key was deliberately **not** touched; changing it is a user-data decision.
- No commit or push was made.

## Next agent first action

Independent QA of this task: re-derive the four zero metrics, read the diff for
historical-context damage (the failure mode above), confirm the `/naran/doran`
redirect still resolves to `/wagle`, and re-run `tsc`/lint plus the backend
suite. Also re-verify the parent QA's own frontend fix, which was authored by
its verifier. Per PM, the full migration/backend QA does not need repeating.

## Forbidden Scope

Removing the `/naran/*` legacy redirects; renaming the persisted
`naran.activeFamily.*` storage key; backend product code (beyond the three new
contract tests); Wave 3 realtime/Push/PIN; Markpoint Mission/Ledger; adding any
Doran alias; and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-08/MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: one new source-backed row for the frontend service-code contract tests.
- CLOSEOUT GATE: `PASS`
