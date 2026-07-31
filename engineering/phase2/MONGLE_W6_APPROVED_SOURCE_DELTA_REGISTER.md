# MONGLE_W6_APPROVED_SOURCE_DELTA_REGISTER

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 9 (승인 Source Delta Gate).

## Baseline (6.0AB time, from committed evidence)

`6.0A/approved_source_start.sha256` = `6.0A/approved_source_end.sha256` (byte-identical, 44 entries,
confirmed unchanged during the 0AB session) lists the `screen_renew` root as of 2026-07-28/29:

- `.DS_Store`, `.thumbnail` (2, non-content)
- `_analysis/wave6_0-analysis/*` (12: prior-session historical docs/images)
- `_analysis/wave6_1a-source/*` (11: prior-session historical docs)
- `standalone-src.html` (153,869 B, 10 screens: A1/A1-S1/A2/A3/A4/A5/EXTRA-01..04)
- `가족 플랫폼 화면 재현.dc.html` (same name, byte-identical to `standalone-src.html` — `DUPLICATE`)
- `support.js` (1)
- `uploads/*.png` (10 raster assets)

## Current (`docs/temp/design_tablet/`, this session, 40 content files)

Full manifest: `/tmp/mongle-wave6-0c-gate/tablet_source_manifest.sha256`.

## Delta classification

| Item | Classification | Basis |
|---|---|---|
| `uploads/*.png` (10 files) | **UNCHANGED_EXISTING_SOURCE** | SHA-256 identical, all 10, to `screen_renew/uploads/` per `6.0A/approved_source_file_inventory.csv` — verified this session (see `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md`) |
| `가족 플랫폼 화면 재현-tablet.dc.html` (root) | **ADDED_TABLET_CANONICAL_SOURCE** | New file, no prior-session counterpart exists at all; PM-confirmed as Tier 1T source this session |
| `가족 플랫폼 화면 재현-tablet.dc.html` (`design_handoff_family_platform/screens/` copy) | **EXPECTED_DUPLICATE** | SHA-256-identical to the root copy |
| `가족 플랫폼 화면 재현-tokenized.html` (root + packaged copy) | **ADDED_TABLET_ASSET** | New file (token-substituted variant of the mobile 71-screen HTML); packaged copy is `EXPECTED_DUPLICATE` of the root |
| `design-system/*` (10 files: style guide HTML, `canonical-tokens.css`/`.json`, 8 classification MD) | **ADDED_TABLET_ASSET** | No prior-session counterpart in the 44-file baseline (which had zero standalone CSS/JSON/style-guide-HTML files — `6.0A/APPROVED_SOURCE_FILE_INVENTORY.md` explicitly recorded "CSS/SVG/JSON/PDF as standalone files: 0"); packaged copy under `design_handoff_family_platform/design-system/` is `EXPECTED_DUPLICATE` (`diff -rq` = zero differences, verified this session) |
| `HANDOFF_PROMPT.md`, `design_handoff_family_platform/README.md` | **ADDED_TABLET_ASSET** | Delivery/application-guidance documents, new this delivery |
| `support.js` | **UNCHANGED_EXISTING_SOURCE (functional match, not byte-verified)** | Same generated-runtime header signature (`// GENERATED from dc-runtime/src/*.ts`) as `6.0A/APPROVED_SOURCE_FILE_INVENTORY.md` describes; exact byte-for-byte SHA was not recorded in the 6.0A manifest for this file's content in a form this session can re-diff, so marked functional match only, not a confirmed identical-bytes claim |
| `.thumbnail` | **EXPECTED_DUPLICATE (functional)** | Same role (macOS Finder thumbnail cache, WebP RIFF), present in both baselines; not analyzed further per `6.0A` precedent (`NOT_APPLICABLE`) |
| `가족 플랫폼 화면 재현.dc.html` (71-screen, 636,567 B, SHA `d0c42227...2d30fb9`) | **MODIFIED_EXISTING_MOBILE_SOURCE — flagged, not auto-allowed** | Same display name as the 44-file baseline's 10-screen `standalone-src.html`/`가족 플랫폼 화면 재현.dc.html` (153,869 B, SHA `5f823d4c...ef3a82a7`), but different byte content, different size, different screen-ID scheme, different screen count (71 vs 10). Per Section 9, `MODIFIED_EXISTING_MOBILE_SOURCE` is explicitly **not** on the auto-allowed list — this delta requires a PM decision, not a default assumption in either direction. Recorded as **PM Decision D13** (`MONGLE_W6_PM_DECISION_REGISTER.md`). This does **not** meet the `UNKNOWN_DELTA` bar (the delta's nature is fully characterized, just not resolved), so it does not on its own trigger a full-task Hard Stop; it blocks only the specific downstream conclusions that would require picking one mobile HTML as ground truth (pixel-level values, D1/D4/D5 confirmation). |
| `_analysis/wave6_0-analysis/*`, `_analysis/wave6_1a-source/*` (23 files), `.DS_Store`, `standalone-src.html` (the 10-screen original itself) | **NOT PRESENT in `docs/temp/design_tablet/`** | Expected absence — these are prior-session historical artifacts and the exact original structural source file; their non-presence here is not itself a delta finding since this directory was never claimed to be a full mirror of `screen_renew`, only the source of the new tablet material plus a shared asset folder |

## Auto-allowed vs. not-auto-allowed (per Section 9 rule)

**Automatically allowed by this session's PM clarification** (new tablet material, matches the prompt's
own stated allowance):
- `ADDED_TABLET_CANONICAL_SOURCE` (the tablet HTML itself)
- `ADDED_TABLET_ASSET` (design-system tokens/style-guide/docs, tokenized HTML, delivery docs)
- SHA-identical duplicates of the above

**Not automatically allowed — explicitly not treated as resolved by this register:**
- Existing approved mobile PNGs — **unchanged** (10/10 SHA match), so this prohibition is not triggered.
- Existing Style Guide — no *prior* style guide existed as a standalone file in the 44-file baseline
  (`6.0A` found none), so there is nothing to compare `design-system/APPROVED_VISUAL_STYLE_GUIDE.html`
  against for a "changed" verdict; it is `ADDED`, not `MODIFIED`.
- Existing mobile HTML — **the one item on this list that IS a same-name, different-content delta.**
  Flagged `MODIFIED_EXISTING_MOBILE_SOURCE`, carried to PM Decision `D13`, not resolved here.
- Existing Logo master — unchanged (both `family_platform_pin_logo_transparent_1024.png` and the 2048²
  sibling are SHA-identical to baseline).
- Unsourced deletion — none observed; the 23 historical-analysis files and `standalone-src.html` simply
  don't exist at this path, which is expected (this directory was never the full `screen_renew` mirror).

## UNKNOWN_DELTA check

**Zero `UNKNOWN_DELTA` items.** Every file difference found this session has a specific, evidenced
classification above. The task does not halt on this Gate.

## Verdict for this Gate

**SOURCE_DELTA_CLASSIFIED — 1 item flagged for PM decision (D13), 0 unknown, 0 auto-stop conditions.**
Proceeding to Section 10 (independent tablet measurement) using the tablet HTML as Tier 1T and treating
the 71-screen mobile HTML strictly as unverified/reference-only context (never as a substitute for the
6.0A `standalone-src.html` pixel measurements already on record for A1–A5).
