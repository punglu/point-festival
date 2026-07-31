# MONGLE_W6_1_FONT_DELIVERY_CONTRACT

Task: MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001, Gate B (§10). Determines an approvable Noto Sans KR
delivery mechanism, or Hard Stops before product implementation.

## 1. Exhaustive search performed (this session)

| Location searched | Result |
|---|---|
| `find . -iname "*.woff*" -o -iname "*.ttf" -o -iname "*.otf"` (repo-wide, excluding `node_modules`/`.git`) | **0 hits.** No font files exist anywhere in the repo. |
| `frontend/public/**` | Only icon/manifest assets (`favicon-*.png`, `apple-touch-icon.png`, `logo*.png`, `manifest.json`, `og-image.png`). No fonts. |
| `frontend/src/assets/**` | Not present as a distinct dir; no font assets found in `src/**`. |
| `grep -rn "@font-face\|fonts.googleapis\|fonts.gstatic\|@import" frontend/src` | **1 hit**: `frontend/src/styles/global.css:3` — a **live, already-shipping** `@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&family=Black+Han+Sans&family=Inter:wght@300;500;700&display=swap')`. This delivers Pretendard/Black Han Sans/Inter today — **not** Noto Sans KR. |
| `frontend/package.json` dependencies/devDependencies | No font package (`@fontsource/*`, `typeface-*`, etc.) present. |
| `node_modules` (top-level and `.pnpm/`) | No font package installed. |
| `frontend/index.html` | No `<link>` font tag of any kind (only favicon/manifest/OG tags). |
| `grep -rIn "Noto Sans"` across the whole repo (non-`node_modules`) | Hits only in: (a) two CSS Module fallback stacks — `UserDashboard.module.css:40`, `Auth.module.css:29` — `--user-font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', sans-serif;` (Noto Sans KR listed as a **fallback name only**, never actually delivered — no `@font-face`/`@import`/package backs it, so it only renders if a visitor's OS happens to ship a font with that exact family name, which is not a standard OS default); (b) the permanently-archived tablet-canonical design evidence (below). |
| `docker`/CI files | No font-related build steps; out of scope to touch anyway (absolute constraint). |

## 2. Approved-design-source evidence (the decisive finding)

The permanently archived, PM-approved tablet-canonical evidence
(`engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/*.html` and
`.../assets/design-system/APPROVED_VISUAL_STYLE_GUIDE.html`) **explicitly embeds** a real, working font
delivery mechanism for Noto Sans KR, verbatim in all four archived HTML files:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
```

This is not something I sourced or invented — it is baked into the canonical, frozen, already-approved
design evidence archive (`MONGLE_W6_0C_PM_DECISION_CLOSEOUT.md` §12 confirms this archive is
SHA-verified, byte-identical to its originals, and immutable/do-not-edit for this task). The exact CDN
origin (`fonts.googleapis.com` / `fonts.gstatic.com`), the exact family name (`Noto+Sans+KR`), and the
exact API shape (`css2?family=...&display=swap`) are all explicitly named in current canonical evidence.

## 3. Discrepancy found vs. `MONGLE_W6_DESIGN_TOKEN_FREEZE.md`

That freeze document's closeout section states: *"no font-file/CDN dependency found in this repo — only a
static-HTML-embedded Google Fonts `<link>` in the design sources."* This underclaims what's actually
available: the design sources' embedded `<link>` **is** a concrete, workable, already-approved CDN
delivery mechanism (§2 above) — not merely a design reference. This document corrects that
characterization rather than silently repeating it. It does **not** contradict the freeze's bottom line
(`FONT_DELIVERY_REQUIRED`, unresolved at closeout time) — it resolves that exact open flag, as the freeze
itself said Wave 6.1's Start Gate should.

Separately: `frontend/src/styles/global.css` **already** carries a live, shipping Google Fonts `@import`
for three other families (Pretendard/Black Han Sans/Inter). This is pre-existing product code, not
something this task added — flagged here as context (the product has already accepted this exact class of
external CDN dependency for typography before), but not used as the sole justification; §2's archived,
approved-source evidence is the actual basis for this decision.

## 4. Classification

**EXISTING_APPROVED_EXTERNAL_DELIVERY** (category C in §10's approvable-paths list): the exact CDN
origin + family + API shape is explicitly named in current, permanently-archived canonical design
evidence that the PM has already signed off on (`MONGLE_W6_0C_PM_DECISION_CLOSEOUT.md`).

Explicitly **not** any of: `SYSTEM_ONLY` (a real network delivery is being added, not a system-font
assumption), `DESIGN_REFERENCE_ONLY` (the mechanism is concretely usable, not merely descriptive),
`LICENSE_UNKNOWN` (Google Fonts' Noto Sans KR is distributed under the SIL Open Font License, a
well-documented, unambiguous open license — same license family already implicitly accepted for the
product's existing Pretendard/Inter Google Fonts usage), or `NOT_FOUND`.

## 5. Implementation decision (weight subset)

The archived source requests weights `400;500;700;900`. This task's actual typography need (per
`MONGLE_W6_DESIGN_TOKEN_FREEZE.md`'s typography-scale comment: Display/Page/Section/Card headings = 700,
Body = 400, Body Strong = 600, Meta/Label = 700) does not include 500 or 900. Per §16's explicit
prohibition on "unused full weight bundles," this task requests only **400;600;700** — a documented,
minimal subset of the same already-approved family/origin, not a wider or different delivery mechanism.
This is disclosed as a judgment call: the exact archived URL uses `400;500;700;900`; this implementation
uses `400;600;700` (fewer weights, same origin/family/API), chosen to match actual current typography-scale
consumption and avoid shipping unused weight bundles.

## 6. Forbidden actions checked — none taken

- No new/unrelated CDN host was introduced (same `fonts.googleapis.com`/`fonts.gstatic.com` already named
  in canonical evidence and already used elsewhere in this file for other families).
- No font files were downloaded or copied into the repo.
- No font package dependency was added (`package.json` untouched, no lockfile change).
- No unknown-provenance font was used.
- Completion is **not** declared based on system-font presence alone — §16/§22 require verifying the CDN
  resource actually resolves (200, correct content-type) and that computed `font-family` reflects Noto
  Sans KR, not merely that a fallback silently rendered. See Baseline/Post-Implementation Validation for
  the actual resolution check (`curl` confirmed `200` from the exact CDN URL this session, see Foundation
  Report §"Font Load").

## Verdict for this Gate

**FONT_DELIVERY_CONFIRMED — EXISTING_APPROVED_EXTERNAL_DELIVERY.** No Hard Stop (#9/#10/#11) fires.
Noto Sans KR will be delivered via `@font-face`-equivalent `@import` of the same CDN origin/family already
embedded in the approved, archived tablet-canonical design evidence, requesting only the weights (400/600/700)
this Foundation's typography scale actually consumes.
