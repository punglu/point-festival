# MONGLE_ROUTE_NAMESPACE_MIGRATION_PLAN

TASK ID: MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-DESIGN-001
**This is a plan, not an implementation.** No phase below has been executed. Built on the recommended Option C (`/naran/doran`→`/wagle`, `/naran/family`→`/family`) and the recommended storage Option C (copy-forward, legacy key retained for a window) from the companion design documents.

> **Implementation update (MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001):** Phases 1–7 were executed (collapsed into one implementation pass rather than run as fully separate sequential deployments, since this was a single bounded task rather than a multi-release rollout) — canonical routes, legacy alias with `replace` redirect, storage copy-forward migration, tests, and full verification (cold-start ×2, 66/66 PASS, Visual Delta 0) are complete. **Phase 8 (legacy route/key disposal) remains explicitly un-executed** — it is a PM Gate, not a code phase, and stays open per this plan's own design. See `MONGLE_FE_ROUTE_NAMESPACE_MIGRATION_REPORT.md` for full evidence.

## Guiding principle (per task's own closing note)

The goal is not to delete the string `naran`. The goal is to introduce Mongle's new canonical URLs for the two affected screens **without** breaking existing bookmarks, Family selection state, or (if one exists) an installed PWA instance — verified at every phase, not assumed.

## Phase 0 — Baseline freeze

- **변경 대상**: none (this design task itself).
- **변경 금지 영역**: everything — this phase is the measurement baseline already captured in `MONGLE_CURRENT_ROUTE_AND_PERSISTENCE_INVENTORY.md`.
- **선행 조건**: none.
- **rollback**: N/A.
- **테스트**: baseline `lint`/`build`/cold-start E2E already confirmed 30/30 PASS in this design task (§5 gate).
- **시각 증거**: not required at this phase (no visual change).
- **완료 조건**: this design package (5 documents) reviewed and approved by PM.
- **PM Gate**: approval to proceed to Phase 1 at all, plus the specific decisions listed in the main design report's PM Decision Gate (route candidate confirmation = Option C, storage option confirmation = Option C, new storage key literal name).

## Phase 1 — Add new routes as aliases (old routes untouched)

- **변경 대상**: `frontend/src/App.tsx` — add two new `<Route>` entries (`/wagle`, `/family`) pointing at the exact same elements (`MongleAppShell><DoranLanding/></MongleAppShell>` and the Family equivalent) that `/naran/doran`/`/naran/family` already use. The old two routes **remain registered, unchanged, fully functional** at the end of this phase.
- **변경 금지 영역**: `/naran/doran`/`/naran/family`'s own route definitions (not removed or redirected yet), `Doran`/`doran` internal identifiers, `naran.activeFamily.*` storage key, backend, DB, PWA manifest, nginx.
- **선행 조건**: Phase 0 PM approval.
- **rollback**: Delete the two new `<Route>` lines — zero impact on existing functionality since nothing else references them yet.
- **테스트**: New E2E assertions confirming `/wagle` and `/family` render identically to `/naran/doran`/`/naran/family` (same component, same content) — added *alongside* existing tests, not replacing them.
- **시각 증거**: One screenshot per new path per viewport, compared pixel-for-pixel against the existing `/naran/doran`/`/naran/family` screenshots — expected **zero diff** (same component tree renders at both URLs).
- **완료 조건**: Both old and new paths independently reachable and visually identical; existing 30/30 E2E suite still passes unmodified.
- **PM Gate**: none additional — mechanical addition, no policy decision at this phase.

## Phase 2 — Point internal navigation at the new routes

- **변경 대상**: `MongleAppShell.tsx`'s desktop nav `to=`, mobile Dock `to=` (×2), `isDoranConversationMobile`/`doranState`-unavailable-banner path checks — all switched from `/naran/doran`/`/naran/family` literals to `/wagle`/`/family`. Any other `navigate()`/`<Link>` call site found to reference these two paths (per the inventory doc, none currently exist beyond the Shell itself and `DoranLanding.tsx`'s own internal `?room=` query handling, which is path-relative and needs no change).
- **변경 금지 영역**: the old routes stay registered (Phase 1's aliases remain valid — a user with an old tab open mid-navigation, or a stale cached asset referencing the old path, still lands somewhere valid).
- **선행 조건**: Phase 1 complete and verified.
- **rollback**: Revert the `to=`/path-check literals back to `/naran/*` — the old routes are still registered so nothing breaks.
- **테스트**: E2E clicks through the Dock/desktop nav and asserts the resulting URL is now `/wagle`/`/family`, not the old path.
- **시각 증거**: Re-capture the 5-screen × 3-viewport set; expect **zero visual delta** (only the URL bar's contents differ, not any rendered pixel).
- **완료 조건**: All internal navigation produces the new URLs; the old URLs are only reachable via direct entry/bookmark, no longer via any in-app click.
- **PM Gate**: none additional.

## Phase 3 — Redirect old → new (compatibility layer)

- **변경 대상**: Replace the old routes' element from "render `DoranLanding`/`FamilyLanding` directly" to `<Navigate to="/wagle" replace />` / `<Navigate to="/family" replace />` — preserving query string (React Router's `<Navigate>` with a relative target and no explicit search-param stripping keeps the current location's search/hash by default when using `useLocation`-based redirect components; the concrete redirect component implementation detail is left to the implementation task, not fixed here).
- **변경 금지 영역**: query/hash must survive the redirect (e.g. `/naran/doran?room=42` → `/wagle?room=42`, not a bare `/wagle`); the 404 catch-all route must not intercept `/naran/doran`/`/naran/family` (they remain explicitly registered redirect routes, not "unmatched").
- **선행 조건**: Phase 2 complete — no internal code should still be *producing* the old URLs, only *consuming* them (i.e., only external bookmarks/shared links should hit this redirect from this point on).
- **rollback**: Revert the redirect element back to Phase 1's direct-render aliases.
- **테스트**: Direct entry to `/naran/doran?room=42` → asserts final URL is `/wagle?room=42` and the correct room is shown; same for `/naran/family`; assert **no redirect loop** (a single hop, not chained); assert browser Back from the redirected page returns to whatever page linked to the old URL, not back into the redirect itself (verify with `replace`, not `push`, semantics).
- **시각 증거**: Screenshot of the *final* rendered page after redirect — expect it to match Phase 2's `/wagle`/`/family` screenshots exactly (same destination component).
- **완료 조건**: Old URLs redirect correctly with query/hash preserved, single-hop, no loop, `Back` behaves sanely.
- **PM Gate**: **Redirect retention duration** (how long `/naran/*` keeps redirecting before optional removal) — PM Decision Gate item #3/#4.

## Phase 4 — Storage migration (independent of routes, can run in parallel with Phases 1–3)

- **변경 대상**: `useFamilyContextStore.ts`'s `load()` — add the copy-forward logic from the Storage design doc's Option C: if the new-named key is absent and the legacy `naran.activeFamily.${accountId}` key has a valid value, copy it to the new key, then proceed unchanged.
- **변경 금지 영역**: the legacy key is **not deleted** in this phase; `selectFamily()`'s write path switches to the new key name going forward.
- **선행 조건**: PM has confirmed the new key's literal name (PM Decision Gate item #5).
- **rollback**: Remove the copy-forward branch; since the legacy key was never deleted, behavior reverts to exactly today's.
- **테스트**: Three deterministic scenarios per the Storage doc §2.1: legacy-only, new-only, both-present-differing — each asserted against the expected resulting `activeFamilyId`.
- **시각 증거**: Not applicable (no visual surface for this change) — screenshot evidence not required for this phase.
- **완료 조건**: All three scenarios pass; multi-account and multi-tab behavior unchanged from today (no new race condition introduced — verified by the same test running under two concurrent browser contexts if the implementation task has capacity for it, otherwise documented as a known pre-existing limitation, not introduced by this migration).
- **PM Gate**: **Legacy key removal timing** (PM Decision Gate item #6).

## Phase 5 — Test suite migration

- **변경 대상**: `tests/e2e/specs-mongle/01-shell.spec.ts` — update the 3 `page.goto('/naran/...')` calls to the new paths (per Phase 2's completion, these represent "what the app now actually does"); **add** (not replace) explicit redirect-compatibility tests for the old paths per Phase 3.
- **변경 금지 영역**: no existing assertion is weakened, skipped, or deleted — only path-string inputs change to match the app's new default navigation, exactly as was done for the Naran→Mongle identifier rename in the prior task.
- **선행 조건**: Phases 1–3 complete.
- **rollback**: Revert path strings; since Phase 1's aliases and Phase 3's redirects both still exist, either old or new path strings continue to work in tests.
- **테스트**: The updated suite itself is the test — run cold-start ×2 exactly as in prior tasks.
- **시각 증거**: Screenshot artifact filenames may be renamed to drop `naran-doran`/`naran-family` in favor of `wagle`/`family` (cosmetic, matching `MONGLE_NARAN_REMAINING_ALLOWLIST.md`'s precedent of allowing artifact-label cleanup separately from route-string values).
- **완료 조건**: Cold-start ×2, 30/30 (or the new total, if redirect-specific tests are added) PASS, identical between runs.
- **PM Gate**: none additional.

## Phase 6 — Documentation/manifest alignment

- **변경 대상**: Per the PWA design doc's Part 1.3 conclusion, **no manifest change is actually required**. This phase is limited to: updating `MONGLE_ROUTE_AUDIT.md`/`MONGLE_SCREEN_ROUTE_DOCK_MATRIX.md`-style current-state docs (if they are still being actively referenced) to reflect the new canonical paths, following the same "supplement note, don't rewrite historical citations" pattern established in the prior namespace-alignment task.
- **변경 금지 영역**: historical/archived documents, Task IDs, any `Status: canonical` doc's `doran.*`/`doran_*` contract text.
- **선행 조건**: Phases 1–5 complete and verified.
- **rollback**: Documentation-only; trivially revertible.
- **테스트**: N/A (docs).
- **시각 증거**: N/A.
- **완료 조건**: Current-state docs accurately describe the new canonical paths; historical docs untouched.
- **PM Gate**: none additional.

## Phase 7 — Full verification

- **변경 대상**: none (verification-only phase).
- **변경 금지 영역**: everything, by definition.
- **선행 조건**: Phases 1–6 complete.
- **테스트**: Full E2E matrix per §15 of the design task instructions — old-route direct entry, new-route direct entry, redirect, refresh, query, hash, invalid nested path, 404, login redirect, logout, Family switching, account switching, browser Back/Forward — across all 5 viewports/projects already established in `playwright.mongle.config.ts`. Cold-start ×2, identical results required.
- **시각 증거**: Full 3-viewport × N-screen recapture (5 existing + 2 new canonical paths = 7 screens), diffed against Phase 2's captures; expect zero delta outside the intentional URL-bar difference.
- **완료 조건**: All DoD items from the (future) implementation task's own Definition of Done are met — this design's job ends at defining what that DoD must contain (§15 of the design instructions), not at running it.
- **PM Gate**: sign-off to proceed to Phase 8's disposal question.

## Phase 8 — Old-route disposal decision (PM Gate only, no default execution)

- **변경 대상**: nothing is removed automatically. This phase is purely the PM decision of *whether and when* to eventually stop serving the `/naran/*` redirect routes and delete the legacy storage key.
- **변경 금지 영역**: N/A — this phase doesn't touch code by definition until a future, separately-scoped task executes whatever the PM decides here.
- **선행 조건**: sufficient time elapsed per whatever redirect-retention window the PM set in Phase 3's gate.
- **rollback**: N/A (this phase is a decision record, not code).
- **테스트**: N/A at this phase.
- **시각 증거**: N/A.
- **완료 조건**: PM decision recorded (keep redirect indefinitely / remove after date X / remove after usage drops below threshold Y — whichever the PM prefers).
- **PM Gate**: this entire phase **is** the gate — see main design report §16 items #3/#4/#6.

## Explicit non-goals of this plan (do not let a future implementation task drift into these)

- Renaming `/dashboard` or restructuring `/admin/*` (that's Option D territory, explicitly deferred).
- Building a Service Worker, offline support, or `id`/`scope` manifest fields (PWA Foundation, separate task).
- Adopting `www.mongle.life` as a live Origin (separate task, no code dependency on this migration).
- Any change to `backend/app/domains/doran/**`, `doran.*` permissions, or `doran_*` tables.
