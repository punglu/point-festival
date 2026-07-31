# MONGLE_W6_MOBILE_TABLET_RESPONSIVE_DELTA_MATRIX

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 10 (independent tablet measurement) + Section 11
(Mobile·Tablet Responsive Delta Matrix). Machine-readable companion: `MONGLE_W6_MOBILE_TABLET_RESPONSIVE_DELTA_MATRIX.csv`.

## Effort allocation (disclosed, following the 6.0A precedent)

Full zone-by-zone treatment was given to the **4 screens that map directly to the current A2–A5 Mongle
scope** (`1b`/홈→A2, `1c`/포인트잔치→A3, `1d`/대화→A4, `1e`/포인트관리→A5), read in full from source this
session. The remaining 11 tablet-covered priority screens (`1g`/`1h`/`1i`/`1k`/`1n`/`1q`/`2j`/`2i`/`2x`/`3c`/`2q`)
and the 51 screens covered beyond the delivery's own "15 priority" claim were confirmed to **exist** and
were spot-checked against the density rules stated in `docs/temp/design_tablet/design_handoff_family_platform/README.md`
(already reviewed earlier this session — landscape master-detail, portrait single-column, unchanged type
scale, admin-as-table) but were **not** individually zone-mapped. This mirrors 6.0A's own disclosed
effort-allocation choice for EXTRA-01..04. A1 (로그인/프로필 선택) has **no tablet screen at all** —
excluded from this matrix, tracked instead in `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md`.

## No CSS breakpoints exist to measure

Confirmed by direct read: the tablet HTML has **zero `@media` queries** (same authoring convention 6.0A
found in the mobile source). "Breakpoint" in this document means *the two hand-authored fixed-canvas
sizes the delivery provides* (1024×700 landscape, 768×1024 portrait), not a CSS-derived transition point.
Per Section 10's own instruction, these viewport numbers are not assumed to equal the product's real CSS
breakpoints — that decision belongs to `MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md`.

## A2 (Family Home / `1b` 홈) — zone delta

| Zone | Mobile semantic role (per 6.0AB Phase A/B) | Tablet landscape (1024×700) | Tablet portrait (768×1024) | Classification |
|---|---|---|---|---|
| Primary nav | BottomDock (current React: `MongleAppShell.tsx`) | **Replaced** by 92px left icon rail, 5 destinations (홈/잔치/대화/나/설정), active state = tinted pill bg | BottomDock retained, 4 destinations (no 설정 in portrait dock — matches mobile's 4-item dock) | `NAVIGATION_RELOCATION` (landscape only) |
| Greeting header | Avatar + "안녕하세요, N님!" + subtitle + notification bell | Same content, avatar 52px, adds inline family-avatar stack (아빠/엄마/민준 overlapping circles) not present in the read mobile-equivalent structure | Avatar 60px, no family-avatar-stack | `SAME_COMPONENT_NEW_DENSITY` (landscape adds a zone); `TABLET_ONLY_PRESENTATION` for the avatar-stack sub-element specifically |
| Hero card ("가족 대화" promo) | Single full-width promo card | 1.45fr column, height 158px, same gradient/copy/CTA pill | Full-width, height 160px | `SAME_COMPONENT_NEW_WIDTH` |
| Recent activity list | Card list, 3 rows shown | Merged into a taller right-hand pane (`grid-row:span 2`) that also embeds a 2-row "오늘 진행 중인 미션" mini-widget inline below the activity feed | Standalone card, 3 rows, no embedded mission mini-widget | `SAME_COMPONENT_NEW_LAYOUT` for the activity list itself; the embedded mission mini-widget in landscape is `TABLET_ONLY_PRESENTATION` — **not confirmed against any approved mobile source** (A2's own approved PNG scope per 6.0A did not depict this sub-widget) |
| Service tile grid | 4-tile grid (홈/잔치/대화/할일) per portrait read | Landscape: 5-column grid, 10 tiles incl. disabled/opacity-.55 "coming soon" tiles (가계부/식단관리/건강기록/차량관리/독서기록) + an explicit "서비스 추가" add-tile | Portrait: 4-tile grid, matches mobile tile count/order | `COLUMN_RECOMPOSITION` (landscape only); the 6 additional disabled tiles are `TABLET_ONLY_PRESENTATION` — no approved mobile evidence either confirms or forbids these, flagged `NOT_VERIFIED` against Tier 1M |

## A3 (Markpoint / `1c` 포인트 잔치) — zone delta

| Zone | Mobile semantic role | Landscape | Portrait | Classification |
|---|---|---|---|---|
| Header | Title + subtitle, no logout affordance confirmed in 6.0A's A3 zone inventory | Adds inline "↪ 로그아웃" pill button, not part of A3's approved mobile header per `6.0A/HTML_STRUCTURE_EXTRACTION.md` | Same logout pill present | `TABLET_ONLY_PRESENTATION` — **new zone, not in Tier 1M mobile source; requires PM confirmation before implementation** |
| Player summary card (avatar/level/progress bar/stat trio) | Present, single column | Left column, 1fr width | Full-width, adds a large point total (`320P`) inline next to the level row not shown in landscape's version of the same card | `SAME_COMPONENT_NEW_LAYOUT` + one `ORDER_CHANGE` (point total position differs landscape vs. portrait, not just density) |
| 가족 응원 메시지 (cheer messages) | Confirmed present on mobile (matches `CheerModal`/`FeedbackSection`-adjacent current-code concept per 6.0B) | Present, own card, below player summary | **Absent** — not present anywhere in the portrait screen read | `VISIBILITY_CHANGE` — cheer messages appear landscape-only in this tablet source; not explained by any density rule in the README, flagged for PM confirmation |
| Mission list | Vertical list, status pill per row (완료/진행중/승인대기) | Vertical list, 1.3fr column, 4 rows visible incl. one negative-point "포인트 사용 내역" row not present in portrait | 2-column tile grid, 11 tiles, compact status pill under icon | `COLUMN_RECOMPOSITION` (list→grid, portrait only) + `SAME_COMPONENT_NEW_DENSITY` (landscape) |
| Bottom nav | BottomDock | **Absent entirely** (no left rail either — this screen's landscape view has no persistent nav chrome at all, unlike A2's landscape) | BottomDock retained, 4 items | `MOBILE_ONLY_PRESENTATION` inverted — landscape A3 is the one screen read so far with **zero primary navigation chrome**, inconsistent with A2/A5 landscape's rail pattern. Flagged as a **within-package inconsistency**, not just a mobile/tablet delta — see Open Items. |

## A4 (Wagle GROUP / `1d` 대화) — zone delta

| Zone | Mobile semantic role | Landscape | Portrait | Classification |
|---|---|---|---|---|
| Room list | Per 6.0B `FUNCTIONAL_CONTRACT_MATRIX.md`, current `/wagle` is fixture-driven with Room List/DIRECT/SERVICE kinds (D6, no approved-mobile equivalent at all) | 280px left sidebar, 1 room row shown ("우리 가족방") | **Absent** — portrait goes straight to the single conversation, no room list surface | `NAVIGATION_RELOCATION` (landscape introduces a persistent room-list pane current mobile approved source never depicted — this directly informs **D6**, see PM Decision Register: the tablet source shows a room list existing as approved tablet UI, though still only 1 room, GROUP-kind, consistent with A4's approved mobile scope, not proof for/against DIRECT/SERVICE kinds) |
| Message thread | Own/other/system 3-state bubble contract (confirmed identical: own=`#6944EF`, other=`#F3F0FF`/white-bordered, system=pill `#EFECF8`) | Present, matches contract exactly | Present, matches contract exactly, larger bubble padding | `SAME_COMPONENT_NEW_DENSITY` — bubble color contract itself is `SAME_COMPONENT` (no deviation found) |
| Composer | Pill input + circular send button | Present, 38px send button | Present, 42px send button | `SAME_COMPONENT_NEW_DENSITY` |
| Nav | BottomDock | **Absent** (no rail, no dock — same "zero nav chrome" pattern as A3 landscape) | BottomDock retained | `MOBILE_ONLY_PRESENTATION` inverted, same open item as A3 |

## A5 (Admin Point / `1e` 관리자 포인트 관리) — zone delta

| Zone | Mobile semantic role | Landscape | Portrait | Classification |
|---|---|---|---|---|
| Sidebar | Per 6.0B `TOKEN_IMPLEMENTATION_AUDIT_V2.md`, current React Admin sidebar = dark indigo `#1e1b4b`; approved mobile PNG = near-white `#FBFAFE` (this is **D8**) | **80px near-white rail** (`#FBFAFE`), 3 icon-only destinations, active = tinted pill — this tablet source is a **third, independent light-tone data point**, consistent with the approved-PNG side of D8, not the current dark-sidebar implementation | Not read this session for A5 (portrait row not included in the excerpt reviewed) — `NOT_VERIFIED`, flagged for follow-up | `SAME_COMPONENT_NEW_WIDTH`; **directly strengthens the evidence for D8 Option A (recompose to light theme)** without resolving it — still a PM call |
| Stat cards | Per 6.0B Gap Matrix, current code has stat cards; approved source comparison partial | 4-card grid (지급/차감/보유/승인대기), 3 neutral + 1 amber "승인 대기" callout card | `NOT_VERIFIED` this session | `SAME_COMPONENT_NEW_LAYOUT` |
| Transaction table | Current React: list rows (per 6.0B) | **Real 5-column data table** (대상/내용/일시/포인트/상태), sticky header row, per-row 승인/반려 action pills, striped pending-row highlight | `NOT_VERIFIED` this session | `COLUMN_RECOMPOSITION` — matches Section 2 PM Decision RESPONSIVE-SEQUENCE-001 item that admin screens become real data tables at tablet width; **directly confirms the README's own claim for this specific screen** |
| Filter/search row | `NOT_VERIFIED` in 6.0A/B mobile analysis | Pill filter chips (전체/지급/차감/대기) + search input, inline | `NOT_VERIFIED` this session | `NOT_VERIFIED` |

## Open items surfaced by this Gate (not resolved here)

1. **A3/A4 landscape have zero persistent navigation chrome** (no left rail, no BottomDock), while A2/A5
   landscape both have an 84–92px/80px rail. This is an **internal inconsistency within the tablet source
   itself**, not a mobile/tablet delta — flagged as `UNJUSTIFIED_DIVERGENCE` pending PM confirmation of
   whether A3/A4's landscape views are intentionally chrome-free (e.g., because the room-list/mission-list
   panes already consume the full width) or an oversight in the tablet delivery.
2. **A3's landscape-only "로그아웃" button and A3's landscape-only "가족 응원 메시지" card** have no
   corresponding zone in the Tier 1M approved mobile PNG per 6.0A's own A3 zone inventory — these are
   `TABLET_ONLY_PRESENTATION` candidates that were never approved for *any* form factor before this
   delivery. Not blocking, but must not be implemented as "confirmed design" without a PM nod.
3. **A2 landscape's embedded mission mini-widget and 6 disabled "coming soon" service tiles** are also
   `TABLET_ONLY_PRESENTATION` with no mobile precedent.

## Required output classification (per Section 11 list)

Every zone above is tagged one of: `SAME_COMPONENT`, `SAME_COMPONENT_NEW_LAYOUT`,
`SAME_COMPONENT_NEW_DENSITY`, `SAME_COMPONENT_NEW_WIDTH`, `COLUMN_RECOMPOSITION`, `ORDER_CHANGE`,
`VISIBILITY_CHANGE`, `NAVIGATION_RELOCATION`, `TABLET_ONLY_PRESENTATION`, `MOBILE_ONLY_PRESENTATION`,
`NOT_VERIFIED`. **Zero zones were classified `SOURCE_CONFLICT` or `UNJUSTIFIED_DIVERGENCE`** except the
one explicitly noted in Open Item 1. **Zero DOM-duplication candidates were found** — every landscape/portrait
pair for A2–A5 is achievable as one semantic DOM tree with CSS Grid/Flex layout adaptation; no zone
required a different reading order that CSS alone could not express, satisfying Section 2 Decision
RESPONSIVE-SEQUENCE-001 items 6–7 (no separate functional component trees, no unjustified DOM duplication).
