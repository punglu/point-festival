# Measurement Table V2

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 10). Full data: `measurement_table_v2.csv` (84 rows, categories A-G).

Every row is tagged with a `source_class`: `CSS_LITERAL` (read directly from a `style="..."` attribute
in `standalone-src.html`), `COMPUTED_STYLE` (from the Playwright render's `getComputedStyle`),
`PNG_MEASURED` (Pillow `Image.size` on the approved PNG), `INFERRED` (no explicit value exists; derived
from surrounding values, always noted as such), `NOT_VERIFIED` (could not be determined at all), or
`SOURCE_MISSING`. No `INFERRED` value is presented anywhere in this package as if it were a confirmed
token — every consuming document (token candidates, PM decision brief) repeats the `INFERRED`/`NOT_VERIFIED`
flag rather than dropping it.

## A. Layout

The single biggest layout finding is the **480px mobile mockup canvas vs. real device resolution
mismatch** already detailed in `TIER1_HTML_VISUAL_DELTA.md` — repeated here as a measurement fact: the
rendered HTML's own bounding boxes (`COMPUTED_STYLE`, e.g. A1 = 480×920px, A5 = 1440×1030px) do not
match the intrinsic pixel size of their corresponding approved PNGs (`PNG_MEASURED`, e.g. A1's PNG =
853×1844px, aspect delta 12.79%), except for A5 where the desktop canvas (1440×1030, aspect 1.398) and
the approved PNG (1448×1086, aspect 1.333) are close (4.85% delta) — A5 is the *only* screen where the
HTML canvas dimensions can be trusted as a literal layout measurement without a large aspect correction.
Grid column layouts (`BottomDock`, `ServiceGrid`, `WeekDateStrip`, `StatCardRow`,
`DeductionDataTable` header) are all fixed-column CSS Grid with no responsive column-count change (no
media queries exist at all — see `HTML_STRUCTURE_EXTRACTION.md`).

## B. Spacing

Padding and gap values are **not** a clean multiple-of-4/8 scale. The most common gap value by far is
`3px` (97 occurrences, mostly icon-to-label spacing inside the BottomDock and status-bar mock), followed
by `7px` (33), `2px` (32), `4px`/`10px` (30 each), `12px` (26), `6px` (24) — i.e. a large fraction of
real spacing values are odd numbers (3/5/7/9/11px) that do not map cleanly onto the current
implementation's 4px-based `--space-1..12` scale (see `APPROVED_TOKEN_CANDIDATES.md`, category
`spacing-gap`/`spacing-padding`, classified mostly `REPEATED_LITERAL` with an explicit `TOKEN_CONFLICT`
note against the current scale).

## C. Typography

Font family is **Noto Sans KR** (loaded from Google Fonts CDN) throughout the entire approved source —
this is a hard, confirmed mismatch against the current implementation's `'Pretendard'` /
`'Black Han Sans'` / `'Inter'` stack in `global.css` (`REQUIRES_PM_DECISION` in the token candidates,
not a simple alias). Font sizes span 26 distinct literal values from 9px to 37px, with 11px/13px/12px/
10px/14px as the 5 most common (54-73 occurrences each) — i.e. the approved design's actual type scale
is much finer-grained than a typical 6-8-step design-token scale, and no named scale (Display/Page/
Section/etc.) is encoded in the source itself; any such naming is a Phase-B-side interpretation only
(see the note under `global.css` line 51-57 in `TOKEN_IMPLEMENTATION_AUDIT_V2.md`), not something this
Phase A measurement can confirm as present in the design source.

## D. Surface

Border-radius is dominated by `50%` (108 occurrences, circular avatars/icons) and `999px` (50, pills) —
both already exist as exact-match tokens in the current implementation (`--radius-pill: 999px`). Three
near-identical "white" surface colors are used across the source (`#fff`/`#FFF` 107×, `#FBFAFE` 12×,
`#FDFDFF` 14× — the latter reserved for `BottomDock` backgrounds specifically), suggesting an
intentional (if subtle) surface-elevation distinction rather than a single flat white — flagged as a
`SEMANTIC_CANDIDATE` requiring PM confirmation rather than collapsed into one value. The chat bubble
colors (`#6944EF` own / `#F3F0FF` other) are an **exact, already-implemented match** against the current
`--color-chat-own` / `--color-chat-other` tokens — the one unambiguous full win in this whole
measurement pass.

## E. Controls

Avatar sizing is **not standardized** across screens (52px/70px/66px/78px/38px/30px/42px/36px/64px
depending on screen and context) — this is recorded as a fact, not smoothed into a single "avatar size"
token. The only control with an explicit `44px` touch target is A4's Composer send button, which matches
the current implementation's `--size-touch-min: 44px` exactly. No screen shows an explicit `disabled`-
state visual treatment (the "locked" player card on A1 is a distinct color/badge composition, not a
generic disabled style) — `SOURCE_MISSING` for a reusable disabled-state pattern.

## F. Messaging

Bubble corner radii are directional (`6px 18px 18px 18px` incoming vs `18px 6px 18px 18px` outgoing —
mirror-image "tail" corner reduction), `7px` avatar-to-bubble gap, no explicit `max-width` rule found on
any bubble (`NOT_VERIFIED` what the real wrap width should be), and no keyboard-safe-area behavior is
observable in a static mockup (`NOT_VERIFIED`, explicitly, rather than assumed absent).

## G. Admin

A5's sidebar (300px fixed), stat cards (3-column grid, 20px padding, 18px radius), and the 6-column data
table (`1.1fr 2fr 1fr 1fr 1fr .9fr`) are all directly measurable `CSS_LITERAL` values with no ambiguity.
No dialog/modal image exists anywhere in the approved source for the edit/delete actions visible in the
table (`SOURCE_MISSING`) — row height is `INFERRED` (~68-72px) from padding + avatar size, not an
explicit value.
