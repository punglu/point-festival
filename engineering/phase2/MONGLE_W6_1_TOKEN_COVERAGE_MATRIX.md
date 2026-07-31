# MONGLE_W6_1_TOKEN_COVERAGE_MATRIX

Task: MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001, §24. Final state of every token touched or added by
this task, cross-referenced to its canonical source and verification method.

| Token | Old value | New value | Canonical source | Verified by |
|---|---|---|---|---|
| `--color-brand-600` | `#5835DF` | `#5A35DF` | D2, `MONGLE_W6_DESIGN_TOKEN_FREEZE.md` | Static test (`tokenContract.test.mjs`), build-output grep (`5A35DF` present in `dist/assets/index-*.css`) |
| `--color-ink-900` | `#171D3A` | `#17103A` | D3, same freeze | Static test, build-output grep (`17103A` present) |
| `--admin-sidebar-bg` | `#1e1b4b` | `#FBFAFE` | D8, same freeze | Static test, build-output grep (`FBFAFE` present); confirmed 0 consumers so zero visual delta |
| `--font-family-base` (new) | n/a | `'Noto Sans KR', Pretendard, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | D4, same freeze; §1 canonical stack | Static test; CDN URL curl `200`; build-output grep (`Noto+Sans+KR` present) |
| `--space-16` (new) | n/a | `64px` | D14, same freeze (global semantic base 4-64px) | Static test |
| `--radius-card-list` (new) | n/a | `18px` | "Card families," same freeze | Static test |
| `--radius-card-stat` (new) | n/a | `20px` | same | Static test |
| `--size-avatar-xs/sm/md/lg` (new) | n/a | `34/44/60/78px` | "Avatar scale," same freeze + Component Boundary Freeze promotion recommendation | Static test; `Avatar.tsx` named-size map cross-check |
| `--border-width-hairline` (new) | n/a | `1px` | Existing de facto convention (`--color-line` + literal `1px`) | Static test |
| `--layout-gutter-mobile` (new) | n/a | `var(--space-4)` = `16px` | `MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md` item 6 | Static test |
| `--layout-gutter-tablet` (new) | n/a | `var(--space-6)` = `24px` | same, item 6 | Static test |
| `--layout-content-max-width` (new) | n/a | `1440px` | same, item 3 (desktop reference viewport) | Static test |
| `--safe-area-inset-{top,right,bottom,left}` (new) | n/a | `env(safe-area-inset-*, 0px)` | same, item 15 | Static test |
| `--danger` (legacy) | `#ef4444` | unchanged, comment-flagged `DEPRECATED_CANDIDATE` | Inventory §2 (0 consumers, confirmed) | Static test asserts the flag comment is present |
| `--color-danger` | `#EF4665` | unchanged | Already `FROZEN_SEMANTIC_TOKEN` | Static test (still correct) |
| `--color-canvas`, `--color-chat-own/-other`, `--radius-pill`, `--size-touch-min` | unchanged | unchanged | Already `FROZEN_GLOBAL_TOKEN`/`FROZEN_COMPONENT_TOKEN`, 3-way agreement | Static test (touch-min), no change needed |

## Tokens explicitly NOT added (avoiding invented values)

- A full elevation/shadow scale beyond existing `--shadow-sm`/`-md` — Design Token Freeze classifies this
  `DEFERRED` (tablet-only evidence, not cross-checked against approved mobile PNGs). Not implemented.
- A hard CSS breakpoint constant — see `MONGLE_W6_1_RESPONSIVE_BREAKPOINT_AUDIT.md`,
  `BREAKPOINT_IMPLEMENTATION_DEFERRED`.
- Any change to `--color-brand-700/500/400/200/100/50` or `--color-ink-950/700/500` — not part of D2/D3,
  no evidence to justify touching them.
- `--admin-sidebar-text`/`--admin-sidebar-active`/`--admin-sidebar-width` — not part of D8's decision text
  (only the background tone was resolved); left unchanged to avoid fabricating unevidenced values.

## Verdict

**TOKEN_COVERAGE_COMPLETE for this task's 17-item scope.** Every value change traces to a PM-resolved
decision (D2/D3/D4/D8/D14) or an already-`FROZEN`/`FROZEN_COMPONENT_TOKEN` classification; every new
addition is additive-only with 0 forced consumers, verified by both static test and production build
output.
