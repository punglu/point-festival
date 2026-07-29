# Tier-1 HTML vs Approved-PNG Visual Delta

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 12)

## Method

1. Rendered `standalone-src.html` live in a browser using the **existing** Playwright install at
   `minecraft_points_festivals_doran_ui/tests/e2e/node_modules/playwright` (no new dependency installed), served over a local
   `python3 -m http.server` on the approved-source folder (read-only, nothing under `screen_renew/` was written to).
   Script: `/tmp/mongle-wave6-0ab/scripts/render.js`.
2. Captured a full-canvas screenshot plus one cropped screenshot per screen ID, and the computed
   bounding box / `border-radius` / `background` / `box-shadow` of each screen's `[data-screen-label]`
   root, via `page.evaluate(getComputedStyle(...))`. Zero console errors, zero page errors on render
   (`/tmp/mongle-wave6-0ab/evidence/approved-html-render/console_errors.json` = `[]`).
3. For the 5 screens with a dedicated approved PNG (A1, A2, A3, A4, A5), resized the rendered crop to
   the PNG's pixel dimensions and computed a pixel-difference histogram with Pillow (`ImageChops.difference`,
   stdlib-only, no new dependency) — script `/tmp/mongle-wave6-0ab/scripts/visual_diff.py`, raw output
   `/tmp/mongle-wave6-0ab/evidence/approved-html-render/visual_diff_results.json`.
4. Independently re-opened each of the 5 approved PNGs visually (not relying solely on the pixel-diff
   number) to identify *what* differs, because the resize-based diff is confounded by an aspect-ratio
   mismatch (see below) and cannot by itself distinguish "structural crop difference" from "real content
   difference."
5. Cross-checked qualitative findings against the prior session's own independent visual walkthrough at
   `_analysis/wave6_1a-source/TIER1_VISUAL_DELTA.md` (classified `DERIVED_REFERENCE`, not trusted blindly —
   every claim reused below was independently re-confirmed by directly viewing the relevant PNG in this
   session; see the "independently re-verified" column).

## Confound: aspect-ratio mismatch (affects all 5 comparisons)

The HTML mockup renders every mobile screen inside a fixed **480px-wide** canvas frame with heights
determined purely by content (806–1005px, aspect ≈ 0.48–0.60). The approved PNGs are captured at real
device resolution and are noticeably taller/narrower per pixel: 853×1844 (A1, aspect 0.463), 941×1672
(A2/A3/A4, aspect 0.563), 1448×1086 (A5, aspect 1.333 vs. the HTML's 1440×1030 = 1.398 — the *only*
screen where HTML and PNG canvas aspect are close). Resizing the render to the PNG's pixel size to
diff it therefore **stretches** the render vertically for every mobile screen, which inflates the raw
pixel-diff percentage independent of any real content difference. This is recorded as its own
`SOURCE_CONFLICT` (see SOURCE_AUTHORITY_MATRIX.md) rather than folded silently into the per-screen
verdicts below.

## Per-screen classification

| Screen | Rendered size | Approved PNG size | Aspect delta | Raw pixel-diff % | Aspect-confound-adjusted classification | Independently re-verified content delta |
|---|---|---|---|---|---|---|
| A1 (1a) | 480×920 | 853×1844 | 12.79% | 10.61% | `MINOR_RENDERING_NOISE` (structure/spacing/color match closely once aspect is discounted — see full-size crops, both use initials-circle avatars, no photos) | None found — this is the cleanest match of the 5, consistent with prior-session finding |
| A2 (1b) | 480×806 | 941×1672 | 5.82% | 8.26% | `MATERIAL_VISUAL_DELTA` | **(a)** Greeting avatar: HTML = initials-in-gradient-circle; PNG = **real photograph headshot**. **(b)** Hero illustration: HTML reuses the pin-logo mascot (`family_platform_pin_logo_transparent_1024.png`) as a bottom-right watermark; PNG shows a **different, 3-character "blob mascot family" illustration** (1 large + 2 small rounded characters with faces, plus a speech bubble) that has **no corresponding standalone asset file anywhere in `uploads/`** — `SOURCE_MISSING` for this asset. **(c)** The 3 "준비중" service tiles and the active tile use **real flat icon illustrations** in the PNG (calendar+heart, photo-frame, clipboard-check, purple droplet mascot) vs. **emoji** (🗓️🖼️📋) in the HTML for the 3 inactive tiles — none of these icon assets exist as standalone files either (`SOURCE_MISSING`). **(d)** Bottom-dock icon glyphs differ in style between HTML (generic line-icon SVG paths) and PNG (rounder, slightly different iconography, purple house glyph for the active Home tab). |
| A3 (1c) | 480×1005 | 941×1672 | 15.14% | 7.01% | `MATERIAL_VISUAL_DELTA` (driven mostly by the confound + one real delta) | Structure, spacing, avatar-initials, cheer-message layout **match** closely. The **one real delta**: mission-row icons are **real flat illustrations** in the PNG (broom, open book, two-people/friendship, credit-card) vs. **emoji** (🧹📖👥💳) in the HTML — same `SOURCE_MISSING` pattern as A2. |
| A4 (1d) | 480×935 | 941×1672 | 8.78% | 6.40% | `MINOR_RENDERING_NOISE` (structure/message-rhythm/avatar-colors/composer all match) | Photo-attachment thumbnails: HTML uses an honest striped-texture placeholder + "사진 1/2/3" label; PNG shows what look like real travel photos. Per source-authority rules this is not a pixel-for-pixel asset to copy — treated as `PNG_ONLY_DETAIL`, deferred (no real photo pipeline is in scope for this Wave). One structural note independently confirmed: **both** HTML and PNG place a small pin-logo-adjacent icon in the chat header's top-right — this is *not* an HTML-only invention, but see `PM_DECISION_REQUIRED` below, since the broader Asset Registry text (referenced in a separate, already-existing `FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md`, outside this task's approved-source folder) reportedly restricts the pin-logo's placement — flagged, not resolved, here. |
| A5 (1e) | 1440×1030 | 1448×1086 | 4.85% | 3.17% | `EXACT_OR_NEAR_MATCH`-adjacent → `MINOR_RENDERING_NOISE` | **Best agreement of the 5** (lowest aspect delta, lowest pixel-diff). Sidebar, header, filter tabs, 3 stat cards, and the 6-row data table all match zone-for-zone and color-for-color on direct visual comparison of both images. No material content delta identified. |

Diff images and crops: `/tmp/mongle-wave6-0ab/evidence/approved-html-render/diff_*.png`,
`screen_*.png`, `full_canvas.png`. Raw numbers: `visual_diff_results.json`, `zone_bounding_boxes.json`.

## Screens with no dedicated approved PNG (not comparable)

A1-S1 (순수 로그인), EXTRA-01 (나 프로필), EXTRA-02 (가족 일정), EXTRA-03 (앨범), EXTRA-04 (할 일):
classified `NOT_COMPARABLE` — `SOURCE_MISSING`, no approved PNG exists for these screen IDs. HTML
structure alone was captured (renders and bounding boxes exist for all of them in
`zone_bounding_boxes.json` / `screen_1a_1.png`, `screen_1f.png`..`screen_1i.png`), but there is no
independent visual-truth source to compare it against — recorded as a gap, not silently treated as
"HTML = approved."

## Recurring pattern across A2/A3 (and likely A4's header icon)

The dominant, repeating real (non-confound) delta across every mobile content screen is: **the HTML
mockup substitutes emoji or the reused pin-logo mascot wherever the approved PNG actually specifies a
distinct, purpose-made flat icon or illustration asset that does not exist as a standalone file in this
approved-source folder.** This is recorded once here and referenced from `ASSET_MANIFEST.md`,
`APPROVED_TOKEN_CANDIDATES.md`, and the PM Decision Brief, rather than repeated as unrelated one-off
findings — it is the single most consequential Phase A finding for implementation planning, because it
means the HTML's structure/CSS-literal extraction is safe to use directly, but its icon/illustration
choices are **not** approved-equivalent and several required source assets are simply missing from this
folder (`SOURCE_MISSING`, `PM_DECISION_REQUIRED`: source or commission these assets before any Wave 6.1
icon work).
