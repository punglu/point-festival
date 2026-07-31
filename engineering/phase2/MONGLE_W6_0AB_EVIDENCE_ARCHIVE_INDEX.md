# MONGLE_W6_0AB_EVIDENCE_ARCHIVE_INDEX

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 7 (6.0AB Evidence Preservation Gate).

## Deviation from the prescribed procedure (recorded explicitly, not silently)

Section 7 instructs this task to locate the **raw** `/tmp/mongle-wave6-0ab` package (or a listed
alternate archive candidate), copy it to a permanent path, and hash-verify the copy. None of the
prescribed locations exist in this environment:

| Candidate path (from task prompt) | Result |
|---|---|
| `/tmp/mongle-wave6-0ab` | **NOT FOUND** |
| `/Users/mac/mac_Project/minecraft_points_festivals/temp/wave6_evidence/` | **NOT FOUND** (Mac-only path; this session runs on Linux/WSL at `/appl/point-festival`) |
| `/Users/mac/mac_Project/minecraft_points_festivals/temp/` | **NOT FOUND** (same reason) |
| `engineering/phase2/**/evidence/**` | **FOUND** — see below |

Per PM clarification given in this session (2026-07-31), this environment (`/appl/point-festival`,
branch `dev-newmarkp`) is the authoritative worktree for this task, not the Mac path in the original
prompt. Mac-only paths are explicitly **not** used as Hard Stop grounds. Instead, the task's own
already-committed substitute was located and verified:

**`engineering/phase2/wave6-0ab-baseline-analysis/`** (committed in `0861929
docs(phase2): archive Wave 6.0AB baseline analysis`, the direct parent-plus-one of the current HEAD;
see `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md` for the HEAD-intent verification).

Classification: **COMMITTED_6_0AB_EVIDENCE_SUBSTITUTE** (not `RAW_6_0AB_PACKAGE`). This directory is
the same evidence Section 19 of the 0AB final report describes as "88 files under `/tmp/mongle-wave6-0ab/`
... reproducible via `find /tmp/mongle-wave6-0ab -type f`" — it is the *persisted copy* of that
ephemeral package (93 files here vs. 88 reported at `/tmp` time; the +5 delta is the `_gate/` End Gate
files plus this indexing pass's own additions, not missing content — see file-count table below).

## Explicit unavailability labels (per PM instruction, carried into every downstream document)

- `RAW_6_0AB_PACKAGE_UNAVAILABLE` — the original `/tmp/mongle-wave6-0ab` ephemeral directory cannot be
  located or re-verified byte-for-byte in this environment. This document does not claim to have done so.
- `ORIGINAL_MOBILE_SOURCE_UNAVAILABLE_AT_REPORTED_PATH` — `/Users/mac/mac_Project/minecraft_points_festivals/temp/screen_renew`
  (the Tier 1M/Tier 3 approved-source root analyzed by 6.0A) does not exist at that path in this
  environment. **Partial mitigation found and independently verified this session**: the 10 raster
  assets under `screen_renew/uploads/` (5 approved PNGs, brand logo pair, 2 style-guide PNGs, 1 unknown
  PNG) are present, byte-identical (SHA-256 match, all 10 files), at `docs/temp/design_tablet/uploads/`
  in this repo. The **HTML structural source** (`standalone-src.html`, 10-screen A1-A5 scheme) is
  **not** present at that path or reproduced anywhere found in this repo — see
  `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md` §"Mobile HTML source conflict" for the full finding.
- `COMMITTED_DERIVED_EVIDENCE_USED` — every 6.0A/6.0B measurement, matrix, and PM decision cited by this
  Wave 6.0C document set traces to the committed files listed below, not to a freshly re-run analysis.
  Where this task re-verifies a claim directly against a file present in this environment (the tablet
  HTML, the shared uploads/ assets, current React source), that is marked `EVIDENCE_BACKED` /
  `RE-VERIFIED_THIS_SESSION` in the relevant document. Where it is not, it is marked `NOT_REVERIFIED`.

## Committed evidence inventory (verified this session)

| Metric | Value |
|---|---|
| Root | `engineering/phase2/wave6-0ab-baseline-analysis/` |
| Total files (recursive) | 93 |
| Origin commit | `0861929` — `docs(phase2): archive Wave 6.0AB baseline analysis` |
| Relationship to current HEAD | `0861929` **is** current HEAD (`08619298ff7b7a175ba4d30537be92e0387b2eb4`) |
| Local modification since commit | **None** — `git status --short` / `git diff --stat` scoped to this path are both empty |
| Full recursive SHA-256 manifest (this session) | `/tmp/mongle-wave6-0c-gate/committed_6_0ab_evidence_manifest.sha256` (93 entries) |

### By subdirectory

| Subdir | File count | Contents |
|---|---|---|
| `6.0A/` | 26 | Phase A (approved-source re-measurement): 10 `.md` deliverables, 8 `_raw_*` CSV/JSON extraction data, 6 named CSVs, 2 SHA-256 manifests (`approved_source_start.sha256`, `approved_source_end.sha256`) |
| `6.0B/` | 15 | Phase B (current-implementation audit): 9 `.md` deliverables, 6 named CSVs |
| `cross-reference/` | 3 | `W6_0AB_EVIDENCE_JOIN.md` + CSV, **`W6_0C_INPUT_PACKAGE.md`** (routing index written specifically for this task) |
| `evidence/` | 22 | Playwright render evidence: 10 screen crops, full-canvas render, 5 diff images, console-error/bounding-box/visual-diff JSON, httpserver log |
| `_gate/` | 10 | Start/End Gate git-status/diff/manifest files from the 0AB session itself |
| `scripts/` | 16 | Python/Node extraction & render scripts (kept for reproducibility, not counted as a deliverable) |
| `final/` | 1 | `MONGLE_W6_0AB_FINAL_REPORT.md` (42-item umbrella report, Verdict: CONDITIONAL) |

### Core deliverables referenced by this Wave 6.0C document set

- Screenshot evidence: `evidence/approved-html-render/` (10 screen crops + full canvas + 5 diff images)
- Source authority: `6.0A/SOURCE_AUTHORITY_MATRIX.md`
- Reproduction scripts: `wave6-0ab-baseline-analysis/scripts/*.py`, `scripts/render.js`
- 12 PM decisions: `6.0B/PM_DECISION_BRIEF_V2.md`
- Umbrella verdict and full item-by-item record: `final/MONGLE_W6_0AB_FINAL_REPORT.md`

## Archive verification performed this session

- File-count check: 93 files recursively confirmed via `find`.
- Integrity check: full recursive SHA-256 manifest generated (`committed_6_0ab_evidence_manifest.sha256`,
  93 entries) and saved to `/tmp/mongle-wave6-0c-gate/`.
- Drift check: `git status --short` / `git diff --stat` scoped to
  `engineering/phase2/wave6-0ab-baseline-analysis/` — both empty, confirming zero local modification
  since the `0861929` commit.
- Approved-source asset overlap check (new this session): 10/10 raster files in
  `docs/temp/design_tablet/uploads/` SHA-256-match the corresponding entries in
  `6.0A/approved_source_file_inventory.csv` (which recorded them from `screen_renew/uploads/`). This is
  the strongest available evidence that `docs/temp/design_tablet/` and the original `screen_renew` share
  at least one common origin, without claiming they are wholesale identical (they are not — see
  `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md`).

## Missing / not reconstructable in this environment

- `/tmp/mongle-wave6-0ab/scripts/*` outputs beyond what was committed (e.g., any intermediate file the
  0AB session did not choose to persist) — cannot be reconstructed; not required, since all listed
  deliverables were persisted.
- The original `standalone-src.html` (10-screen A1-A5 mobile structural source) — not found anywhere in
  this repository or in `docs/temp/design_tablet/`. Its measurements survive only as
  `COMMITTED_DERIVED_EVIDENCE` in `6.0A/MEASUREMENT_TABLE_V2.md` / `HTML_STRUCTURE_EXTRACTION.md`; they
  cannot be re-verified against the original file in this session.

## Verdict for this Gate

**EVIDENCE_PACKAGE_SUBSTITUTE_ACCEPTED** — the committed `engineering/phase2/wave6-0ab-baseline-analysis/`
directory satisfies the completeness bar Section 7/9 requires of an evidence package (see
`MONGLE_W6_APPROVED_SOURCE_DELTA_REGISTER.md` for the itemized required-artifact checklist), with the
explicit caveat that it is derived/committed evidence, not the raw ephemeral package, and that the
original mobile HTML structural source remains unavailable and unreconciled (carried forward as PM
Decision `D13` in `MONGLE_W6_PM_DECISION_REGISTER.md`).
