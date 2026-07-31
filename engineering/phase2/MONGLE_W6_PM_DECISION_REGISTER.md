# MONGLE_W6_PM_DECISION_REGISTER

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 19. Migrates D1-D12 from `6.0B/PM_DECISION_BRIEF_V2.md`
(none auto-resolved), adds `D13` (new this session). No item below was resolved by this task.

| ID | Topic | Status (this session) | New tablet-source evidence | Blocking? |
|---|---|---|---|---|
| D1 | Mobile HTML canvas aspect ratio vs. approved PNG aspect ratio | `PM_DECISION_REQUIRED`, unchanged | None — this session's tablet-source work does not bear on mobile aspect ratio; tablet canvases (1024×700, 768×1024) are their own presentation frames, not evidence toward D1 | **BLOCKING** (cross-cutting, affects every mobile screen's proportions) |
| D2 | Brand accent near-miss (`#5A35DF` approved vs. `#5835DF` current) | `PM_DECISION_REQUIRED`, **evidence strengthened** | Tablet `canonical-tokens.css` uses `#5A35DF` — a second independent source agreeing with the approved PNG against current code | NON_BLOCKING (low risk, 1 token) but should be decided before any token-finalization task |
| D3 | Ink/text-primary near-miss (`#17103A` approved vs. `#171D3A` current) | `PM_DECISION_REQUIRED`, **evidence strengthened** | Tablet `--color-text-primary: #17103A` — second independent source agreement | NON_BLOCKING but affects nearly every text element once decided |
| D4 | Font family (`Noto Sans KR` approved vs. `Pretendard` current) | `PM_DECISION_REQUIRED`, **evidence strengthened, not resolved** | Tablet `--font-family-base: 'Noto Sans KR'` — second independent source agreement. Per Section 15's own explicit instruction, this corroboration does **not** authorize auto-adoption | **BLOCKING before any typography token work** (cross-cutting) |
| D5 | Icon/illustration asset gap (Home-hero illustration, service-tile/mission icons) | `PM_DECISION_REQUIRED`, **re-confirmed unsolved by the tablet delivery** | Tablet A2/A3 use the **same emoji workaround**, not real assets — see `MONGLE_W6_ASSET_POLICY_FREEZE.md` "D5 status update" | **BLOCKING for A2 visual work specifically**; A3 has legacy emoji debt so lower urgency there |
| D6 | Room List / DIRECT / SERVICE scope for A4 (current fixture has 3 kinds, approved mobile PNG shows only 1 GROUP room) | `PM_DECISION_REQUIRED`, **new evidence, still not resolved** | Tablet `1d` landscape **does** show a room-list pane (280px sidebar), but with only 1 room, GROUP-kind — consistent with the *narrow* option (A) in the original brief, not proof of the *current fixture's* wider 3-kind scope. This is evidence the room-list **layout concept** is tablet-approved; it is not evidence that DIRECT/SERVICE kinds are approved. | NON_BLOCKING for the room-list *layout* (can proceed); BLOCKING for the 3-kind *scope* question specifically |
| D7 | Desktop Room auto-selection behavior (`≥701px`, code comment claims "§3 PM 정책") | `PM_DECISION_REQUIRED`, **new evidence, still not resolved** | Direct code re-read this session (Functional Deep Audit §E) confirms the exact behavior in more detail than 6.0B had: fires exactly once, gated on `pageState==='normal'`, does not re-fire after manual back-navigation. This does not confirm the claimed PM provenance — it confirms the behavior is deliberate and specific, which raises (does not lower) the cost of guessing wrong | NON_BLOCKING in the sense that current behavior can be left alone; BLOCKING if anyone wants to change it without confirming the provenance claim first |
| D8 | Admin sidebar tone (dark `#1e1b4b` current vs. near-white `#FBFAFE` approved) | `PM_DECISION_REQUIRED`, **evidence strengthened to 2 independent sources** | Tablet `1e` landscape rail directly re-measured this session: `background:#FBFAFE`, matching the approved PNG exactly, against current code's dark value | **BLOCKING for A5 sidebar specifically** before Wave 6.1 A5 kickoff, per the original brief's own scoping |
| D9 | A1-S1 (순수 ID/PW 로그인) — no current implementation, no dedicated approved PNG | `PM_DECISION_REQUIRED`, unchanged | Tablet `1a-1` also has **no tablet variant** (confirmed this session) — the sub-screen remains completely unevidenced in any responsive form | NON_BLOCKING (isolated screen), but now doubly unevidenced |
| D10 | Bottom Dock 4th/5th destinations (개별-tab access to 가족일정/앨범/할일) | `PM_DECISION_REQUIRED`, unchanged | Tablet portrait BottomDocks read this session (A2/A3/A4) all show exactly **4 items** (홈/잔치/대화/나) — consistent with Option B (no persistent Dock destination beyond the existing 4), corroborating but not deciding the brief's own lean | NON_BLOCKING, lean B further supported |
| D11 | `FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md` supersession | `PM_DECISION_REQUIRED`, unchanged | None new this session | NON_BLOCKING (documentation hygiene) but affects traceability, and now there are **two** stale/parallel documents to reconcile (this one and the `D13` mobile-HTML question below) |
| D12 | `docker-compose.phase0.yml` missing, legacy `specs/` unrunnable | `PM_DECISION_REQUIRED`, unchanged | This session independently re-read all 4 legacy spec files (Functional Deep Audit §C) — confirms they are infra-blocked, not content-stale; strengthens the case for **restoring** the phase0 stack (Option A) over retiring the suite, since the assertions themselves remain relevant | MEDIUM (blocks regression coverage for A1/A3/A5's legacy routes) |
| **D13** | **NEW.** `docs/temp/design_tablet/`'s mobile 71-screen HTML (`가족 플랫폼 화면 재현.dc.html`, 636,567B, SHA `d0c42227...`) shares the exact display name with, but is **not the same file as**, the 10-screen `standalone-src.html` (153,869B, SHA `5f823d4c...`) that 6.0A actually measured for A1-A5 | **`PM_DECISION_REQUIRED`, new** | Full finding in `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md` "Mobile HTML source conflict". Two explanations equally consistent with available evidence: (1) the 71-screen file is a later, more complete pass superseding `standalone-src.html`; (2) the two are independent deliverables sharing only a brand-asset folder. **Options**: (A) treat the 71-screen file as the new Tier 3/structural-reference source going forward, re-deriving any needed A1-A5 structural detail from it instead of the unreachable `standalone-src.html`; (B) treat `standalone-src.html`'s 6.0A measurements as still authoritative and the 71-screen file as unranked reference only (this document set's current default, conservative choice) | **BLOCKING** for any future task that needs new pixel-level A1-A5 mobile measurements beyond what 6.0A already recorded — not blocking for this task's own tablet-focused conclusions, which never depended on the 71-screen file's structural authority |

## Spacing-scale note (not opened as a separate decision)

`MONGLE_W6_DESIGN_TOKEN_FREEZE.md` found a 3-way spacing-scale mismatch (approved odd-number literals vs.
current code's 4px-ladder vs. tablet source's own distinct 10-step scale). Recommended to fold into the
`D4` typography/token conversation rather than open a `D14`, since no screen is currently blocked on it —
flagged here so it is not silently lost, but not given a separate ID per this session's own judgment call
(reviewable by the PM; can be split out later if it turns out to matter sooner than expected).

## Reclassification summary (Section 19 required categories)

| Status | Items |
|---|---|
| `PM_RESOLVED` | none |
| `RESOLVED_BY_NEW_TABLET_SOURCE` | none — every item with new tablet evidence is *strengthened*, not resolved (Section 15's explicit rule) |
| `RESOLVED_BY_CURRENT_CODE` | none |
| `RECOMMENDATION_READY` | D2, D3 (lean B, low risk); D10 (lean B, further corroborated); D12 (lean toward restoring phase0 stack) |
| `PM_DECISION_REQUIRED` | D1, D4, D5, D6, D7, D8, D9, D11, D13 (all) |
| `BLOCKING` | D1, D4 (cross-cutting); D5 (A2 specifically); D8 (A5 specifically); D13 (any future mobile pixel-measurement work) |
| `NON_BLOCKING` | D2, D3, D6 (layout portion), D7, D9, D10, D11, D12 |
| `DEFERRED` | none newly deferred this session |

## Recommended resolution order for whatever task consumes this register next (non-binding, mirrors the
original brief's own framing)

D4 and D1 first (cross-cutting, now with added-but-not-decisive evidence for D4); then D13 (determines
what mobile source future measurement work should even use); then D5 (blocks A2 outright); then D2/D3
(low risk); then the screen-specific items D6/D7 (A4) and D8 (A5, now with stronger evidence); D9/D10/D11/D12
remain lowest urgency.

---

## PM Closeout Final Resolution (MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, PM 확정)

**Everything above this line is the historical record of the D1-D13 open-question state as of the
preceding `MONGLE-W6-0C-CANONICAL-FREEZE-001` task — preserved verbatim, not edited.** The PM has since
reviewed that register and issued the final decisions below, which supersede the "PM_DECISION_REQUIRED"
status shown above for every item they cover. D14 and D15 are new items, not present in the table above
(spacing scale and tablet nav-chrome policy, respectively — both raised as open questions in
`MONGLE_W6_DESIGN_TOKEN_FREEZE.md` and `MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md` but not previously
opened as their own numbered decision).

| ID | Final status | PM decision | Reconciles register topic |
|---|---|---|---|
| D1 | `PM_RESOLVED` | Mobile visual authority = the approved PNG, at a **390×844 reference viewport**. No fake chrome (status bar/home-indicator/phone frame) carried into product UI. Where the mobile HTML source's own canvas aspect ratio disagrees with the PNG, the PNG wins. | Settles the original D1 (mobile canvas vs. PNG aspect ratio) by fiat: PNG is final for proportions. |
| D2 | `PM_RESOLVED` | Brand accent migration target = **`#5A35DF`** (matches approved PNG + tablet `canonical-tokens.css`, both independent of current code's `#5835DF`). No CSS edit performed by this closeout — value is a target for Wave 6.1 token work. | Unchanged topic, now decided (Option B). |
| D3 | `PM_RESOLVED` | Ink/text-primary migration target = **`#17103A`** (matches approved PNG + tablet source, against current code's `#171D3A`). No CSS edit performed by this closeout. | Unchanged topic, now decided (Option B). |
| D4 | `PM_RESOLVED` | Font family target = **Noto Sans KR**, with a defined fallback stack (`'Noto Sans KR', system-ui, sans-serif`, matching the tablet `canonical-tokens.css` value), replacing current code's `Pretendard`. **`FONT_DELIVERY_REQUIRED`** flag raised — no font-file/CDN-license delivery mechanism was found in this repo (only a Google Fonts CDN `<link>` inside the static HTML design sources, not a project dependency or self-hosted asset). This flag is **not resolved here**; it is resolved at the **Wave 6.1 Start Gate**, not by this closeout. No CSS edit performed now. | Unchanged topic, now decided in principle, with an explicit follow-up gate. |
| D5 | `LOCALIZED_BLOCKER` | Missing icon/illustration assets (A2 hero illustration, A2 service-tile icons, A3 mission icons — all currently emoji placeholders in both mobile and tablet sources) are **not fabricated** by any task in this chain. Sourcing is delegated to a dedicated follow-up: **`MONGLE-W6-ASSET-SOURCING-001`**. This is a **localized** blocker (A2 primarily, A3 secondarily) — it does **not** block the Wave 6.1 token/primitive foundation stage. | Unchanged topic — re-confirmed unsolved, explicitly scoped down from "global blocker" to "localized to A2/A3" per Review 1 requirement. |
| D6 | `PM_RESOLVED` | Wagle (`/wagle`) room scope for Wave 6 = **GROUP only**. DIRECT and SERVICE room kinds are **deferred**, not built as visual/functional scope in this wave, even though the current fixture (`DoranLanding.tsx`) technically supports all 3 kinds. | Settles the register's D6 (room-list/DIRECT/SERVICE scope) — narrow option confirmed, matching the tablet source's own 1-room/GROUP-only landscape read. |
| D7 | `PM_RESOLVED_AS_EXISTING_CONTRACT` | Desktop/tablet room auto-select behavior (`≥701px`, fires once, gated on `pageState==='normal'`, no re-fire after manual back-navigation) is **preserved as-is**. Its claimed "§3 PM 정책" provenance is not independently re-verified by this closeout, but the behavior itself is treated as an existing, deliberate functional contract not to be casually rewritten. | Unchanged topic, now decided — keep, don't guess-and-rewrite. |
| D8 | `PM_RESOLVED` | Admin sidebar = **bright `#FBFAFE`** (matches approved PNG + tablet A5 landscape rail, against current code's dark `#1e1b4b`). Existing edit/delete (and approve/reject) functionality in the sidebar-adjacent Admin views **must be preserved** — this is a visual recompose only, not a functional rewrite. | Unchanged topic, now decided (Option A, light theme). |
| D9 | `RESOLVED_BY_SEQUENCE_ADJUSTMENT` | A1 ships **mobile-only first**. No tablet layout for A1's top-level login/profile screen is invented to fill the gap `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md` found (no tablet variant exists for `1a`/`1a-1`). A1's tablet adaptation is deferred until a real tablet source for it exists or is commissioned. | Reconciles the register's D9 (A1-S1 sub-screen, no tablet variant) — resolved not by inventing a layout, but by adjusting the implementation sequence so A1 doesn't need one yet (see Implementation Sequence Freeze closeout section). |
| D10 | `PM_RESOLVED_FOR_VISUAL_CONTRACT` | Bottom dock = exactly **4 items**: 홈 → `/family`, 포인트잔치 → `/dashboard`, 와글와글 → `/wagle`, 나 → **`ROUTE_BINDING_DEFERRED`** (no "나"/my-page route exists in `frontend/src/App.tsx` as of this closeout — confirmed by direct read; not invented). No 5th destination is added. | Settles the register's D10 (4th/5th dock destination) — Option B (no extra destination) confirmed, with the 4th item's own route left explicitly open rather than guessed. |
| D11 | `PM_RESOLVED` | Historical Naran/Doran documents (`FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md`, `DORAN_*.md`, pre-rename `MONGLE_ROUTE_*`/`MONGLE_NAMING_*` docs) are **preserved as-is** — not renamed, not deleted — and remain **not authoritative** (Tier 5 per `MONGLE_W6_CANONICAL_SOURCE_FREEZE.md`). | Settles the register's D11 (supersession question) — no supersession/deletion, just a non-authoritative label, consistent with what Tier 5 already said. |
| D12 | `NON_BLOCKING_DEFERRED` | Legacy E2E infra (missing `docker-compose.phase0.yml`, confirmed absent again this closeout — `find` returned zero hits) is deferred to a dedicated follow-up: **`MONGLE-LEGACY-E2E-INFRA-RECOVERY-001`**. The **current Playwright Mongle suite** (`tests/e2e/playwright.mongle.config.ts` + `tests/e2e/specs-mongle/`, both confirmed present) is the **regression baseline** for Wave 6.1 onward, not the blocked legacy `specs/` suite. | Unchanged topic, now decided — deferred, with a named successor task and a named current baseline. |
| D13 | `PM_RESOLVED_BY_SOURCE_ROLE_PARTITION` | The ~153 KB, 10-screen `standalone-src.html` (not present in this repo; its A1-A5 measurements survive as `COMMITTED_DERIVED_EVIDENCE` in `engineering/phase2/wave6-0ab-baseline-analysis/6.0A/`) and the ~636 KB (actual size 636,567 B), 71-screen `docs/temp/design_tablet/가족 플랫폼 화면 재현.dc.html` are **not merged or auto-superseded** into a single source. Roles are partitioned: the missing 10-screen file's 6.0A measurements remain the only pixel-level mobile evidence for A1-A5; the 71-screen file is classified **`EXTENDED_MOBILE_STRUCTURE_SOURCE`** — usable as structural/content reference (e.g. for the 15 tablet-covered screens' stated mobile counterpart), never as a substitute pixel-level source, and it does **not** auto-supersede the approved PNGs. Conflict resolution order where these ever disagree: **approved PNG > PM decision > current functional contract** (the 71-screen file itself is never above any of these three). | Unchanged topic, now decided — source-role partition, not a merge, matching Review 1's explicit requirement that D13's sources not be blended. |
| D14 | `PM_RESOLVED` | Spacing scale: **4/8/12/16/20/24/32/40/48/64px** is the **global semantic base** (extends current code's existing 4px-ladder token set with a 64px step; matches neither the approved-PNG's odd-number literals nor the tablet source's own distinct 10-step scale exactly). Values measured directly off a specific approved screen that don't fit this ladder are `SCREEN_LOCAL_MEASURED_VALUE`; values that only make sense at a specific responsive breakpoint are `RESPONSIVE_LAYOUT_VALUE`. Both categories are **allowed to coexist** with the global base — they are not treated as scale violations. Decided independently of D4 (font), per `MONGLE_W6_DESIGN_TOKEN_FREEZE.md`'s own recommendation not to conflate the two. | New item — formalizes the "spacing-scale note" already logged in this file (see above) as its own numbered, PM-decided item, per this closeout task's explicit instruction to give it a D14 ID. |
| D15 | `PM_RESOLVED` | Tablet navigation chrome must **never be removed**. Portrait may use a 4-item bottom dock **if the source shows one** (A2/A3/A4 portrait all do, per the Delta Matrix). Landscape may use a nav rail **only if the tablet source explicitly shows one** (A2, A5 landscape do; A3, A4 landscape do not). Where a landscape capture shows **no** nav chrome at all (A3, A4 landscape — Delta Matrix Open Item 1), this is classified **`SOURCE_PRESENTATION_OMISSION`**, not an approval to ship an immersive/chrome-free layout — the **current nav** (existing dock/rail behavior) must be preserved for those screens instead of following the source's chrome-free presentation literally. | New item — directly resolves Delta Matrix Open Item 1 / Responsive Freeze item 8's "A3/A4 landscape lack persistent nav chrome" `PM_DECISION_REQUIRED` flag, without permitting nav removal. |

### Reclassification summary (superseding the Section 19 table above)

| Status | Items |
|---|---|
| `PM_RESOLVED` | D1, D2, D3, D4 (+`FONT_DELIVERY_REQUIRED`), D6, D8, D11, D14, D15 |
| `PM_RESOLVED_AS_EXISTING_CONTRACT` | D7 |
| `RESOLVED_BY_SEQUENCE_ADJUSTMENT` | D9 |
| `PM_RESOLVED_FOR_VISUAL_CONTRACT` | D10 |
| `LOCALIZED_BLOCKER` | D5 (A2 primary, A3 secondary — not global) |
| `NON_BLOCKING_DEFERRED` | D12 (→ `MONGLE-LEGACY-E2E-INFRA-RECOVERY-001`) |
| `PM_RESOLVED_BY_SOURCE_ROLE_PARTITION` | D13 |
| `PM_DECISION_REQUIRED` (remaining, none) | — all 15 items above have a final status |

**Verdict: D1-D15 ALL INDIVIDUALLY RESOLVED.** No item remains `PM_DECISION_REQUIRED`. D5 remains a real
blocker for its localized scope (A2 hero/tiles, A3 mission icons) and D4's font question carries one
explicit unresolved sub-flag (`FONT_DELIVERY_REQUIRED`) forward to the Wave 6.1 Start Gate — both are
disclosed above, not hidden, and neither blocks the Wave 6.1 token/primitive foundation stage itself.
