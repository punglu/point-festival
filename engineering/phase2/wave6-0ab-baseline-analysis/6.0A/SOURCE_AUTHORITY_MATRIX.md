# Source Authority Matrix

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 7)

Classification taxonomy (per brief): `PRIMARY_STRUCTURE_SOURCE / PRIMARY_VISUAL_SOURCE / SHARED_STYLE_REFERENCE / ASSET_MASTER_CANDIDATE / DERIVED_REFERENCE / HISTORICAL / DUPLICATE / UNKNOWN / SOURCE_CONFLICT`.

| File | Classification | Rationale |
|---|---|---|
| `standalone-src.html` | `PRIMARY_STRUCTURE_SOURCE` | DOM structure, inline CSS literals, repeated component patterns, screen boundaries (`id="1a"`..`"1i"`, `data-screen-label`) all live here. Used as the primary source for HTML_STRUCTURE_EXTRACTION, MEASUREMENT_TABLE_V2, APPROVED_TOKEN_CANDIDATES. |
| `가족 플랫폼 화면 재현.dc.html` | `DUPLICATE` | Byte-identical (SHA-256 match) to `standalone-src.html`. Not read independently; any statement about `standalone-src.html` applies equally. |
| `uploads/screen_login_approved.png` | `PRIMARY_VISUAL_SOURCE` | Final rendered visual truth for screen A1. Used for hierarchy/impression/HTML-render verification in TIER1_HTML_VISUAL_DELTA. |
| `uploads/screen_family_home_approved.png` | `PRIMARY_VISUAL_SOURCE` | Same role for A2. |
| `uploads/screen_point_festival_approved.png` | `PRIMARY_VISUAL_SOURCE` | Same role for A3. |
| `uploads/screen_family_chat_approved.png` | `PRIMARY_VISUAL_SOURCE` | Same role for A4 (single GROUP conversation state only — no Room List visual exists, see APPROVED_SOURCE_GAP notes). |
| `uploads/screen_admin_point_approved.png` | `PRIMARY_VISUAL_SOURCE` | Same role for A5. Best HTML/PNG agreement of the set (see TIER1). |
| `uploads/family_platform_style_guide_v1.png` | `SHARED_STYLE_REFERENCE` | Long-form style-guide raster (1600×6773). Not tied to a specific screen; used only for corroborating common design language, never as the sole basis for a measurement. |
| `uploads/family_platform_style_guide_preview.png` | `SHARED_STYLE_REFERENCE` | Shorter companion (1600×4400), same role. Content overlap with v1 not byte-verified (`NOT_VERIFIED`). |
| `uploads/family_platform_pin_logo_transparent_1024.png` | `ASSET_MASTER_CANDIDATE` | The only brand-mascot raster actually referenced by `src=` in the HTML (6+ references across A1/A1-S1/A2/A3/A4/A5). Highest-resolution version *that is actually used*. |
| `uploads/brand_pin_logo_transparent.png` | `ASSET_MASTER_CANDIDATE` | Higher resolution (2048²) than the 1024 version but **not referenced anywhere in `standalone-src.html`** (verified via `grep -oE 'src="[^"]*"'`). Candidate master for future use, not a confirmed in-use asset. |
| `uploads/19de6297-c168-45f4-be59-878a01bc0641.png` | `UNKNOWN` | UUID filename, not referenced in the HTML, no other metadata identifying its purpose. Not reclassified without evidence — flagged for PM/human visual check. |
| `_analysis/wave6_0-analysis/*.md` (10 files) | `DERIVED_REFERENCE` / `HISTORICAL` | Prior session's own analysis of this same source (COMPONENT_CATALOG, MEASUREMENT_TABLE, TOKEN_PROPOSAL, GAP_MATRIX, WAVE_PLAN, SCREEN_INVENTORY, SCREEN_ASSEMBLY_PLAN, SCREEN_FLOW, FINAL_REPORT, PROGRESS). Cited only as corroborating/conflicting reference in this task's own STALE/authority notes (see STALE_ANALYSIS_REGISTER.md); never treated as ground truth per the task brief's explicit instruction. |
| `_analysis/wave6_0-analysis/*.png` (6 files) | `DERIVED_REFERENCE` | Prior session's own cropped screenshots of the style guide, not new design content. |
| `_analysis/wave6_0-analysis/approved-assets.sha256` | `DERIVED_REFERENCE` | Prior session's own SHA manifest of a subset of assets — **not** the manifest produced by this task (`approved_source_start.sha256`/`_end.sha256`, which cover the full tree). Not cross-diffed further; out of scope to validate someone else's manifest. |
| `_analysis/wave6_1a-source/*.md` (10 files) | `DERIVED_REFERENCE` / `HISTORICAL` | Prior session's deeper HTML→React extraction pass (COMPONENT_EXTRACTION, HTML_SCREEN_STRUCTURE, HTML_TO_REACT_RULES, INLINE_LITERAL_INVENTORY, TOKEN_MAPPING, TYPOGRAPHY_MAPPING, TIER1_VISUAL_DELTA, etc.). Same treatment as above. |
| `support.js` | `SHARED_STYLE_REFERENCE` (tooling only) | Not design content; it is the generic "design-canvas" (`dc-runtime`) render engine that turns `<x-dc>` markup into a live page via React/Babel loaded from `unpkg.com`. Its only relevance to design authority is that it explains *how* the HTML renders (used to justify the Playwright-based render approach in TIER1). |
| `.DS_Store`, `.thumbnail` | `NOT_APPLICABLE` | macOS filesystem metadata, no content relevance. |
| current React implementation (`minecraft_points_festivals_doran_ui/frontend/src/**`) | **Not part of this matrix** — per the brief, current code is the current-implementation baseline (Phase B), never a design authority. Referenced only for Phase B / cross-reference, never used to resolve a Phase A ambiguity. |

## HTML vs PNG conflicts (do not silently prefer one)

Recorded in detail in `TIER1_HTML_VISUAL_DELTA.md`. Headline conflict, stated here because it affects authority interpretation for **every** mobile screen (A1/A1-S1/A2/A3/A4 + EXTRA-01..04): the HTML mockup frame is a fixed 480px-wide canvas box with an approx. 1.9–2.0 aspect ratio, while the actual approved PNGs are real-device-resolution captures with a taller aspect ratio (0.46–0.56, i.e. ~2.0–2.2 height/width). This is a structural `SOURCE_CONFLICT` between "PRIMARY_STRUCTURE_SOURCE" (HTML, which fixes 480px canvas width for every mobile screen) and "PRIMARY_VISUAL_SOURCE" (PNG, which shows a taller device). Per the brief's authority rule, this is **not resolved** here — HTML remains authoritative for DOM structure/CSS literals, PNG remains authoritative for final rendered hierarchy/impression, and the aspect-ratio mismatch itself is logged as `PM_DECISION_REQUIRED` (does the real target device viewport match the PNG's aspect or the HTML canvas's aspect?).

No file was reclassified as `UNKNOWN` without evidence; the one `UNKNOWN` entry above (`19de6297-...png`) remains so because no reference, filename semantics, or metadata ties it to a specific role.
