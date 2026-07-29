# Approved Token Candidates

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 11). Full data: `approved_token_candidates.csv` (93 rows: colors, font-size, spacing-padding, spacing-gap, border-radius, box-shadow, layout-width, control-height, font-family). Raw, unfiltered occurrence counts (every distinct literal, not just the curated top-N in the CSV) are preserved in `_raw_colors.csv`, `_raw_font_sizes.csv`, `_raw_radii.csv`, `_raw_paddings.csv`, `_raw_gaps.csv`, `_raw_shadows.csv`, `_raw_widths.csv` for full audit trail.

**No token is confirmed/finalized in this document** — every row is a *candidate* with a classification
and confidence, per the brief's explicit prohibition on token confirmation in this Wave.

## Method

Cross-referenced every candidate's raw hex/px value against the current implementation's `global.css`
token list (read directly from `minecraft_points_festivals_doran_ui/frontend/src/styles/global.css`,
lines 26-57 — Phase B current-implementation fact, used here only for comparison, never as design
authority). A color within ±4 per RGB channel of an existing token is flagged `SOURCE_CONFLICT` (close
enough to be the same design intent with rounding drift, but not proven identical); an exact hex match
is `MIGRATION_ALIAS_CANDIDATE`; no match at all, with ≥6 occurrences, is `SEMANTIC_CANDIDATE`; no match
with <6 occurrences is `ONE_OFF_LITERAL`.

## Headline findings

1. **Three exact-hex matches already exist between the approved source and the current implementation**:
   `#EEE8FF` = `--color-brand-100`, `#EF4665` = `--color-danger`, `#F7F6FC` = `--color-canvas`, plus the
   chat colors `#6944EF`/`#F3F0FF` = `--color-chat-own`/`--color-chat-other`, plus `999px` = `--radius-pill`,
   `16px` = `--radius-control`, and `44px` = `--size-touch-min`. These are the safest migration-alias
   candidates — HIGH confidence, but still flagged `pm_gate_required=YES` because the brief prohibits
   auto-confirming even exact matches as final tokens in this Wave.
2. **Two near-miss (not exact) color matches requiring an explicit PM call**: `#17103A` (188 occurrences,
   the most-used color in the whole document) is within 3 of `--color-ink-900` (`#171D3A`) but not
   identical; `#5A35DF` (117 occurrences, the primary brand accent) is within 2 of `--color-brand-600`
   (`#5835DF`) but not identical. Both are classified `SOURCE_CONFLICT`, not silently treated as the same
   color — a PM must decide whether this is rounding noise or an intentional shift.
3. **Font family is a hard mismatch, not a token-alias question**: approved source uses Noto Sans KR
   exclusively; current implementation uses Pretendard/Black Han Sans/Inter. Classified
   `REQUIRES_PM_DECISION` rather than any alias category.
4. **Spacing scale mismatch**: the approved source's most frequent gap/padding values (3px, 7px, 5px,
   9px, 11px) are largely odd numbers that do not fit the current 4px-based `--space-1..12` scale.
   Classified `REPEATED_LITERAL` with an explicit conflict note rather than forced onto the existing scale.
5. **Several frequently-used muted/secondary text colors have no current-implementation counterpart at
   all** (`#8A83A8` 82×, `#4A3F72` 70×, `#A8A5B6` 50×, `#6B6880` 21×) — these are new `SEMANTIC_CANDIDATE`
   entries, not derivable from any existing token, and would need genuinely new token slots if adopted.
6. One shadow value (`0 30px 70px rgba(40,20,90,.22)`, 9 occurrences) is exclusively the **phone-mockup-
   frame's own shadow** (a presentation artifact, not a real card/component elevation) and is explicitly
   marked `SOURCE_CONFLICT`/excluded rather than proposed as a new `--shadow-*` token.

No existing project token name was invented or forced onto an approved-source value without either an
exact hex/px match or an explicit near-miss/conflict flag — per the brief's instruction not to fit
approved values into existing names by convenience.
