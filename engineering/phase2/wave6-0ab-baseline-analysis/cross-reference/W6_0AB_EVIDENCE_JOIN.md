# A/B Evidence Join

Umbrella: MONGLE-W6-0AB-BASELINE-ANALYSIS-001 (Section 26). Full data: `w6_0ab_evidence_join.csv` (5 rows, A1-A5).

This document connects each screen's Phase A evidence (approved source, zones, measurements) to its
Phase B evidence (current route, component, functional contract, gaps) and assigns a readiness
classification. It does **not** finalize any token, component API, or implementation order, and does
**not** resolve any PM decision — every readiness call below is qualified by the specific PM decision(s)
that must be resolved first (cross-referenced by ID to `PM_DECISION_BRIEF_V2.md`).

## Readiness by screen

| Screen | Readiness | Blocking factor(s) |
|---|---|---|
| A1 (로그인) | `READY_WITH_PM_DECISION` | D1 (aspect ratio), D2/D3 (color near-miss), D4 (font family), D9 (A1-S1 scope) — none of these block *starting* work, but each affects how it should look |
| A2 (가족 홈) | `BLOCKED_BY_SOURCE` + `BLOCKED_BY_FUNCTION` | Hero illustration and 3 service-tile icons are missing source assets (D5); the screen itself is an unbuilt stub — this is the only screen blocked on two independent axes at once |
| A3 (마크포인트) | `READY_WITH_PM_DECISION` | D5 (mission icon assets) is the main open item; the screen is otherwise functionally complete and route-stable |
| A4 (와글와글) | `BLOCKED_BY_FUNCTION` / `BLOCKED_BY_BACKEND` | Visually the closest of all 5 to its approved source (TIER1: `MINOR_RENDERING_NOISE`), but has **zero live backend integration** — the blocker is entirely functional, not visual, and is the most consequential blocker in the whole package because "와글와글"/도란 is a named product surface with an explicit non-negotiable API contract that this analysis is not authorized to touch |
| A5 (관리자 포인트) | `READY_WITH_PM_DECISION` | D8 (sidebar dark/light tone) is the only open item; functionally this screen already exceeds its approved-source depiction |

## Cross-cutting pattern

Three of the five screens (A2, A3, and — via its underlying icon assets — indirectly A4/A5's broader
icon system) share the exact same root blocker: **the approved PNGs specify flat icon/illustration
assets that do not exist as files anywhere in the approved-source folder**, forcing every consumer of
this evidence package to treat "source real icons" as a prerequisite task rather than something Wave 6.1
can source internally from the design material alone (`D5`).

A4 is the outlier in the opposite direction: its *design* readiness is the best of the five (closest
visual match, exact-match chat token colors already wired), but its *functional* readiness is the worst
(entirely fixture-driven) — a reminder that "READY" must be qualified by which axis (design vs. function)
is being asked about, which is why this join keeps them as separate columns rather than collapsing to one
score.

This document is an evidence connector for MONGLE-W6-0C-CANONICAL-FREEZE-001's use; it is not itself a
freeze decision, and 6.0C has not been started.
