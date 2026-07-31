# MONGLE_W6_1_FOUNDATION_IMPLEMENTATION_PLAN

Task: MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001, §14. Exact per-change plan, written before any code
edit. Scope intentionally kept small — every row below is additive or a single-value alias; nothing
requires touching page JSX, Doran, routes, or Docker/CI.

| # | File | Current role | Intended change | Canonical source | Affected consumers | Expected visual delta | Functional risk | Rollback | Test | Prohibited adjacent change |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `frontend/src/styles/global.css` | Token SSOT | Extend `@import` with `Noto+Sans+KR:wght@400;600;700`; add `--font-family-base` token; `body`/`input,select,textarea` → `var(--font-family-base)` | Font Delivery Contract §5, §1 canonical stack | Every page (root font) | Body text renders Noto Sans KR instead of Pretendard where system doesn't already substitute | Low — additive CDN request, existing fallback chain preserved (`Pretendard` remains 2nd in stack, itself CDN-delivered) | Revert 4 lines | Static contract test (font-family value, import string) | No per-screen font override added |
| 2 | `frontend/src/styles/global.css` | Token SSOT | `--color-brand-600: #5835DF` → `#5A35DF` | D2, Design Token Freeze | 5 files referencing `--color-brand-600` | Slightly deeper purple on brand-600 consumers (IconButton brand tone via `--color-brand-500` unaffected — different token) | Low — single hex value, no structural change | Revert 1 line | Static contract test (hex value) | No other brand-* step touched |
| 3 | `frontend/src/styles/global.css` | Token SSOT | `--color-ink-900: #171D3A` → `#17103A` | D3, Design Token Freeze | 9 files referencing `--color-ink-900` | Marginally darker/purpler ink text | Low | Revert 1 line | Static contract test | No other ink-* step touched |
| 4 | `frontend/src/styles/global.css` | Token SSOT | `--admin-sidebar-bg: #1e1b4b` → `#FBFAFE` | D8, Design Token Freeze | **0** (confirmed dead token; `Sidebar.module.css` hardcodes `#312E81` independently) | **None visible** — token has no consumer yet | None | Revert 1 line | Static contract test (value only, not visual) | Do **not** wire `Sidebar.module.css` to consume it — that is Stage 4 (A5), out of scope |
| 5 | `frontend/src/styles/global.css` | Token SSOT | Add `--space-16: 64px` | D14 canonical scale | None yet (additive) | None | None | Delete 1 line | Static contract test | No renumbering of existing steps |
| 6 | `frontend/src/styles/global.css` | Token SSOT | Add `--radius-card-list: 18px`, `--radius-card-stat: 20px` | Design Token Freeze "Card families", `FROZEN_COMPONENT_TOKEN` | None yet (additive; `Card.module.css` not rewired) | None | None | Delete 2 lines | Static contract test | No change to `Card.module.css` |
| 7 | `frontend/src/styles/global.css` | Token SSOT | Add `--border-width-hairline: 1px` | Existing de facto convention (`--color-line` + literal `1px` already paired everywhere) | None yet (additive) | None | None | Delete 1 line | Static contract test | No mass replace of existing `1px solid var(--color-line)` occurrences |
| 8 | `frontend/src/styles/global.css` | Token SSOT | Add `--size-avatar-xs: 34px`, `-sm: 44px`, `-md: 60px`, `-lg: 78px` | Design Token Freeze "Avatar scale" (candidate→promoted), Component Boundary Freeze recommendation | `Avatar.tsx` (Phase 3, row 12) | None until Avatar consumes them (additive) | None | Delete 4 lines | Static contract test | No renaming of existing numeric `AvatarSize` union |
| 9 | `frontend/src/styles/global.css` | Token SSOT | Add `--layout-gutter-mobile: var(--space-4)`, `--layout-gutter-tablet: var(--space-6)`, `--layout-content-max-width: 1440px` | Responsive Canonical Freeze item 6 (gutter ranges), item 3 (desktop reference viewport ceiling) | None yet (additive, foundation-only) | None | None | Delete 3 lines | Static contract test | No forcing onto any existing screen's CSS |
| 10 | `frontend/src/styles/global.css` | Token SSOT | Add `--safe-area-inset-{top,right,bottom,left}: env(safe-area-inset-*, 0px)` | Responsive Canonical Freeze item 15 (safe-area), existing 3-file `env()` precedent | None yet (additive; existing 3 direct `env()` usages left untouched) | None | None | Delete 4 lines | Static contract test | Do not replace existing direct `env()` call sites |
| 11 | `frontend/src/styles/global.css` | Token SSOT | Comment-flag `--danger: #ef4444` as `DEPRECATED_CANDIDATE, 0 consumers` | Inventory §2 | None (comment only) | None | None | Delete comment | — | Do not delete the declaration itself |
| 12 | `frontend/src/pages/AdminDashboard/AdminLayout.module.css` | Screen-local override | `font-family: 'Pretendard', sans-serif` → `var(--font-family-base)` | Row 1 | AdminLayout wrapper | Admin shell text renders Noto Sans KR | Low — value-only change | Revert 1 line | Manual visual check (no automated DOM render available) | No structural/layout change |
| 13 | `frontend/src/pages/UserDashboard/components/WeeklyDateBar.module.css` | Screen-local override | Same as row 12 | Row 1 | WeeklyDateBar | Same | Low | Revert 1 line | Same | Same |
| 14 | `frontend/src/pages/UserDashboard/UserDashboard.module.css` | `--user-font` declaration (1 declaration, ~35 `var()` consumers) | Reorder to canonical: `'Noto Sans KR', Pretendard, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | §1 canonical fallback stack | UserDashboard (all `var(--user-font)` call sites, single declaration point) | UserDashboard text now actually renders Noto Sans KR (previously never reached — system fonts always won) | Low — single-line, no JSX/layout change | Revert 1 line | Static contract test (declared value) | No JSX/structure change |
| 15 | `frontend/src/pages/Auth/Auth.module.css` | `--user-font` declaration (1 declaration, ~12 `var()` consumers) | Same as row 14 | Same | Auth pages | Same | Low | Revert 1 line | Same | Same |
| 16 | `frontend/src/shared/components/Button/Button.module.css` + `.tsx` | Unused primitive, legacy tokens | Rewire `.btn`/`.primary`/`.ghost`/`.dangerSm` to canonical tokens (`--color-brand-600`, `--color-ink-700`, `--color-danger`, `--font-family-base`, `--radius-control`/`-pill`, `--size-touch-min` min-height, `focus-visible` outline); add `type = 'button'` default in `.tsx` | §17(C), Component Boundary Freeze | **0** (no current consumer — confirmed) | None visible anywhere (unused) | None — 0 consumers | Revert file | Static + component-shape test | Do not rename variant keys (`primary`/`ghost`/`dangerSm` kept); do not add `loading` (no existing API for it); do not consume Button on any screen |
| 17 | `frontend/src/shared/components/Avatar/Avatar.tsx` | `AvatarSize` numeric union | Extend type to also accept `'xs'\|'sm'\|'md'\|'lg'` mapped to row-8 tokens, **in addition to** existing numeric literals (union widened, not replaced) | Component Boundary Freeze | 4 existing consumers (all pass numeric literals today — zero behavior change for them) | None for existing consumers; new named-size option available for future use | Low — additive union member | Revert file | Static contract test (size-map values) | Do not remove any existing numeric option |
| 18 | `frontend/src/shared/components/IconButton/*` | Already compliant | **No functional change** — confirmed already meets 44px touch target, mandatory `aria-label`, `focus-visible`, disabled state | §17(B) | 2 existing consumers | None | None | N/A | Static contract test only (documents compliance) | — |
| 19 | New: `frontend/src/shared/tokens/tokenContract.test.mjs` (or similar, see §Testing note below) | none | New static contract test file, zero new dependency (Node's built-in `node:test`/`node:assert`) | §19 | — | None (test-only) | None | Delete file | Is itself the test | No product code branch added for tests |
| 20 | New: `engineering/phase2/MONGLE_W6_1_TOKEN_COVERAGE_MATRIX.md`, `..._PRIMITIVE_CONTRACT.md`, `..._RESPONSIVE_FOUNDATION_MATRIX.md`, `..._TOKEN_PRIMITIVE_FOUNDATION_REPORT.md` | none | New documentation | §24 | — | None | — | Delete files | — | — |

## Explicitly excluded from this plan (per §14's own exclusion list)

Page component reconstruction; global Doran-domain component promotion; global `Card`/`MainLogo`
promotion; Dock implementation; A1-A5 screen work; any hard CSS breakpoint value (per Gate C's
`BREAKPOINT_IMPLEMENTATION_DEFERRED`); `Sidebar.module.css` rewiring (Stage 4); any elevation/shadow
scale beyond the existing `--shadow-sm`/`-md` (still `DEFERRED` per Design Token Freeze); any change to
`platform/doran/**`, `platform/pages/DoranLanding.*`, routes, backend, Docker, nginx, Vite config,
lockfiles, or `package.json`.

## Testing note (constraint discovered this session, disclosed here rather than worked around)

`frontend` has **no test runner installed** (`grep` of `node_modules`/`.pnpm` for `vitest`/`jest`/
`@testing-library/*` returns zero hits; `package.json` has no `test` script). Installing one would be a
dependency/lockfile change, which is an absolute constraint violation for this task. Per §19's own
principle ("don't branch product code for tests," implicitly: don't fabricate passing results either),
this plan implements only what is genuinely executable with zero new dependencies: **static, source-level
contract tests** using Node's built-in `node:test` + `node:assert` (ships with Node itself, already
installed, touches no `package.json`/lockfile) that read the actual CSS/TSX source text and assert the
canonical values/attributes are present. This covers §19 category (A) in full and parts of (B)/(C)/(D) as
static-shape checks (e.g., "IconButton source declares a required `label` prop and renders `aria-label`"),
but **cannot** cover true rendered-DOM behavior (image-load-failure fallback rendering, real click/focus
event simulation, computed-style assertions) without React Testing Library + jsdom, which are not
installed. This gap is disclosed explicitly in the Foundation Report rather than silently narrowed or
fabricated as full coverage.
