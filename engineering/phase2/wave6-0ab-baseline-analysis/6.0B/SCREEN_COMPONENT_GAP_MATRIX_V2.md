# Screen / Component Gap Matrix V2

Task: MONGLE-W6-0B-CURRENT-IMPLEMENTATION-AUDIT-001 (Section 21). Full data: `screen_component_gap_matrix_v2.csv` (9 representative rows spanning A1, A2, A3, A4, A5 — the most consequential zone per screen, not an exhaustive every-zone listing given this session's effort budget; the exhaustive zone list is in Phase A's `html_zone_inventory.csv`, and this matrix connects the highest-signal subset of those zones to current code).

Gap classification legend: `MATCH / PARTIAL / MISSING / EXTRA_CURRENT_UI / STRUCTURE_CONFLICT /
TOKEN_CONFLICT / ASSET_MISSING / FUNCTION_BLOCKER / BACKEND_GAP / APPROVED_SOURCE_GAP /
PM_DECISION_REQUIRED / NOT_VERIFIED`.

## Per-screen summary

- **A1**: `PARTIAL` — the player-selector structure has a plausible current counterpart
  (`PlayerSelectView.tsx`/`PlayerCard.tsx`) but visual 1:1 match is `NOT_VERIFIED` (not read in detail this
  session). The admin-entry link is implemented as a full mode-switch rather than the approved inline
  footer link (`PARTIAL`). A1-S1 (순수 로그인) has **no current counterpart at all** → `MISSING`.
- **A2**: the single biggest finding in this whole gap matrix. The approved Home screen's entire zone set
  → `MISSING` at `/family` (15-line stub). The Dock, which does exist, is `PARTIAL`: current code's own
  comments admit it dropped the icon+label treatment for label-only because of an **asset gap**
  (`ASSET_GAP_BOTTOM_DOCK_ICONS`) and left an **unresolved routing question**
  (`PM_DECISION_REQUIRED_BOTTOM_DOCK_ROUTE`) — both surfaced verbatim from the code, not invented here.
- **A3**: `PARTIAL` — functionally strong (real API, real level/mission/cheer logic per project history)
  but visual comparison against the approved PNG was not performed on the *current* running app this
  session (no dev server; static-only analysis) → visual delta itself is `NOT_VERIFIED`, while the
  component-existence match is confirmed.
- **A4**: `PARTIAL` overall, but this masks two very different sub-findings: the **visual/structural**
  layer is close (10 already-built components map cleanly onto approved zones, and TIER1 found only
  `MINOR_RENDERING_NOISE` between HTML and PNG for this screen) while the **functional** layer is a
  `FUNCTION_BLOCKER` — there is no live backend behind any of it. A Room List concept exists in current
  code with no approved-source counterpart at all → `EXTRA_CURRENT_UI`.
- **A5**: `PARTIAL` with a `TOKEN_CONFLICT` — component/functional coverage (including dialogs the
  approved source doesn't even depict) is ahead of the design source, but the current legacy admin
  sidebar's dark theme conflicts with the approved design's light sidebar tone.

## What was deliberately not done

A full zone-by-zone (all 61 rows of Phase A's zone inventory) gap trace was not attempted in the time
available for this session; the 9 rows here were chosen because they carry a decision-relevant finding
(a real gap, conflict, or already-resolved match) rather than restating "component exists, appearance
unknown" 61 times. This is recorded as an explicit judgment call, consistent with the brief's allowance
for reasonable granularity choices, and is not intended to imply the remaining zones have no gaps — they
are simply `NOT_VERIFIED` at this granularity and should be revisited with either a running dev-server
screenshot pass or a deeper code read before a canonical freeze decision (6.0C) is made.
