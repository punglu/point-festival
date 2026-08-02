# MONGLE_W6_A2_FAMILY_HOME_SOURCE_MATRIX

Task: `MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-001`
Companion to `MONGLE_W6_A2_FAMILY_HOME_MEASUREMENT.md`.

Target component: `frontend/src/pages/FamilyHomePreview/index.tsx`
Stylesheet: `frontend/src/pages/FamilyHomePreview/FamilyHomePreview.module.css`

Authority order applied throughout:

```text
approved PNG  >  PM decision  >  canonical HTML 1b  >  current React
```

with the measured constraint from `§3` of the measurement document: the
approved PNG carries **structure/presence** authority but **cannot** supply CSS
px (four landmark pairs imply four different scales, 1.93–2.38). Where the PNG
shows something the HTML does not encode, the row is `PM_DECISION_REQUIRED`
rather than agent-resolved — `MONGLE_W6_CANONICAL_SOURCE_FREEZE.md` rules 9/10.

State vocabulary: `EXACT_REUSE`, `VALUE_REUSE`, `REBUILD_REQUIRED`,
`APPROVED_PNG_OVERRIDE`, `HTML_STRUCTURE_REFERENCE`,
`CURRENT_CODE_REFERENCE_ONLY`, `UNKNOWN`, `NOT_IMPLEMENTED_BY_AUTHORITY`.

---

## 1. Zone rows

### Z1 — family identity / profile row

| Column | Value |
|---|---|
| PNG evidence | Avatar + greeting + subtitle + bell with dot, single row, top of app content |
| HTML evidence | `1b` block, first child of content wrapper |
| Exact text | `서` / `안녕하세요, 서연님!` / `우리 가족의 행복한 하루를 응원해요 💜` |
| Asset | none (gradient + initial); bell is the source's own `🔔` glyph |
| Geometry | `flex; align-items:center; gap:10px`; avatar `52×52`; dot `13×13`; bell `28×28`; badge `9×9` |
| Typography | 17/900 `#17103A`; 12/400 `#8A83A8`; avatar 17/700 `#fff` |
| Responsive | copy column `flex:1`, avatar and bell `flex:none` |
| Current code candidate | none reachable |
| Target | `.profile` / `[data-visual-zone="profile"]` |
| State | **`REBUILD_REQUIRED`** |
| Unresolved | avatar photo vs gradient+initial → `ASSET_AUTHORITY_UNRESOLVED` (D-A2-4) |

### Z2 — hero 가족 대화

| Column | Value |
|---|---|
| PNG evidence | Full-width gradient card, large title, 2-line body, purple CTA pill, mascot bleeding bottom-right, white typing bubble top-right |
| HTML evidence | `1b` block, second child |
| Exact text | `가족 대화` / `지금 가족들과`⏎`이야기 나눠보세요` / `바로가기 ›` |
| Asset | `family-platform-mascot.png` — SHA `dd5c48b3…`, byte-identical to canonical |
| Geometry | `radius 28px; padding 15px 20px; min-height 196px`; mascot `210×210 @ right:-26 bottom:-30`; bubble `right:22 top:26`, radius `20 20 6 20` |
| Typography | 28/900; 13/500 `#3A3060` `line-height 1.5`; CTA 14/700 |
| Responsive | copy column intrinsic, mascot absolutely positioned and clipped by `overflow:hidden` |
| Current code candidate | none |
| Target | `.hero` / `[data-visual-zone="hero"]` |
| State | **`REBUILD_REQUIRED`**; asset `EXACT_REUSE` |
| Unresolved | PNG's 3-character scene vs single pin logo → `ASSET_AUTHORITY_UNRESOLVED` (D-A2-4) |

### Z3 — recent-activity card

| Column | Value |
|---|---|
| PNG evidence | White rounded card; title + 더보기; 3 rows, each circular icon + 2-line copy + right-aligned timestamp; hairline dividers after rows 1 and 2 |
| HTML evidence | `1b` block, third child |
| Exact text | see measurement §7 — 3 rows, verbatim, curly quotes preserved |
| Asset | none — `★` `↑` `♥` are the source's own text glyphs |
| Geometry | card `radius 26px; padding 12px; gap 8px`; row `gap 10px`; icon `44×44`; rows 1–2 `padding-bottom 8px; border-bottom 1px #F0EEF7` |
| Typography | 16/700; 12/400; 13/700; 12/700 `#5A35DF`; 11/400 `#A8A5B6` |
| Responsive | copy column `flex:1`, icon and timestamp `flex:none` |
| Current code candidate | none |
| Target | `.activity` / `[data-visual-zone="activity"]`, rows `[data-visual-zone="activity-row"]` |
| State | **`REBUILD_REQUIRED`** |
| Unresolved | PNG row sub-containers (icon inset 75 vs title 41) → `PM_DECISION_REQUIRED` (D-A2-2) |

### Z4 — service navigation tiles

| Column | Value |
|---|---|
| PNG evidence | Section title + 4 equal tiles; tile 1 purple-outlined and active; tiles 2–4 carry 준비중 badges |
| HTML evidence | `1b` block, fourth child |
| Exact text | `우리 서비스`; 4 labels + 4 sublabels + 3 × `준비중` |
| Asset | tile 1 `family-platform-mascot.png`; tiles 2–4 use the source's own `🗓️` `🖼️` `📋` |
| Geometry | `grid repeat(4,1fr) gap 7px`; tile `radius 20px; padding 24px 8px 8px; gap 4px`; tile1 `border 2px #5A35DF`; tiles 2–4 `border 1px #EFECF8`; icon box `48×48 radius 14px #EDE7FB`; badge `top:7 right:7` |
| Typography | 16/700; 11/700; 9/400 `#8A83A8`; badge 9/700 `#7C5AEF` |
| Responsive | 4 columns held at all three viewports; sublabels wrap by width — identical on both comparison sides |
| Current code candidate | none |
| Target | `.services` / `[data-visual-zone="services"]`, tiles `[data-visual-zone="service-tile"]` |
| State | **`REBUILD_REQUIRED`** |
| Unresolved | **white card wrapper present in PNG, absent in HTML → `PM_DECISION_REQUIRED` (D-A2-1)**; illustrated icons vs emoji → `ASSET_AUTHORITY_UNRESOLVED` (D-A2-4) |

### Z5 — bottom navigation dock

| Column | Value |
|---|---|
| PNG evidence | 4-item dock pinned to bottom; 홈 active in brand purple; others muted |
| HTML evidence | `1b` block, sibling after content wrapper |
| Exact text | `홈` / `포인트 잔치` / `대화` / `나` |
| Asset | 4 inline SVGs — path data copied verbatim from canonical `1b` |
| Geometry | `grid repeat(4,1fr); padding 7px 20px 5px; border-top 1px #F0EEF7; background #FDFDFF`; item `gap 3px`; svg `23×23`, `stroke-width 1.8`, round caps/joins |
| Typography | 10/700 `#5A35DF` active; 10/400 `#A8A5B6` inactive |
| Responsive | equal columns at all three viewports |
| Current code candidate | `PointFestivalPreview` renders the identical canonical dock |
| Target | `.dock` / `[data-visual-zone="dock"]` |
| State | **`VALUE_REUSE`** — canonical values and SVG path data reused; **no import from the 1c page**, redeclared locally per the colocation contract |
| Unresolved | none |

---

## 2. Cross-cutting rows

| Item | Source | Target | State |
|---|---|---|---|
| Font family | `--font-family-base`, `MONGLE_W6_1_FONT_DELIVERY_CONTRACT.md` | `.page` | `VALUE_REUSE` |
| Brand `#5A35DF` | `D2` `PM_RESOLVED` | local CSS var | `VALUE_REUSE` |
| Ink `#17103A` | `D3` `PM_RESOLVED` | local CSS var | `VALUE_REUSE` |
| Canvas `#F7F6FC` | canonical `--color-canvas` | `.page` | `VALUE_REUSE` |
| Hero mascot asset | `frontend/src/assets/logos/family-platform-mascot.png` | `.heroMascot` | `EXACT_REUSE` |
| Dock SVG path data | canonical `1b` literals | local icon components | `EXACT_REUSE` |
| OS status bar | canonical `1b` first child | — | `NOT_IMPLEMENTED_BY_AUTHORITY` (`DEVICE_CHROME`) |
| Home indicator | canonical `1b` last child | — | `NOT_IMPLEMENTED_BY_AUTHORITY` (`DEVICE_CHROME`) |
| `1b` / 가족 홈 badge | canonical gallery row | — | `NOT_IMPLEMENTED_BY_AUTHORITY` (`GALLERY_DECORATION`) |
| Card radius 44px + drop shadow | canonical gallery card | — | `NOT_IMPLEMENTED_BY_AUTHORITY` (`GALLERY_DECORATION`) |
| `frontend/src/pages/family-home/**` | current React | — | `CURRENT_CODE_REFERENCE_ONLY` — read, never modified, never imported |
| `/dashboard` | current React | — | `CURRENT_CODE_REFERENCE_ONLY` — not replaced |
| `/__wave6/1b` route | task contract | `App.tsx` | `NOT_IMPLEMENTED_BY_AUTHORITY` this round — `App.tsx` owned by the 1e lane (D-A2-6) |
| Services card wrapper | approved PNG only | — | `PM_DECISION_REQUIRED` (D-A2-1) — **not** applied as `APPROVED_PNG_OVERRIDE`, because the PNG supplies no px contract and rule 10 forbids inventing one |
| Activity row sub-containers | approved PNG only | — | `PM_DECISION_REQUIRED` (D-A2-2) |
| Effective CSS viewport of PNG | — | — | `UNKNOWN` / `RESPONSIVE_VIEWPORT_AUTHORITY_UNRESOLVED` (D-A2-5) |

---

## 3. Reuse decisions that were deliberately refused

| Candidate | Why refused |
|---|---|
| Import the dock from `PointFestivalPreview` | Would promote a preview-local component to shared and would couple A2 to a 1c-owned file. Colocation contract forbids it. Values reused, code not. |
| Reuse `frontend/src/pages/family-home/**` | Service/hook/type-layer screen; contract differs from a presentation-only canonical reproduction. Visual similarity is not a reuse criterion → `REBUILD_REQUIRED`. |
| Reuse `1c` copy or fixtures | Different screen. Every A2 string is read out of canonical `1b`. |
| Promote any A2 piece to `shared/` | Out of scope; would mutate protected paths. |
| Add tokens to global CSS | Prohibited; local CSS vars are scoped to `.page`. |

---

## 4. UI-only contract

| Guarantee | Mechanism |
|---|---|
| backend API request = 0 | no client, no `fetch`, no `axios` import |
| WebSocket = 0 | none |
| localStorage / sessionStorage write = 0 | none |
| cookie mutation = 0 | none |
| navigation / redirect = 0 | no `<a href>`, no router hook; buttons are `type="button"` with a no-op |
| timer / polling = 0 | no `setTimeout`, `setInterval`, or `useEffect` |
| analytics = 0 | none |
| product data mutation = 0 | fixtures are module-level `const`, page-local |

All fixture data is static and colocated. Interactive affordances reproduce
**visual state only**; the dock's active item is a static canonical fact, not
routing state.
