# Per-Screen Expected File Change Plan

Task: MONGLE-W6-0B-CURRENT-IMPLEMENTATION-AUDIT-001 (Section 23). No code was changed to produce this
plan — it is a forward-looking estimate only, for the *next* Wave (6.0C and beyond) to consume. Paths
marked **exact path** were confirmed to exist by direct file listing/reading this session. Paths marked
**PROPOSED_PATH** do not exist yet and are naming guesses only, never implied to already exist.

## A1 — 로그인

- Likely modify (exact path): `frontend/src/pages/Auth/index.tsx`, `frontend/src/pages/Auth/components/PlayerSelectView.tsx`, `PlayerCard.tsx`, `Auth.module.css`
- Likely add: `PROPOSED_PATH: frontend/src/pages/Auth/components/CredentialLoginView.tsx` (if A1-S1's ID/PW flow is approved for implementation — currently `KNOWN_GAP`, no such component exists)
- Must not touch: `frontend/src/pages/Auth/api/authApi.ts` request contracts (functional, `MUST_PRESERVE`), `useAuthStore.ts` JWT payload handling
- Functional owner / style owner / test owner: all currently the same team surface (`pages/Auth/`)
- Asset owner: brand pin-logo asset (exists, `ASSET_MASTER_CANDIDATE` confirmed in Phase A)
- Route impact: none expected unless A1-S1 becomes a real route
- API impact: none for the select→PIN flow; a new endpoint may be needed only if A1-S1 is real (`PM_DECISION_REQUIRED`)
- DB impact: none expected
- PWA impact: none identified
- Regression risk: MEDIUM (login is the very first screen every E2E test depends on via `loginAsFirstPlayer`)
- Screenshot viewport: 480px mobile (per approved mockup) — actual target viewport still `PM_DECISION_REQUIRED` given the aspect-ratio conflict in `TIER1_HTML_VISUAL_DELTA.md`
- Hard Stop condition for that future task: must not touch `PlayerAuth`/JWT `sub` semantics documented in CLAUDE.md Phase 1/5

## A2 — 가족 홈 / Shell

- Likely modify (exact path): `frontend/src/platform/pages/FamilyLanding.tsx` (currently a 15-line stub — this is where the bulk of new work lands), `frontend/src/platform/shell/MongleAppShell.tsx` / `.module.css` (Dock icon/asset work, already has an open `PM_DECISION_REQUIRED_BOTTOM_DOCK_ROUTE` comment)
- Likely add: `PROPOSED_PATH: frontend/src/platform/family/components/{GreetingHeader,PromoHeroCard,RecentActivityCard,ServiceGrid}.tsx` (none of these exist yet; naming is this task's own suggestion, not a confirmed spec)
- Must not touch: `useFamilyContextStore.ts` storage-key contract (`MUST_PRESERVE`, extensively tested), `AccessBoundary.tsx` permission gating
- Functional owner: Family Context team surface; Style owner: new (currently none); Test owner: `tests/e2e/specs-mongle/`
- Asset owner: **blocked** — Hero illustration and 3 service-tile icons are `SOURCE_MISSING` (Phase A `ASSET_MANIFEST.md`); cannot be sourced by this analysis task
- Route impact: none (route already exists, currently a stub)
- API impact: `NOT_VERIFIED` whether a "recent activity" feed API already exists; likely a `BACKEND_GAP` for the real Home content
- DB impact: `NOT_VERIFIED`
- PWA impact: none identified
- Regression risk: LOW-MEDIUM (currently near-empty, so little to regress, but Dock changes affect every screen)
- Screenshot viewport: 480px mobile
- Hard Stop condition: must not alter `family.services`/permission shape consumed by `AccessBoundary`/`MongleAppShell`

## A3 — 마크포인트 (레거시 UserDashboard)

- Likely modify (exact path): `frontend/src/pages/UserDashboard/index.tsx` and its `components/*` (11+ files, all exist, see App structure)
- Likely add: none expected (this screen is fully built functionally; work here would be visual recomposition of existing components, not new ones) — `PROPOSED_PATH` only if a CSS-Modules-based visual refresh needs new sub-components
- Must not touch: `dashboardApi.ts` response contracts, `adjust_daily_point`/level-calculation backend logic (CLAUDE.md: `MUST_PRESERVE`, has operational history of prior bugfixes)
- Functional owner / style owner / test owner: `pages/UserDashboard/`
- Asset owner: mission icons are `SOURCE_MISSING` per Phase A (emoji-vs-flat-icon gap repeats here)
- Route impact: none
- API impact: none expected (existing endpoints sufficient)
- DB impact: none expected
- PWA impact: none identified
- Regression risk: HIGH (this is the most functionally mature and most-tested current screen; visual-only changes still risk breaking `specs/02-mission.spec.ts` selectors)
- Screenshot viewport: 480px mobile
- Hard Stop condition: must not touch `level_tiers`/`total_earned` sync logic (CLAUDE.md P7-PATCH-005/006)

## A4 — 와글와글 (GROUP)

- Likely modify (exact path): `frontend/src/platform/pages/DoranLanding.tsx`, all 10 files under `frontend/src/platform/doran/components/`, `frontend/src/platform/doran/preview/*.ts` (would need to be **replaced**, not modified, once real API wiring begins)
- Likely add: `PROPOSED_PATH: frontend/src/platform/doran/api/doranApi.ts` (no such file currently exists — confirmed by directory listing; this is the single largest missing piece: a real API client for the `/api/families/{family_id}/doran` contract)
- Must not touch: the `doran`/`SERVICE_CODE="doran"`/user-facing "와글와글" naming contract (explicit, non-negotiable per this task's baseline context)
- Functional owner: new (backend integration does not yet exist on the frontend side); Style owner: `platform/doran/components/` (already substantially built); Test owner: `specs-mongle/`
- Asset owner: chat-related assets are in reasonable shape (bubble colors are an exact token match already)
- Route impact: none expected for `/wagle` itself; a Room List sub-route or query contract may need explicit definition (currently informal, `?room=id`)
- API impact: **HIGH** — this is the actual functional gap; wiring real messages/rooms is a backend-integration task, not a visual one
- DB impact: `NOT_VERIFIED` (outside this frontend-focused audit's read scope)
- PWA impact: `NOT_VERIFIED`
- Regression risk: MEDIUM (fixture removal could break every `specs-mongle` test that currently depends on the fixture rendering deterministically)
- Screenshot viewport: 480px mobile (conversation), plus a ≥701px desktop split-view state (already implemented)
- Hard Stop condition: **must not change the Doran API contract path or `SERVICE_CODE` value** — explicit, repeated instruction from this task's baseline context

## A5 — 관리자 · 포인트 관리

- Likely modify (exact path): `frontend/src/pages/AdminDashboard/views/PointView/PointView.tsx` and its `components/*`, `frontend/src/styles/global.css` (`--admin-sidebar-*` tokens, if the dark→light sidebar change is approved)
- Likely add: none expected (dialogs already exist, ahead of the approved design)
- Must not touch: `adminApi.ts` request/response contracts, RBAC (`get_current_admin`) semantics
- Functional owner / style owner / test owner: `pages/AdminDashboard/`
- Asset owner: N/A (no new assets identified as required)
- Route impact: none
- API impact: none expected
- DB impact: none expected
- PWA impact: none identified
- Regression risk: MEDIUM (sidebar dark→light token change would visually affect every Admin view, not just PointView, since `[data-domain="admin"]` is a global selector)
- Screenshot viewport: 1440px desktop
- Hard Stop condition: must not touch `deductions`/`daily_points` table semantics or the Row-Lock point-engine logic (CLAUDE.md Phase 2 pattern)
