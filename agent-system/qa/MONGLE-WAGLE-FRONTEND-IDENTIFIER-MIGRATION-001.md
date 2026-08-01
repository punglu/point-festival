# MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001

- Task ID: `MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged start → end)
- environment: repository root `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`; disposable volume-less PostgreSQL 16.9, no host port published; frontend checks in the existing `mongle-frontend-toolchain` container
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Verdict

```text
ACTIVE_FRONTEND_DORAN_IDENTIFIER_COUNT: 0
ACTIVE_FRONTEND_DORAN_FILE_IMPORT_COUNT: 0
ACTIVE_FRONTEND_DORAN_SERVICE_CODE_COUNT: 0
ACTIVE_FRONTEND_DORAN_API_REFERENCE_COUNT: 0
FRONTEND_WAGLE_NAMING_MIGRATION_COMPLETE
PRODUCTION_BUILD: BLOCKED_BY_PRE_EXISTING_ENVIRONMENT
INDEPENDENT_QA_PENDING
```

All four PM target metrics are zero. Production build could not run for a cause
proven unrelated to this work (§7), so the active-screen behaviour was verified
by integration instead of by build output, as the directive requires.

## 2. Why this task exists

The parent independent QA classified the ~127 frontend occurrences as a
non-blocking follow-up. **PM retracted that classification**, and was right to:
the user's decision was that Doran must not be used in the current product at
all, not merely in the backend runtime. The QA's own need to patch
`DoranLanding.tsx` was itself evidence that active frontend code still carried
the name.

## 3. Scope executed

| Area | Action |
|---|---|
| Module directory | `platform/doran/` → `platform/wagle/` (38 files, `git mv`) |
| Page | `DoranLanding.tsx`/`.module.css` → `WagleLanding.tsx`/`.module.css` (`git mv`) |
| Identifiers | `DoranLanding`, `DoranPreviewRoom`, `DoranPreviewMessage`, `DoranPreviewPageState`, `DoranPreviewServiceEvent`, `DoranPreviewRoomKind`, `DoranPreviewMessageReadState`, `DoranPreviewMessageDirection`, `DoranConversationMobile` → `Wagle*` |
| CSS classes | `.doranConversationMode` → `.wagleConversationMode` |
| Imports | every `platform/doran/...` path updated |
| Generated OpenAPI | **regenerated from the real backend schema**, not text-substituted |
| Fixtures/preview | renamed — they model Target behaviour, so per the directive they move to `wagle` |

`git status` confirms these as renames (`R`/`RM`), not delete/add pairs, so file
history is preserved.

## 4. Generated OpenAPI

Not edited as text. The schema was produced from the live application object
(`app.openapi()`) against a database migrated to head, then fed through the
project's own `openapi-typescript`:

```
paths in generated schema:  doran 0 | wagle 11 | markpoint 9
src/generated/openapi.d.ts: doran 0 | /wagle/ 11 | /markpoint/ 9 | 7894 lines
```

The previous file described 41 `/doran/` paths the backend had already stopped
serving — it was stale, not merely misnamed.

## 5. Deliberate keeps — reported, not hidden

Three occurrences remain in active frontend source. All three are the **legacy
URL redirect** and its explaining comments:

```
App.tsx:38   comment describing the legacy aliases
App.tsx:107  <Route path="/naran/doran" element={<LegacyRouteRedirect to="/wagle" />} />
MongleAppShell.tsx:81  comment: canonical path는 /wagle (구 /naran/doran)
```

These are **not** an oversight and **not** my own judgement call. They are
already classified by an approved prior task:

`engineering/phase2/MONGLE_NARAN_REMAINING_ALLOWLIST.md`
(`MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001`) records
`frontend/src/App.tsx` `/naran/doran`, `/naran/family` route strings as
`ROUTE_CONTRACT_KEEP` — "URL/route contract — explicit prohibition, out of
scope". `App.tsx` itself carries the rule inline: *"KEEP UNTIL EXPLICIT CLEANUP
GATE — do not remove without a separate, explicit PM-approved cleanup task."*

**A bulk sweep did break this and it was caught.** The scripted substitution
rewrote the redirect's own path to `/naran/wagle`, which would have 404'd every
bookmark the redirect exists to preserve — the redirect would have pointed at a
URL that never existed. Restored, with a comment stating why it must not be
renamed.

### `naran` is also deprecated — status

PM raised this mid-task. It is correct, and the same allowlist already covers
it:

| Occurrence | Allowlist class | Why it is not this task's to change |
|---|---|---|
| `App.tsx` / `MongleAppShell.tsx` `/naran/*` route strings | `ROUTE_CONTRACT_KEEP` | URL contract; removing breaks live bookmarks. Needs the explicit cleanup gate. |
| `useFamilyContextStore.ts` `` `naran.activeFamily.${accountId}` `` | `EXTERNAL_OR_PERSISTED_CONTRACT` | **Persisted browser storage key.** Renaming silently resets every existing user's selected-Family state on their next visit. The allowlist names this an off-limits category requiring a dedicated PM-approved migration. |

The store already reads the legacy key and copies forward to
`mongle.activeFamily.*`, so the migration path exists — but flipping the key is
a user-data decision, not a naming side effect. **Not touched.** Recorded as a
distinct follow-up rather than folded into this task.

## 6. Verification

| Check | Result |
|---|---|
| `tsc --noEmit` | **EXIT=0**, no errors |
| `npm run lint` (eslint) | **clean**, no output |
| Active import graph | **0** `doran` imports; `platform/doran/` gone |
| `tokenContract.test.mjs` | **29 pass / 0 fail** |
| Backend regression | **173 passed, 0 failed** (170 + 3 new contract tests) |
| `git diff --check` | clean |

### Integration verification of the active screen (the directive's requirement)

Type checking cannot catch this class of defect — both sides of the comparison
are `string`. So the seam itself was pinned with three new backend tests
(`backend/tests/test_frontend_service_code_contract.py`) plus a live payload
dump:

```
real /api/account-context response:
  family: CtxDump
    service_code='wagle' status='active'

frontend literals that consume it:
  MongleAppShell.tsx:90   serviceStatus('wagle')
  WagleLanding.tsx:136    service.service_code === 'wagle'
```

The tests assert the API emits exactly the literal the frontend compares, that
the historical code appears nowhere in the payload, and that the stored
subscription row carries the Target code. A future rename of either side now
fails a test instead of silently blanking the UI.

## 7. Production build — `BLOCKED_BY_PRE_EXISTING_ENVIRONMENT`

Cause reproduced and identified precisely:

```
Error: Cannot find module '@rollup/rollup-linux-arm64-musl'
container arch: linux-arm64   installed native binding: rollup-darwin-arm64
```

`node_modules` was installed on the macOS host and is bind-mounted into an
Alpine/musl Linux container, so the platform-specific rollup binary present is
the wrong one. `require('rollup')` fails on its own, with no source involved —
independent of this task's changes. Fixing it means reinstalling dependencies
inside the container, which would rewrite the host's mounted `node_modules` and
is outside this task's scope.

Per the directive, typecheck alone is **not** treated as approval of screen
behaviour; §6's integration verification stands in its place.

## 8. Defects found and fixed during this task

| # | Finding | Disposition |
|---|---|---|
| 1 | Bulk sweep rewrote the legacy redirect path itself (`/naran/doran` → `/naran/wagle`), which would 404 the bookmarks it exists to serve | **Fixed** — restored, with an inline comment stating it must not be renamed |
| 2 | Same sweep inverted a historical comment (`구 /naran/doran` → `구 /naran/wagle`), making it describe a path that never existed | **Fixed** |
| 3 | Generated `openapi.d.ts` described 41 `/doran/` routes the backend no longer serves | **Fixed** by regenerating from the live schema |

Defects 1 and 2 are the same failure mode that inverted a naming-guard test
during the backend rename: a blind substitution cannot tell a Target identifier
from a historical one. Checking the diff for historical context specifically is
what caught them.

## 9. Five-Gate review

- **환각:** every count is a command result from this session; the OpenAPI file was regenerated from the real schema rather than asserted to be correct; the build failure was reproduced rather than assumed.
- **누락:** components, hooks, types, constants, filenames, import paths, API client, route constants, service-code comparison, generated symbols, fixtures, CSS, UI copy — all covered; the two deliberate keeps are enumerated with their approved classification.
- **오작업:** no Doran alias added; no legacy backfill; the persisted storage key and the URL redirect were **not** silently changed; no unrelated refactoring; backend untouched except three new tests.
- **축혼동:** current Wagle identifiers, the historical URL contract, the persisted-storage contract, and archived documents are kept distinct.
- **신선도:** generated types match the live schema; no broken import; `git diff --check` clean.

## 10. Changed-file manifest

**Renamed (44):** `platform/doran/**` → `platform/wagle/**` (38);
`DoranLanding.tsx`/`.module.css` → `WagleLanding.*` (2); plus the 4 already
counted in the directory move.

**Modified (6):** `App.tsx`, `MongleAppShell.tsx`, `MongleAppShell.module.css`,
`shared/components/Avatar/Avatar.tsx`, `styles/global.css`,
`generated/openapi.d.ts` (regenerated).

**New (1):** `backend/tests/test_frontend_service_code_contract.py`.

## 11. Residual risks

1. **Independent QA of this task has not run.**
2. **Production build unverified** (§7); a bundling-time failure would not have been caught.
3. **`naran` remains** in the route contract and the persisted storage key — both approved keeps, each needing its own PM-gated task.
4. **No frontend component-test framework exists** — only `tokenContract.test.mjs` (node:test). The screen behaviour is pinned at the API-contract seam rather than by rendering the component.
5. E2E specs under `tests/e2e/` still navigate `/naran/doran` deliberately (allowlist `ROUTE_CONTRACT_KEEP`), which is correct while the redirect exists.

## 12. Follow-up tasks (not opened here)

- `MONGLE-LEGACY-ROUTE-CLEANUP-001` — retire `/naran/*` redirects at the explicit cleanup gate.
- `MONGLE-STORAGE-KEY-MIGRATION-001` — move `naran.activeFamily.*` to the canonical key without resetting user state.
- Frontend component-test harness, so screen behaviour can be verified directly.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/qa/MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: one new source-backed row for the frontend service-code contract tests.
- CLOSEOUT GATE: `PASS`

Documentation synchronization only — not independent QA, not PM approval.
