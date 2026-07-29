# HTML Structure Extraction

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 9). Full zone data: `html_zone_inventory.csv` (61 rows, A1/A1-S1/A2/A3/A4/A5).

## Parsing method

No `bs4`/BeautifulSoup available and none installed (Hard Stop #8 constraint). Used Python's stdlib
`re` module against the raw file text: `style="..."` attribute extraction, `id="..."` boundary
detection (10 screen boundaries found by locating every `<div id="...">` and treating the byte range
until the next such div — or EOF — as that screen's content), and `data-screen-label="..."` extraction.
Script: `/tmp/mongle-wave6-0ab/scripts/extract_styles.py`; raw per-screen style dump (for full
traceability / re-derivation) at `/tmp/mongle-wave6-0ab/6.0A/_raw_per_screen_styles.json`.

## Document-level structure

- `<!DOCTYPE html><html><head>...<script src="./support.js"></script></head><body><x-dc><helmet>...meta/link/style...</helmet>` then a single `<section>` containing all 10 screens as flex-wrapped siblings, closed by `</x-dc>` and a `<script type="text/x-dc" data-dc-script data-props="{&quot;$preview&quot;:{&quot;width&quot;:1600,&quot;height&quot;:1100}}">` tag.
- **No `<title>` tag** anywhere in the document (verified: `grep -io '<title>.*</title>'` returns nothing).
- **Exactly one `<style>` block** (lines 15-19), containing only 3 rules: a `body` reset (margin/background/font-family/antialiasing), `a { color }`, `a:hover { color }`. **Zero `@media` queries in the entire file** (verified via `grep -c '@media'` = 0) — the document has no responsive breakpoints of its own; every screen is a fixed-size box.
- No standalone `class="..."` selectors are used for layout at all — virtually 100% of visual styling is inline `style="..."` attributes (only the 3 global rules above use a real selector). This means there is no CSS cascade/specificity system to reverse-engineer; every value is a direct per-element literal.
- The only `id` attributes in the whole document are the 10 screen-boundary markers (`1a`, `1a-1`, `1b`..`1i`) — no other IDs exist.

## Repeated component patterns identified (structural, cross-screen)

1. **Phone mockup frame**: `width:480px; border-radius:44px; overflow:hidden; box-shadow:0 30px 70px rgba(40,20,90,.22); display:flex; flex-direction:column` — present on all 9 mobile screens (A1, A1-S1, A2, A3, A4, EXTRA-01..04), only the `background` value varies (gradient for A1/A1-S1, solid `#F7F6FC` for A2/A3/EXTRA, solid `#F8F7FD` for A4).
2. **Fake iOS status bar**: identical markup (down to the exact SVG-less `<i>`/`<span>` battery/wifi/signal glyphs) repeated verbatim in all 9 mobile screens.
3. **BottomDock**: `display:grid; grid-template-columns:repeat(4,1fr)` nav bar with 4 identical SVG icon sets (홈/포인트 잔치/대화/나), only the active-tab color (`#5A35DF` vs `#A8A5B6`) and `font-weight` differ, present on A2, A3, A4, EXTRA-01, EXTRA-04 (EXTRA-02/03 not fully verified — see effort-allocation note).
4. **Home indicator bar**: `132px × 5px`, `border-radius:3px`, `background:#17103A` — present on all 9 mobile screens, always the last child.
5. **Card pattern**: white/near-white rounded panel (`border-radius` 18-26px range) with `box-shadow: 0 5px 16px rgba(60,30,120,.05)` or similar — reused for `ProfileSummaryCard`, `RecentActivityCard`, `FamilyCheerCard`, `TodayMissionListCard`, `ActivityListCard`, `SettingsListCard`, `StatCard` (A5).
6. **Pill badge**: `border-radius:999px` — reused for level badges, status badges (완료/진행중/승인대기), filter tabs, screen-ID labels (the "1a"/"1b" canvas meta-labels), and the AdminSidebar's active-tab background.
7. **Circular avatar with initial**: `border-radius:50%`, `linear-gradient` or flat background, single-Korean-character content — reused in A1 (78px), A2 (52px), A3 (70px), A4 (38/30/42px), A5 (36/64px), EXTRA-01 (66px). Size is not standardized across screens (see `MEASUREMENT_TABLE_V2.md` category E).

## Per-zone data

See `html_zone_inventory.csv` for the full 61-row breakdown covering, per screen (A1/A1-S1/A2/A3/A4/A5):
zone name, DOM basis, parent, `display`, `width`/`height`, `padding`, `gap`/`margin`, alignment,
`overflow`, responsive behavior (nearly always "고정, 반응형 규칙 없음" since there are zero media
queries), whether the pattern repeats elsewhere, and a component-candidate name. Every row's
`source_class` is `CSS_LITERAL` (i.e., read directly from a `style="..."` attribute, not inferred).

## Explicit non-claims

- Because there are no media queries, **no responsive breakpoint behavior can be extracted from this
  HTML** — anything about how these screens behave at other widths is `NOT_VERIFIED`, not merely
  unspecified. Any responsive design intent must come from a Human Gate / PM decision, not from
  re-reading this file harder.
- Computed-style values (via the Playwright render, see `TIER1_HTML_VISUAL_DELTA.md`) were captured only
  for the 10 screen-root bounding boxes/`border-radius`/`background`/`box-shadow` (see
  `zone_bounding_boxes.json`) — not for every zone in `html_zone_inventory.csv`, which remains
  `CSS_LITERAL` (the raw inline value, not a browser-resolved computed value). Where the two happen to be
  captured for the same element they agreed exactly (e.g. A1's `border-radius:44px` literal matches the
  computed `44px`), so no literal-vs-computed discrepancy was found in the overlap that was checked.
