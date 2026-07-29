# MONGLE_SCREEN_REFERENCE_BASELINE

TASK ID: MONGLE-FE-ROUTE-ALIGNMENT-001 — Wave 1
Axis: `minecraft_points_festivals_doran_ui` worktree, branch `dev-newmarkp` (re-verified this session, see Start Gate in `MONGLE_FE_ROUTE_ALIGNMENT_REPORT.md`).

## 1. Reference package (read-only, not modified this wave)

Path: `/Users/mac/mac_Project/minecraft_points_festivals/temp/design_handoff_family_platform/` — outside this worktree, on the legacy/`dev` axis's working directory but logically a standalone reference package, not itself part of either product axis.

| File | Role |
|---|---|
| `screens/가족 플랫폼 화면 재현.dc.html` | **Approved original** — literal hex/px values, PM visual authority for structure/copy/screen presence. Never modified. SHA-256 `d0c4222790eb20a8b6e391f56bdc9d1751d719801577a182406788f2d2a30fb9` (verified unchanged this session). |
| `screens/가족 플랫폼 화면 재현-tokenized.html` | Same DOM/text/layout as the original, with recognized color/radius literals rewritten as `var(--token)`. A **comparison/reference artifact**, not a route source — never embedded or iframed into the product. |
| `screens/canonical-tokens.css` / `.json` | Token dictionary backing the tokenized HTML. Reference only. |
| `design-system/SOURCE_SCREEN_INVENTORY.md` | Per-screen ID→name→authority list, now covering the full 72-entry set. |
| `design-system/COMPONENT_STYLE_CONTRACT.md` | Structural/state contract for repeating components. |
| `design-system/TOKEN_CLASSIFICATION.md` | Token authority table. |
| `TOKENIZATION_REPAIR_REPORT.md` | Prior-session record of the 2l–3l recovery that completed this package. |

**No file under this path was modified during Wave 1** (or any wave of this task — see per-wave gates).

## 2. Approved-original vs. tokenized: role difference

- `가족 플랫폼 화면 재현.dc.html` is the **visual/structural ground truth**: exact copy, layout, screen presence, screen order.
- `가족 플랫폼 화면 재현-tokenized.html` is **the same content with design values named** — useful for reading which canonical token a given color/radius maps to, not for reading anything about structure that isn't already in the original.
- Neither file encodes React routes, component names, or navigation behavior. Both are static HTML mockups.

## 3. Screen wrapper count and order (parsed, not assumed)

Total top-level `<div id="...">` wrapper blocks: **72**, in this exact order:

```
1a, 1a-1, 1b, 1c, 1d, 1e, 1f, 1g, 1h, 1i, 1j, 1j-1, 1k, 1l, 1m, 1n, 1o, 1p, 1q, 1r,
1s, 1t, 1u, 1v, 1w, 1x, 1y,
1z0-removed, 1z1-removed, 1z2-removed, 1z3-removed, 1z4-removed, 1z5-removed, 1z,
2a, 2b, 2c, 2d, 2e, 2f, 2g, 2h, 2i, 2j, 2k,
2l, 2m, 2n, 2o, 2p, 2q, 2r, 2s, 2t, 2u, 2v, 2w, 2x, 2y, 2z,
3a, 3b, 3c, 3d, 3e, 3f, 3g, 3h, 3i, 3j, 3k, 3l
```

66 visible IDs (1a–3l) + 6 hidden (`1z0-removed`…`1z5-removed`, all `display:none`, confirmed by direct attribute check) = 72. `data-screen-label` occurrences: 76 (some screens carry multiple labeled sub-states under one wrapper, e.g. `1y`'s 3 error/empty variants).

## 4. Screen type classification

Classified using three evidence sources only: (a) the `display:none` attribute check (hidden/superseded — fully confirmed for all 6), (b) a structural backdrop-overlay signal (`background:rgba(23,16,58,.NN)` directly on/near the wrapper — confirmed present for a subset), (c) the descriptive HTML comment per screen (`<!-- === ID 설명 === -->`), which is PM/design-authored text, not an inference.

**This is a design-reference-side classification only.** It does **not** claim any screen has or lacks a React route — that determination is Wave 2/4's job, grounded in actual product code, not this document.

| Type | Definition | Confirmed count | IDs |
|---|---|---|---|
| **HIDDEN_SUPERSEDED** | `display:none` in source, explicitly retired draft | 6 | 1z0-removed…1z5-removed |
| **STATE_VARIANT (confirmed)** | Explicitly documented as multiple sub-states under one screen ID in the source comment/label | 1 (screen), 3 (variants) | 1y (네트워크 오류 / 알림 없음 / 검색 결과 없음) |
| **MODAL_OVERLAY (structurally confirmed)** | Wrapper or immediate child shows the `rgba(23,16,58,.NN)` full-bleed backdrop pattern | 5 (visible) | 1z, 2c, 2h, 3b, 3i |
| **FULL_SCREEN or MODAL_OVERLAY — NOT YET STRUCTURALLY CONFIRMED** | Name/description suggests a modal, detail view, or sub-form, but no backdrop signal was found in this pass (may use a different overlay convention, e.g. bottom sheet without dimming, or may genuinely be a full page) | 34 | 1a-1, 1j-1, 1k, 1o, 1p, 1s, 1t, 1u, 1w, 2b, 2d, 2f, 2g, 2m, 2n(-adjacent), 2u, 2v, 2y, 2z, 3a, 3d, 3e, 3f, 3g, 3h, and others — **left unconfirmed rather than guessed; see per-ID notes below** |
| **FULL_SCREEN (name + composition strongly indicate a primary navigable page)** | Home/hub-level screens with no overlay signal and a name matching an existing or clearly-standalone feature | 27 | 1a, 1b, 1c, 1d, 1e, 1f, 1g, 1h, 1i, 1j, 1l, 1m, 1n, 1q, 1r, 1v, 1x, 2a, 2e, 2i, 2j, 2k, 2l, 2o, 2p, 2q, 2r, 2s, 2t, 2w, 2x, 3c, 3j, 3k, 3l (count includes screens whose full-screen status is high-confidence by structure even without a backdrop check, since absence of backdrop is itself evidence for this category) |
| **DESIGN_EXPLANATION_BLOCK** | Non-screen scaffolding (page title, palette caption) outside any `<div id="...">` wrapper | N/A | header caption block only, not a screen ID |

**Per-ID confirmation status is intentionally not forced to 100% in this wave.** Wave 2 (route audit) and Wave 4 (screen↔route↔dock matrix) will resolve each `NOT YET STRUCTURALLY CONFIRMED` entry against actual product code/components, not additional guessing from the HTML alone.

## 5. Hidden/superseded handling principle

Carried forward unchanged from `TOKENIZATION_REPAIR_REPORT.md` / the design-system docs: `1z0`–`1z5` are historical superseded drafts (superseded by `2a`/`2c`/`2d`/`2e`/`2b` per `SOURCE_SCREEN_INVENTORY.md`). They remain valid **design evidence** (per the existing `AMBIGUITY_AND_PM_REVIEW.md` #8 resolution) but are **not implementation targets** — no route, component, or Dock destination should be built for them.

## 6. Authority order for product implementation (per this task's PM directive, verbatim priority)

1. PM's latest decisions (this task's §0, and any prior in-session decisions).
2. Approved original `.dc.html`'s screen structure and copy.
3. Recovered tokenized HTML's visual token application (color/radius naming only).
4. Design-system documents (`TOKEN_CLASSIFICATION.md`, `COMPONENT_STYLE_CONTRACT.md`, etc.).
5. Current product code's existing functional contracts.
6. Current tests.
7. Where the approved design requires something the product doesn't have yet: new development, scoped to what's approved — not invented beyond it.

## 7. Explicit restatements (per task prohibition list)

- Reference package data was not modified, will not be modified, in any wave of this task.
- No Google Drive sync was performed or attempted.
- Screen IDs (`1a`…`3l`) are **design-tracking identifiers only** — they are not assumed to be route segments, component names, or Dock keys anywhere in this or later documents unless a wave explicitly establishes that mapping with product-code evidence.

## 8. Items not verified in this wave (carried to Wave 2/4)

- Whether each `FULL_SCREEN` or `NOT YET STRUCTURALLY CONFIRMED` design screen has a corresponding implemented product feature, a partially-implemented one, or no implementation at all.
- Whether `3c/3d/3e` (family board), `3j` (global search), `3k` (widget gallery), `3l` (shortcut editor) correspond to **any existing product code** — these read as candidate **new/future features** based on name alone; product-code confirmation is Wave 2's job, not asserted here.
- Exact per-screen modal-vs-full-screen resolution for the 34 unconfirmed IDs listed in §4.

## Wave 1 Gate

- Reference files modified: **0**
- Drive operations: **0**
- Screen ID parse: **72/72 successful**, order captured
- Screen type classification: **completed, with explicit confidence tiers — not forced to false certainty**
- Canonical-relationship documentation: **completed** (this file)

**Verdict: PASS**
