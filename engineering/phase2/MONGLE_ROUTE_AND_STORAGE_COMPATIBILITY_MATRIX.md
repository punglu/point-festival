# MONGLE_ROUTE_AND_STORAGE_COMPATIBILITY_MATRIX

TASK ID: MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001

## Route compatibility

| Legacy path | Canonical path | Mechanism | Query preserved | Hash preserved | Auth guard applies |
|---|---|---|---|---|---|
| `/naran/doran` | `/wagle` | `<Route path="/naran/doran" element={<LegacyRouteRedirect to="/wagle" />} />` — client-side `<Navigate replace>` | Yes (verified on narrow viewports; on ≥701px, DoranLanding's own pre-existing auto-room-select subsequently rewrites the query — see Known Interaction below, unrelated to this migration) | Yes | Applied at `/wagle` (the redirect itself carries no guard) |
| `/naran/family` | `/family` | Same pattern | Yes (all viewports — `FamilyLanding` has no query-rewriting effect) | Yes | Applied at `/family` |

**Cleanup status: `KEEP UNTIL EXPLICIT CLEANUP GATE`.** Neither legacy route was removed or scheduled for automatic removal. Removal requires a separate, explicitly PM-approved task (per `MONGLE_ROUTE_NAMESPACE_MIGRATION_PLAN.md` Phase 8).

### Known interaction (not a regression, not introduced by this migration)

`DoranLanding.tsx` (unmodified by this task) auto-selects the first Room and rewrites the URL's query string on desktop/wide (≥701px) viewports during its first `normal`-state render, regardless of how `/wagle` was reached (direct navigation or via the legacy redirect). This was verified to reproduce **identically** whether the pre-migration `/naran/doran` or the new `/wagle` is visited directly with a query string, on the same viewport. It is a pre-existing characteristic of the destination screen, not something this migration's redirect mechanism introduces or worsens — confirmed by manual reproduction (mobile: query/hash survive exactly; desktop: query gets replaced by `?room=...` regardless of entry path).

## Storage compatibility

| Item | Legacy | Canonical |
|---|---|---|
| Key format | `naran.activeFamily.${accountId}` | `mongle.activeFamily.${accountId}` |
| Written by this task | Never (read-only from this point forward) | `load()`'s auto-select/validated-restore path, `selectFamily()` |
| Read priority | Only consulted when canonical is absent | Always checked first; if present (valid or not), legacy is never consulted |
| Copy-forward | N/A | One-time, only when legacy holds a value valid for an accessible Family |
| Deleted on explicit logout | Yes (same account only) | Yes (same account only) |
| Deleted on session-expiry (401 full reload) | No (documented Known Limitation, unchanged from before this task) | No (same) |
| Cross-account isolation | Namespaced by `accountId`, verified via E2E (different login) | Same |

## E2E coverage added this task

`tests/e2e/specs-mongle/01-shell.spec.ts`: 8 new tests (`Canonical route migration` ×4, `Active Family storage migration` ×4), plus 3 existing tests' `page.goto()` inputs updated from `/naran/*` to canonical paths (assertions unchanged, unweakened). All 6 pre-existing tests plus 8 new tests = 14 tests × up to 5 viewport projects (one test is desktop-only by design) = 66 executed test instances, verified PASS on 2 independent cold starts.
