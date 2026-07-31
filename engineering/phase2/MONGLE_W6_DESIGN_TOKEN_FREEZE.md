# MONGLE_W6_DESIGN_TOKEN_FREEZE

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 15. Merges: `6.0A/APPROVED_TOKEN_CANDIDATES.md` (mobile
approved-source measurement), `6.0B/TOKEN_IMPLEMENTATION_AUDIT_V2.md` (current `global.css`, full read),
and `docs/temp/design_tablet/design-system/canonical-tokens.css`/`TOKEN_CLASSIFICATION.md` (tablet source,
read in full earlier this session). Three-way comparison, not two-way — this is new relative to 6.0AB.

| Category | Item | Approved mobile (6.0A) | Current code (6.0B, `global.css`) | Tablet source (this session) | Classification |
|---|---|---|---|---|---|
| Color | Brand accent | `#5A35DF` (117× — highest-frequency accent) | `--color-brand-600: #5835DF` (near-miss, R-channel 2/256 off) | `--color-brand-600: #5A35DF` (**exact match to approved**, `canonical-tokens.css`) | `SOURCE_CONFLICT` (current vs. the other two) → **`D2`, strengthened toward Option B (update token) by a second independent source, still PM call** |
| Color | Ink/text-primary | `#17103A` (188× — single highest-frequency color in the file) | `--color-ink-900: #171D3A` (near-miss, G-channel 13/256 off) | `--color-text-primary: #17103A` (**exact match to approved**) | `SOURCE_CONFLICT` → **`D3`, same strengthening as D2** |
| Color | Canvas | `#F7F6FC` | `--color-canvas: #F7F6FC` (exact match) | `--color-canvas: #F7F6FC` (exact match) | `FROZEN_GLOBAL_TOKEN` — 3-way agreement, no PM call needed |
| Color | Danger | `#EF4665` (per 6.0A candidates) | Two co-existing values: legacy `--danger: #ef4444` and `--color-danger: #EF4665` | `--color-danger: #EF4665` | `FROZEN_SEMANTIC_TOKEN` = `#EF4665`; the legacy `--danger: #ef4444` is `DEPRECATED_CANDIDATE` (unclear consumer count, `NOT_VERIFIED` per 6.0B — do not delete blind, but do not use in new work) |
| Color | Chat own/other | `#6944EF` / `#F3F0FF` (approved, both A4/A2-chat context) | `--color-chat-own`/`--color-chat-other` exact match | `.token-bubble-own`=`#6944EF`, `.token-bubble-other`=`#F3F0FF` exact match | `FROZEN_COMPONENT_TOKEN` — **3-way agreement**, the single strongest-evidenced token pair in this entire freeze |
| Color | Admin sidebar tone | Approved PNG: near-white `#FBFAFE` | `[data-domain="admin"] --admin-sidebar-bg: #1e1b4b` (dark indigo) | Tablet `1e` landscape rail: `background:#FBFAFE` (**directly re-measured this session**, matches approved PNG) | `SOURCE_CONFLICT` → **`D8`, now evidenced by 2 independent sources (approved PNG + tablet HTML) against 1 (current code)** — still PM call per Section 14 rule 7 (incumbency doesn't win) |
| Typography | Font family | `Noto Sans KR` (Google Fonts CDN, confirmed both HTML sources) | `'Pretendard', sans-serif` (global body) | `--font-family-base: 'Noto Sans KR', system-ui, sans-serif` (tablet `canonical-tokens.css` line 82) | `SOURCE_CONFLICT` → **`D4`, now 2-source-agreed (approved mobile + tablet) vs. 1 (current code)** — task prompt explicitly forbids resolving this as a side effect of any other task; remains `PM_DECISION_REQUIRED`, not auto-adopted despite the added corroboration |
| Spacing | Scale shape | Odd-number literals (3/5/7/9/11px) dominant, no clean ladder | Strict 4px-multiple ladder: 4/8/12/16/20/24/32/40/48 | **A third, distinct scale**: 4/6/8/10/12/14/16/18/22/24 (`canonical-tokens.css` `--space-1..10`) | `SOURCE_CONFLICT`, newly complicated by a 3rd distinct value set — **new PM decision needed, not covered by any existing D1-D12 item; recommend folding into `D4`'s "typography/token work" gate as a combined "spacing scale" question rather than opening a 14th item, since no implementation depends on resolving it before Wave 6.1 A1 kickoff** |
| Radius | Pill | 999px | `--radius-pill` present, exact | `--radius-pill: 999px` exact | `FROZEN_GLOBAL_TOKEN` |
| Radius | Control/input | ~14-16px (approved) | `--radius-control: 16px` (6.0B "exact match") | `--radius-sm: 14px` (input), close but not identical to current's 16px | `RESPONSIVE_LAYOUT_VALUE`-adjacent near-miss, low risk (2px), not escalated to a new PM item — recommend accepting current `16px` as the implementation value per Section 14 rule 5 (Tier 1M PNG doesn't give sub-pixel precision here either) |
| Radius | Card families | Two families in approved source: 18px (list-group) / 20px (stat/summary) | Not confirmed as a 2-family split in current code (6.0B did not report this distinction) | Tablet source confirms same 2-family split: `--radius-md-list: 18px`, `--radius-md-stat: 20px` | `FROZEN_COMPONENT_TOKEN` (2-family split itself); current-code alignment `NOT_VERIFIED`, deferred to Component Boundary Freeze |
| Sizing | Touch target min | Not directly measured in 6.0A | `--size-touch-min: 44px`, exact match per 6.0B | Tablet avatar `sm`=44px coincides numerically but is a different semantic (avatar size, not touch target) — **not the same token, do not conflate** | `FROZEN_GLOBAL_TOKEN` (touch-min=44px, current code already correct) |
| Component | Avatar scale | Not established as a named scale in 6.0A (approved mobile source measured individual instances, no explicit ramp) | Not established in 6.0B's audit | **New, explicit**: `xs`34/`sm`44/`md`60/`lg`78px, `RESOLVED` per tablet's own `AMBIGUITY_AND_PM_REVIEW.md` item 3 (only observed-repeat sizes named) | `DEFERRED` — this is tablet-sourced-only evidence; per Section 3's caution, a tablet-only pattern is not auto-promoted to a shared token without corroboration from the mobile Tier 1M PNGs, which were not measured for an avatar ramp by 6.0A. Recommend as **candidate** for Wave 6.1, not frozen yet. |
| Shadow | Card/CTA/modal/sheet shadow scale | Not itemized as a named scale in 6.0A | Not itemized in 6.0B | Full named scale present in `canonical-tokens.css` (`--shadow-card`, `--shadow-cta`, `--shadow-modal`, `--shadow-sheet`, etc.) | `DEFERRED`, same reasoning as Avatar scale — tablet-only evidence, not yet cross-checked against approved mobile PNGs pixel-by-pixel |
| Motion | Duration/easing | Explicitly `EXCLUDED_FROM_CANONICAL_VISUAL_TOKENS` per both 6.0A and the tablet delivery's own `AMBIGUITY_AND_PM_REVIEW.md` item 7 | `--duration-*` tokens exist in current `global.css` per the V1-doc-sourced semantic block (not itemized in detail this session) | Explicitly excluded, "Motion: not defined in the source" per tablet `README.md` | `DEFERRED` — two independent design sources agree motion is out of scope for this freeze; current code's existing `--duration-*` values are left untouched, not re-derived from either design source |

## Newly-corroborated vs. genuinely-new findings (explicit, to avoid double-counting evidence as "resolved")

- **Corroborated, not resolved**: `D2` (brand accent), `D3` (ink color), `D4` (font family), `D8` (admin
  sidebar tone) all now have a **second independent design-source data point** (the tablet HTML) agreeing
  with the original approved-mobile-PNG position against current code. Per `MONGLE_W6_CANONICAL_SOURCE_FREEZE.md`
  rule 4, this corroboration is recorded as strengthened evidence, **not** as an automatic resolution —
  each remains a live item in `MONGLE_W6_PM_DECISION_REGISTER.md`.
- **Genuinely new**: the spacing-scale 3-way mismatch (approved odd-number literals vs. current 4px-ladder
  vs. tablet's own distinct 10-step scale) was not previously flagged as a 3-way conflict; folded into the
  `D4`-adjacent typography/token conversation per the recommendation above rather than opened as a new
  top-level decision, to avoid decision-fatigue on a low-urgency item (no screen is blocked on it).
- **3-way agreement (highest confidence, safe to build on immediately)**: canvas color, chat bubble
  own/other colors, pill radius, touch-target-min size, danger color (the *newer* value only).

## Verdict for this Gate

**TOKEN_SET_CLASSIFIED.** 5 `FROZEN_GLOBAL_TOKEN`/`FROZEN_SEMANTIC_TOKEN`/`FROZEN_COMPONENT_TOKEN` items
ready to build on without further PM input. 4 `SOURCE_CONFLICT` items (`D2`, `D3`, `D4`, `D8`) carried to
the PM Decision Register, now with strengthened (not resolved) evidence. 2 `DEFERRED` items (avatar scale,
shadow scale) pending mobile-PNG cross-check before promotion. 1 `DEPRECATED_CANDIDATE` (`--danger:
#ef4444`) flagged, not removed.

## Closeout Update (MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, PM 확정)

All 4 `SOURCE_CONFLICT` items above are now **`PM_RESOLVED`**. No CSS file has been edited by this
closeout task (`frontend/**` is out of scope) — the values below are **migration targets** for Wave 6.1
token/primitive work, not yet implemented:

| Item | Confirmed value | Current code (unchanged until Wave 6.1) | Status |
|---|---|---|---|
| Brand accent (`D2`) | **`#5A35DF`** | `--color-brand-600: #5835DF` | `PM_RESOLVED` |
| Ink/text-primary (`D3`) | **`#17103A`** | `--color-ink-900: #171D3A` | `PM_RESOLVED` |
| Font family (`D4`) | **Noto Sans KR**, fallback `'Noto Sans KR', system-ui, sans-serif` | `'Pretendard', sans-serif` | `PM_RESOLVED` + **`FONT_DELIVERY_REQUIRED`** (no font-file/CDN dependency found in this repo — only a static-HTML-embedded Google Fonts `<link>` in the design sources; resolved at the **Wave 6.1 Start Gate**, not here) |
| Admin sidebar tone (`D8`) | **`#FBFAFE`** (bright/near-white) | `[data-domain="admin"] --admin-sidebar-bg: #1e1b4b` | `PM_RESOLVED` — existing edit/delete/approve/reject functionality in Admin views must be preserved; this is a visual recompose only |

**Spacing scale (`D14`, new item, decided independently of `D4` per this document's own prior
recommendation)**: `PM_RESOLVED` — **4/8/12/16/20/24/32/40/48/64px** is the **global semantic base**
(current code's 4px-ladder, extended with a 64px step). The approved-PNG's odd-number literals and the
tablet source's own distinct 10-step scale (`--space-1..10`, 4/6/8/10/12/14/16/18/22/24) are **not**
adopted as the base; screen-specific values that don't fit the base ladder are recorded as
`SCREEN_LOCAL_MEASURED_VALUE`, and values that only make sense at one responsive breakpoint are
`RESPONSIVE_LAYOUT_VALUE`. Both categories may coexist with the global base without being treated as
violations of it.

This closeout does not change the `DEFERRED` status of the avatar-scale or shadow-scale candidates, nor
the `DEPRECATED_CANDIDATE` status of `--danger: #ef4444` — none of those were part of D1-D15.
