# MONGLE_W6_1_CURRENT_TOKEN_PRIMITIVE_INVENTORY

Task: MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001, §13. Fresh grep-verified inventory of
`frontend/src/**` as it exists at HEAD `08619298`, before any Wave 6.1 edit.

## 1. Token SSOT

**`frontend/src/styles/global.css`** is the confirmed **CURRENT_SSOT** for all shared design tokens
(`:root` custom properties + the `[data-domain="admin"]` block). No competing global token file exists
(`reset.css` has no custom properties). Hard Stop #12 (SSOT unidentifiable) does not fire.

## 2. Color tokens

| Token | Value | Consumers (grep, `.css`) | Classification |
|---|---|---|---|
| `--color-brand-600` | `#5835DF` | 5 files | `ACTIVE_TOKEN`, migration target per D2 → `#5A35DF` |
| `--color-brand-700/500/400/200/100/50` | unchanged ramp | 11 files total reference some `--color-brand-*` | `ACTIVE_TOKEN`, not part of D2, left unchanged |
| `--color-ink-900` | `#171D3A` | 9 files | `ACTIVE_TOKEN`, migration target per D3 → `#17103A` |
| `--color-ink-950/700/500` | unchanged | 14 files total reference some `--color-ink-*` | `ACTIVE_TOKEN`, not part of D3, left unchanged |
| `--color-canvas` | `#F7F6FC` | multiple | `CURRENT_SSOT` / `FROZEN_GLOBAL_TOKEN`, 3-way agreement, no change |
| `--color-danger` | `#EF4665` | 5 files | `ACTIVE_TOKEN`, matches `FROZEN_SEMANTIC_TOKEN`, no change |
| `--danger` (legacy, root-level, distinct from `--color-danger`) | `#ef4444` | **0** (`grep -rn "var(--danger)"` returns zero hits, fresh-confirmed this session) | `DUPLICATE_SEMANTIC` / `DEPRECATED_CANDIDATE`, now **consumer-count-proven zero** — flagged in-place, not deleted (§15 "don't delete deprecated candidates immediately") |
| `--admin-sidebar-bg` | `#1e1b4b` | **0** — fresh grep of `pages/AdminDashboard/**` finds no reference; the live `Sidebar.module.css` hardcodes `background: #312E81` directly, entirely independent of this variable | `UNUSED` token / dead alias. Actual current Admin sidebar visual is driven by literals, not this variable. Migration target per D8 → `#FBFAFE`, safe to update (zero consumer impact) |
| `--color-chat-own` / `--color-chat-other` | `#6944EF` / `#F3F0FF` | Doran components | `FROZEN_COMPONENT_TOKEN`, 3-way agreement, no change |
| `--color-line` / `--color-surface` / `--color-surface-soft` | as declared | widely used | `ACTIVE_TOKEN`, no change |
| Non-semantic legacy root vars (`--bg`, `--accent`, `--blue`, `--text`, `--muted`, `--gold`, `--shadow`, `--input-bg`, `--brand-purple/coral/orange/mint/skyblue/pink/gold`) | various | still consumed by `Button.module.css` (`--accent`, `--input-bg`, `--muted`, `--text`) and elsewhere | `LEGACY_TOKEN`, `OUT_OF_SCOPE` for Wave 6.1 wholesale removal (used outside this task's 3-primitive scope in places not audited exhaustively); Button's specific 4 references are addressed in Phase 3 (Button reconciliation) only |

## 3. Typography

| Item | Current | Classification |
|---|---|---|
| `body { font-family }` | `'Pretendard', sans-serif` (global.css) | `CURRENT_SSOT`, migration target per D4 |
| `@import` (global.css line 3) | Google Fonts CDN: Pretendard/Black Han Sans/Inter — **live, already shipping** | `ACTIVE_TOKEN`-equivalent (delivery mechanism), Noto Sans KR to be added to this same mechanism (see Font Delivery Contract) |
| `--user-font` (2 files: `UserDashboard.module.css:40`, `Auth.module.css:29`) | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', sans-serif` — Noto Sans KR listed **last**, so on virtually every real OS it never actually gets selected (system fonts win first) | `DUPLICATE_SEMANTIC` competing with the root font declaration, order inverted vs. the PM-confirmed canonical stack. Single declaration point each (~35 and ~12 `var(--user-font)` consumers respectively, but only 1 edit point per file) |
| `Pretendard` literal (hardcoded, not via token) | `pages/AdminDashboard/AdminLayout.module.css`, `pages/UserDashboard/components/WeeklyDateBar.module.css`, `shared/components/Button/Button.module.css` | `SCREEN_LOCAL_LITERAL` overriding root font at 3 points |

## 4. Spacing

Current ladder: `--space-1`(4) `-2`(8) `-3`(12) `-4`(16) `-5`(20) `-6`(24) `-8`(32) `-10`(40) `-12`(48).
81 `var(--space-N)` usages counted (`grep -c`). Matches D14's canonical base exactly except missing the
64px step (`--space-16`, following the file's own `suffix × 4 = px` naming convention). Classification:
`CURRENT_SSOT`, `ACTIVE_TOKEN`, additive gap only (no existing step is wrong).

## 5. Radius / Elevation / Border / Sizing

| Item | Current | Classification |
|---|---|---|
| `--radius-pill` (999px), `--radius-control` (16px), `--radius-card` (24px), `--radius-hero`/`-dialog` (28px) | present | `ACTIVE_TOKEN`, `FROZEN_GLOBAL_TOKEN`, no change |
| Card 2-radius family (`card-list` 18px / `card-stat` 20px) | **not present as tokens** — `Card.module.css`'s single `.card` uses `--radius-card` (24px) uniformly, no 2-family split implemented | `MIGRATION_ALIAS` candidate — additive tokens only (§ Implementation Plan); not wired into `Card.module.css` this task (Card has 1 consumer, `RECOMPOSE`-status per Component Boundary Freeze, not this task's scope to rewire) |
| `--shadow-sm` / `--shadow-md` | present, 2 steps | `ACTIVE_TOKEN`; a fuller named scale (`--shadow-card/-cta/-modal/-sheet`) is `DEFERRED` per Design Token Freeze (tablet-only evidence, not cross-checked) — **not implemented this task**, avoiding invented values |
| `--color-line` | `#E8E6F2` | doubles as the de facto border-color token already; no new border-color token needed |
| 1px hairline border literal | scattered (`border: 1px solid var(--color-line)` pattern already consistent) | `ACTIVE_TOKEN`-adjacent; a named `--border-width-hairline: 1px` alias is additive-only, zero-risk |
| `--size-touch-min` | `44px` | `ACTIVE_TOKEN`, `FROZEN_GLOBAL_TOKEN`, already correct — item 7 (Control Height/Touch Target) already satisfied, no change needed |
| Avatar scale (xs/sm/md/lg = 34/44/60/78) | **not present** — `AvatarSize` type is a numeric union `28 | 36 | 44 | 56 | 72` | `MIGRATION_ALIAS` candidate — `DEFERRED`→`CANDIDATE` per Design Token Freeze, explicitly recommended for promotion in Wave 6.1 by Component Boundary Freeze |
| Layout width/gutter | no dedicated tokens; screens use `--space-*` values directly for padding | `NOT_VERIFIED` as a named token, additive tokens proposed (see Implementation Plan) |
| Safe-area | `env(safe-area-inset-*)` used directly (not tokenized) in `MongleAppShell.module.css`, `ChatComposer.module.css`, `DoranLanding.module.css` — **3 files, functioning correctly already** | `ACTIVE_TOKEN`-equivalent pattern, not touched; a named token alias is additive only |

## 6. Primitive inventory (fresh grep, this session)

| Primitive | Path | Consumers (grep-verified, this session) | API surface | Classification |
|---|---|---|---|---|
| `Avatar` | `shared/components/Avatar` | 4: `DoranLanding.tsx`, `RoomItem.tsx`, `ChatHeader.tsx`, `MessageBubble.tsx` | `size?: 28\|36\|44\|56\|72` | `CURRENT_PRIMITIVE`, `REUSE_WITH_VARIANT` (size scale extension planned) |
| `IconButton` | `shared/components/IconButton` | 2: `ChatHeader.tsx`, `ChatComposer.tsx` | `label` (required), `icon`, `tone?`, `badgeCount?`; already `min-width/height: var(--size-touch-min)`, `aria-label` mandatory, `focus-visible` present | `CURRENT_PRIMITIVE`, `REUSE_AS_IS` — already compliant with §17(B)'s contract, no functional gap found |
| `Button` | `shared/components/Button` | **0** (fresh grep confirms, matches Component Boundary Freeze) | `variant?: 'primary'\|'ghost'\|'dangerSm'` | `CURRENT_PRIMITIVE`, unused. CSS wired to **legacy** non-canonical tokens (`--accent` #10b981 green, `--input-bg`, `--muted`, `--text`, hardcoded `#059669`/`#ef4444`/`#fee2e2`/`#fecaca`, hardcoded `'Pretendard'` font) — none of these are the canonical Brand/Ink system |
| `Card` | `shared/components/Card` | 1: `ServiceActionCard.tsx` | `variant`, `as` | `SCREEN_LOCAL_KEEP`, out of this task's scope (not in §3's 17-item list) |
| `MainLogo`, `PhotoUpload`, `Toast`, `ChatModal`, `AppIcon`, icons | various | per prior CLAUDE.md history | `OUT_OF_SCOPE` — not named in §3, not touched |

## Verdict for this Gate

**INVENTORY_COMPLETE.** SSOT confirmed (`global.css`). No Hard Stop #12/#13 fires — no token competes
unresolvably across files; the only true duplicate (`--danger` vs `--color-danger`) already has a
documented, unambiguous canonical winner and a proven-zero-consumer loser. Avatar/IconButton APIs are both
extendable without breaking any of their combined 6 consumers. Button has genuinely 0 consumers, matching
§17(C)'s explicit "finish only the foundation contract, don't force it onto a screen" instruction.
