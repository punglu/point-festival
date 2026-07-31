# MONGLE_W6_VISUAL_ACCEPTANCE_GATE_FREEZE

Task: MONGLE-W6-0C-CANONICAL-FREEZE-001, Section 21.

## Evidence required per viewport (frozen)

| Viewport class | Size(s) | Compare against | Notes |
|---|---|---|---|
| Mobile | 390×844 | Approved PNG (Tier 1M), side-by-side | 6.0A's own Playwright render pipeline (`scripts/render.js` + `visual_diff.py`, both preserved in the committed evidence) is the reusable reference implementation — not re-run this session |
| Tablet | 768×1024, 1024×1366 | Tablet HTML (Tier 1T) side-by-side | **Note**: the tablet source's own authored landscape canvas is 1024×700, not 1024×1366 — the task's minimum-verification viewport (1366 height) is taller than the design artifact's own presentation frame. Comparison at 1024×1366 must account for this extra vertical space explicitly (e.g., as additional breathing room, not a stretched 700px design) rather than silently stretching the 700px-tall composition |
| Desktop | 1440×900 | Only for screens with an approved desktop source — **A5 only**, confirmed this session (A5's PNG is 1448×1086, already desktop-shaped; A1-A4 have no desktop Tier 1M source) | |

## Per-screen evidence status (what exists vs. what's still needed)

| Screen | Mobile PNG available | Tablet HTML available | Desktop source available | Render evidence already produced |
|---|---|---|---|---|
| A1 (top-level) | Yes | **No** | No | `evidence/approved-html-render/screen_1a.png`/`screen_1a_1.png` (6.0AB, mobile HTML render only) |
| A1 (PIN/lock/onboarding sub-screens) | n/a (no dedicated PNG per `D9`/inventory) | Yes | No | none |
| A2 | Yes | Yes | No | `evidence/.../screen_1b.png`, `diff_1b.png` (6.0AB) |
| A3 | Yes | Yes | No | `evidence/.../screen_1c.png`, `diff_1c.png` (6.0AB) |
| A4 | Yes | Yes | No | `evidence/.../screen_1d.png`, `diff_1d.png` (6.0AB) |
| A5 | Yes | Yes (landscape only, this session) | Yes (PNG itself) | `evidence/.../screen_1e.png`, `diff_1e.png` (6.0AB) |

## Visual Delta classification (applied retroactively to what's already measured, per Section 21's list)

- **A5**: `EXACT_OR_NEAR_MATCH` region for aspect ratio (6.0A: "best overall match, lowest aspect delta,
  lowest pixel-diff") — closest to a clean pass of the 5 mobile screens.
- **A1-A4 (mobile)**: `MATERIAL_DELTA`/`ACCEPTABLE_RENDERING_NOISE` mix, confounded by the D1 aspect-ratio
  question per 6.0A's own disclosure — **not re-classified cleanly until D1 resolves**.
- **A2 hero illustration + service/mission icons (both mobile and tablet)**: `ASSET_BLOCKED` (D5).
- **A3/A4 tablet-only zones** (logout pill, cheer-card, room-list): `SOURCE_CONFLICT`-adjacent —
  `APPROVED_RESPONSIVE_ADAPTATION` only once the PM confirms these zones are intentional tablet additions,
  otherwise `NOT_COMPARABLE` (no mobile baseline to diff against).
- **A5 sidebar tone**: `MATERIAL_DELTA` between current implementation and both design sources (`D8`) —
  will remain `MATERIAL_DELTA` until `D8` resolves and the implementation is updated to match.

## PASS criteria (re-confirmed, all still apply, none loosened by this session)

Functional regression 0, blank screen 0, overflow 0, mock chrome 0 (status-bar-look row on tablet A2
flagged for scrutiny — see Responsive Freeze item 15 — must be resolved one way before this criterion can
be checked cleanly), emoji-as-functional-icon 0 (currently **failing** for A2/A3 per D5 — this is a known,
disclosed blocker, not a silent pass), unapproved-asset 0, mobile/tablet component-meaning parity
(confirmed by the Delta Matrix's "zero DOM-duplication-required" finding), source-less arbitrary layout 0
(the A3/A4 landscape "no nav chrome" pattern must be confirmed intentional, not arbitrary, before it can
be called a PASS-compliant layout).

## Verdict for this Gate

**VISUAL_GATE_FRAMEWORK_FROZEN.** No screen has actually been visually approved by this task (this task
performs no implementation). A5 is closest to a clean PASS path once `D8` resolves; A2 cannot reach PASS
until `D5` resolves; A3/A4 have specific open zones needing PM confirmation before their otherwise-solid
evidence can be called complete.

## Closeout Update (MONGLE-W6-0C-PM-DECISION-CLOSEOUT-001, PM 확정)

The gate framework itself is unchanged (PNG-based mobile gate, tablet-HTML-based tablet gate) and remains
**not executed** by this closeout — no Playwright render was run, no screen received an actual PASS/FAIL
verdict; that is Wave 6.1+ execution work, out of this task's DOCUMENTATION-ONLY scope.

What the closeout confirms:

- **No PASS is possible for a source-less tablet screen.** A1's top-level login/profile screen has no
  tablet HTML source (unchanged finding) and per `D9` will not receive an invented one — its tablet
  Visual Gate row remains `n/a`/blocked by source, not silently marked ready.
- **A5's `D8` gate is now closed** (`PM_RESOLVED`, `#FBFAFE`) — A5 is no longer "closest to PASS pending a
  decision," it has the decision; an actual PASS still requires the render/diff work itself (not performed
  here).
- **A2 cannot reach PASS** — `D5` remains a `LOCALIZED_BLOCKER` for A2 specifically; unchanged.
- **A3/A4's previously-open zones are resolved, not silently dropped**: A3's landscape-only logout
  pill/cheer-card and A4's landscape-only room-list pane are covered by `D15`'s
  `SOURCE_PRESENTATION_OMISSION` framework (nav) and the general `TABLET_ONLY_PRESENTATION` classification
  (non-nav zones) — both remain flagged for PM-aware visual comparison, not treated as ordinary parity.
- **Fixture vs. visual-PASS separation is reconfirmed**: A4 may reach a visual PASS on its `VISUAL_READY`
  axis while remaining `FUNCTION_BACKEND_DEFERRED` on its functional axis (`D6`-scoped to GROUP-only) — a
  visual PASS for A4 must never be reported as a functional PASS.
