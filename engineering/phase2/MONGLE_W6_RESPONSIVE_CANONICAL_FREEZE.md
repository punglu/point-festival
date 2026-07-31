# MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 12.

Basis: `MONGLE_W6_MOBILE_TABLET_RESPONSIVE_DELTA_MATRIX.md`, `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md`,
Section 2 PM Decision `RESPONSIVE-SEQUENCE-001` (already approved, treated as Tier 0).

| # | Item | Frozen value | Evidence |
|---|---|---|---|
| 1 | Mobile reference viewport | **390×844** (per Section 12 minimum-verification list; the approved mobile PNGs themselves are native-device-resolution renders, not a fixed canvas — D1 in the PM Decision Brief is the still-open question of which aspect ratio a *build* viewport should target) | Task prompt Section 12; `D1` unresolved |
| 2 | Tablet reference viewport | **768×1024** (portrait) and **1024×1366** (landscape, minimum-verification list) — the tablet HTML's own authored canvases are 768×1024 / 1024×700; the shorter 700px landscape height is the *design artifact's presentation frame*, not necessarily the implementation target height | `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md` |
| 3 | Desktop reference viewport | **1440×900** — only screens with an approved desktop source (A5) use this; A5's approved PNG dimensions (1448×1086, per `6.0A/approved_source_file_inventory.csv`) are close but not identical | Task prompt; `6.0A` CSV |
| 4 | CSS breakpoint candidates | **Not frozen as exact pixel cutoffs.** Evidence supports two transition zones — a mobile→tablet transition somewhere ≤768px and a tablet-portrait→tablet-landscape (or →desktop) transition somewhere ≥1024px — but the tablet source itself contains zero `@media` queries to derive an exact number from, and Hard Stop rules forbid treating a design artifact's fixed canvas size as an automatic breakpoint. **`PM_DECISION_REQUIRED`** before Wave 6.1 CSS is written. | `MONGLE_W6_MOBILE_TABLET_RESPONSIVE_DELTA_MATRIX.md` "No CSS breakpoints exist to measure" |
| 5 | Content max-width | Screen-dependent, not a single global value: A2/A3/A4 landscape content areas are edge-to-edge within their 1024px frame (no additional max-width constraint observed); A5's `<main>` is also edge-to-edge within its 1024px frame minus the 80px rail | Delta Matrix zone reads |
| 6 | Gutter | Tablet screens consistently use **22–30px** outer padding and **10–24px** inter-zone gaps (vs. mobile's tighter 16–34px outer / 8–16px inter-zone per `6.0A/MEASUREMENT_TABLE_V2.md` §categories) — `RESPONSIVE_LAYOUT_VALUE`, not a new global spacing token (see Token Freeze) | Delta Matrix |
| 7 | Column behavior | A2 landscape: 2-column grid (`1.45fr 1fr`) with one spanning cell; A3 landscape: 2-column (`1fr 1.3fr`); A4 landscape: fixed 280px sidebar + flex-1 thread; A5 landscape: fixed 80px rail + flex-1 main. Portrait: single column throughout, A3 mission list becomes a 2-up tile grid. **No column count is shared across all 4 screens** — column behavior is `RESPONSIVE_LAYOUT_VALUE` per-screen, not a single frozen rule | Delta Matrix |
| 8 | Tablet navigation | **Landscape**: persistent left icon rail replaces BottomDock **on A2 and A5 only** (92px/80px respectively); A3 and A4 landscape have **no persistent nav chrome at all** in the tablet source — flagged `UNJUSTIFIED_DIVERGENCE` in the Delta Matrix, not silently normalized to "always show a rail." **Portrait**: BottomDock retained everywhere it was checked (A2/A3/A4), consistent with Section 2 Decision item 12 (mobile dock stays, only landscape gets a rail) | Delta Matrix Open Item 1 — `PM_DECISION_REQUIRED` on whether A3/A4 landscape's chrome-free treatment is intentional |
| 9 | Tablet Dock processing | Portrait Dock = same 4-destination BottomDock as mobile (icon+label, active=brand-600+bold, inactive=text-disabled) — `SAME_COMPONENT`, no new component needed | Delta Matrix (nav rows, A2/A3/A4 portrait) |
| 10 | Header change | Screen-dependent: A2 gains an inline family-avatar-stack (landscape only, `TABLET_ONLY_PRESENTATION`); A3 gains a logout pill (both orientations, `TABLET_ONLY_PRESENTATION`, no mobile precedent); A4/A5 headers were not found to diverge structurally beyond density | Delta Matrix |
| 11 | Dialog width | **`NOT_VERIFIED`** — no modal/dialog zone was read in the 4 screens analyzed in depth this session; the 11 lower-priority tablet screens (which include `1z`/기본모달, `2h`/교환확인, `2c`/레벨업축하) were not zone-mapped (disclosed effort-allocation, see Delta Matrix) | — |
| 12 | Card grid | A3 portrait mission grid = 2-up; A2 landscape service grid = 5-up (`repeat(5,1fr)`); A2 portrait service grid = 4-up. No single "the tablet card grid is N-up" rule holds across screens — per-screen `RESPONSIVE_LAYOUT_VALUE` | Delta Matrix |
| 13 | Table processing | **Frozen, single rule, directly evidenced**: Admin screens (A5 confirmed) become a real data table at tablet width — CSS Grid row (`grid-template-columns:150px 1fr 118px 96px 100px`), sticky-style header row (`background:#FBFAFE`), inline action pills (승인/반려) on the pending row, striped-highlight for the pending row. This directly confirms Section 2/README's own claim for this specific screen; not yet re-confirmed for other admin screens (`1v`/가족규칙, `2e`/미션목록관리 etc. — not zone-mapped this session) | Delta Matrix A5 `transaction_table` row |
| 14 | Chat pane processing | A4: room-list sidebar (280px, landscape-only) + message thread, bubble contract unchanged (`own`/`other`/`system` 3-state, colors match `COMPONENT_STYLE_CONTRACT.md` exactly) — `SAME_COMPONENT`, layout wrapper is the only new piece | Delta Matrix A4 rows |
| 15 | Safe-area | **`NOT_VERIFIED`** — the tablet source (unlike the mobile source) was not observed to include a fake-status-bar/home-indicator chrome in the screens read this session (A2 landscape includes a real status-bar-style time/battery row at the top of its content, distinct from the mobile mockup's fake-chrome pattern flagged `PRESENTATION_ARTIFACT` in `6.0A/ASSET_MANIFEST.md` — **this specific status-bar-look row in the tablet source needs the same `PRESENTATION_ARTIFACT` scrutiny before Wave 6.1**, flagged here, not resolved) | A2 landscape read, lines 48-55 of tablet source |
| 16 | Touch target | **`NOT_VERIFIED`** — no explicit touch-target-size measurement was taken this session (would require pixel-level re-measurement of every tappable element across all screens; out of this Gate's disclosed effort allocation) | — |
| 17 | Orientation policy | Both orientations are separately, fully hand-authored (not derived from one DOM via a rotation transform) — confirms Section 2 Decision item 7 ("same semantic DOM + breakpoint adaptation," not "two different screens"). No orientation-*lock* policy evidence found either way (`NOT_VERIFIED`) | Delta Matrix — zero `DOM duplication needed` rows |
| 18 | Overflow policy | Confirmed pattern: scrollable content regions use `overflow-y:auto` with `min-height:0` on a flex ancestor (A2 activity list, A3 mission list, A5 transaction table body) — consistent CSS pattern across all 4 screens, safe to freeze as the shared technique | Delta Matrix — repeated across A2/A3/A5 |
| 19 | Text wrapping | **`NOT_VERIFIED`** — no long-Korean-text overflow case was specifically exercised in the screens read | — |
| 20 | Long-content behavior | Confirmed: lists that could grow (활동 피드, 미션 목록, 거래 내역) are all wrapped in a scroll container with a `flex:1; min-height:0` parent rather than letting the whole screen scroll — same technique as #18, freeze together | Same evidence as #18 |

## Explicitly forbidden (re-confirmed, not re-litigated)

- 480px fixed canvas as a real breakpoint — the tablet source's own 1024×700/768×1024 canvases are
  **design-artifact presentation frames**, same category, not automatically promoted to CSS breakpoints
  either (see item 4).
- Device-model-name dependency, user-agent sniffing, tablet-only routes/API/fixtures, full-screen scale
  transforms, naive mobile-scale-up or desktop-scale-down — none were found in the tablet source (every
  screen is independently hand-authored per orientation, confirming compliance with this prohibition at
  the *design* level; the *implementation* must independently avoid scale-transform shortcuts).

## Verdict for this Gate

**PARTIALLY_FROZEN.** Items 6, 9, 13, 14, 17 (technique), 18, 20 are frozen with direct evidence. Items 4
(breakpoint pixel value), 8 (nav-chrome inconsistency on A3/A4 landscape) are `PM_DECISION_REQUIRED`.
Items 11, 15 (partial), 16, 19 are `NOT_VERIFIED_WITH_REASON` (outside this session's zone-mapping depth
or requiring pixel-level re-measurement not yet performed) — carried to
`MONGLE_W6_FUNCTIONAL_DEEP_AUDIT_SUPPLEMENT.md` / follow-up.

## Closeout Update (MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, PM 확정)

Item 8 (tablet navigation, A3/A4 landscape nav-chrome inconsistency, Delta Matrix Open Item 1) is now
**`PM_RESOLVED`** via PM Decision `D15`: **navigation chrome must never be removed for tablet.**

- Portrait: 4-item bottom dock is allowed **if the source shows one** — confirmed for A2/A3/A4 portrait
  (all show the same 4-item BottomDock).
- Landscape: a nav rail is allowed **only if the tablet source explicitly shows one** — confirmed for A2
  (92px rail) and A5 (80px rail).
- A3 and A4 landscape show **no** nav chrome at all in the tablet source. This is now classified
  **`SOURCE_PRESENTATION_OMISSION`**, explicitly **not** an approval to ship an immersive/chrome-free
  layout for those two screens. The **current nav** (existing dock/rail behavior already in the product)
  must be preserved for A3/A4 landscape instead of following the source literally.

Reference viewports (items 1-3) are reconfirmed unchanged and now PM-backed rather than provisional:
mobile **390×844** (`D1`), tablet **768×1024** (portrait) / **1024×1366** (landscape, minimum-verification
value — taller than the tablet source's own 700px-tall landscape canvas, per this document's item 2 note,
still not silently stretched), desktop **1440×900** (A5 only). Shared semantic components (item 20's
"zero DOM-duplication-required" finding) remain the frozen technique — no mobile/tablet functional tree
duplication is authorized by this closeout. The 480px fixed canvas remains explicitly **not adopted** as a
real breakpoint (unchanged from the "Explicitly forbidden" section above).

Item 4 (exact CSS breakpoint pixel value) remains genuinely open — `D15` resolves the nav-chrome question,
not the breakpoint-number question. This is disclosed as residual scope for Wave 6.1's own token/layout
foundation work, not silently closed.
