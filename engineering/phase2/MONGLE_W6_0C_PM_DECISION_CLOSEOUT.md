# MONGLE_W6_0C_PM_DECISION_CLOSEOUT

Task: MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001. Closes the `CONDITIONAL` verdict left open by the preceding
`MONGLE-W6-0C-CANONICAL-FREEZE-001` task (see `MONGLE_W6_0C_FINAL_REPORT.md`, preserved unedited as the
historical preceding record) by recording the PM's final D1-D15 decisions, permanently archiving the
tablet-source evidence, and reconciling every current canonical document to those decisions.

## 1. Task ID

`MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001`

## 2. Preceding verdict

`MONGLE-W6-0C-CANONICAL-FREEZE-001` (commit `0861929`, `MONGLE_W6_0C_FINAL_REPORT.md`) reached
**CONDITIONAL** / `CONDITIONALLY_READY_FOR_MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION`, with 5 blocking PM
decisions open (`D1`, `D4`, `D5`, `D8`, `D13`) and 8 more non-blocking-but-undecided items (`D2`, `D3`,
`D6`, `D7`, `D9`, `D10`, `D11`, `D12`). That document is preserved verbatim — not edited, not renamed,
not deleted — as the historical evidence trail this closeout resolves against.

## 3. PM decisions (source)

The PM's final decisions D1-D15 were issued as the governing input to this closeout task and are recorded
verbatim (status strings and rationale) in `MONGLE_W6_PM_DECISION_REGISTER.md`, section "PM Closeout Final
Resolution (MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, PM 확정)". This document does not re-derive them; it
reconciles the rest of the canonical document set to them.

## 4. D1-D15 final status

| ID | Final status |
|---|---|
| D1 | `PM_RESOLVED` — mobile visual authority = approved PNG, 390×844 reference viewport, no fake chrome |
| D2 | `PM_RESOLVED` — brand accent migration target `#5A35DF` |
| D3 | `PM_RESOLVED` — ink color migration target `#17103A` |
| D4 | `PM_RESOLVED` — font Noto Sans KR + fallback stack; `FONT_DELIVERY_REQUIRED` flag resolved at Wave 6.1 Start Gate |
| D5 | `LOCALIZED_BLOCKER` — missing icon/illustration assets, no fabrication, deferred to `MONGLE-W6-ASSET-SOURCING-001`, does not block Wave 6.1 foundation |
| D6 | `PM_RESOLVED` — Wagle room scope = GROUP only for Wave 6, DIRECT/SERVICE deferred |
| D7 | `PM_RESOLVED_AS_EXISTING_CONTRACT` — desktop/tablet room auto-select preserved as-is |
| D8 | `PM_RESOLVED` — admin sidebar `#FBFAFE`, preserve edit/delete/approve/reject |
| D9 | `RESOLVED_BY_SEQUENCE_ADJUSTMENT` — A1 mobile-only first, no invented tablet layout |
| D10 | `PM_RESOLVED_FOR_VISUAL_CONTRACT` — bottom dock 4 items mapped to `/family`, `/dashboard`, `/wagle`, and `ROUTE_BINDING_DEFERRED` for "나" |
| D11 | `PM_RESOLVED` — historical Naran/Doran docs preserved, not renamed/deleted, not authoritative |
| D12 | `NON_BLOCKING_DEFERRED` — legacy E2E infra deferred to `MONGLE-LEGACY-E2E-INFRA-RECOVERY-001`; current Playwright Mongle suite is the regression baseline |
| D13 | `PM_RESOLVED_BY_SOURCE_ROLE_PARTITION` — 10-screen evidence vs. 71-screen `EXTENDED_MOBILE_STRUCTURE_SOURCE`, no auto-supersession, order = PNG > PM decision > current functional contract |
| D14 | `PM_RESOLVED` — spacing scale 4/8/12/16/20/24/32/40/48/64px global semantic base; `SCREEN_LOCAL_MEASURED_VALUE`/`RESPONSIVE_LAYOUT_VALUE` categories allowed; independent of D4 |
| D15 | `PM_RESOLVED` — tablet nav chrome never removed; portrait dock / landscape rail only if source shows one; missing landscape nav = `SOURCE_PRESENTATION_OMISSION`, not immersive-mode approval |

All 15 items carry a final, non-`PM_DECISION_REQUIRED` status. Full rationale and evidence citations:
`MONGLE_W6_PM_DECISION_REGISTER.md`.

## 5. Source authority

Reconciled in `MONGLE_W6_CANONICAL_SOURCE_FREEZE.md` closeout section. Summary: Tier 1M (approved PNGs)
= mobile visual authority (`D1`); Tier 1T (tablet HTML, SHA `24a02ab6...571d6`) = tablet layout authority,
now permanently archived; Tier 2 (shared style source) token values `PM_RESOLVED` per `D2`/`D3`/`D4`/`D14`;
Tier 3 (mobile HTML structure) still unfilled by the 71-screen file, which is separately classified
`EXTENDED_MOBILE_STRUCTURE_SOURCE` per `D13`'s role partition, never auto-superseding Tier 1M; Tier 4
(current React) functional authority unchanged, constrained by `D15` on nav-removal; Tier 5 (historical)
unchanged, `D11`-confirmed non-authoritative.

## 6. Token decisions

Reconciled in `MONGLE_W6_DESIGN_TOKEN_FREEZE.md` closeout section. Brand `#5A35DF` (`D2`), ink `#17103A`
(`D3`), font Noto Sans KR + `FONT_DELIVERY_REQUIRED` (`D4`), admin sidebar `#FBFAFE` (`D8`), spacing scale
4/8/12/16/20/24/32/40/48/64px global semantic base with `SCREEN_LOCAL_MEASURED_VALUE`/
`RESPONSIVE_LAYOUT_VALUE` allowances (`D14`) — all `PM_RESOLVED` as migration targets. **No CSS file was
edited by this closeout task**; `frontend/**` remains untouched.

## 7. Responsive decisions

Reconciled in `MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md` closeout section. Mobile 390×844, tablet
768×1024 (portrait) / 1024×1366 (landscape), desktop 1440×900 (A5 only) — all reconfirmed. Shared semantic
components / zero DOM-duplication reconfirmed. Portrait-dock / landscape-rail policy and the
`SOURCE_PRESENTATION_OMISSION` classification for A3/A4's chrome-free landscape captures resolved via
`D15`. Nav chrome is never removed. The 480px fixed canvas is not adopted as a real breakpoint. The exact
CSS breakpoint pixel value (item 4) remains open — disclosed as residual scope, not silently closed.

## 8. Component decisions

Reconciled in `MONGLE_W6_COMPONENT_BOUNDARY_FREEZE.md` closeout section. `Avatar`/`IconButton` remain
reusable `SHARED_PRIMITIVE`s. `Button` remains the first-consumer candidate for A3/A5 (built, 0 current
consumers). No global Doran-domain component promotion yet — the promotion trigger (a second real React
consumer) still hasn't occurred, even with `D6`'s GROUP-only scope and the tablet room-list structural
match. A responsive layout wrapper is allowed as new composition. No mobile/tablet functional tree
duplication is authorized. `AdminSidebar`-equivalent settles to `RECOMPOSE` (light rail) per `D8`, with
existing mutation functionality explicitly preserved.

## 9. Asset blockers

`D5` = `LOCALIZED_BLOCKER`, not a global blocker. Scope: A2 hero illustration + A2 service-tile icons
(primary), A3 mission icons (secondary, lower urgency — A3 already ships with legacy emoji debt). No asset
is fabricated by this or any preceding task. Sourcing is delegated to `MONGLE-W6-ASSET-SOURCING-001`. This
does not block Wave 6.1's token/primitive/responsive-layout-foundation stage, which touches no icon or
illustration asset.

## 10. Per-screen readiness

Reconciled in `MONGLE_W6_SCREEN_SPEC_FREEZE.md` closeout section:

- **A1**: `MOBILE_ONLY_FIRST` (top-level, `D9`) — no invented tablet layout; PIN/lock/onboarding
  sub-screens remain tablet-ready where sourced.
- **A2**: `BLOCKED_BY_ASSET` + `BLOCKED_BY_FUNCTION`, unchanged — `D5` `LOCALIZED_BLOCKER`.
- **A3**: `READY_FOR_FIRST_MOBILE_TABLET_PAIR` — promoted from `READY_WITH_PM_DECISION`, confirmed as the
  first mobile+tablet pattern-setting pair.
- **A4**: `VISUAL_READY` + `FUNCTION_BACKEND_DEFERRED` + **GROUP only** (`D6`) — Doran REST remains Wave 7.
- **A5**: `READY_FOR_IMPLEMENTATION` — promoted from `READY_WITH_PM_DECISION`, `D8` closed, bright sidebar,
  existing functionality preserved.

## 11. Implementation sequence

Reconciled in `MONGLE_W6_IMPLEMENTATION_SEQUENCE_FREEZE.md` closeout section. Frozen Stage 0-6: Stage 0 =
this closeout (done); Stage 1 = `MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001` (tokens/primitives only);
Stage 2 = A1 mobile-only; Stage 3 = A3 first mobile+tablet pair; Stage 4 = A5 admin (bright sidebar);
Stage 5 = A4 Wagle GROUP visual-only fixture; Stage 6 = A2 (blocked pending asset/data policy). This
closeout does not execute Stage 1 or later.

## 12. Archive results

Permanent tablet-source archive created at
`engineering/phase2/evidence/mongle-wave6-tablet-canonical/{source,assets,manifests,provenance}/` — 26
files (~15 MB), byte-identical to their `docs/temp/design_tablet/` originals (SHA-256 verified, see
§9/§21 of the companion report). Duplicate copies (`design_handoff_family_platform/screens/*`,
`design_handoff_family_platform/design-system/*`), OS metadata (`.thumbnail`), and download-zone markers
(`:Zone.Identifier`) were excluded with documented rationale in `provenance/PROVENANCE.md`. The previously
undocumented `가족 플랫폼 화면 재현-tokenized.html` was investigated and classified
`PARTIAL_TOKENIZED_DERIVATIVE_OF_71_SCREEN_SOURCE` (not a duplicate, not tablet-related, archived for
provenance completeness, granted no additional source authority beyond `D13`).

## 13. Wave 6.1 start gate

See §16 for the frozen entry conditions and §17/companion report for allowed/forbidden scope. Font
delivery mechanism (`D4`'s `FONT_DELIVERY_REQUIRED` flag) must be measured and resolved as part of that
gate, not assumed resolved by this closeout.

## 14. Deferred tasks

- `MONGLE-W6-ASSET-SOURCING-001` — real icon/illustration assets for A2 (primary) and A3 (secondary),
  per `D5`.
- `MONGLE-LEGACY-E2E-INFRA-RECOVERY-001` — restore `docker-compose.phase0.yml`-backed legacy `specs/`
  suite, per `D12`. Non-blocking; current Playwright Mongle suite (`playwright.mongle.config.ts` +
  `specs-mongle/`) is the regression baseline in the meantime.
- A1 tablet source commissioning (or a further sequence adjustment) — needed before A1 can gain a tablet
  variant; not scheduled by this closeout.

## 15. Residual risk

(a) `D4`'s `FONT_DELIVERY_REQUIRED` flag is real and unresolved — Wave 6.1 must measure an actual font
delivery mechanism (self-hosted files, package, or CDN-with-license-check) before shipping Noto Sans KR,
not assume the design source's CDN `<link>` is production-ready. (b) `D5`'s localized-not-global
reclassification narrows scope but does not solve the underlying asset-sourcing gap — A2 stays blocked
until `MONGLE-W6-ASSET-SOURCING-001` delivers real files. (c) The exact CSS breakpoint pixel value
(Responsive Freeze item 4) remains open; Wave 6.1's own responsive-layout-foundation work must set it
explicitly rather than inherit a guess. (d) The unclassified `19de6297-...png` asset's purpose remains
`UNKNOWN`, archived but not resolved. (e) 11 of 15 tablet-priority screens beyond A2-A5 were never
zone-mapped (carried forward from the preceding task, unchanged by this closeout) — future screen work
outside A1-A5 should expect to repeat that zone-mapping method.

## 16. Closeout verdict

**CONDITIONAL.** All 15 PM decisions (D1-D15) are individually resolved with no item left
`PM_DECISION_REQUIRED`. The tablet-source evidence is permanently archived with SHA-verified integrity and
zero mutation of originals. Every current canonical freeze document was reconciled to the D1-D15 decisions
via minimal, additive closeout sections — the consistency audit (companion report §23) found zero
`CURRENT_DOC_UPDATE_REQUIRED` items outstanding. Wave 6.1 scope is clearly bounded (§13, companion report
§24). Zero product code (`frontend/**`, `backend/**`, `tests/**`, config, lockfiles) was changed by this
task. This corrects an internal-consistency error in the original draft, which labeled this verdict `PASS`
while the companion report (§4, §40) correctly recorded `CONDITIONAL`, driven by two disclosed, bounded
gaps: `D4`'s `FONT_DELIVERY_REQUIRED` flag left open for the Wave 6.1 Start Gate, and the consistency
audit's file/topic-level (not exhaustive line-by-line) classification of high-volume terms. See
`MONGLE_W6_0C_PM_DECISION_CLOSEOUT_REPORT.md` for the full 44-item gate/verdict record.

**CONDITIONALLY_READY_FOR_MONGLE_W6_1_TOKEN_PRIMITIVE_FOUNDATION**
