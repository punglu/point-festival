# QA — MONGLE-W7-3-FULL-NON-CONFLICT-CANONICAL-VISUAL-CLOSEOUT-001

## Status

```
DEVELOPER_SELF_VALIDATION: COMPLETE (6 correction passes)
INDEPENDENT_QA_PENDING: TRUE — no second agent/reviewer has examined this
  work. Do not report this task as independently verified.
```

## Coverage

```
Non-conflict canonical screens: 64 / 64
Visual comparison rows:         192 / 192
```

## Severity Progression

```
Pass 1 (initial audit):      S0 26  S1 74   S2 49  S3 43
Pass 2 (systemic + 6 fix):   S0 35  S1 90   S2 47  S3 20
Pass 3 (S3 elimination):     S0 71  S1 87   S2 34  S3  0
Pass 4 (5 more S2 fixes):    S0 71  S1 87   S2 34  S3  0
Pass 5 (13 IDs, 1 left):     S0 88  S1 101  S2  3  S3  0
Pass 6 (2g visual-authority
  resolution, final):        S0 88  S1 104  S2  0  S3  0
```

**S2 = 0. S3 = 0. PM_DECISION_REQUIRED = 0.**
192/192 (100%) cells are PASS or PASS_RASTER_ONLY.

## Per-Viewport Final Result

```
Mobile:            S0 34 · S1 30 · S2 0 · S3 0
Tablet portrait:   S0 27 · S1 37 · S2 0 · S3 0
Tablet landscape:  S0 27 · S1 37 · S2 0 · S3 0
```

## This Pass's Methodology Note (important)

Before touching any of the 13 previously-flagged screens, each was
re-verified at full resolution first, per instruction not to modify
implementation before re-confirming the finding. This caught **3 false
positives** from earlier thumbnail-scale review:
- `1g` (tablet) — stale finding, already fixed via a shared component,
  never re-verified after that fix.
- `1i` — filter chips were already present and correct in code.
- `2u` — header-contrast claim was wrong; `getComputedStyle` showed the
  correct color. (Real defects on this screen — missing badge, missing
  info rows, missing footer buttons — were genuine and got fixed.)

`3j` was reclassified from a hypothesized "capture-state artifact" to its
true cause: the same un-rebuilt generic-placeholder-template defect found
in 6 other screens in an earlier pass.

`1p` and `2h` were confirmed as genuine presentation/theme differences
(not misjudgments) and corrected to match source, since they were pure
chrome/theme differences with no information-architecture change.

`2g` was initially (Pass 5) confirmed as a genuine information-architecture
difference and flagged `PM_DECISION_REQUIRED` rather than arbitrarily
decided. **Pass 6 revisited that conclusion against the primary sources**
(`MONGLE_W7_FULL_SCREEN_AUTHORITY_MATRIX.csv`,
`MONGLE_W7_SCREEN_OWNERSHIP_MATRIX.csv`, both authority HTML files directly
— not the tokenized rendering) per the instruction not to trust an
existing `PM_DECISION_REQUIRED` record without re-checking: the visual
authority was unambiguous (mobile + tablet wrappers show the identical
in-thread overlay composition, no conflict), and the Ownership Matrix
already had `PM_DECISION_REQUIRED=NO` for 2g's product-integration
question. The prior flag had conflated "this needs more implementation
work than a styling tweak" with "the visual target is unclear" — only the
former was true. Rebuilt to match source; closed at S1 all 3 viewports.
See Report §10 (Revision 5) for full detail.

## Corrections Applied (40 screens total across the full task, 117 files)

See Report §8 for the per-screen table of Pass 5's 12 corrections
(1s, 1u, 1w, 2j, 2k, 3c, 1p, 2h, 2u, 3j — full rebuilds/targeted fixes)
plus 2 confirmed-false-positive corrections requiring no code change
(1g-tablet, 1i). Pass 6 added one more: `2g` (`ChatReplyPreview/index.tsx`
+ `.module.css`, full rebuild — see Report §10 Revision 5).

## Scope Violations Check

```
Product Route creation: 0     App.tsx changes: 0
Navigation wiring: 0          package.json/lockfile changes: 0
API/Backend wiring: 0         New top-level directories: 0
Shared component extraction: 0
```

117 modified files, all under `frontend/src/pages/**` or
`frontend/src/screens/**`, all pre-existing tracked files.

## Lint / Build / Diff-check

```
npm run lint    → PASS, every run across all 6 passes
npm run build   → PASS, every run across all 6 passes
git diff --check → clean
```

## Runtime Regression (re-verified after every pass, 6× full recapture)

```
Detached DOM render:        63 / 63 PASS
Canonical marker exactly 1: 192 / 192 PASS (0 mismatches, all 6 passes)
Detached /api/* requests:   0
Detached console errors:    0
Detached page errors:       0
/login regression:          PASS
```

**Marker-count clarification** (flagged by the continuation prompt as
worth documenting precisely): the canonical-marker *identity space* is
**64** — one `data-canonical-screen-id` per canonical screen. "192/192"
above means 192 independent capture-verifications each confirmed exactly
one matching marker, not that 192 distinct markers exist.

## Evidence Durability Checkpoint (updated after r5 final recapture)

`findings.jsonl` and `canonical-manifest.json` — the two artifacts that
exist **exclusively** in the ephemeral `/tmp/mongle-w7-3-visual-closeout/`
working directory — are on Drive in two checkpoint folders (both under
shared root `0AER2l-A3LpkxUk9PVA`):

```
W7.3-checkpoint (1PU5eaUPcZYRI_nvyuqasU2sfuINMALnk)
  findings.jsonl            → 14pmkkgTUyEppcTH6RdaDgqIeMzMps2zl
  canonical-manifest.json   → 1EeLbd_Hh_Y3K_jepaFns5zSJZ7AwtbKC

W7.3-checkpoint-final-r5 (1_K1xKfQjCO2aC1qmKoygM97aQysjnjUj)
  findings.jsonl (post-r5)  → 1vk8g6_whCg-ZVCHjW5mg_-qlqZkmjAhw
```

The Matrix CSV and Evidence Manifest CSV were **committed to git instead
of duplicated to Drive** (commit `6f414fe`, this repo,
`engineering/phase2/MONGLE_W7_3_CANONICAL_VISUAL_MATRIX.csv` +
`MONGLE_W7_3_VISUAL_EVIDENCE_MANIFEST.csv`) — a user decision made after
an attempted verbatim Drive upload showed the ~154KB combined text would
cost on the order of 300-400K tokens to transcribe through the assistant
(the Drive tool takes inline text content, not a file-path reference, so
every byte must pass through the model twice: once to read, once to
re-emit in the upload call). Git commit achieves the same durability
goal — versioned, outside `/tmp`, safe against session loss — at
negligible cost. Both CSVs were verified byte-consistent with
`findings.jsonl` immediately before commit (0 severity mismatches across
192 rows; 0 stale/missing SHA256 hashes against the current PNG set).

**Not uploaded/committed:** the 643 evidence PNGs (~73MB) — still judged
out of scope for a mid-task checkpoint; cheaply regenerable from current
code + unchanged authority sources.

## Post-checkpoint Recapture Confirmation (r5)

```
impl-capture-r5.log:      192 entries, OK=192, Problems=0
build-comparisons.mjs:    re-run, 192/192 OK
Regression (r5):          consoleErr=0 pageErr=0 apiReq=0 markerMismatch=0
reference-capture-log:    6 non-OK, all pre-documented tablet-mockup
                           fallbacks (1a/1a-1/1f) — not new issues
Matrix CSV vs findings:   0 mismatches across 192 rows (cross-checked)
Manifest CSV vs disk:     0 stale hashes, 0 missing files (recomputed)
S2 count at this point:   3 cells, all id=2g, PM_DECISION_REQUIRED
```

## Pass 6: `2g` Resolution and Final 192-cell Recapture

```
ChatReplyPreview rebuilt: index.tsx + .module.css (Screen-local only)
2g-only capture (exact methodology script, filtered): markerCount=1,
  consoleErrorCount=0, pageErrorCount=0, apiRequestCount=0, all 3 vp
  (an initial ad-hoc recapture script had shown apiRequestCount=5 via a
  looser URL substring match — re-run with the actual capture-
  implementations.mjs logic, which matches only pathname.startsWith
  ('/api/'), confirmed 0; the 5 was a false positive from the ad-hoc
  script, not a real regression)
Full 192-cell recapture (final, current code): 192 entries, OK=192,
  Problems=0
build-comparisons.mjs:    re-run, 192/192 OK
Matrix CSV vs findings:   0 mismatches across 192 rows (recomputed)
Manifest CSV vs disk:     0 stale hashes, 0 missing files (recomputed;
  one incidental stale hash found on 1e/mobile — a previously-untouched
  screen, non-deterministic capture jitter with diffRatio unchanged from
  baseline, not a code regression — hash refreshed to match)
Final severity:           S0=88 S1=104 S2=0 S3=0, PM_DECISION_REQUIRED=0
lint / build:             clean (final run)
git scope:                0 modified files outside frontend/src/**
```

## Known Methodology Gaps (disclosed)

1. Tablet-landscape findings for screens not individually corrected this
   task were bulk-inherited from tablet-portrait after an early
   spot-check validated strong correlation. Every screen actually
   corrected across all 6 passes (including `2g`) was independently
   re-captured and re-verified at all 3 viewports.
2. A residual sweep of other `frontend/src/screens/**` files for the same
   bare-CSS-selector leak pattern (beyond the files already touched for
   content fixes) was not performed — disclosed as a follow-up risk.
3. Full Drive evidence sync (192×4 images) and readback — not performed;
   not required for this visual-baseline PASS (see Report §21).
4. Independent QA — not performed.

## Verdict

```
MONGLE_W7_3_FULL_NON_CONFLICT_CANONICAL_VISUAL_CLOSEOUT_PASS
S0=88  S1=104  S2=0  S3=0  PM_DECISION_REQUIRED=0  SOURCE_CONFLICT=0
```

All 192 cells are `S0`/`PASS` or `S1`/`PASS_RASTER_ONLY`. The final open
item (`2g`) was closed by re-reading the primary authority sources rather
than trusting the existing `PM_DECISION_REQUIRED` record — see Report §10
(Revision 5). `INDEPENDENT_QA_PENDING` remains `TRUE`; this PASS is
developer-self-validated only.
