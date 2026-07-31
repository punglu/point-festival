# MONGLE_W6_COMPONENT_BOUNDARY_FREEZE

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 16. Merges `6.0B/COMPONENT_REUSE_MATRIX_V2.md`
(current-code consumer counts, grep-verified) with `docs/temp/design_tablet/design-system/COMPONENT_STYLE_CONTRACT.md`
(design-side structural contract, read in full earlier this session) and the A2–A5 tablet zone reads in
`MONGLE_W6_MOBILE_TABLET_RESPONSIVE_DELTA_MATRIX.md`.

| Canonical name | Current path | Design contract source | Current consumers (grep-verified, 6.0B) | Tablet consumer(s) this session | Classification |
|---|---|---|---|---|---|
| `Avatar` | `shared/components/Avatar` | Tablet: `xs/sm/md/lg` (34/44/60/78px) scale, circle, initials-on-gradient fallback | 4 (`ChatHeader`, `MessageBubble`, `RoomItem`, `DoranLanding`) | A2 greeting (52-60px), A3 player card (60-64px), A4 room-list/participant (36-42px), A5 table row (30px) — sizes cluster near but not exactly on the tablet's own named scale | `SHARED_PRIMITIVE`, `EXISTING_REUSE` — already past the 2nd-consumer bar; **recommend snapping the component's size prop to the tablet-confirmed xs/sm/md/lg scale in Wave 6.1**, not inventing new intermediate sizes (matches tablet delivery's own `AMBIGUITY_AND_PM_REVIEW.md` item 3 ruling) |
| `IconButton` | `shared/components/IconButton` | No dedicated contract entry in tablet's `COMPONENT_STYLE_CONTRACT.md`; closest analogue is the tablet's plain-icon nav-rail items | 2 (`ChatComposer`, `ChatHeader`) | Not a clean 1:1 — tablet nav-rail icons are simpler (icon+label composites, not standalone icon buttons) | `SHARED_PRIMITIVE`, `EXISTING_REUSE` for its current 2-consumer role; `DEFER_PROMOTION` for any nav-rail-icon use case until a concrete tablet nav-rail component is built and shown to actually need this primitive |
| `Button` | `shared/components/Button` | Tablet: Primary Pill (radius 14-16px, brand-600 bg, CTA shadow) + Secondary/Outline contract, both directly matched by A3/A5 tablet buttons (로그아웃 pill, CSV 내보내기/포인트 지급/차감 추가 buttons in A5) | **0** — no current consumer anywhere in `frontend/src` (6.0B, grep-confirmed) | A3 로그아웃 pill, A5's 3-button toolbar are direct visual matches to this exact primitive's variant set | `SHARED_PRIMITIVE`, built but `LEGACY_CANDIDATE`-adjacent (unused, not legacy — never adopted). **Recommend as the first real consumer target for Wave 6.1 A3/A5 tablet buttons**, since its variants already match the tablet contract; flag for close review on first use since it is currently unverified by any real usage (per 6.0B's own caution) |
| `Card` | `shared/components/Card` | Tablet: 2 explicit radius families, `card-list` (18px) and `card-stat` (20px) — directly confirmed again this session in A2's activity-list card (22-24px, closer to `card-stat`) and A3's mission-list card (20-22px) | 1 (`ServiceActionCard` only) | A2/A3/A5 all use card-shaped containers extensively but **not through this component** — they're inline-styled in the design source, so this is about the *target* component's readiness, not an existing tablet consumer | `SCREEN_LOCAL_KEEP` per 6.0B's single-consumer rule — **not promoted yet**, but flagged that Wave 6.1 A2/A3 work is exactly the "2nd/3rd consumer" event that would justify revisiting this, provided the implementation respects the 2-radius-family split rather than collapsing to one |
| `MainLogo` | `shared/components/MainLogo` | Tablet uses the same `family_platform_pin_logo_transparent_1024.png` asset directly (not a styled component) in A2 hero card, A4 room-list header | 1 (`PlayerSelectView` only) | Asset reused, but not through this component in the design source (design source is static HTML, not componentized) | `SCREEN_LOCAL_KEEP`, unchanged from 6.0B |
| `MessageBubble` (+`DateDivider`/`UnreadDivider`/`ChatHeader`/`ChatComposer`/`RoomItem`/`ServiceActionCard`/`LoadingState`/`EmptyState`/`ErrorState`) | `platform/doran/components/*` (10 components) | Tablet A4 confirms the exact same 3-state bubble contract (own/other/system) these components already implement, plus a room-list-row pattern matching `RoomItem` | 1 file each (`DoranLanding.tsx`, barrel-import grep confirmed by 6.0B) | A4 landscape's room-list sidebar row is a strong structural match for `RoomItem`; A4's bubble contract is an exact color/shape match for `MessageBubble`'s existing own/other states | `REUSE_WITH_VARIANT` (within-Doran-domain) — **the tablet A4 landscape room-list is the "second real surface" this matrix already predicted would justify revisiting `RoomItem`'s domain-local status**, but that second surface does not exist in current React yet (only the design source shows it) — so promotion remains `DEFER_PROMOTION` until Wave 6.1 A4 actually builds the tablet room-list pane, not before |
| `AdminSidebar`-equivalent (current: `AdminDashboard/components/Sidebar`) | `pages/AdminDashboard/components/Sidebar` | Tablet A5 landscape: 80px near-white (`#FBFAFE`) icon rail, 3 destinations, tinted-pill active state | Not re-grepped this session (6.0B: `NOT_VERIFIED` by fresh grep, documented via CLAUDE.md only) | **Directly re-measured this session** — see Delta Matrix A5 `sidebar` row | `RECOMPOSE` if `D8` resolves toward the light theme (Option A); `KEEP_SCREEN_LOCAL` (as dark) if `D8` resolves Option B. **Not decided by this document** — component shape (rail width, icon-only + tinted-pill active state) is reusable either way, only the color token depends on `D8` |
| `StatCard`-equivalent (current: `AdminDashboard/components/StatCard`) | `pages/AdminDashboard/components/StatCard` | Tablet A5 landscape: 4-card grid, 3 neutral + 1 amber-callout variant | Not re-grepped this session | A5 `stat_cards` zone, this session | `REUSE_WITH_VARIANT` — needs a callout/amber variant added if not already present (`NOT_VERIFIED` whether current `StatCard` supports a tone prop) |
| Admin transaction/table row (no current equivalent confirmed) | — | Tablet A5 landscape: 5-column CSS Grid data table, sticky-style header, inline action-pill pair (승인/반려) on pending rows | Not confirmed to exist in current AdminDashboard as a distinct component (PointView per CLAUDE.md uses `.deductionCard` card-style list per the P-HOTFIX-ADMIN-VIEWS-002 history, not a grid table) | A5 `transaction_table` zone, this session | `RECOMPOSE` — this is very likely a genuinely new component (`AdminDataTable` or similar), since the current implementation's card-list pattern (per CLAUDE.md §13) is structurally different from the tablet's grid-table pattern. **Flagged, not designed here** — belongs to `MONGLE_W6_SCREEN_SPEC_FREEZE.md`'s A5 rebuild-zone list |
| `PhotoUpload` | `shared/components/PhotoUpload` | No direct tablet contract entry found (avatar/album photo slot contract exists but as a contract, not this specific upload-affordance component) | 2 per CLAUDE.md history (`NOT_VERIFIED` fresh this session) | Not encountered in the 4 zone-mapped tablet screens | `EXISTING_REUSE`, unchanged from 6.0B, `DEFER` fresh verification to whichever Wave 6.1 screen actually touches photo upload |

## Principles re-confirmed (Section 16 defaults, none overridden this session)

- No component was promoted to global/shared status on single-consumer evidence.
- No Doran-domain component was auto-promoted to platform-wide despite strong tablet-source structural
  matches — the promotion trigger (a second real *consumer in current React*, not merely a second design
  screen) has not yet occurred.
- No desktop Admin component was forced into a mobile/tablet-shared shape; A5's new table pattern is
  scoped `RECOMPOSE`, kept Admin-local pending its own design.
- Page components remain composition-only; no primitive in this table was found to own screen policy.

## Verdict for this Gate

**COMPONENT_BOUNDARIES_CLASSIFIED.** 2 items `SHARED_PRIMITIVE`/`EXISTING_REUSE` outright (`Avatar`,
`IconButton`), 1 ready-but-unadopted primitive flagged for first real use (`Button`), 2
`SCREEN_LOCAL_KEEP` (`Card`, `MainLogo`), 1 domain-local set held at `REUSE_WITH_VARIANT`/`DEFER_PROMOTION`
(Doran's 10 components), 1 `RECOMPOSE`/`PM_DECISION_REQUIRED`-adjacent item pending `D8`
(`AdminSidebar`), 1 likely-new component flagged (`AdminDataTable`), 1 `REUSE_WITH_VARIANT` needing a
tone-prop check (`StatCard`).

## Closeout Update (MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, PM 확정)

`D8` is now `PM_RESOLVED` (bright `#FBFAFE`, see Token Freeze closeout section). The `AdminSidebar`-
equivalent row's conditional (`RECOMPOSE` if `D8` resolves toward light, `KEEP_SCREEN_LOCAL` if dark) is
therefore settled: **`RECOMPOSE`** to the light-rail shape, with existing edit/delete/approve/reject
functionality explicitly preserved (per `D8`'s own PM decision text) — this is a visual recompose, not a
functional rewrite, and no component in this table is authorized to drop its current mutation logic as a
side effect.

Confirmed, unchanged by this closeout: **`Avatar`/`IconButton`** remain reusable `SHARED_PRIMITIVE`s;
**`Button`** remains the flagged first-real-consumer candidate for A3/A5 (0 current consumers, variants
already match the tablet contract); **no Doran-domain component is promoted to global/shared status** —
the tablet A4 room-list pane strengthens the case for revisiting `RoomItem`'s domain-local status but the
actual promotion trigger (a second real consumer in current React) still doesn't exist until Wave 6.1 A4
is built; a **responsive layout wrapper is allowed** as new composition (not a new primitive) per Section
16's "no primitive owns screen policy" principle; **no mobile/tablet functional tree duplication** is
authorized — this matches the Delta Matrix's own "zero DOM-duplication-required" finding, reconfirmed in
the Responsive Freeze closeout section above.
