# MONGLE_W6_2_A1_VISUAL_DELTA

Task: MONGLE-W6-2-A1-MOBILE-VISUAL-PUBLISHING-001
Worktree: `/Users/mac/mac_Project/mongle_ui-a1-visual-worktree` (isolated, branch `w6-2-a1-visual`)
Authoritative design source: `engineering/phase2/evidence/mongle-wave6-tablet-canonical/assets/uploads/screen_login_approved.png` (Tier 1M, per `MONGLE_W6_SCREEN_SPEC_FREEZE.md` A1 item 2), cross-checked against `MONGLE_W6_DESIGN_TOKEN_FREEZE.md`, `MONGLE_W6_ASSET_POLICY_FREEZE.md`, `MONGLE_W6_COMPONENT_BOUNDARY_FREEZE.md`.
Viewport: 390×844 (D9 `RESOLVED_BY_SEQUENCE_ADJUSTMENT` — mobile-only, no invented tablet layout).

## Approved-design elements and their disposition

| Element | Approved | Implemented | Result |
|---|---|---|---|
| Brand header background | Purple/violet gradient | `linear-gradient(180deg, --color-brand-500, --color-brand-600)` | MATCH (canonical token, not a hand-picked hex; see D2 in Token Freeze) |
| Mascot illustration | Purple balloon character, smiling, confetti/sparkles | `family_platform_pin_logo_transparent_1024.png` (copied verbatim from the canonical-master evidence file into `frontend/src/assets/logos/`) | MATCH — pixel-identical source asset (see §Delta 1 below for why this needed a mid-task correction) |
| Title / subtitle | "가족 플랫폼" / "우리 가족의 공간, 함께 연결되는 하루" | Same strings, `<h1>`/`<p>` | MATCH |
| "사용할 프로필을 선택하세요" heading | Present | Present | MATCH |
| Profile cards | Avatar (colored ring + green online dot), name, `Lv.N 모험가` pill, star+points badge, chevron | Avatar (existing shared `Avatar` primitive, `status="online"`), name, level pill (numeric only, no job title), star icon + points, chevron | PARTIAL — see Delta 2, 3 |
| Locked profile card | Grayed avatar, lock badge, "잠김·5회 실패", "5분 후 다시 시도할 수 있어요" | Grayed avatar (`status="locked"`), "🔒 잠김" only | PARTIAL — see Delta 4 |
| Lock notice banner | Shield icon + reassurance copy, shown when a profile is locked | Text-only reassurance copy, shown conditionally when any profile is locked; copy rewritten (see Delta 5) | PARTIAL |
| Footer row | Standalone settings gear icon (left) + "관리자 로그인 ›" (right) | Same layout; gear icon is now a real button wired to the same admin-login action (see Delta 6) | MATCH (functionally; visual layout unchanged) |

## Deltas

1. **IMPLEMENTATION_DEFECT (self-corrected mid-task).** First implementation used the already-in-repo `frontend/src/assets/logos/brand-icon.png` for the mascot, assuming it was the intended asset. Visual comparison against the approved screenshot showed it did not match (different illustration entirely — small plain face, no confetti). Found the actual canonical master via `MONGLE_W6_ASSET_POLICY_FREEZE.md`'s asset table (`family_platform_pin_logo_transparent_1024.png`, tagged `CANONICAL_MASTER`, SHA-confirmed, "in-use master"), confirmed it is visually identical to the approved screenshot's mascot, and copied that exact file into `frontend/src/assets/logos/family-platform-mascot.png`. This is use of an already-approved deliverable, not new asset creation.

2. **DYNAMIC_CONTENT.** All profile cards show `0P` and no level pill in this environment. Root cause: the synthetic seed data behind this isolated test stack has `total_points: 0` for every fixture player (confirmed via direct `/api/players` call), and the level pill's data source, `GET /api/configs/level.thresholds`, requires authentication and is called before login — so it always 401s and `thresholds` stays `null`, and the level pill never renders. This exact unauthenticated pre-login fetch call is **unchanged from the pre-A1 code** (verified against the original `PlayerSelectView.tsx` before this task's edits) — it is a pre-existing condition, not a regression introduced here, and this task does not touch backend/auth policy, so it was left as-is.

3. **API_GAP (not fabricated).** The approved design's "Lv.3 모험가" combines a numeric level with a job-style title (모험가). `backend/app/domains/level_tier/models.py` does have a `title` field, but `GET /api/players` does not expose it in its response schema. Rather than inventing a title string or a new DTO field, the implementation keeps the existing client-side `calcLevel()` numeric-only fallback (pre-existing code, unchanged) and renders only `Lv.N`. Wiring a real title requires either an API contract change (forbidden by this task) or PM confirmation that the numeric-only fallback is acceptable for A1.

4. **API_GAP (not fabricated).** The approved locked-card detail ("잠김·5회 실패", "5분 후 다시 시도할 수 있어요") requires per-attempt count and remaining-lock-time data. `GET /api/players` only returns `is_locked: boolean` (confirmed in `backend/app/domains/player/schema.py` and `service.py`); the detailed counters only exist inside the authenticated login attempt's own 423 error response (`backend/app/domains/auth/service.py`), which is not available on the pre-login player list. Implementation shows only "🔒 잠김" rather than fabricating a failure count or countdown.

5. **APPROVED_INTENTIONAL_DELTA candidate, PM confirmation still required.** Because of Delta 4, the lock notice banner copy could not reference a specific unlock condition truthfully. Rewrote it from the approved text (which implies immediate unlock on correct PIN) to a generic reassurance pointing to admin contact, since the actual unlock timing/condition per profile is not known to this screen. Flagged here rather than silently deviating; PM should confirm or provide corrected copy.

6. **RESOLVED (2026-07-31, PM-directed).** The footer settings icon had no wired destination — grep of `frontend/src/App.tsx` and `frontend/src/pages` found no existing `/settings`-style route or handler for it to call. PM directed it be connected to the existing admin-login entry point rather than invented as a new destination. Implemented: the icon is now a real `<button>` (`aria-label="관리자 로그인"`, matching its actual behavior rather than mislabeling it "설정") calling the same `onAdminClick` handler as the adjacent "관리자 로그인" link. Re-verified after the change: lint PASS, build PASS, target E2E (`specs-mongle/01-shell.spec.ts`, iphone+desktop) 27 passed/1 correctly-scoped skip/0 failed, and a direct click-through confirmed the icon opens the admin login view.

## Judgement calls requiring explicit PM sign-off

- Delta 2 (level pill never renders pre-login) — accept as pre-existing, or treat as a bug to fix in a separate, properly-scoped task?
- Delta 3/4 (no job title, no lock detail) — accept numeric/boolean-only rendering for A1, or authorize a scoped API contract addition later?
- Delta 5 (rewritten lock notice copy) — accept the rewritten copy, or supply the correct copy once the real unlock condition is confirmed?
- Delta 6 — RESOLVED, no longer requires sign-off (see Delta 6 above).

See `MONGLE_W6_2_A1_TOKEN_PRIMITIVE_GAPS.md` for the Foundation-owned Avatar status-dot clipping defect (item 1), which is a separate, non-visual-content gap.
