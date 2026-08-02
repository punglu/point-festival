# MONGLE_W6_A2_FAMILY_HOME_MEASUREMENT

Task: `MONGLE-W6-PARALLEL-A2-FAMILY-HOME-MOBILE-VISUAL-001`
Parallel model: `SAME_WORKTREE_PATH_OWNERSHIP` (external worktree exception `DENIED`)

This document records what was **measured**, what was **inferred**, and what
remains **unresolved**. Every number below is either a literal read out of a
canonical source file or a pixel measurement of the approved PNG; derived
values are labelled `INFERRED` at the point of use.

---

## 1. Metadata

| Field | Value |
|---|---|
| Screen ID | `A2` |
| HTML anchor | `1b` |
| Screen label (task) | 가족 플랫폼 홈 |
| Screen label (canonical HTML badge) | 가족 홈 |
| Screen label (`data-screen-label`) | 홈 |
| Form factor | Mobile |
| Target component | `FamilyHomePreview` |
| Worktree | `/Users/mac/mac_Project/mongle_ui` |
| Branch | `dev-newmarkp` |
| HEAD at measurement | `3294c902a88a846d75e0896741784f75aa827fbe` |

### Canonical sources, hashed at this HEAD

| Role | Path | SHA-256 |
|---|---|---|
| Approved PNG (Tier 1M) | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/screen_family_home_approved.png` | `d486d0eb921b1cf5ed4085fe9d23bc5d4597399c5415406af5674c5c4070e9f2` |
| Canonical HTML — render source | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현.dc.html` | `d0c4222790eb20a8b6e391f56bdc9d1751d719801577a182406788f2d2a30fb9` |
| Canonical HTML — tokenized twin | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/가족 플랫폼 화면 재현-tokenized.html` | `1d11874d0bceb227b5cecd81bdb8954fd3d620818292f9b608300aa925da5327` |
| Style guide (Tier 2) | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/design-system/APPROVED_VISUAL_STYLE_GUIDE.html` | `50a6d5732ebdc27ddc5ce9e81d4b97cec8b74a74e13df1940b42ea99503ce41c` |
| Hero / tile asset | `engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/family_platform_pin_logo_transparent_1024.png` | `dd5c48b3e670636b7822a5893e213ce8e99fd667b82b4cb53026e344bea4f0b8` |

Both HTML files were diffed across the whole `1b` block. They are
**structurally identical**; the only differences are `var(--token)` versus the
literal value. The `.dc.html` twin is used as the render source because it is
the file the passed `1c` capture harness already uses, keeping A2's canonical
evidence directly comparable to A1/1c.

Anchor `1b` is at line `210` (`.dc.html`) / `212` (tokenized).
`data-screen-label="홈"` occurs **exactly once** in the source — no ambiguity.

---

## 2. Approved PNG — measured bounds

```text
Full PNG dimensions      : 941 × 1672
Colour mode              : RGB
File size                : 1,281,570 B
Flat border rows/cols    : 0 on all four edges
Outer device frame       : NOT PRESENT
Gallery label / badge    : NOT PRESENT
Presentation background  : NOT PRESENT
CONTENT_BOUNDS           : (0, 0, 941, 1672) — full frame
Crop required            : NO
```

The four corner pixels are already canvas background
(`≈ #F3F1FA … #FDFCFD`), and a flat-run scan from each edge returned `0`, so the
approved PNG is a full-bleed app render, not a gallery mock-up. **No crop is
performed**; no resize, stretch, or warp is performed anywhere in this task.

The canvas carries a faint vertical brightness gradient (row 0 `≈ (246,244,252)`
→ row 1671 `≈ (253,252,253)`) that the canonical HTML flattens to a single
`#F7F6FC`. Recorded as a non-blocking raster observation, not a layout finding.

### Mock-chrome classification

| Element | Classification | Handling |
|---|---|---|
| `9:41` clock | `DEVICE_CHROME` | Excluded from comparison |
| Signal bars | `DEVICE_CHROME` | Excluded |
| Wi-Fi glyph | `DEVICE_CHROME` | Excluded |
| Battery glyph | `DEVICE_CHROME` | Excluded |
| Home indicator bar | `DEVICE_CHROME` | Excluded |
| `1b` / 가족 홈 badge row | `GALLERY_DECORATION` | Excluded |
| Card `border-radius:44px` + drop shadow | `GALLERY_DECORATION` | Neutralised in canonical render |
| Everything between the status bar and the dock | `APP_CONTENT` | Implemented |
| Bottom dock | `APP_CONTENT` | Implemented |

This matches the exclusion set the passed `1c` harness already applies
(`screen.firstElementChild` = status bar, `screen.lastElementChild` = home
indicator, both removed; radius and shadow forced to `0`/`none`).

---

## 3. Responsive / viewport authority — `RESPONSIVE_VIEWPORT_AUTHORITY_UNRESOLVED`

The approved PNG's aspect ratio does **not** match any named mobile viewport:

```text
approved PNG   941 × 1672  ratio 1 : 1.777
375 × 812                  ratio 1 : 2.165
390 × 844                  ratio 1 : 2.164
430 × 932                  ratio 1 : 2.167
```

Three independent landmark pairs were measured to test whether the approved PNG
is the canonical HTML rendered at one scale factor. **It is not:**

| Landmark | Canonical HTML (480 canvas) | Approved PNG | Implied scale |
|---|---|---|---|
| Page content width | 444 px | 858 px | **1.932** |
| Page side padding | 18 px | 41 px | **2.28** |
| Hero minimum height | 196 px | 466 px | **2.38** |
| Home indicator width | 132 px | 292 px | **2.21** |

A single-scale reproduction would return one constant. It returns four
different values spanning 1.93–2.38.

```text
FINDING: the approved PNG is an independent design render, not a
         scaled screenshot of the canonical HTML.
```

> **RETRACTED (PM correction, 2026-08-02).** An earlier revision of this document
> concluded from the above that "the approved PNG is authority for structure …
> exact px authority is the canonical HTML literal." **That inverted the
> authority order and is withdrawn.** Non-uniform landmark ratios prove only
> that the PNG is not a uniform-scale capture of the HTML; they do not promote
> the HTML to pixel authority. The binding order is:
>
> ```text
> approved PNG    = visual-final authority
> tokenized HTML  = structure / content / CSS reference only
> current React   = comparison material only
> ```
>
> Consequently the previously reported "0.00 px parity across every zone" was
> parity **with the HTML target only**. It is not evidence of canonical visual
> parity and must not be quoted as such.

This is consistent with `MONGLE_W6_CANONICAL_SOURCE_FREEZE.md`, which records
that the Tier 3 pixel-level mobile source (`standalone-src.html`) is **not
present in this environment** and that the surviving HTML is
`EXTENDED_MOBILE_STRUCTURE_SOURCE` — "structure/content reference only, never a
Tier 3 pixel-level substitute".

```text
TIER_3_MOBILE_PIXEL_HTML : NOT_AVAILABLE
PRIMARY_COMPARISON_BASE  : approved PNG, native content bounds, crop only
                           (see §15.6) — the fidelity gate
SECONDARY_BASE           : canonical HTML rendered at 375/390/430 — responsive
                           regression only, never quoted as fidelity
APPROVED_PNG_ROLE        : VISUAL_FINAL_AUTHORITY
```

The approved PNG's own CSS viewport is no longer unknown — see §15.1, which
resolves it to a 2× export of a ~470×836 canvas and closes `D-A2-5`.

### Viewport set actually used

`375×812`, `390×844`, `430×932` are retained, on recorded grounds rather than
by assumption:

- `MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md` item 1 — mobile reference
  viewport **390×844**, `PM_BACKED` via `D1`.
- A1 and 1c both shipped and passed on exactly this three-viewport set
  (`engineering/phase2/evidence/MONGLE-W6-R2-1C-VISUAL/final/**`).

The 480 px canvas is **not** treated as a breakpoint — the same freeze
explicitly forbids promoting a design-artifact canvas to a CSS breakpoint.

---

## 4. Zone map

Confirmed present in **both** the approved PNG and canonical HTML `1b`, in this
order:

| # | Zone | `data-visual-zone` | Notes |
|---|---|---|---|
| — | OS status bar | — | `DEVICE_CHROME`, excluded |
| 1 | Family identity / profile row | `profile` | Avatar + greeting + notification bell |
| 2 | Hero — 가족 대화 | `hero` | Gradient card, CTA, mascot, typing bubble |
| 3 | Recent-activity card | `activity` | Title + 더보기 + 3 rows |
| 4 | Service navigation tiles | `services` | Title + 4-column grid |
| 5 | Bottom navigation dock | `dock` | 4 items, 홈 active |
| — | Home indicator | — | `DEVICE_CHROME`, excluded |

Zones **not** present in the canonical authority and therefore **not**
implemented: top app header / app bar, search, banner carousel, points-balance
summary card, family-member strip, floating action button.

---

## 5. Geometry — canonical HTML literals

Read directly out of the `1b` block. These are the implemented values.

### Root

```text
screen container : display:flex; flex-direction:column
                   background #F7F6FC   (--color-canvas)
                   width/height forced to 100vw / 100dvh at capture
                   border-radius 44px and box-shadow neutralised (gallery-only)
content wrapper  : flex:1 0 auto; display:flex; flex-direction:column
                   gap 10px; padding 10px 18px 12px
```

### Zone 1 — profile row

```text
row              : display:flex; align-items:center; gap:10px
avatar wrapper   : position:relative; width:52px; height:52px; flex:none
avatar           : 52×52; border-radius:50%; border:2px solid #fff
                   background linear-gradient(160deg,#DAD3EE,#B9AEDD)
                   box-shadow 0 3px 10px rgba(60,30,120,.14)
presence dot     : 13×13; border-radius:50%; background #22C55E
                   border:2.5px solid #fff; right:0; bottom:0
copy column      : flex:1; display:flex; flex-direction:column; gap:2px
bell             : 28×28; position:relative
bell badge       : 9×9; border-radius:50%; background #5A35DF
                   border:2px solid #F7F6FC; right:0; top:1px
```

### Zone 2 — hero

```text
card             : border-radius:28px; padding:15px 20px; min-height:196px
                   background linear-gradient(135deg,#D9CBF8 0%,#C3AAF3 55%,#B79AF0 100%)
                   position:relative; overflow:hidden; display:flex
copy column      : display:flex; flex-direction:column; gap:8px; z-index:1
CTA pill         : background #5A35DF; padding:9px 22px; border-radius:999px
                   margin-top:4px; align-self:flex-start; gap:7px
                   box-shadow 0 8px 18px rgba(70,35,180,.30)
mascot           : 210×210; object-fit:contain; opacity:.95
                   position:absolute; right:-26px; bottom:-30px
typing bubble    : position:absolute; right:22px; top:26px
                   background #fff; border-radius:20px 20px 6px 20px
                   padding:7px 14px; gap:3px
                   box-shadow 0 6px 14px rgba(50,25,110,.16)
bubble dots      : 3 × 7×7 circles, #8A83A8
```

### Zone 3 — recent-activity card

```text
card             : background #fff; border-radius:26px; padding:12px
                   box-shadow 0 6px 18px rgba(60,30,120,.06)
                   display:flex; flex-direction:column; gap:8px
title row        : display:flex; align-items:center; justify-content:space-between
row              : display:flex; align-items:center; gap:10px
rows 1–2         : padding-bottom:8px; border-bottom:1px solid #F0EEF7
row 3            : no border, no padding-bottom
row icon         : 44×44; flex:none; border-radius:50%
                   row1 linear-gradient(160deg,#FFE9A8,#F7CD5C)
                   row2 linear-gradient(160deg,#8B63F3,#5A35DF)
                   row3 linear-gradient(160deg,#FF9DBB,#EF4665)
row copy         : flex:1; display:flex; flex-direction:column; gap:2px
```

### Zone 4 — service tiles

```text
section          : display:flex; flex-direction:column; gap:7px
grid             : display:grid; grid-template-columns:repeat(4,1fr); gap:7px
tile (all)       : border-radius:20px; padding:24px 8px 8px
                   display:flex; flex-direction:column; align-items:center; gap:4px
tile 1 (active)  : background #fff; border:2px solid #5A35DF
tiles 2–4        : background #fff; border:1px solid #EFECF8; position:relative
tile 1 icon      : <img> 52×52; object-fit:contain
tiles 2–4 icon   : 48×48 box; border-radius:14px; background #EDE7FB
badge (2–4)      : position:absolute; top:7px; right:7px
                   background #EEE8FF; color #7C5AEF
                   padding:2px 6px; border-radius:999px
```

### Zone 5 — bottom dock

```text
dock             : background #FDFDFF; border-top:1px solid #F0EEF7
                   padding:7px 20px 5px
                   display:grid; grid-template-columns:repeat(4,1fr)
item             : display:flex; flex-direction:column; align-items:center; gap:3px
icon             : svg 23×23; fill:none; stroke:currentColor; stroke-width:1.8
                   stroke-linecap:round; stroke-linejoin:round
active item      : color #5A35DF, label font-weight 700
inactive items   : color #A8A5B6
```

---

## 6. Typography

Family for every row: `"Noto Sans KR", system-ui, sans-serif`
(`--font-family-base`, `MONGLE_W6_1_FONT_DELIVERY_CONTRACT.md`).
No `letter-spacing` is declared anywhere in the canonical `1b` block.

| Text | Size | Weight | Colour | Notes |
|---|---|---|---|---|
| 안녕하세요, 서연님! | 17 | 900 | `#17103A` | `white-space:nowrap` — canonical |
| 우리 가족의 행복한 하루를 응원해요 💜 | 12 | 400 | `#8A83A8` | wraps freely |
| 서 (avatar initial) | 17 | 700 | `#fff` | |
| 가족 대화 | 28 | 900 | `#17103A` | |
| 지금 가족들과 / 이야기 나눠보세요 | 13 | 500 | `#3A3060` | `line-height:1.5`, explicit `<br>` |
| 바로가기 › | 14 | 700 | `#fff` | |
| 가족 최근 활동 | 16 | 700 | `#17103A` | |
| 더보기 › | 12 | 400 | `#8A83A8` | |
| 민준이가 “독서 미션”을 완료했어요! | 13 | 700 | `#17103A` | curly quotes U+201C/U+201D |
| +200P 획득 | 12 | 700 | `#5A35DF` | |
| 서연이가 Lv.3 모험가가 되었어요! | 13 | 700 | `#17103A` | |
| 레벨업 축하해요 🎉 | 12 | 400 | `#8A83A8` | |
| 아빠가 서연이에게 포인트를 선물했어요 | 13 | 700 | `#17103A` | |
| +500P | 12 | 700 | `#5A35DF` | |
| 12분 전 / 1시간 전 / 3시간 전 | 11 | 400 | `#A8A5B6` | |
| 우리 서비스 | 16 | 700 | `#17103A` | |
| 포인트 잔치 / 가족 일정 / 앨범 / 할 일 | 11 | 700 | `#17103A` | tile labels |
| 다양한 미션과 보상 … 함께 목표를 관리해요 | 9 | 400 | `#8A83A8` | tile sublabels |
| 준비중 | 9 | 700 | `#7C5AEF` | |
| 홈 (dock, active) | 10 | 700 | `#5A35DF` | |
| 포인트 잔치 / 대화 / 나 (dock) | 10 | 400 | `#A8A5B6` | |

**Truncation guard.** The canonical `1b` block declares
`text-overflow`, `line-clamp`, `-webkit-line-clamp`: **zero occurrences**.
`white-space:nowrap` appears **once**, on 안녕하세요, 서연님!. `overflow:hidden`
appears only on the gallery card wrapper and the hero (for the bleeding mascot).
The implementation reproduces exactly this set and adds none.

---

## 7. Text inventory (complete, verbatim)

```text
Zone 1  서
        안녕하세요, 서연님!
        우리 가족의 행복한 하루를 응원해요 💜
Zone 2  가족 대화
        지금 가족들과⏎이야기 나눠보세요
        바로가기 ›
Zone 3  가족 최근 활동
        더보기 ›
        민준이가 “독서 미션”을 완료했어요!   +200P 획득     12분 전
        서연이가 Lv.3 모험가가 되었어요!      레벨업 축하해요 🎉   1시간 전
        아빠가 서연이에게 포인트를 선물했어요   +500P        3시간 전
Zone 4  우리 서비스
        포인트 잔치   다양한 미션과 보상
        준비중  가족 일정   소중한 일정을 함께
        준비중  앨범       우리의 추억 모아보기
        준비중  할 일      함께 목표를 관리해요
Zone 5  홈   포인트 잔치   대화   나
```

Excluded as `DEVICE_CHROME`: `9:41`.
Excluded as `GALLERY_DECORATION`: `1b`, `가족 홈`.

No string was invented, and no string was copied from `1c` or any other screen.

---

## 8. Asset inventory

| Asset | Source | Dimensions | SHA-256 | Authority |
|---|---|---|---|---|
| Hero mascot **and** tile-1 icon | `frontend/src/assets/logos/family-platform-mascot.png` | 1024 × 1024 | `dd5c48b3e670636b7822a5893e213ce8e99fd667b82b4cb53026e344bea4f0b8` | `EXACT_REUSE` |
| Dock icons ×4 | inline SVG path data, canonical `1b` | 23 × 23 viewBox 24 | n/a — literal path strings | `EXACT_REUSE` |

The in-repo asset is **byte-identical** to the canonical
`family_platform_pin_logo_transparent_1024.png` (same SHA-256). The canonical
`1b` block references that one image for both the hero and tile 1 — verified by
extracting every `src=` in the block, which returns exactly one distinct value.
**No asset was created, converted, or regenerated.**

### `ASSET_AUTHORITY_UNRESOLVED`

The approved PNG shows richer artwork than the canonical HTML specifies. No
corresponding asset exists anywhere in the worktree, so none was invented:

| Element | Approved PNG shows | Canonical HTML specifies | State |
|---|---|---|---|
| Hero illustration | 3-character mascot scene + speech bubble | one 210×210 pin-logo image | `ASSET_AUTHORITY_UNRESOLVED` |
| Profile avatar | photographic portrait | gradient circle + initial 서 | `ASSET_AUTHORITY_UNRESOLVED` |
| Notification bell | line-art bell icon | `🔔` emoji glyph | `ASSET_AUTHORITY_UNRESOLVED` |
| Tiles 2–4 icons | illustrated 3D icons | `🗓️` `🖼️` `📋` emoji glyphs | `ASSET_AUTHORITY_UNRESOLVED` |
| Activity row icons | filled star / arrow / heart | `★` `↑` `♥` text glyphs | `ASSET_AUTHORITY_UNRESOLVED` |

The emoji in the implementation are **the canonical source's own glyphs**, not
an agent substitution for a missing icon. The prohibition on replacing icons
with emoji is not triggered by faithfully reproducing a source that itself
specifies emoji — but the gap between that source and the approved PNG is real
and is escalated above rather than closed by agent judgement.

---

## 9. Approved-PNG vs canonical-HTML deltas — `AUTHORITY_CONFLICT`

Measured, reproducible differences. Per
`MONGLE_W6_CANONICAL_SOURCE_FREEZE.md` conflict-resolution rules **9 and 10**
("unclear or conflicting items go to the PM Decision Gate, not to agent
judgement" / "source conflicts are never resolved by agent preference"), these
are **declared, not silently resolved**. The implementation follows the
canonical HTML, which is both the px authority and the pixel-diff base.

### D-A2-1 — services section card wrapper (`PM_DECISION_REQUIRED`)

The approved PNG places the 우리 서비스 title and tile grid on a **white card**.
The canonical HTML places them directly on the page background.

Evidence — same-row inside/outside probe. A card reads white-neutral
(`b−r ≈ 0`); bare canvas reads lavender (`b−r ≈ +3`):

```text
control, known gap      y=1150   x=20 (250,249,253) b-r +3 | x=45 (249,248,252) b-r +3
control, known gap      y= 660   x=20 (248,247,252) b-r +4 | x=45 (249,247,252) b-r +3
control, activity card  y=1100   x=20 (251,250,254) b-r +3 | x=45 (254,254,254) b-r  0
TEST,   services band   y=1400   x=20 (251,250,254) b-r +3 | x=45 (254,254,254) b-r  0
TEST,   services band   y=1470   x=20 (251,250,253) b-r +2 | x=45 (254,254,254) b-r  0
```

The services band carries the **same signature as the known card** and not the
signature of a known gap. Corroborating: the 우리 서비스 title sits `39 px` from
the card's left edge, and 가족 최근 활동 sits `41 px` from its card's left edge —
equal inset, as two sibling cards would give.

```text
services card bounds (PNG px) : x 41–899, y ≈1170–1495
```

Not implemented, because the PNG cannot supply the card's px contract and rule
10 forbids the agent inventing one.

### D-A2-2 — activity row inner containers (`PM_DECISION_REQUIRED`)

In the approved PNG the first activity icon is inset **75 px** from the card's
left edge while the card title is inset **41 px**. The canonical HTML makes the
icon a direct flex child, which would place both at the same inset. This is
consistent with per-row sub-containers in the PNG that the HTML does not encode.
Contrast is near the noise floor; recorded as measured, not asserted as final.

### D-A2-3 — canvas gradient (non-blocking)

Approved PNG background brightens `(246,244,252) → (253,252,253)` top to bottom;
canonical HTML uses flat `#F7F6FC`. Raster/finish difference, no layout impact.

### D-A2-4 — asset richness

See §8 `ASSET_AUTHORITY_UNRESOLVED` table.

---

## 9b. Defects found by the evidence harness, and fixed

Three implementation defects were found by measurement, not by inspection.
Their superseded evidence is retained under `revision-history/`.

### F1 — `box-sizing` (fixed)

The canonical source declares `box-sizing` **zero** times, so every literal in
it is authored against the browser default `content-box`. The app's
`reset.css` sets `border-box` globally. Reproducing the literals under
`border-box` silently changed their meaning: the hero's `min-height:196px`
rendered 226 px in canonical (196 content + 15+15 padding) but 196 px in the
implementation, pushing every zone below it up by exactly 30 px. Pixel diff
33.88 / 31.98 / 27.61 %. Fixed by scoping `content-box` to the preview subtree.

### F2 — text alignment (fixed)

`.tile { text-align: center }` was an implementation invention with no canonical
basis, and the `<button>` elements used for affordances carry the UA default
`text-align: center` that the canonical `<div>`-based source never had. Every
wrapped tile sublabel was recentred. Fixed by removing the invented rule and
adding `.page button { text-align: start }`.

### F3 — unreadable diff artefacts (fixed, harness)

Diff PNGs were produced by an RGBA `ImageChops.difference`, whose alpha channel
is 0 everywhere for two opaque inputs — every saved diff rendered fully
transparent and carried no information. Inherited from the 1c harness. Now
produced from RGB, with an 8× amplified companion. **The 1c evidence set has the
same defect and its diff PNGs should be regarded as non-informative.**

### Mis-attribution, corrected

`text-rendering: auto` was added on suspicion that `optimizeLegibility` (set by
`global.css`) was shifting glyphs. Direct measurement showed it changes nothing
for these fonts in Chromium. The rule is kept because it restores the canonical
value, but it is recorded as a corrected mis-attribution, not as a fix.

---

## 9c. D-A2-7 — residual sub-pixel space advance (`UNRESOLVED`, non-blocking)

After F1 and F2, the residual pixel difference is **3.221 / 3.075 / 2.567 %** at
375 / 390 / 430, and it is confined to one cause.

```text
Korean glyph run '포인트잔치'  11px/700 : 50.609 px canonical | 50.609 px implementation  IDENTICAL
U+0020 space      11px/700 :  2.500 px canonical |  3.094 px implementation  Δ 0.594 px (0.054em)
```

Every remaining ghost in the amplified diff is on a string containing a space;
every space-free string (앨범, 홈, 대화, 나) is pixel-identical. Text after a
space shifts sub-pixel, which antialiasing then spreads over the following
glyphs.

**Ruled out by direct measurement** — each tested and rejected as the cause:

```text
font stylesheet / delivery  RULED OUT — decisive: re-rendering the canonical
                            document under the app's own four-family Google
                            Fonts stylesheet produces images BYTE-IDENTICAL to
                            the primary canonical captures (all three
                            viewports; see manifest/font-env-probe/)
text-rendering              RULED OUT — auto / optimizeLegibility /
                            optimizeSpeed / geometricPrecision all give 3.094
font-kerning, font-synthesis, word-spacing, font-stretch,
-webkit-font-smoothing, lang, box-sizing, text-align   ALL RULED OUT
font-family, font-size, font-weight, line-height, letter-spacing
                            IDENTICAL computed values on both sides
font gate                   PASSES IDENTICALLY on both sides, including
                            document.fonts.check(700 11px Noto Sans KR, ' ')
substituting face           NOT IDENTIFIED — Inter 700 (2.609), Inter 500
                            (2.938), Black Han Sans (3.313) and system-ui
                            (2.906) were each measured and none is 3.094
```

```text
Status  : UNRESOLVED — mechanism not identified after nine isolation probes
Impact  : sub-pixel only. No reflow, no wrap change, no truncation, no
          overflow, no geometry change (worst-case zone delta 0.00 px)
Class   : NON_BLOCKING_RASTER
```

Escalated rather than worked around: the honest position is that the effect is
measured and bounded, and its mechanism is not yet known.

---

## 10. Current-code survey (read-only — nothing was modified)

| Item | Finding |
|---|---|
| `/dashboard` route | declared in `frontend/src/App.tsx`; **not touched** |
| `/__wave6/1b` | **not registered** — `App.tsx` is owned by the 1e lane this round |
| Existing `/__wave6` route | `App.tsx:80` → `/__wave6/1c` only |
| A1 pattern | `frontend/src/pages/A1AccountLogin/{index.tsx, *.module.css}` |
| 1c pattern | `frontend/src/pages/PointFestivalPreview/{index.tsx, *.module.css}` |
| Legacy A2 candidate | `frontend/src/pages/family-home/` — `components/ hooks/ services/ styles/ tests/ types/` |
| Duplicate A2 preview | none found |

`frontend/src/pages/family-home/` is a functional legacy screen with services,
hooks and types. It is **not** canonical, is **not** replaced, and was read only
for comparison. Its structure is a service-layer screen, not a
presentation-only canonical reproduction, so its contract differs from A2's →
`REBUILD_REQUIRED` rather than reuse.

**Responsive authority of current code: none.** No `@media`, `clamp()` or `vw`
appears in the passed 1c preview stylesheet; it is a single fluid layout using
the canonical px literals, with flex/grid absorbing the width difference between
the 480 px design canvas and the 375–430 device range. A2 follows the same
proven approach.

---

## 11. Responsive matrix

Measured from the live implementation at capture time via
`getBoundingClientRect()`; raw per-viewport payload, canonical and
implementation side by side, in
`engineering/phase2/evidence/MONGLE-W6-PARALLEL-A2-FAMILY-HOME-VISUAL-DRAFT-001/final/manifest/a2-visual-manifest.json`.

| Property | 375×812 | 390×844 | 430×932 |
|---|---|---|---|
| Root width | 375 | 390 | 430 |
| Horizontal padding | 18 | 18 | 18 |
| Content width | 339 | 354 | 394 |
| Hero y / height | 72 / 226 | 72 / 226 | 72 / 226 |
| Activity y / height | 308 / 235 | 308 / 222 | 308 / 222 |
| Activity row heights | 53 / 53 / 57 | 53 / 53 / 44 | 53 / 53 / 44 |
| Services y / height | 553 / 169 | 540 / 169 | 540 / 163 |
| Tile grid | 4 × 1fr, gap 7 | 4 × 1fr, gap 7 | 4 × 1fr, gap 7 |
| Tile column width | 79.50 | 83.25 | 93.25 |
| Tile height | 138 | 138 | 132 |
| Dock y / height | 758 / 54 | 790 / 54 | 878 / 54 |
| Horizontal overflow | 0 | 0 | 0 |
| Scroll (x, y) | 0, 0 | 0, 0 | 0, 0 |
| Scrollbar | none | none | none |

**Every value in this table is identical on the canonical side.** The measured
worst-case delta between canonical and implementation, across every zone,
every activity row, every tile, every dock item, in x / y / width / height, at
all three viewports, is **0.00 px**.

Two width-driven reflows are visible in the numbers and are properties of the
canonical design, not implementation defects — the canonical render reproduces
each of them at the same viewport, to the pixel:

- At 375, activity row 3 grows 44 → 57 because 아빠가 서연이에게 포인트를 선물했어요
  wraps to two lines; the services section therefore starts 13 px lower.
- At 430, tile height shrinks 138 → 132 because the tile sublabels stop wrapping.

No viewport-specific patch, `@media` rule, `clamp()` or `vw` unit exists in the
implementation; all three viewports are served by one fluid layout.

---

## 12. Guard results

```text
Font guard        : document.fonts.status = loaded; Noto Sans KR 400/500/700/900 = true
                    enforced for BOTH canonical and implementation, per viewport;
                    capture throws rather than emitting a fallback-font PNG
Scroll guard      : window.scrollTo(0,0); asserted scrollX = 0, scrollY = 0
Truncation guard  : no ellipsis / line-clamp / arbitrary max-width added;
                    canonical's single white-space:nowrap reproduced, nothing else
Vertical rhythm   : per-zone y/height/next-y captured for canonical and
                    implementation at all three viewports
Viewport patch    : zero viewport-specific patches; zero @media; zero clamp; zero vw
Evidence revision : current/ separated from revision-history/
Verdict guard     : this document declares no GPT Visual PASS
```

---

## 13. Unresolved register

```text
D-A2-1  services section card wrapper           PM_DECISION_REQUIRED
D-A2-2  activity row inner containers           PM_DECISION_REQUIRED
D-A2-3  canvas vertical gradient                NON_BLOCKING_RASTER
D-A2-4  hero / avatar / bell / tile / row icons ASSET_AUTHORITY_UNRESOLVED
D-A2-5  effective CSS viewport of approved PNG  RESPONSIVE_VIEWPORT_AUTHORITY_UNRESOLVED
D-A2-6  /__wave6/1b route registration          DEFERRED_TO_INTEGRATION_RELAY (App.tsx owned by 1e lane)
D-A2-7  U+0020 advance 2.500 vs 3.094 px        UNRESOLVED / NON_BLOCKING_RASTER (§9c)
D-A2-8  1c diff PNGs are non-informative        HARNESS_DEFECT_FOUND_IN_NEIGHBOURING_EVIDENCE (§9b F3)
```

## 14. Evidence location

```text
engineering/phase2/evidence/MONGLE-W6-PARALLEL-A2-FAMILY-HOME-VISUAL-DRAFT-001/
  capture-a2.mjs
  supplementary-font-environment-probe.mjs
  final/{canonical,implementation,side-by-side,diff,overlay,manifest,network,build-fingerprint}/
  revision-history/REV-FAIL-2026-08-02-boxsizing/
  revision-history/REV-FAIL-2026-08-02-textrendering/
  revision-history/REV-2026-08-02-textalign/
```

The PM brief named `engineering/phase2/evidence/mongle-w6-a2-family-home-draft/`.
The repository's existing evidence rule is an uppercase task-ID folder
(`MONGLE-W6-R1-A1-VISUAL`, `MONGLE-W6-R2-1C-VISUAL`, and the 1e lane's live
`MONGLE-W6-R3-1E-ADMIN-POINT-DESKTOP-VISUAL-001`), so the A2-specific path above
was selected inside that existing rule, as the brief directs, and is reported
here. No new top-level or parallel evidence scheme was created.

Status: `DRAFT_NOT_MAIN_WORKTREE_INTEGRATED`.

---

## 15. Approved-PNG authority correction (2026-08-02)

Applied after the PM ruled the approved PNG visual-final. Section 3's earlier
conclusion is retracted in place; this section records what changed.

### 15.1 D-A2-5 RESOLVED — the design scale

A least-squares fit of PNG-measured landmark heights against the
implementation's own CSS heights, **assuming no HTML value**, returns:

```text
fitted deviceScaleFactor = 1.9961  ->  2.0
design canvas            = 941/2 x 1672/2 = 470.5 x 836 CSS px
rms residual             = 9.44 px
alternatives tested      = 1.9604 -> 10.12 | 2.05 -> 10.17 | 2.2951 -> 23.20
```

The approved PNG is a **2× export of a ~470×836 CSS design canvas**. This is the
signature of a standard design-tool export and it reconciles the previously
"irreconcilable" landmarks. `RESPONSIVE_VIEWPORT_AUTHORITY_UNRESOLVED` is closed.

### 15.2 D-A2-1 IMPLEMENTED — 우리 서비스 card wrapper

Confirmed by a same-row inside/outside probe against two controls; the services
band carries the signature of a known card (`b−r ≈ 0` inside, `+3` outside) and
not of a known gap. Implemented: `background #fff`, `border-radius 26px`,
`padding 7px` (tile 1's border sits 16 PNG px inside the card edge), activity
card's shadow.

### 15.3 D-A2-2 REFUTED — no activity row containers

The earlier claim rested on the first row icon measuring an inset of 75 PNG px
against the title's 41. **Both numbers were wrong.** A loose-mask re-measurement
puts the row content at **x = 75**, exactly where the row divider starts, and a
statistical background test returns:

```text
row interior vs inter-row gap, text-free window : max delta 0.21
row interior vs card bottom padding             : max delta 0.11
known card vs page canvas (control)             : max delta 6.32
```

There is no inner container. The rows are direct flex children on the card's own
background, exactly as the canonical HTML specifies. The original observation
was an artefact of a colour mask too strict to catch the icon's pale gradient
edge. **Nothing is implemented for D-A2-2.**

### 15.4 Corrections applied under approved-PNG authority

| # | Element | Canonical HTML | Approved PNG | Applied |
|---|---|---|---|---|
| 1 | 우리 서비스 wrapper | none | white card | card added |
| 2 | Hero height | `min-height:196` → 226 total | 417 PNG px → 208.5 | `min-height:178` → 208 |
| 3 | Section gap | 10 | 34 / 41 PNG px → 17 / 20.5 | 17 |
| 4 | Profile avatar | 52 px, gradient + 서 | 92 PNG px photo → 46 | 46 px, PNG crop |
| 5 | Notification bell | `🔔` glyph | line-art icon | 24.5×26 PNG crop |
| 6 | Active dock icon | stroked | filled, interior (101,61,231) | `fill="currentColor"` |
| 7 | Active dock colour | — | (82,42,223) | specificity bug fixed |

Item 7 was a genuine defect: `.dockActive` (0,1,0) lost to `.dock button`
(0,1,1), leaving the active item grey — implementation (167,164,182) against the
PNG's (82,42,223). Found by sampling the rendered dock, not by reading the CSS.

### 15.5 Assets — D-A2-4

Repository re-searched. Only `family-platform-mascot.png` is a byte-exact
canonical asset (`dd5c48b3…`). Two assets were cropped from the approved PNG,
crop-only, and recorded in `final/manifest/a2-asset-crop-manifest.json` with
source SHA, crop box and result SHA:

```text
a2-profile-avatar.png     crop (52,102,92,92)   sha 921d4414…  shown at 46 CSS px
a2-notification-bell.png  crop (833,122,49,52)  sha f5443bcd…  shown at 24.5 CSS px
```

Declined, because they do not separate cleanly from their background — the rule
is crop-only, and no icon was invented, substituted or generated:

```text
hero mascot scene    sits on the hero's purple gradient; a crop would bake it in
service tile icons   three independent measurements of the tinted rounded box
                     disagreed (widths 177/120/121/114 px; vertical runs 8-25 px)
=> ASSET_AUTHORITY_UNRESOLVED, unchanged
```

### 15.6 Primary comparison result — approved PNG, native, crop only

```text
base   : screen_family_home_approved.png, app-content crop (0,83,941,1558)
render : CSS viewport 470x779 at deviceScaleFactor 2.0  -> 940x1558 raster
rule   : crop only. resize 0, stretch 0, warp 0.
```

| Zone | Delta (CSS px, implementation − approved PNG) |
|---|---|
| profile top | **0.0** |
| hero top | **+2.5** |
| hero height | **−0.5** |
| activity top | **−1.0** |
| activity height | **−1.5** |
| services top | −15.0 |
| services height | +18.5 |
| dock top | +11.0 |

Pixel diff **45.26 %** of the 940×1558 frame, by band:

```text
profile row      22.81% of band    1.76% of frame
hero card        85.47% of band   19.20% of frame   <- mascot asset
activity card    39.31% of band   11.10% of frame
services card    34.40% of band    8.39% of frame
dock             28.00% of band    4.82% of frame
hero mascot sub-region (x470-940, y150-460): 90.33% of that region
```

**The residual is explicitly NOT attributed to a single cause.** Enumerated,
still-open contributors:

```text
1  hero mascot artwork          ASSET_AUTHORITY_UNRESOLVED  (~9% of frame alone)
2  service tile icons           ASSET_AUTHORITY_UNRESOLVED
3  page canvas gradient + card shadow rendering — the PNG's canvas brightens
   246->253 top to bottom while the implementation is flat #F7F6FC; measured on a
   card-free strip, 16.9% of canvas-only pixels exceed the diff threshold on
   background alone, in every band, independent of content   (D-A2-3)
4  inactive dock icon tone      canonical (99,107,136) vs implementation
                                (168,165,182) — new, unresolved
5  services block position/height  −15 / +18.5 px, above measurement noise
6  U+0020 advance               D-A2-7, still unresolved
```

Per the PM's condition, D-A2-7 is **not** yet certifiable as the sole residual:
contributors 1–5 are still present.

### 15.7 Comparison contract

`final/COMPARISON-CONTRACT.md` is binding. The 375/390/430 canonical-HTML
figures (32.18 / 30.24 / 26.36 %) are a **responsive regression** check only.
They are expected to be large because the implementation now deliberately
departs from the canonical HTML wherever the approved PNG overrides it. Mixing
them with the primary figure is a category error.
