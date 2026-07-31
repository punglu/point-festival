# MONGLE_W6_1_RESPONSIVE_BREAKPOINT_AUDIT

Task: MONGLE-W6-1-TOKEN-PRIMITIVE-FOUNDATION-001, Gate C (§11). Inventories every current media
query/JS viewport branch in `frontend/src`, classifies each, and decides whether a shared CSS breakpoint
can be safely implemented this task or must be deferred.

## 1. Full inventory (`grep -rn "@media" --include="*.css" frontend/src`, 28 matches across 22 files)

| Value | Files (count) | Classification |
|---|---|---|
| `min-width: 701px` | `platform/doran/components/ChatHeader/ChatHeader.module.css` (1) + `window.matchMedia('(min-width: 701px)')` in `platform/pages/DoranLanding.tsx` (1) | **FUNCTIONAL_BREAKPOINT_CONTRACT** — drives Doran's split-view vs. back-button auto-selection logic (JS + CSS both keyed to the same 701px value). Explicitly called out by the task brief as not to be touched/promoted. |
| `max-width: 700px` | `platform/pages/DoranLanding.module.css` (1) | **FUNCTIONAL_BREAKPOINT_CONTRACT** (same Doran split-view boundary, complementary max-width of the 701px min-width above; one logical contract, two CSS expressions) |
| `max-width: 768px` / `min-width: 768px` | `AdminLayout` (indirectly via 1023), `MobileHeader`, `StatCard`, `ConfigView`, `DashboardView`, `MissionView`, `NotificationView`, `PlayerView`, `PointView`, `BalanceSection`, `CardDetailTable` (Admin, 10 files); `MissionList`, `WeeklyDateBar` (UserDashboard, 2 files, `min-width:768px`); `MongleAppShell` (`min-width:768px`); `ChatModal` (`max-width:768px`); `MessageBubble` (`min-width:768px`) — **15 occurrences total** | **CANDIDATE_SHARED_BREAKPOINT** — by far the single most-repeated literal in the codebase, and it numerically matches the frozen tablet reference-viewport **width** (768×1024, `MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md` item 2). See §3 for why this is not promoted to an enforced token this task despite the strong frequency signal. |
| `max-width: 1023px` / `min-width: 1024px` | `AdminLayout`, `DashboardView`, `MissionRanking`, `ProposedMissionSection` (Admin, 4 files, `1023px`); `Auth.module.css`, `UserDashboard.module.css`, `platform/pages/DoranLanding.module.css` (`min-width:1024px`, 3 files) | **CANDIDATE_SHARED_BREAKPOINT** — second most-repeated pair, matching the tablet-landscape/desktop reference-viewport width boundary (1024×1366 tablet landscape, 1440×900 desktop). Same non-promotion reasoning as 768px, §3. |
| `max-width: 480px` | `DashboardView`, `BalanceSection`, `MissionRanking` (Admin, 3 files); `UserDashboard.module.css`, `MissionCard`, `ScheduleManager`, `TemplateManager` (UserDashboard/Admin views, 4 files) | **LEGACY_LITERAL / SCREEN_LOCAL_BREAKPOINT** — this is an **existing, already-shipping, code-level** small-phone tier, not the design mockup's 480px canvas (which the Responsive Canonical Freeze explicitly forbids adopting as a breakpoint). These are two different things sharing a number by coincidence; this audit does not conflate them. Left exactly as-is — not touched, not consolidated. |
| `max-width: 600px` | `LevelConfig.module.css` (1) | **SCREEN_LOCAL_BREAKPOINT** — single-file, no repetition elsewhere, no promotion candidate. |
| `max-width: 360px` | `MissionList.module.css` (1) | **SCREEN_LOCAL_BREAKPOINT** — same reasoning. |
| `min-width: 640px` | `ChatModal.module.css` (1) | **SCREEN_LOCAL_BREAKPOINT** — same reasoning. |
| `max-width: 767px` | `MongleAppShell.module.css` (1, paired with the same file's `min-width:768px`) | **VISUAL_LAYOUT_BREAKPOINT** — this is the shell's own mobile/tablet dock-vs-rail switch, a real functional-adjacent layout decision already in production. Left untouched. |
| `prefers-reduced-motion: reduce` | `styles/global.css` (1) | Not a layout breakpoint — accessibility media feature, out of scope for this audit. |

## 2. Test-viewport vs. CSS-breakpoint distinction (explicitly not conflated)

The Mongle Playwright suite (`tests/e2e/playwright.mongle.config.ts`, not run this task per the
Docker/E2E resolution) defines device/viewport **projects** for test execution (e.g., mobile/tablet/desktop
profiles). Those are **TEST_VIEWPORT_ONLY** — they select what size the test browser launches at; they are
not CSS `@media` rules and do not, by themselves, prove or require any particular CSS breakpoint value.
This audit does not treat the two as interchangeable evidence.

## 3. Why 768px/1024px are not promoted to an enforced shared-breakpoint token this task

Despite 768px and the 1023/1024px pair being the most frequent literals in the codebase (15 and 7
occurrences respectively) and both numerically matching the frozen reference-viewport widths, this task
does **not** introduce a new enforced CSS breakpoint constant (e.g., a custom media rule or shared SCSS-like
variable) for three reasons, matching §11/§18's explicit guidance to prefer `BREAKPOINT_IMPLEMENTATION_DEFERRED`
over a forced decision when evidence is inconsistent:

1. **No existing single mechanism to attach it to.** This is a plain CSS Modules codebase with no
   preprocessor and no existing shared breakpoint constant (no PostCSS custom-media, no SCSS variable, no
   JS/TS constant consumed by `matchMedia`). Introducing one now, with zero consumers wired to it, would be
   a symbolic addition only — and *wiring* it to the 22 files above would mean editing per-screen CSS
   Modules, which is screen-level/composition work, explicitly out of this task's scope (§4, §18 forbidden
   list: "per-screen column composition").
2. **The values are not perfectly uniform even at the "same" boundary** — some files pair `max-width:1023px`
   with others' `min-width:1024px` (consistent, fine), but 768px appears as both a `max-width` and
   `min-width` boundary across different files for different purposes (some treat "≥768" as tablet-and-up,
   others treat "≤768" as mobile-and-down for a *different* layout decision). Forcing a single named
   breakpoint over inconsistent directional usage would be a silent behavior-changing consolidation, which
   §11 explicitly forbids ("don't force-consolidate screen-local values").
3. **`MONGLE_W6_RESPONSIVE_CANONICAL_FREEZE.md` item 4 (closeout-updated) explicitly leaves the exact pixel
   value open** — "Item 4 (exact CSS breakpoint pixel value) remains genuinely open... disclosed as residual
   scope for Wave 6.1's own token/layout foundation work, not silently closed." This audit treats that as
   permission to *propose* a strong candidate (done, above) without being required to *freeze* it.

## 4. Decision

**`BREAKPOINT_IMPLEMENTATION_DEFERRED`.** No new hard breakpoint is introduced or enforced this task.
Instead, Phase 4 (Responsive Layout Foundation) implements only the fluid/foundation pieces §18 explicitly
allows without a breakpoint: container max-width tokens, gutter tokens, safe-area tokens, and an overflow
utility pattern — all additive, all zero-consumer-breaking, all breakpoint-agnostic. The two convergent
candidates (**768px** mobile↔tablet, **1024px** tablet↔desktop) are recorded here as the strongest
evidence-backed starting point for whichever future task (per the Implementation Sequence Freeze, most
likely Stage 3's A3 first-mobile-tablet-pair) first needs to wire a real, consumer-bearing shared
breakpoint.

## 5. Doran's functional breakpoint — explicitly preserved, not touched

`701px`/`700px` (JS `matchMedia` + CSS) remains classified `FUNCTIONAL_BREAKPOINT_CONTRACT` and is not
read, referenced, aliased, or renamed by anything this task implements. Zero lines in
`platform/doran/**` or `platform/pages/DoranLanding.*` were edited by this task (confirmed in the Residual
Audit and End Gate diff).

## Verdict for this Gate

**RESPONSIVE_BREAKPOINTS_CLASSIFIED — BREAKPOINT_IMPLEMENTATION_DEFERRED.** 2 `FUNCTIONAL_BREAKPOINT_CONTRACT`
items preserved untouched, 2 `CANDIDATE_SHARED_BREAKPOINT` values documented but not enforced, 1
`VISUAL_LAYOUT_BREAKPOINT` (shell dock/rail) left as-is, remainder `SCREEN_LOCAL_BREAKPOINT`/`LEGACY_LITERAL`.
Phase 4 proceeds as fluid-foundation-only per §18.
