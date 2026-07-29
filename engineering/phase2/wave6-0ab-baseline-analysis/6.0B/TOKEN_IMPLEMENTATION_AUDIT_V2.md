# Token Implementation Audit V2

Task: MONGLE-W6-0B-CURRENT-IMPLEMENTATION-AUDIT-001 (Section 19). Full data: `token_implementation_audit_v2.csv` (14 rows). Source: full read of `frontend/src/styles/global.css` (102 lines, complete file) and `reset.css` (20 lines).

## Structure found

`global.css` contains **two co-existing token generations** in the same file:

1. Lines 6-15: an older, unlabeled set (`--bg`, `--card`, `--accent`, `--blue`, `--text`, `--muted`,
   `--gold`, `--danger: #ef4444`, `--shadow`, `--input-bg`) — no comment identifies its origin, presumed to
   back the legacy UserDashboard/AdminDashboard.
2. Lines 17-24: a "에셋 가이드 팔레트" (`--brand-purple/-coral/-orange/-mint/-skyblue/-pink/-gold`) — also
   unlabeled as to source, and **none of its 7 hex values match any color found in this Wave's approved
   source** (`screen_renew`) — classified `UNUSED_CANDIDATE`/`NOT_VERIFIED`, flagged for the PM to confirm
   what design pass it actually came from.
3. Lines 26-57: an explicitly-commented **"Semantic Design Tokens (FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1.md §5)"**
   block — `--color-brand-*`, `--color-ink-*`, `--color-line/canvas/surface*`, `--color-success/warning/
   danger/reward`, `--color-chat-own/-other`, `--space-*`, `--radius-*`, `--shadow-*`, `--size-touch-min`,
   `--duration-*`, `--layer-*`. This is the block cross-referenced against Phase A's token candidates.

**Duplicate `--danger` finding**: the file defines `--danger: #ef4444` (line 13, older set) *and*
`--color-danger: #EF4665` (line 37, newer set) — two different red hex values for conceptually the same
role, coexisting in the same stylesheet. Neither consuming-component set was fully traced this session
(`usage_count = NOT_VERIFIED` in the CSV) — this is reported as a structural fact, not resolved.

## Cross-reference against Phase A candidates

- **Exact matches** (safe, already-aligned): `--color-brand-100` (#EEE8FF), `--color-danger` (#EF4665, the
  *newer* one), `--color-canvas` (#F7F6FC), `--color-chat-own`/`--color-chat-other` (#6944EF/#F3F0FF),
  `--radius-pill` (999px), `--radius-control` (16px), `--size-touch-min` (44px).
- **Near-miss conflicts** requiring a PM call: `--color-brand-600` (#5835DF) vs. the approved source's most
  common brand accent (#5A35DF, 117 occurrences) — 2/256 delta on the R channel; `--color-ink-900`
  (#171D3A) vs. the approved source's most common text color (#17103A, 188 occurrences, the single
  highest-frequency color in the whole design) — 13/256 delta on the G channel.
- **Hard mismatch, not an alias question**: body font-family is `'Pretendard', sans-serif` (line 76)
  system-wide; the entire approved source uses `'Noto Sans KR'`. `REQUIRES_PM_DECISION`.
- **Scale-shape mismatch**: `--space-1..12` is a strict 4px-multiple ladder (4/8/12/16/20/24/32/40/48);
  the approved source's most frequent spacing literals are odd numbers (3/5/7/9/11px) that don't sit on
  that ladder at all.
- **Admin sidebar tone mismatch**: `[data-domain="admin"] { --admin-sidebar-bg: #1e1b4b; ... }` (dark
  indigo) vs. the approved A5 sidebar, which is a near-white `#FBFAFE` — the current legacy admin surface
  and the approved design use fundamentally different sidebar tones (dark vs. light), not just different
  hex shades of the same tone.

No new token was declared or renamed in this audit — every row is a comparison of what already exists in
code against what Phase A measured, per the brief's read-only constraint.
