# Approved Screen Inventory

Task: MONGLE-W6-0A-APPROVED-SOURCE-REBASE-001 (Section 8). Full data: `approved_screen_inventory.csv` (10 rows).

`standalone-src.html` contains exactly **10** distinct screen sections, each marked by a
`<div id="1a">`..`<div id="1i">` wrapper and a `data-screen-label="..."` attribute on the phone/desktop
mockup frame inside it. All 10 are accounted for below — none were skipped.

| Screen ID | HTML anchor | Label | Maps to task's A1-A5? |
|---|---|---|---|
| A1 | `id="1a"` | 로그인 | A1 (로그인/프로필 선택) |
| A1-S1 | `id="1a-1"` | 로그인 폼 | A1 (variant: 순수 ID/PW 로그인) |
| A2 | `id="1b"` | 홈 | A2 (가족 홈/Shell/Header/Dock) |
| A3 | `id="1c"` | 포인트 잔치 | A3 (마크포인트 사용자 화면) |
| A4 | `id="1d"` | 대화 | A4 (와글와글 GROUP 메시징) |
| A5 | `id="1e"` | 관리자 포인트 관리 | A5 (관리자 포인트 화면) |
| EXTRA-01 | `id="1f"` | 나 프로필 | outside A1-A5 |
| EXTRA-02 | `id="1g"` | 가족 일정 | outside A1-A5 |
| EXTRA-03 | `id="1h"` | 앨범 | outside A1-A5 |
| EXTRA-04 | `id="1i"` | 할 일 | outside A1-A5 |

No route strings are encoded anywhere in the approved HTML (verified: no `href`, no `data-route`, no
`<a>` tags with meaningful paths in the whole document — links are static text spans with `›` glyphs).
Every `route_estimated` field in the CSV is therefore `NOT_VERIFIED` by design, not by omission — any
route mapping in Phase B is Phase-B-only inference from current code, never attributed back to the
approved source.

## Effort-allocation note (explicit, not hidden)

A1 through A5 (6 screens counting the A1/A1-S1 pair) received full zone-by-zone reading and are reflected
in `HTML_STRUCTURE_EXTRACTION.md` / `html_zone_inventory.csv` / `MEASUREMENT_TABLE_V2.md` at high detail.
EXTRA-02/03/04 (가족 일정/앨범/할 일) were confirmed to exist, confirmed to follow the same 480px mockup
frame + fake-status-bar + BottomDock pattern, and had their `data-screen-label` and outer structure
verified, but were **not** decomposed zone-by-zone at the same depth — the brief's own Task 0 scope
statement (Wave 6.0AB covers A1–A5) and the total absence of dedicated approved PNGs or PM-facing
functional requirements for these three "준비중" placeholders made deep measurement of them a poor use
of a single session's effort budget relative to A1–A5. This is recorded as an explicit judgment call,
not a silent gap: see `screen_id = EXTRA-02/03/04` rows in `approved_screen_inventory.csv`
(`visible_zones = NOT_FULLY_READ`), and the corresponding `PM_DECISION_REQUIRED` note asking whether a
follow-up task should decompose them before Wave 6.1 implementation begins.

## Notable structural finding: EXTRA-04 ("할 일") Dock state

The BottomDock on the "할 일" (To-do) screen (`id="1i"`, lines ~1340-1352) renders with **홈 (Home) as the
active/highlighted tab**, not a "할 일" tab (there is no 5th dock item — the dock is fixed at 4 items:
홈/포인트 잔치/대화/나, identical across all 10 screens). This indicates the approved design intends
"가족 일정 / 앨범 / 할 일" to be reached *from* Home's `ServiceGrid`, not via their own persistent Dock
tab — consistent with A2's `ServiceGrid` showing all three as "준비중" tiles rather than Dock destinations.
This directly informs the current-implementation cross-reference in Phase B (`MongleAppShell.tsx`'s Dock
is also fixed at 3 items — 마크포인트/와글와글/가족 — for unrelated current-product reasons; see
`SCREEN_COMPONENT_GAP_MATRIX_V2.md`).
