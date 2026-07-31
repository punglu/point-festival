# PROVENANCE — Mongle Wave 6 Tablet Canonical Archive

Task: MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, Section 4 (permanent tablet-source archive).
Archived: 2026-07-31. Archivist: Claude Code (documentation/evidence-archive mode, read-only on
`docs/temp/design_tablet/**` originals).

## Origin

Source root (untracked, gitignored via `.gitignore:28` `/docs/`): `docs/temp/design_tablet/`.
This is a scratch/reference-drop location (same role as a `temp/` folder), first identified and
classified `TABLET_CANONICAL_SOURCE_IDENTIFIED` by the preceding task
`MONGLE-W6-0C-CANONICAL-FREEZE-001` (see `../../MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md`). This
archive persists that source permanently under version-controllable `engineering/phase2/` so it
survives `docs/temp/` being gitignored/cleared.

## What was archived and why

| Archived path | Origin path | Role |
|---|---|---|
| `source/가족 플랫폼 화면 재현-tablet.dc.html` | `docs/temp/design_tablet/가족 플랫폼 화면 재현-tablet.dc.html` | **Tablet canonical master** (Tier 1T). SHA-256 `24a02ab63b7e4aafccbbc064ba7f99d1ffe429ef4f43f8427f6699defcf571d6`. Landscape (1024×700) + portrait (768×1024) tablet breakpoints, 15 priority screens (66/71-catalog coverage measured, see Source Identification doc). |
| `source/가족 플랫폼 화면 재현.dc.html` | same-named file, root of `docs/temp/design_tablet/` | **Extended mobile structure source** (PM Decision D13: `EXTENDED_MOBILE_STRUCTURE_SOURCE`, does not supersede the approved mobile PNGs and is not the same file as the missing `standalone-src.html` 6.0A measured). 71 screens, `1a`–`3l` ID scheme. SHA-256 `d0c4222790eb20a8b6e391f56bdc9d1751d719801577a182406788f2d2a30fb9`. |
| `source/가족 플랫폼 화면 재현-tokenized.html` | same-named file, root | **Partial tokenized derivative** of the 71-screen file above — see "Tokenized-file relationship" below. Not named in the original closeout task's file list; investigated and documented here per this task's own instruction not to ignore it silently. SHA-256 `1d11874d0bceb227b5cecd81bdb8954fd3d620818292f9b608300aa925da5327`. |
| `source/support.js` | root | Delivery preview-runtime script (`// GENERATED from dc-runtime/src/*.ts` header) referenced by all 3 HTML files above. Not design content; archived for reproducibility of the delivery's own preview mechanism only. |
| `source/HANDOFF_PROMPT.md` | root | Delivery instructions accompanying the drop. |
| `source/DESIGN_HANDOFF_README.md` | `design_handoff_family_platform/README.md` | Renamed on archive (original `README.md` would collide with nothing here, renamed for clarity only — content byte-identical to origin, confirmed by SHA). States "71 screens" scope explicitly, corroborating the extended-mobile-structure classification of the `.dc.html` (non-tablet, non-tokenized) file. |
| `assets/design-system/*` (10 files) | `docs/temp/design_tablet/design-system/*` | Shared Style Source (Tier 2): `APPROVED_VISUAL_STYLE_GUIDE.html`, `canonical-tokens.css`/`.json`, 8 classification MD docs (`AMBIGUITY_AND_PM_REVIEW.md`, `COMPONENT_STYLE_CONTRACT.md`, `FINAL_REPORT.md`, `ONE_OFF_LITERAL_REGISTER.md`, `SCREEN_LOCAL_TOKEN_REGISTER.md`, `SOURCE_SCREEN_INVENTORY.md`, `TOKEN_CLASSIFICATION.md`). |
| `assets/uploads/*.png` (10 files) | `docs/temp/design_tablet/uploads/*.png` | Approved mobile screen mocks (5, Tier 1M), brand logo pair (1024px in-use master + 2048px unreferenced sibling), style-guide preview PNGs (2), 1 unclassified PNG (`19de6297-...`, `SOURCE_MISSING`/`UNKNOWN` classification carried from `MONGLE_W6_ASSET_POLICY_FREEZE.md`, not resolved by this archiving pass). |

Total archived: **26 files**, ~15 MB (`du -sh` of the archive directory; see `manifests/FILE_INVENTORY.csv` for
per-file sizes).

## Duplicate-relationship notes (exclusions, per Section 4's exclusion rule)

The following were found in `docs/temp/design_tablet/` and **excluded** from the archive because they
are byte-identical duplicates, OS metadata, or non-content caches — not because their content differs:

| Excluded path | Reason | Verification |
|---|---|---|
| `design_handoff_family_platform/screens/가족 플랫폼 화면 재현-tablet.dc.html` | `EXPECTED_DUPLICATE` of the archived tablet master | `sha256sum` match: `24a02ab6...571d6` == `24a02ab6...571d6` |
| `design_handoff_family_platform/screens/가족 플랫폼 화면 재현.dc.html` | `EXPECTED_DUPLICATE` of the archived 71-screen file | `sha256sum` match: `d0c42227...2d30fb9` == `d0c42227...2d30fb9` |
| `design_handoff_family_platform/screens/가족 플랫폼 화면 재현-tokenized.html` | `EXPECTED_DUPLICATE` of the archived tokenized file | `sha256sum` match: `1d11874d...25da5327` == `1d11874d...25da5327` |
| `design_handoff_family_platform/design-system/*` (10 files) | `EXPECTED_DUPLICATE` full-tree of the archived `assets/design-system/*` | `diff -rq` (excluding `:Zone.Identifier` files) = zero differences |
| every `*:Zone.Identifier` file (26 in `docs/temp/design_tablet/`) | Windows/WSL download-zone marker, non-content, present alongside every real file | `file` = plain text `[ZoneTransfer]` stub, zero design/code content |
| `.thumbnail` (+ its `:Zone.Identifier`) | OS-level thumbnail cache | `file` = `RIFF ... Web/P image`, a generated preview cache, not a source deliverable |

No `.DS_Store`, `node_modules/`, temp screenshot, or regenerable intermediate files were found under
`docs/temp/design_tablet/` (confirmed by `find`/`du` during the pre-archive integrity check).

## Tokenized-file relationship (investigated, not in the original task's named file list)

`가족 플랫폼 화면 재현-tokenized.html` (464 KB) is **not** a duplicate of either the tablet master or the
71-screen extended mobile structure file — its SHA-256 matches neither. Structural comparison performed
this session:

- It is the only one of the three HTML files that references `canonical-tokens.css` (`var(--token)`
  usage) — confirmed by grep, 0 hits in the other two files.
- Its `id="..."` markers (45 distinct values, e.g. `0a`…`2k`) are an **exact subset** (same values, same
  order) of the 71-screen file's 72 distinct `id="..."` markers — confirmed by `diff` of the sorted id
  lists: the tokenized file's ids diff cleanly against the first 45 of the 71-screen file's 72, with the
  71-screen file only *adding* ids (`2l`…`3l`) beyond what the tokenized file has.
- It contains zero occurrences of "tablet" and does not share the tablet master's `1024×700`/`768×1024`
  canvas-size vocabulary (only `1024` appears, 17× as a `width:1024` device-mock frame, not a labeled
  tablet breakpoint).

**Classification: `PARTIAL_TOKENIZED_DERIVATIVE_OF_71_SCREEN_SOURCE`** — an earlier or partial
design-token-substitution pass over roughly the first 45 of the 71-screen mobile structure file's 72
screens, not tablet-related, not a duplicate, not a superset. Archived for provenance completeness. Per
PM Decision D13's source-role partition (PNG > PM decision > current functional contract), this file is
**not** granted any additional source authority beyond what D13 already assigns the 71-screen file it is
derived from — it does not become a fourth independent source tier.

## Pre-archive integrity checks (performed before copying)

- Size sanity: `docs/temp/design_tablet/` total = 17 MB (`du -sh`); archived subset = ~15 MB (the majority
  of the 17 MB, minus the packaged-duplicate `design_handoff_family_platform/` tree and metadata noise).
- File-count sanity: 40 content files reported by the preceding task's Source Identification gate
  (`.thumbnail`/`Zone.Identifier` excluded from that count); this archive's 26 files = 40 minus (3
  HTML duplicates + 10 design-system duplicates + 1 README already-counted-once).
- Asset-reference resolution: all `src=`/`url()`/`link href` references inside the 3 archived HTML files
  that point at `uploads/*.png` or `design-system/canonical-tokens.css` resolve to files present in this
  archive's `assets/` tree (spot-checked: `family_platform_pin_logo_transparent_1024.png`,
  `canonical-tokens.css`).
- SHA match: every archived file's SHA-256 (see `../manifests/SHA256_MANIFEST.txt`) was diffed against a
  fresh `sha256sum` of its origin file in `docs/temp/design_tablet/` at archive time — zero mismatches.

## Post-archive integrity checks (performed after copying)

- Zero mutation of originals: `docs/temp/design_tablet/가족 플랫폼 화면 재현-tablet.dc.html` SHA-256
  re-read after archiving = `24a02ab63b7e4aafccbbc064ba7f99d1ffe429ef4f43f8427f6699defcf571d6`, unchanged
  from the pre-archive read.
- Zero mutation outside `engineering/phase2/**`: confirmed via End Gate `git status --porcelain=v1 -uall`
  diff against the Start Gate snapshot (see `/tmp/mongle-wave6-0c-closeout-gate/start_end_comparison.md`).
- Archive is not wired into any product build path: not referenced by `frontend/**`, `backend/**`,
  `vite.config.*`, `nginx.conf`, `Dockerfile`, or any import/route/script under those trees (confirmed by
  grep for `mongle-wave6-tablet-canonical` across `frontend/src`, `backend/app`, and root config files —
  zero hits).

## Explicit non-claims

- This archive does not assert the unresolved `19de6297-...png` asset's purpose or origin.
- This archive does not resolve the fake-status-bar-row ambiguity flagged for A2 landscape in
  `MONGLE_W6_ASSET_POLICY_FREEZE.md`.
- This archive does not include the missing `standalone-src.html` (10-screen, 153,869 B,
  SHA `5f823d4cc98755785ff308bf9e3d756d3a40fb5f93a2194c756886ccef3a82a7`) — that file was not found
  anywhere in this repository or in `docs/temp/design_tablet/` and cannot be archived because it does not
  exist in this environment. Its measurements survive only as `COMMITTED_DERIVED_EVIDENCE` in
  `engineering/phase2/wave6-0ab-baseline-analysis/6.0A/`.
