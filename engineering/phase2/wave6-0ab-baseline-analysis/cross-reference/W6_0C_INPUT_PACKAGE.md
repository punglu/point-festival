# Input Package for MONGLE-W6-0C-CANONICAL-FREEZE-001

Section 27. This document is a routing index into the rest of this package for whoever runs 6.0C next.
It does not confirm any PM decision itself.

## Authority per screen (who to trust for what)

For every screen, structure/CSS-literal questions → `standalone-src.html` (via `HTML_STRUCTURE_EXTRACTION.md`
/ `MEASUREMENT_TABLE_V2.md`); final visual hierarchy/impression questions → the matching approved PNG (via
`TIER1_HTML_VISUAL_DELTA.md`); current-implementation fact questions → Phase B documents only. See
`SOURCE_AUTHORITY_MATRIX.md` for the full per-file breakdown.

## Measurement completeness by screen

| Screen | Zone-level detail | Measurement detail | Token candidates | Visual delta | Confidence |
|---|---|---|---|---|---|
| A1/A1-S1 | Full | Full | Full | A1: PNG-compared; A1-S1: no PNG exists | HIGH(A1) / MEDIUM(A1-S1) |
| A2 | Full | Full | Full | PNG-compared, MATERIAL delta found | HIGH |
| A3 | Full | Full | Full | PNG-compared, mostly low delta | HIGH |
| A4 | Full | Full | Full | PNG-compared, lowest structural delta | HIGH |
| A5 | Full | Full | Full | PNG-compared, best overall match | HIGH |
| EXTRA-01..04 | Existence + top-level structure only (explicit effort-allocation call, see `APPROVED_SCREEN_INVENTORY.md`) | Not measured in detail | Not extracted separately | No approved PNG exists for any of the 4 | LOW |

## Approved-source conflicts carried forward (must be resolved, not re-derived)

1. Mobile HTML-canvas aspect ratio vs. approved-PNG aspect ratio (all mobile screens but A5) — `D1`.
2. Near-miss (not exact) brand-accent and ink colors vs. current tokens — `D2`, `D3`.
3. Font family hard mismatch (Noto Sans KR vs Pretendard/Black Han Sans/Inter) — `D4`.
4. Icon/illustration assets specified by approved PNGs (A2 Home hero + service tiles, A3 mission icons)
   have **no corresponding source file anywhere in `screen_renew`** — `D5`. This is a sourcing task, not
   a measurement task; 6.0C cannot resolve it by re-reading the same folder harder.
5. Admin sidebar dark/light tone conflict — `D8`.

## Current functionality that must be preserved regardless of visual outcome

Full detail in `FUNCTIONAL_CONTRACT_MATRIX.md`; headline MUST_PRESERVE items: Family Context storage
contract (`mongle.activeFamily.*` canonical / `naran.activeFamily.*` legacy-read-fallback), the
`/naran/doran`→`/wagle` and `/naran/family`→`/family` redirect contract, RBAC boundaries
(`ProtectedRoute`/`AdminProtectedRoute`/`AccessBoundary`), the Doran service-code/API-path contract
(explicitly non-negotiable), and the mission/points/level/deduction backend logic behind A3/A5.

## Token candidates ready for a freeze conversation

Full list in `APPROVED_TOKEN_CANDIDATES.md` + `TOKEN_IMPLEMENTATION_AUDIT_V2.md`. Lowest-risk items (exact
matches already in code): `--color-brand-100`, `--color-danger`(new value), `--color-canvas`,
`--color-chat-own/-other`, `--radius-pill`, `--radius-control`, `--size-touch-min`. Highest-risk/most
consequential open items: brand-accent/ink near-misses (D2/D3), the font-family question (D4), and the
odd-number (3/5/7/9/11px) spacing scale vs. the current 4px-multiple `--space-*` ladder.

## Component candidates

`Avatar` and `IconButton` are already past the "2nd consumer" bar and are the safest global-promotion
candidates. `Card`/`MainLogo` have exactly 1 consumer each and are not yet promotion-ready per the
brief's own rule. The 10 `platform/doran/components/*` are well-factored but single-consumer; a Room
List or second conversation surface would be the natural trigger for reconsidering their status.

## Asset candidates

`family_platform_pin_logo_transparent_1024.png` is the confirmed, in-use brand-mascot master. Everything
else icon/illustration-related for A2/A3 is `SOURCE_MISSING` (see D5) and needs to be sourced before
those two screens' Wave 6.1 work can be visually faithful.

## Expected change files

Full detail in `PER_SCREEN_FILE_CHANGE_PLAN.md`, with exact-path vs PROPOSED_PATH clearly separated per
screen.

## Test gaps

Zero current tests assert on any visual/layout property matching the approved design (`E2E_COVERAGE_MAP_V2.md`).
The legacy `specs/*.spec.ts` suite (covering A1/A3/A5) cannot currently execute (`docker-compose.phase0.yml`
missing) — `D12`. The newer `specs-mongle` suite is healthy and well-understood (66/70 passing, 4 skipped
by design, traced to one line of code) but covers route/storage migration, not visual reconstruction.

## Pre-implementation blockers, ranked

1. **A4 backend integration** (`doranApi.ts` does not exist) — the single largest gap between "looks
   right" and "works," and the one screen whose functional contract (Doran) is explicitly non-negotiable.
2. **A2 asset sourcing + screen build** — currently 0% implemented and blocked on missing source assets simultaneously.
3. **Font-family decision (D4)** — affects every screen at once; cheap to decide, expensive to leave ambiguous.
4. **Aspect-ratio decision (D1)** — affects every mobile screen's proportions.
5. **Admin sidebar tone (D8)** — affects every Admin view, not just A5.

## Recommended review order for 6.0C (non-binding)

D4 (font) and D1 (aspect ratio) first, since both are cross-cutting and cheap to settle; then D5 (asset
sourcing, needed before A2/A3 visual work can start); then D2/D3 (color near-misses, low risk); then the
screen-specific items D6/D7 (A4 scope) and D8 (A5 sidebar tone); D9/D10/D11/D12 are lower urgency and can
be resolved opportunistically.

No PM decision is confirmed by this document. MONGLE-W6-0C-CANONICAL-FREEZE-001 has not been started.
