# MONGLE_W6_CANONICAL_SOURCE_FREEZE

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 14. This document is the authority-of-record for every
other Wave 6 document; where any other document's wording is ambiguous, this one governs.

## Tier definitions, frozen with this session's evidence

| Tier | Source | Authority over | This-session status |
|---|---|---|---|
| **Tier 0** | PM Explicit Decision (task prompt Section 2 `RESPONSIVE-SEQUENCE-001`; this session's live clarifications on worktree/HEAD/dirty/evidence-substitution) | Everything below | Active, referenced throughout |
| **Tier 1M** | 5 approved mobile PNGs (`screen_login_approved.png`, `screen_family_home_approved.png`, `screen_point_festival_approved.png`, `screen_family_chat_approved.png`, `screen_admin_point_approved.png`) | Mobile final visual impression, hierarchy, density, component shape | **Directly present and SHA-verified this session** at `docs/temp/design_tablet/uploads/` (10/10 asset hash match vs. `6.0A`'s record of `screen_renew/uploads/`) — upgraded from `COMMITTED_DERIVED_EVIDENCE` to `RE-VERIFIED_THIS_SESSION` for asset presence/identity; **pixel-level measurements against these PNGs remain `COMMITTED_DERIVED_EVIDENCE`** (6.0A's own Playwright pixel-diff run, not re-executed this session) |
| **Tier 1T** | `docs/temp/design_tablet/가족 플랫폼 화면 재현-tablet.dc.html` (master, SHA `24a02ab6...571d6`) | Tablet layout, columns, content width, panes, nav placement, tablet density/spacing, tablet screen order, tablet-specific visibility, responsive-transition intent | **`TABLET_CANONICAL_SOURCE_IDENTIFIED`, re-verified this session** — see `MONGLE_W6_TABLET_SOURCE_IDENTIFICATION.md` |
| **Tier 2** | Shared Style Source: `docs/temp/design_tablet/design-system/APPROVED_VISUAL_STYLE_GUIDE.html` + `canonical-tokens.css`/`.json` + 8 classification MD docs; brand/logo asset (`family_platform_pin_logo_transparent_1024.png`) | Global token values, component language, asset contract | New this delivery (no prior-session equivalent existed per `6.0A`'s "0 standalone CSS/JSON files" finding) — `ADDED_TABLET_ASSET`, read in full this session (prior turns of this conversation) |
| **Tier 3** | Existing Mobile HTML Structure Source: `standalone-src.html` (10-screen, A1-A5+EXTRA scheme) | Structure/measurement basis for A1–A5 zone-level detail already on record in `6.0A` | **Not present in this environment.** The file with the same display name found in `docs/temp/design_tablet/` is a *different*, 71-screen file — **not treated as Tier 3**, kept as unranked reference context only (`D13`, unresolved). Fixed canvas / mock chrome from this tier are, per the task's own rule, never product breakpoints or product UI regardless of which file is meant |
| **Tier 4** | Current React (`frontend/src/**`) | Real functionality, API calls, auth, Family/Account Context, permissions, state, loading, error, mutation, route, storage, accessibility semantics *where they actually exist* | Re-confirmed this session for A3 (`useDashboard.ts`), A5 (`useAdminData.ts`), A4 (`DoranLanding.tsx`) — see `MONGLE_W6_FUNCTIONAL_DEEP_AUDIT_SUPPLEMENT.md`. Current React's **visual** state is explicitly not design authority (e.g., Admin's current dark sidebar does not override Tier 1M/1T's light-sidebar evidence for `D8`) |
| **Tier 5** | Historical/Derived: `_analysis/wave6_0-analysis/*`, `_analysis/wave6_1a-source/*` (both `screen_renew`-side, not present here either), `FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md` (pre-Mongle-rename, flagged `D11`) | Nothing — never ground truth, cited only as historical context | Unchanged from 6.0AB's classification |

## Conflict resolution order (frozen, per Section 14 requirement)

1. **Tier 0 (PM Explicit Decision) wins outright.** Nothing below can override an explicit PM decision,
   including this session's live clarifications (worktree = `/appl/point-festival`, HEAD = `08619298`,
   dirty lockfiles = pre-existing/preserved, `docs/temp/design_tablet` = Tier 1T candidate).
2. **For mobile screens, Tier 1M (approved PNG) is the visual-finality tier.** Where a mobile HTML source
   (Tier 3) conflicts with a PNG — e.g. aspect ratio (`D1`) — the PNG wins for final visual proportions;
   HTML remains useful only for structure/CSS-literal values the PNG can't express (exact hex, exact px).
3. **For tablet screens, Tier 1T (the tablet HTML) is the layout-finality tier.** No approved tablet PNG
   exists, so there is no Tier-1T-internal conflict to resolve — but Tier 1T's own **internal**
   inconsistencies (e.g. A3/A4 landscape's missing nav chrome vs. A2/A5 landscape's rail, `Delta Matrix`
   Open Item 1) are not silently resolved by this tier's own authority; they are `PM_DECISION_REQUIRED`.
4. **Shared brand/token values (Tier 2) plus Tier 0 win over any per-viewport visual near-miss.** A brand
   color or font-family is not allowed to silently differ between the mobile and tablet builds just
   because the two design artifacts happened to be produced in different sessions — see
   `MONGLE_W6_DESIGN_TOKEN_FREEZE.md`.
5. **Tier 4 (current React) is authority for function only, never for visual design**, and only for
   functionality *confirmed to exist* by direct code read (not assumed from a route existing).
6. **HTML sample/fixture data is never a functional source of truth.** A4's fixture rooms/messages
   (Tier 4, `DoranLanding.tsx`) describe *current UI behavior*, not real backend contract — the real
   contract is Doran's actual (largely unbuilt, per `D6`/`6.0B`) API.
7. **Current visual implementation is never design authority.** Where current CSS/component visuals
   diverge from Tier 1M/1T (Admin sidebar tone, `D8`; token near-misses, `D2`/`D3`; font family, `D4`),
   the current implementation does not win by incumbency.
8. **Historical source (Tier 5) never overrides current Tier 0–4 evidence**, including the newly
   discovered `D11` document and the unresolved `D13` mobile-HTML conflict — neither is allowed to become
   "the" answer just because it's the only thing available on a given question.
9. **Unclear or conflicting items go to the PM Decision Gate, not to agent judgment.** This session
   added exactly one new such item (`D13`) to the pre-existing `D1`–`D12` set; see
   `MONGLE_W6_PM_DECISION_REGISTER.md`.
10. **Source conflicts are never resolved by agent preference.** Every conflict surfaced in this document
    set (`D1`–`D13`) carries evidence and options, never a forced resolution.

## Tablet-specific-layout vs. shared-token distinction (Section 3 caution, re-confirmed)

Per the task prompt's own caution: the tablet HTML's use of brand/color/font values that also appear in
the mobile source is **not** automatically treated as confirming a new shared token — it is evidence
*toward* the existing near-miss/font questions (`D2`/`D3`/`D4`), not a resolution of them. Concretely this
session: the tablet HTML's `Noto Sans KR` usage and `#5A35DF` brand-600 usage are the **same values**
Tier 1M/Tier 2 already asserted — this **corroborates** (does not newly decide) the "Option A" side of
`D2`/`D4`, and is recorded as such in the Token Freeze, not silently adopted.

## Fixture vs. real-function distinction (frozen)

- A3 (`useDashboard.ts`) and A5 (`useAdminData.ts`): **real**, API-backed, `Tier 4` functional authority
  applies in full.
- A4 (`DoranLanding.tsx`): **100% fixture** (`../doran/preview` imports), confirmed by direct read this
  session (no `doranApi` call exists anywhere in the file) — Tier 4 functional authority does **not**
  apply to any data shape or "sent" state in this screen; only to its **UI mechanics** (room selection,
  read-only SERVICE rendering, desktop auto-select behavior) which are real, shipped interaction code even
  though the data behind them is not live.
- A2 (`/family` route): per `6.0B` (not re-read this session, `NOT_REVERIFIED`), a 15-line stub — no Tier
  4 authority to speak of yet; Wave 6.1 A2 work starts from near-zero function.

## Verdict

**CANONICAL_SOURCE_FREEZE_COMPLETE**, with one carried-forward open item (`D13`, mobile HTML identity)
that constrains scope (no new pixel-level mobile claims) but does not block the freeze itself.

## Closeout Update (MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, PM 확정)

D13 is now **`PM_RESOLVED_BY_SOURCE_ROLE_PARTITION`** (full text in
`MONGLE_W6_PM_DECISION_REGISTER.md`). This does not merge Tier 3 and the 71-screen file into one source
— it partitions their roles explicitly:

- **Tier 1M (5 approved mobile PNGs)** remains mobile final visual authority, unchanged, now further
  confirmed by PM Decision `D1`: reference viewport **390×844**, no fake chrome.
- **Tier 1T (tablet HTML master, SHA `24a02ab6...571d6`)** remains tablet layout-finality authority,
  unchanged, permanently archived (byte-identical) at
  `engineering/phase2/evidence/mongle-wave6-tablet-canonical/source/`.
- **Tier 2 (Shared Style Source)** brand/ink/font/spacing token values are now `PM_RESOLVED` per `D2`
  (`#5A35DF`), `D3` (`#17103A`), `D4` (Noto Sans KR, `FONT_DELIVERY_REQUIRED` carried to Wave 6.1 Start
  Gate), `D14` (4/8/12/16/20/24/32/40/48/64px global semantic base) — see
  `MONGLE_W6_DESIGN_TOKEN_FREEZE.md` closeout section.
- **Tier 3 (mobile HTML structure source)** is **still not filled** by the 71-screen file. The 71-screen
  file (`가족 플랫폼 화면 재현.dc.html`, 636,567 B) is separately classified
  **`EXTENDED_MOBILE_STRUCTURE_SOURCE`** — usable for structure/content reference only (e.g. as the
  tablet companion's own stated mobile counterpart), never as a Tier 3 pixel-level substitute. The
  originally-measured `standalone-src.html` (10-screen, 153,869 B, not present in this environment)
  remains the only Tier 3 pixel-level authority, surviving as `COMMITTED_DERIVED_EVIDENCE`.
- **Conflict order where the approved PNG, a PM decision, and the current functional contract disagree**:
  **approved PNG > PM decision > current functional contract**, with the 71-screen file never entering
  this order above any of the three (D13's explicit scope limit).
- **Tier 4 (current React)** functional authority unchanged; `D15` adds an explicit rule that no tablet
  screen's nav chrome may be treated as "removed by design" on Tier 4's account — see
  `MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md` closeout section.
- **Tier 5 (historical)** unchanged, `D11`-confirmed: preserved, not renamed/deleted, still never
  authoritative.

Permanent archive location and integrity: `engineering/phase2/evidence/mongle-wave6-tablet-canonical/`
(source/assets/manifests/provenance subdirectories; SHA-256 manifest confirms every archived file is
byte-identical to its `docs/temp/design_tablet/` origin as of 2026-07-31).
