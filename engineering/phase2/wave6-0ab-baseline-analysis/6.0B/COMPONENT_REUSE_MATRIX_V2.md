# Component Reuse Matrix V2

Task: MONGLE-W6-0B-CURRENT-IMPLEMENTATION-AUDIT-001 (Section 20). Full data: `component_reuse_matrix_v2.csv` (9 rows). Consumer counts were derived via `grep -rl` against `frontend/src` for each component's import path, not estimated.

## Global-shared components (`frontend/src/shared/components/`)

| Component | Verified consumers | Classification |
|---|---|---|
| `Avatar` | 4 (`ChatHeader`, `MessageBubble`, `RoomItem`, `DoranLanding`) | `REUSE_AS_IS` — already past the "2nd consumer" bar the brief requires before recommending reuse |
| `IconButton` | 2 (`ChatComposer`, `ChatHeader`) | `REUSE_AS_IS` |
| `Toast`/`ToastContainer` | globally mounted in `App.tsx` | `REUSE_AS_IS` (already fully promoted) |
| `Card` | 1 (`ServiceActionCard` only) | `SCREEN_LOCAL_KEEP` — brief explicitly says not to recommend promotion without a confirmed 2nd consumer |
| `MainLogo` | 1 (`PlayerSelectView` only) | `SCREEN_LOCAL_KEEP` |
| `Button` | **0** — grep found no current consumer of this primitive anywhere in `frontend/src` | `REUSE_AS_IS` in principle (it is a clean, already-built primitive with 3 variants: `primary/ghost/dangerSm`) but flagged that its generalization is **unverified by any real usage** — first adoption should be watched closely rather than assumed correct |
| `PhotoUpload` | Not re-verified this session (CLAUDE.md history states 2 consumers: PlayerManager + CheerEditor) | `REUSE_AS_IS`, but on document evidence only — `NOT_VERIFIED` by fresh grep this session |

## Domain-local components (`frontend/src/platform/doran/components/`, 10 components)

All 10 (`ChatHeader`, `RoomItem`, `MessageBubble`, `DateDivider`, `UnreadDivider`, `ChatComposer`,
`ServiceActionCard`, `LoadingState`, `EmptyState`, `ErrorState`) are consumed by **exactly one file**,
`DoranLanding.tsx` — confirmed via barrel-import grep (`from '../doran/components'` has exactly one hit
in the whole codebase). Per the brief's explicit rule ("두 번째 실제 consumer가 확인되지 않은 경우 공통화
권장안을 확정하지 않는다"), these are **not** recommended for promotion to `shared/` in this pass, even
though they are already well-factored and directly map to approved A4 zones. Classified
`REUSE_WITH_VARIANT` (reusable *within* the Doran domain once a Room List or second conversation surface
exists) rather than `REUSE_AS_IS` (which would imply cross-domain readiness that hasn't been demonstrated).

## Legacy Admin components (`AdminDashboard/components/`)

Not re-verified by grep this session (documented via CLAUDE.md project history only — `AdminModal`,
`AdminToast`, `CycleIndicator`, `DateSelector`, `MobileDrawer`, `MobileHeader`, `PlayerBadge`, `PlayerTab`,
`Sidebar`, `StatCard`). Classified `REUSE_WITH_VARIANT`: names and evident roles map onto approved A5
zones (Sidebar → AdminSidebar, StatCard → StatCardRow), but the confirmed dark-vs-light sidebar token
mismatch (`TOKEN_IMPLEMENTATION_AUDIT_V2.md`) means a straight reuse without visual rework is unlikely to
match the approved design.

No component was recommended for global promotion based on a single consumer, and no component's
functional coupling was rewritten or reinterpreted — every classification traces to a specific grep
result or an explicit `NOT_VERIFIED` flag where the underlying file was not read this session.
