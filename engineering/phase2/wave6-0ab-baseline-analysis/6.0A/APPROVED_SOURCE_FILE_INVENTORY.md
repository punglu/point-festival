# Approved Source File Inventory

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 6)
Approved source root: `/Users/mac/mac_Project/minecraft_points_festivals/temp/screen_renew`
Full machine-readable inventory: `approved_source_file_inventory.csv` (44 rows, every file under the root recursively, `.DS_Store`/`.thumbnail` included per instruction).
Start-of-analysis SHA-256 manifest: `approved_source_start.sha256` (44 entries).

## Summary

| Metric | Value |
|---|---|
| Total files (recursive, incl. non-content) | 44 |
| HTML | 2 (`standalone-src.html`, `가족 플랫폼 화면 재현.dc.html`) |
| JS | 1 (`support.js`) |
| PNG (uploads/) | 10 |
| PNG (`_analysis/wave6_0-analysis/`, prior-session screenshots) | 6 |
| Markdown (`_analysis/*`, prior-session docs) | 19 |
| sha256 manifest file (prior session) | 1 (`_analysis/wave6_0-analysis/approved-assets.sha256`) |
| Non-content (`.DS_Store`, `.thumbnail`) | 2 |
| CSS/SVG/JSON/PDF as standalone files | 0 (CSS and SVG exist only inline inside `standalone-src.html`; no standalone `.css`/`.svg`/`.json`/`.pdf`/font files found) |
| Font files | 0 (font is loaded externally via Google Fonts CDN link, not a local file — see External Dependencies) |

## Critical duplicate finding

`standalone-src.html` and `가족 플랫폼 화면 재현.dc.html` are **byte-identical**: both 153,869 bytes and identical SHA-256
`5f823d4cc98755785ff308bf9e3d756d3a40fb5f93a2194c756886ccef3a82a7`. Verified via full SHA-256 (not size-only). Classified as `DUPLICATE` in the Source Authority Matrix — `standalone-src.html` is treated as the working copy for all extraction in this task (arbitrary but harmless choice since the two are provably identical; the Korean-named file is unchanged and unmodified).

## External dependencies (found via source inspection, not assumed)

- Google Fonts CDN: `https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap` (preconnect to `fonts.googleapis.com` and `fonts.gstatic.com`).
- `support.js` (a generic, non-project "design-canvas" runtime, header comment reads `// GENERATED from dc-runtime/src/*.ts — do not edit`) loads, at runtime, three additional CDN scripts from `unpkg.com`: React 18.3.1, ReactDOM 18.3.1, `@babel/standalone` 7.29.0. These are **not part of the design content** — they are the tooling that renders the `<x-dc>` canvas document in a browser. Confirmed by reading `support.js` lines ~1142-1149.
- No missing local references were found (`img src="uploads/..."` all resolve to existing files).

## Non-approved-source but co-located material

`_analysis/wave6_0-analysis/` and `_analysis/wave6_1a-source/` (25 files total: 19 `.md` + 6 `.png` + 1 `.sha256`) are **pre-existing analysis artifacts from an earlier, different work session**, not produced by this task and not part of the design content itself. They are inventoried (in-scope per the task brief because they live inside the approved-source directory tree) but classified `DERIVED_REFERENCE`/`HISTORICAL` in the Source Authority Matrix, never as ground truth. See `STALE_ANALYSIS_REGISTER.md` for freshness classification of each.

## Non-applicable files

`.DS_Store` and `.thumbnail` — macOS Finder metadata / thumbnail cache, classified `NOT_APPLICABLE` in the Source Authority Matrix, not analyzed further.

Full per-file byte size, SHA-256, mtime, and (for images) pixel dimension/mode/alpha-channel data is in `approved_source_file_inventory.csv`.
