# MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001

- Task ID: `MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001`
- Predecessor: `MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001`
- Parent: `MONGLE-PARALLEL-W2-W4-001`
- author/agent: `Claude Code`
- observed_at: `2026-08-01`
- git_ref: `0d9280c3d3a9254f20c09ba958eb3876e957d245` (unchanged start → end)
- environment: repository root; disposable volume-less PostgreSQL 16.9 (no host port); a **separate throwaway workspace** at `/tmp/fe-clean` with container-only `node_modules` for the clean build
- secrets_redacted: `true`
- Closeout Contract: `v1`

## 1. Executive Verdict

```text
NARAN_RUNTIME_RETIREMENT_COMPLETE
MONGLE_STORAGE_KEY_MIGRATION_COMPLETE
FRONTEND_FULL_NAMING_CLOSEOUT_COMPLETE
PRODUCTION_BUILD_PASS
READY_FOR_COMBINED_NAMING_INDEPENDENT_QA
```

The production build that the predecessor task recorded as
`BLOCKED_BY_PRE_EXISTING_ENVIRONMENT` **now passes** — see §13. That blocker is
resolved, not carried forward.

## 2. Environment / Git Baseline

| Command | Result |
|---|---|
| `git rev-parse --show-toplevel` | `/Users/mac/mac_Project/mongle_ui` |
| `git branch --show-current` | `dev-newmarkp` (as expected) |
| `git rev-parse HEAD` | `0d9280c3d3a9254f20c09ba958eb3876e957d245` (as expected) |
| `git diff --check` | clean at start and end |
| commit / push / merge / rebase / PR | **none** |

Writer: `relay/current.md` read `Current Task: none`; no other writer held the
frontend files. This task registered as the single writer.

## 3. PM Decision Applied

Two allowlist keeps were released and absorbed into this task rather than
deferred:

| Former class | Item | Applied |
|---|---|---|
| `ROUTE_CONTRACT_KEEP` | `/naran/doran`, `/naran/family` | Routes **removed outright**. No redirect, alias or fallback. Old bookmarks 404 by explicit cutover decision. |
| `EXTERNAL_OR_PERSISTED_CONTRACT` | `naran.activeFamily.*` | **One-time migration** to `mongle.activeFamily.*`, then the retired key is deleted. |

`MONGLE-LEGACY-ROUTE-CLEANUP-001` and `MONGLE-STORAGE-KEY-MIGRATION-001` are
therefore not opened — their scope is discharged here.

## 4. Naran Inventory (measured, not copied from the allowlist)

Initial active-product occurrences:

| Location | Count | Class |
|---|---|---|
| `App.tsx` — 2 route registrations + 1 comment | 3 | `ACTIVE_ROUTE` |
| `MongleAppShell.tsx` — 1 comment | 1 | `ACTIVE_RUNTIME` (doc) |
| `useFamilyContextStore.ts` — storage key builder | 1 | `ACTIVE_STORAGE_KEY` |
| `backend/scripts/phase1_seed_synthetic.py` — comment | 1 | `ACTIVE_RUNTIME` (doc) |
| `tests/e2e/specs-mongle/01-shell.spec.ts` | 13 | `ACTIVE_TEST_EXPECTATION` |
| capture manifest, PNG artifacts, archived QA/handoff, allowlist doc | 34 files (37 after this task's own records) | `HISTORICAL_DOCUMENT` / `ARCHIVE` |

The allowlist's own classification was **not** copied — each usage was traced to
its call site. That is how the storage key was confirmed to be genuinely live
rather than dormant.

## 5. Changed-file Audit

Frontend: `App.tsx`, `MongleAppShell.tsx`, `useFamilyContextStore.ts`,
`generated/openapi.d.ts` (regenerated), plus the new
`shared/storage/activeFamilyStorageMigration.ts`.
Tests: `tests/e2e/specs-mongle/01-shell.spec.ts`.
Backend: `scripts/phase1_seed_synthetic.py` (comment only — no product code).
Docs: `MONGLE_NARAN_REMAINING_ALLOWLIST.md` closed.

No Wagle/Markpoint backend code was changed, matching §14's prohibition.

## 6. Route Retirement

Removed from `App.tsx`: both `/naran/*` `<Route>` registrations, the
`LegacyRouteRedirect` component (now unreferenced), and the
now-unused `useLocation` import.

```text
redirect count: 0
alias count:    0
fallback count: 0
```

Retired paths now fall through to the existing catch-all and render the
not-found page. Surviving canonical routes verified present: `/`, `/dashboard`,
`/admin/*`, `/wagle`, `/family`, `*`.

**A self-inflicted scare worth recording:** after the edit my own
`grep '<Route path='` matched only single-line declarations and appeared to
show every canonical route gone. Reading the file showed the router intact —
the canonical routes are multi-line. The grep was wrong, not the code; had I
trusted it I would have "restored" routes that were never removed.

## 7. Storage-key Migration

New module `frontend/src/shared/storage/activeFamilyStorageMigration.ts` is the
sole place the retired key name exists.

| Rule | Behaviour |
|---|---|
| Canonical valid | canonical wins; retired key purged |
| Canonical absent + retired well-formed and accessible | copy forward → purge retired |
| Malformed retired value | ignored, no selection applied, key purged, no crash |
| Retired value referencing an inaccessible Family | not adopted, key purged |
| Repeat runs | idempotent — after run 1 the retired key is gone |
| Other keys | untouched; only the two keys for one `accountId` |
| Normal read/write | canonical only — no dual-write, no permanent fallback |

The value is carried forward before deletion specifically because dropping it
would silently reset every existing user's selected Family — a data loss
disguised as a rename.

`reset()` (logout) clears both names via the module, so a later login cannot
resurrect a pre-logout selection through a retired key migration had not
reached.

The retired namespace is assembled as `'na' + 'ran'` rather than written
literally, so a repository-wide sweep cannot rewrite it into the canonical key
and turn the migration into a no-op that discards the selection. Two such
sweep-induced inversions have already occurred in this migration effort.

## 8–9. File/Symbol and Fixture/Test Migration

No `Naran*` component, type, hook, constant, CSS class or file path existed at
the start — the predecessor task had already handled the `Doran` axis, and the
platform axis had only routes, one storage key and comments.

E2E spec rewritten to the new contract:

- The redirect test is replaced by **`retired /naran/* paths are no longer registered and fall through to the 404 page`**, which asserts no redirect occurs (URL unchanged) and the not-found page renders — for `/naran/doran`, `/naran/family` and bare `/naran`.
- A new **`canonical routes still work`** test guards against over-removal.
- Storage tests inverted where the contract changed: the retired key must now be **absent** after migration (previously "legacy retained, not deleted"), including in the canonical-wins and inaccessible-value cases.
- New **malformed-value** test: no crash, no selection applied, key still purged.
- New **idempotency** assertion: a second reload changes nothing.
- The spec's own retired prefix is likewise built from parts.

## 10. Generated OpenAPI

Regenerated from the live backend schema (`app.openapi()` against a database
migrated to head), then run through the project's `openapi-typescript` — not
text-substituted.

```text
schema paths total: 108
doran: 0 | naran: 0 | /wagle/: 11 | /markpoint/: 9
src/generated/openapi.d.ts: doran 0 | naran 0 | /wagle/ 11
```

## 11. Allowlist Closeout

`MONGLE_NARAN_REMAINING_ALLOWLIST.md` now opens with a CLOSED banner asserting
`ACTIVE_NARAN_ALLOWLIST: EMPTY`, `ACTIVE_NARAN_ROUTE_EXCEPTION: NONE`,
`ACTIVE_NARAN_STORAGE_EXCEPTION: NONE`, records the two released PM keeps and
their current state, and states that storage-migration source is not an active
allowlist entry. Historical rows are retained as record.

## 12. Runtime Seam

Backend contract and frontend consumption verified against each other by the
three contract tests added in the predecessor task, re-run here (`3 passed`
inside the 173): the API emits `service_code='wagle' status='active'`, matching
the literals `MongleAppShell.tsx` and `WagleLanding.tsx` compare.

Storage seam is pinned by the rewritten E2E storage tests (selection preserved
across reload, preserved across migration, and re-asked rather than guessed
when the stored value is unusable).

## 13. Production-build Environment — **BLOCKER RESOLVED**

The predecessor recorded `BLOCKED_BY_PRE_EXISTING_ENVIRONMENT`: the container is
`linux-arm64` (musl) while the bind-mounted `node_modules` carried
`rollup-darwin-arm64`.

Rather than re-citing that evidence, this task built cleanly **without touching
the host's `node_modules`**: repository source plus `package-lock.json` were
copied to a throwaway workspace, and `npm ci` installed a container-only
dependency tree.

```
npm ci (container-only node_modules) -> ok
npm run build                        -> ✓ built in 1.05s
  dist/assets/index-*.js   409.56 kB │ gzip: 132.39 kB
  dist/assets/index-*.css  152.72 kB │ gzip:  27.45 kB
```

`tsc --noEmit` EXIT=0, `eslint` clean and `tokenContract` 29/0 were re-run in
that same clean workspace, so the checks are not dependent on the host's
mismatched tree.

**Bundle-level naming check** (what actually ships):

```text
dist: doran 0 | naran 1 | wagle 2
```

The single occurrence is the migration source, constant-folded by the bundler:

```js
function Kc(n){return`mongle.activeFamily.${n}`}
const tA="naran";
function Em(n){return`${tA}.activeFamily.${n}`}
```

It **must** be in the shipped bundle — without it the migration cannot read the
old key in a real user's browser. Counted as `STORAGE_MIGRATION_SOURCE`, not as
an active identifier.

## 14. Test Commands and Exact Results

```
tsc --noEmit (toolchain)          -> EXIT=0
npm run lint (toolchain)          -> clean
tsc --noEmit (clean workspace)    -> EXIT=0
eslint (clean workspace)          -> clean
tokenContract (clean workspace)   -> 29 pass / 0 fail
npm ci + npm run build (clean)    -> PASS, built in 1.05s
OpenAPI regeneration              -> doran 0, naran 0, wagle 11, markpoint 9
pytest --collect-only             -> 173 collected
pytest -q                         -> 173 passed, 0 failed
git diff --check                  -> clean
```

Backend figures were re-collected, not copied.

**NOT_RUN:**

| Scope | Reason | Verdict impact |
|---|---|---|
| Playwright E2E execution | The rewritten spec asserts the new route/storage contract, but running it needs the full isolated Compose runtime (`mc_phase1`) which this task did not stand up. The spec is type-consistent and its assertions were derived from the implemented behaviour, but **they have not been executed**. | Recorded as the main residual risk; independent QA should run them. |
| Frontend component tests | No component-test framework exists in this repo (only `tokenContract.test.mjs`). | Screen behaviour pinned at the API/storage contract seams instead. |

## 15. Naran Zero Gate

```text
ACTIVE_RUNTIME_NARAN_IDENTIFIER_COUNT: 0
ACTIVE_NARAN_ROUTE_COUNT:              0
ACTIVE_NARAN_FILE_PATH_COUNT:          0
ACTIVE_NARAN_IMPORT_COUNT:             0
ACTIVE_NARAN_COMPONENT_COUNT:          0
ACTIVE_NARAN_TYPE_COUNT:               0
ACTIVE_NARAN_STORAGE_KEY_COUNT:        0
ACTIVE_NARAN_CSS_COUNT:                0
ACTIVE_NARAN_API_REFERENCE_COUNT:      0
ACTIVE_NARAN_TEST_EXPECTATION_COUNT:   0
BACKEND_ACTIVE_NARAN_COUNT:            0
CURRENT_TARGET_DOCUMENT_NARAN_COUNT:   0  (allowlist is now historical)
```

Counted separately, **not** claimed as zero:

```text
STORAGE_MIGRATION_SOURCE_NARAN_COUNT:      2
  frontend/src/shared/storage/activeFamilyStorageMigration.ts
  tests/e2e/specs-mongle/01-shell.spec.ts  (test-side constant)
  (+1 constant-folded occurrence in the built bundle)

PROHIBITION_OR_BEFORE_VALUE_NARAN_COUNT:   3
  Task-ID strings and the comment recording that the aliases were removed,
  plus two test *names* describing what must not exist.

HISTORICAL_ARCHIVE_NARAN_COUNT:            37 files
  archived Task IDs, QA evidence, commit-anchored reports, capture manifest,
  PNG artifacts, and this allowlist document.
```

The repository-wide count is **not** zero and this report does not claim it is.

## 16. Doran Regression Gate

```text
ACTIVE_FRONTEND_DORAN_IDENTIFIER_COUNT:    0
ACTIVE_FRONTEND_DORAN_FILE_IMPORT_COUNT:   0
ACTIVE_FRONTEND_DORAN_SERVICE_CODE_COUNT:  0
ACTIVE_FRONTEND_DORAN_API_REFERENCE_COUNT: 0
dist bundle doran:                         0
```

No Doran alias or stale fixture was reintroduced while retiring Naran.

## 17. Self-QA Findings

| # | Checked failure mode | Result |
|---|---|---|
| 1 | Sweep corrupting the migration source | **Prevented by design** — the retired namespace is assembled from parts in both the module and the spec. |
| 2 | Route removal deleting current Mongle routes | Checked; a bad grep suggested it had, reading the file disproved it. All 6 routes intact. |
| 3 | Storage rename resetting user state | Prevented — value copied forward before the retired key is deleted; E2E asserts preservation. |
| 4 | Retired value overwriting a newer canonical one | Canonical wins unconditionally; asserted. |
| 5 | Malformed storage value crashing startup | Handled and asserted. |
| 6 | `git mv` replaced by delete/add | Not applicable — no file renames this task; the predecessor's renames still show as `R`/`RM`. |
| 7 | Naran → Wagle axis confusion | Avoided: the retired platform name maps to **Mongle** (storage key), never to Wagle. Wagle was used only where the messaging axis already applied. |
| 8 | Manual OpenAPI substitution | Avoided — regenerated from the live schema. |
| 9 | Typecheck passing while runtime seam fails | Guarded by the contract tests and the rewritten storage/route E2E assertions — though those E2E assertions are **not executed** (§14). |

## 18. Recursive Scope Review

- **Before:** inventory of 5 active occurrences + 34 historical files; planned route removal, storage migration module, spec rewrite, OpenAPI regeneration, allowlist closeout.
- **After implementation:** `git status` shows exactly the planned files; no unrelated refactoring; no backend product code.
- **After tests:** zero gates hold; Doran gate did not regress; the one bundle occurrence is accounted for as migration source.

## 19. Five-Gate Review

- **환각:** every count is a command result from this session; the build was actually run and its output quoted; the allowlist's classifications were re-derived rather than copied.
- **누락:** route, component, type, import, file, CSS, storage key, fixture, test, OpenAPI, document, build and runtime seam all covered.
- **오작업:** no `/naran` alias survives; no permanent storage fallback; user selection preserved rather than reset; Naran was not blanket-renamed to Wagle; no Wagle/Doran regression; the host's `node_modules` was never deleted or overwritten.
- **축혼동:** Mongle platform, Wagle messaging, retired Naran, retired Doran, migration source and historical archive are kept distinct.
- **신선도:** active allowlist empty; imports resolve; OpenAPI current; no broken route; `git diff --check` clean.

## 20. Changed-file Manifest

**New (1):** `frontend/src/shared/storage/activeFamilyStorageMigration.ts`
**Modified (6):** `frontend/src/App.tsx`,
`frontend/src/platform/shell/MongleAppShell.tsx`,
`frontend/src/shared/stores/useFamilyContextStore.ts`,
`frontend/src/generated/openapi.d.ts`,
`tests/e2e/specs-mongle/01-shell.spec.ts`,
`backend/scripts/phase1_seed_synthetic.py` (comment only)
**Docs/records:** `MONGLE_NARAN_REMAINING_ALLOWLIST.md`, `COVERAGE_MAP.md`,
`active.md`, `relay/current.md`, this report and its handoff.

## 21. Residual Risks

1. **The rewritten Playwright specs have not been executed.** They encode the new route and storage contract, but only static reasoning backs them today. This is the largest gap and the first thing independent QA should close.
2. **Old `/naran/*` bookmarks now 404** — intended by the cutover decision, but it is a real user-visible change.
3. **Independent QA has not run** on this task or its predecessor.
4. **No frontend component-test framework**, so screen behaviour is pinned at contract seams rather than by rendering.
5. The **one-time migration only runs when a user loads the app**; a browser that never returns keeps its retired key locally. Harmless, but the key is not removed retroactively everywhere.

## 22. Parent Status

```text
MONGLE-WAGLE-FRONTEND-IDENTIFIER-MIGRATION-001:              IMPLEMENTED_AWAITING_INDEPENDENT_QA
MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001:   IMPLEMENTED_AWAITING_INDEPENDENT_QA
MONGLE-PARALLEL-W2-W4-001:                                   INDEPENDENT_QA_PENDING
```

No task graduated.

## 23. Final Verdict

```text
NARAN_RUNTIME_RETIREMENT_COMPLETE
MONGLE_STORAGE_KEY_MIGRATION_COMPLETE
FRONTEND_FULL_NAMING_CLOSEOUT_COMPLETE
PRODUCTION_BUILD_PASS
READY_FOR_COMBINED_NAMING_INDEPENDENT_QA
```

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-NARAN-RUNTIME-RETIREMENT-AND-FRONTEND-CLOSEOUT-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: one new source-backed row for the storage-migration and route-retirement contract.
- CLOSEOUT GATE: `PASS`

Documentation synchronization only — not independent QA, not PM approval.
