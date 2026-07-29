# Stale Analysis Register

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 14)

Classification taxonomy: `CURRENT_AND_USABLE / USABLE_WITH_SUPPLEMENT / STALE_ROUTE / STALE_NAMESPACE /
STALE_IMPLEMENTATION / HISTORICAL_ONLY / CONFLICTING / UNKNOWN`. None of the documents below were
modified.

## Group 1 — `_analysis/wave6_0-analysis/` (inside the approved-source folder, 10 `.md` + 6 `.png` + 1 `.sha256`)

| Document | Classification | Note |
|---|---|---|
| `SCREEN_INVENTORY.md`, `MEASUREMENT_TABLE.md`, `COMPONENT_CATALOG.md`, `TOKEN_PROPOSAL.md`, `GAP_MATRIX.md`, `SCREEN_ASSEMBLY_PLAN.md`, `SCREEN_FLOW.md`, `WAVE_PLAN.md`, `PROGRESS.md`, `FINAL_REPORT.md` | `HISTORICAL_ONLY` / `USABLE_WITH_SUPPLEMENT` | Prior session's own first-pass analysis of the identical `standalone-src.html`/PNGs. Not re-derived route/namespace claims (this earlier pass predates this task and is silent on Mongle/route topics, so `STALE_ROUTE`/`STALE_NAMESPACE` do not apply — it simply never made those claims). Where its measurements were spot-checked against this session's independent extraction (e.g. screen count, mission-icon-vs-emoji delta) they were **consistent**, so it is usable as corroboration, never as a substitute for this task's own fresh measurement. |
| `approved-assets.sha256` | `HISTORICAL_ONLY` | A prior, narrower SHA manifest (subset of assets, not the full tree). Not cross-diffed against this task's `approved_source_start.sha256` — out of scope to validate someone else's manifest; noted only as existing. |
| `sg_crop_*.png` (6 files) | `HISTORICAL_ONLY` | Prior session's own cropped screenshots of the style-guide PNG. Not new design content, not used as a measurement source here. |

## Group 2 — `_analysis/wave6_1a-source/` (inside the approved-source folder, 10 `.md`)

| Document | Classification | Note |
|---|---|---|
| `TIER1_VISUAL_DELTA.md` | `USABLE_WITH_SUPPLEMENT` | Contains a genuinely valuable qualitative HTML-vs-PNG walkthrough (real-photo-vs-initials avatars, emoji-vs-real-icon findings, the pin-logo-in-ChatHeader Tier-1-internal conflict). **Every claim from it that is repeated in this task's `TIER1_HTML_VISUAL_DELTA.md` was independently re-verified this session** by directly opening the relevant approved PNG again — it was not trusted blindly. Classified `DERIVED_REFERENCE` in the Source Authority Matrix, cited as corroboration only. |
| `HTML_SCREEN_STRUCTURE.md`, `COMPONENT_EXTRACTION.md`, `INLINE_LITERAL_INVENTORY.md`, `TOKEN_MAPPING.md`, `TYPOGRAPHY_MAPPING.md`, `HTML_TO_REACT_RULES.md`, `SOURCE_DRIVEN_IMPLEMENTATION_SEQUENCE.md`, `A1_SOURCE_TO_COMPONENT_SPEC.md`, `START_GATE.md`, `PROGRESS.md`, `FINAL_REPORT.md` | `HISTORICAL_ONLY` | Same treatment — a prior, independent extraction pass over the same primary source. Not re-read line-by-line for this task (effort budget), but not contradicted by anything found in this session's own fresh extraction either, where spot-checked. |

## Group 3 — Documents found in the *current repository* (`minecraft_points_festivals_doran_ui`) that bear directly on this task's freshness question (not inside the approved-source folder; found during Phase B code reading, reported here because Section 14 explicitly asks for freshness relative to "현재 저장소")

| Document | Path | Classification | Note |
|---|---|---|---|
| `FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md` | `engineering/phase2/FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md` | `STALE_NAMESPACE` (self-declared even at authoring time) | A **prior, separate canonical design-integration document** (dated 2026-07-26, i.e. before this task), which already fed real code: `global.css`'s `--color-brand-*`/`--color-ink-*`/`--space-*`/`--radius-*` block is annotated "PM contract normative values… §5" citing this exact document, and `MongleAppShell.tsx`/`DoranLanding.tsx`/`ChatComposer.tsx`/`ChatHeader.tsx`/`UnreadDivider.module.css` all carry inline comments referencing a "Wave 6.0B §…" numbering scheme not otherwise documented as a handoff/progress file anywhere in this repository's own `agent-system/`/`engineering/` tree (`grep`-verified — zero hits for `wave6`/`W6` filenames under this repo besides this one document and 3 unrelated `MONGLE_*` reports that only mention "wave6" in passing text). This document **uses the pre-rename names "나란"(platform)/"도란"(chat)/"마크포인트"(points)** throughout, explicitly self-flagging its own `PRODUCT_DECISION_STALENESS`/`TERMINOLOGY_STALENESS` in its §3 Conflict Register — i.e. it predates and is superseded by the later Mongle namespace migration referenced in this task's baseline context. It also references a **higher-priority "PM component contract"** stored in Google Drive (`family_platform_component_contract_v1.md`, two IDs cited, confirmed `EQUIVALENT_COPIES` by the document's own author) that is **outside this task's approved-source scope** (`/temp/screen_renew`) and was **not fetched** in this session — fetching an external Drive document was judged out of scope for a task whose Context section explicitly names only the local `screen_renew` folder as the approved source; its existence is reported here for PM awareness, not acted on. |
| Code comments citing "Wave 6.0B §…" (7 files: `MongleAppShell.tsx`/`.module.css`, `ChatComposer.tsx`/`.module.css`, `UnreadDivider.module.css`, `ChatHeader.module.css`, `DoranLanding.module.css`) | various, see grep below | `USABLE_WITH_SUPPLEMENT` | These comments show that **some** of this task's exact subject matter (A2 Home Dock icon+label treatment, A4 chat components) already received a prior implementation pass referencing this same design source, under a numbering ("Wave 6.0B") this task cannot fully trace to a stored document. One explicit, still-open decision surfaced directly in code: `MongleAppShell.tsx` lines 133-142 record `ASSET_GAP_BOTTOM_DOCK_ICONS` and `PM_DECISION_REQUIRED_BOTTOM_DOCK_ROUTE` as the reasons the Dock could not be fully re-skinned to the approved icon+label pattern — this is carried into `PM_DECISION_BRIEF_V2.md` verbatim rather than re-litigated. |

Grep evidence for the "Wave 6.0B" claim (reproducible):
```
grep -rln "Wave 6.0\|WAVE_6\|MONGLE-W6\|ASSET_GAP\|PM_DECISION_REQUIRED" frontend/src
→ platform/shell/MongleAppShell.tsx, .module.css; platform/doran/components/ChatComposer/{.tsx,.module.css};
  platform/doran/components/UnreadDivider/.module.css; platform/doran/components/ChatHeader/.module.css;
  platform/doran/preview/types.ts; platform/pages/DoranLanding.module.css
```

## Net conclusion for Phase A freshness

This Wave's approved-source folder (`screen_renew`) is the correct, current input for A1-A5 design
measurement — no staleness in the *design content itself* was found (it is a single static HTML/PNG
snapshot with no version history to be stale relative to). The staleness that *does* exist is entirely
on the **current-implementation side**: a prior design-integration document already exists, already
partially informed real code, already uses the pre-Mongle-rename product names, and already left at
least one explicit unresolved PM decision in the code. None of this changes any Phase A measurement in
this package; it is carried forward into Phase B and the PM Decision Brief so the next Wave does not
re-litigate ground already covered, nor mistake the older document's stale naming for current fact.
