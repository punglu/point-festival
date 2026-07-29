# MONGLE_SCREEN_ROUTE_DOCK_MATRIX

TASK ID: MONGLE-FE-ROUTE-ALIGNMENT-001 — Wave 4 (matrix)
Built from Wave 1's screen inventory + Wave 2's route audit + direct grep/read confirmation of each candidate component this session. Rows marked "not deeply verified" are reported honestly as such rather than guessed — per-feature deep audits beyond routing are out of this task's scope.

> **Namespace rename note (MONGLE-TECHNICAL-NAMESPACE-ALIGNMENT-001, added after this document was written):** `NaranAppShell` → `MongleAppShell`. Citations below are as-observed at write time. Route strings (`/naran/doran`, `/naran/family`) are unaffected.

Status legend: see task spec §6 (`IMPLEMENTED_MATCH`, `IMPLEMENTED_ROUTE_MISMATCH`, `IMPLEMENTED_VISUAL_MISMATCH`, `ROUTE_EXISTS_SCREEN_MISSING`, `SCREEN_EXISTS_ROUTE_MISSING`, `DOCK_TARGET_MISMATCH`, `REDIRECT_REQUIRED`, `LEGACY_ALIAS_REQUIRED`, `MODAL_NO_ROUTE_REQUIRED`, `STATE_NO_ROUTE_REQUIRED`, `NOT_PRODUCT_SCREEN`, `FUTURE_IMPLEMENTATION`).

| Screen ID | Screen label | Product feature | React component | Current route | Intended route | Entry point | Dock service | Requires auth | Role | Data source | Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1a | 로그인/프로필 선택 | Login hub | `AuthPage` (select) | `/` | `/` (unchanged) | direct nav | n/a | No | any | REAL_API | IMPLEMENTED_MATCH | `App.tsx:36` |
| 1a-1 | 순수 로그인 | Admin ID/PW login | `AuthPage`→`AdminLoginView` | `/` (internal mode) | `/` (unchanged) | link from 1a | n/a | No | admin | REAL_API | IMPLEMENTED_MATCH | `AdminLoginView.tsx` |
| 1b | 가족 홈 | Home hub (per-service hero cards) | **none found** | — | — | — | — | — | — | — | **SCREEN_EXISTS_ROUTE_MISSING** | No dedicated home-hub component found; `/dashboard` serves as the de facto post-login landing instead (see 1c) |
| 1c | 포인트 잔치 | Mission/point gamification | `UserDashboard` | `/dashboard` | unchanged | Dock "마크포인트" | dashboard | Yes | player | REAL_API | IMPLEMENTED_MATCH (naming caveat: Dock label "마크포인트" ≠ design's "포인트 잔치"/"몽글" scheme — naming-only, not a route defect, carried to non-blocking list) | `UserDashboard/index.tsx` |
| 1d | 대화 | Chat / Room List | `DoranLanding` | `/naran/doran` | unchanged | Dock "와글와글" | doran | Yes | player | **FIXTURE** (not wired to real API) | IMPLEMENTED_MATCH (structure), flagged for data-source gap | `DoranLanding.tsx:250-252` dev notice |
| 1e | 관리자·포인트 관리 | Admin point ledger | `PointView` | `/admin/points` | unchanged | Dock/nav | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH | `PointView.tsx:32` |
| 1f | 나·프로필 | Player profile | `ProfileCard` (embedded widget only) | none (embedded in `/dashboard`) | — | — | — | — | — | — | SCREEN_EXISTS_ROUTE_MISSING (exists as a dashboard widget, not a navigable screen) | `UserDashboard/components/ProfileCard.tsx` |
| 1g | 가족 일정 | Calendar | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | grep found no calendar feature |
| 1h | 앨범 | Album | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | grep found no album feature |
| 1i | 할 일 | To-dos | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | grep found no to-do feature |
| 1j | PIN 입력 | PIN entry | `AuthPage`→`PinInputView` | `/` (internal mode) | unchanged | link from 1a | n/a | No | player | REAL_API | IMPLEMENTED_MATCH (state variant of 1a) | `PinInputView.tsx` |
| 1j-1 | PIN 잠김 | Lockout state | `AuthPage`→`PinInputView` locked state | `/` (internal state) | unchanged | auto (failed attempts) | n/a | No | player | REAL_API | STATE_NO_ROUTE_REQUIRED | not a separate route by design |
| 1k | 미션 상세+인증 제출 | Mission detail/proof submit | `MissionList`/`MissionProposal` (player) | `/dashboard` (in-page) | unchanged | list item click | n/a | Yes | player | REAL_API | MODAL_NO_ROUTE_REQUIRED (assumed — component exists, exact modal-vs-inline UI not deeply re-verified this pass) | `UserDashboard/components/MissionList.tsx`, `MissionProposal.tsx` |
| 1l | 포인트 사용/보상 교환 | Point redemption | not confirmed as a distinct redeem flow | `/dashboard` (partial — deductions only) | — | — | — | Yes | player | REAL_API (partial) | **SCREEN_EXISTS_ROUTE_MISSING** (not deeply verified — `DeductionAccordion` shows deduction history, not a redeem/spend action; no dedicated redeem UI found) | `UserDashboard/components/DeductionAccordion.tsx` |
| 1m | 관리자 승인 대기함 | Mission approval queue | `MissionView` (admin) | `/admin/missions` | unchanged | Dock/nav | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH | `MissionView.tsx:78` |
| 1n | 알림 목록 | Notifications | `NotificationView` (admin only confirmed) | `/admin/notifications` | unchanged | bell icon | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH (admin-side only; player-side notification list not found — flagged) | `NotificationView.tsx:12` |
| 1o | 일정 추가 폼 | Add calendar event | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | tied to missing 1g |
| 1p | 사진 상세 뷰어 | Photo viewer | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | tied to missing 1h |
| 1q | 가족 구성원 관리 | Player/member management | `PlayerView` | `/admin/players` | unchanged | Dock/nav | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH | `PlayerView.tsx:39` |
| 1r | 온보딩/가족 만들기 | Family creation onboarding | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | grep for "온보딩"/"가족 만들기"/family-create found nothing in FE |
| 1s | 미션 반려 확인 | Mission rejection reason | assumed part of `MissionView` reject action | `/admin/missions` (in-page) | unchanged | reject button | n/a | Yes | admin | REAL_API | MODAL_NO_ROUTE_REQUIRED (not deeply re-verified this pass) | `MissionView.tsx` (not line-confirmed) |
| 1t | 가족 채팅방 설정 | Room settings | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | no room-settings UI found in `platform/doran/**` |
| 1u | PIN 변경 | Change PIN | `PinChangeModal` — **admin-initiated only**, not player self-service | `/admin/players` (in-page) | unchanged (admin scope) | admin action | n/a | Yes | admin | REAL_API | IMPLEMENTED_ROUTE_MISMATCH (design shows a player-facing settings screen; actual implementation is admin-managing-player, a different actor) | `PlayerView/components/PinChangeModal.tsx` |
| 1v | 관리자 가족규칙/포인트정책 | Family rules/point policy | `ConfigView` (assumed) | `/admin/config` | unchanged | Dock/nav | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH (not deeply re-verified for full rule-set coverage) | `ConfigView.tsx:14` |
| 1w | 앨범 검색 결과 | Album search | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | tied to missing 1h |
| 1x | 자녀 주간 리포트 | Weekly report | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | not found in this pass |
| 1y | 에러/빈 상태 (3 variants) | Empty/error state pattern | `EmptyState`/`ErrorState`/`LoadingState` (shared, `platform/doran/components`) | in-page (any route) | unchanged | automatic | n/a | n/a | n/a | n/a | STATE_NO_ROUTE_REQUIRED | `DoranLanding.tsx:188-225` uses exactly this pattern |
| 1z | 기본 모달 폼 (관리자 미션 생성) | Mission create modal | `MissionView` create modal (assumed) | `/admin/missions` (in-page) | unchanged | "+ 새 미션"/"🗂️ 미션 관리" button | n/a | Yes | admin | REAL_API | MODAL_NO_ROUTE_REQUIRED | per `CLAUDE.md` P7-PATCH-003 |
| 2a | 사용자 관리 상세 | Player detail | `PlayerView` detail (assumed) | `/admin/players` (in-page) | unchanged | list item click | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH | `PlayerView.tsx` |
| 2b | 사진/파일 전체보기 | Chat media gallery | none confirmed | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION (not deeply checked against legacy `ChatModal`) | — |
| 2c | 레벨업 축하 모달 | Level-up celebration | `ConfettiEffect` | `/dashboard` (in-page) | unchanged | mission approval trigger | n/a | Yes | player | REAL_API | IMPLEMENTED_MATCH | `UserDashboard/components/ConfettiEffect.tsx`, `CLAUDE.md` P7-PATCH-005 |
| 2d | 비밀번호 찾기 | Forgot password | none found (players use PIN, not password) | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION or NOT_PRODUCT_SCREEN (unclear which actor this applies to — admin ID/PW login has no forgot-password flow found either) | grep found nothing |
| 2e | 미션 목록 관리 | Mission list management | `MissionView` | `/admin/missions` | unchanged | Dock/nav | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH | `MissionView.tsx` |
| 2f | 자녀 초대 승인 | Child invite approval | none found in FE | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | grep for "초대"/"invite" found 0 FE files |
| 2g | 채팅 답장 UI | Reply/long-press menu | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | not in `DoranLanding`/`platform/doran/components` |
| 2h | 포인트 교환 확인 다이얼로그 | Redeem confirm | tied to missing 1l | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 1l |
| 2i | 부모 대시보드 | Admin/parent dashboard | `DashboardView` | `/admin` (index) | unchanged | default admin landing | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH | `DashboardView.tsx:49` |
| 2j | 아이 리워드샵 | Reward shop | tied to missing 1l | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 1l |
| 2k | 설정 전체 목록 | Settings index | `ConfigView` exists but scoped to **admin app-config**, not a player-facing personal settings index | `/admin/config` | — | Dock/nav | n/a | Yes | admin | REAL_API | IMPLEMENTED_ROUTE_MISMATCH (design implies a general/player settings hub; actual is admin-only app config) | `ConfigView.tsx:14` |
| 2l | 미션 만들기 폼 (전체 화면) | Mission create, full page | implemented as a **modal** (`1z`), not a full page | `/admin/missions` (in-page modal) | — | button | n/a | Yes | admin | REAL_API | IMPLEMENTED_VISUAL_MISMATCH (design shows full-screen form; product uses a modal for the same function) | same as 1z |
| 2m | 미션 상세 폼 (수정) | Mission edit | `MissionView` edit modal (assumed) | `/admin/missions` (in-page) | unchanged | edit button | n/a | Yes | admin | REAL_API | MODAL_NO_ROUTE_REQUIRED | `MissionView.tsx` |
| 2n | 알림 세부설정 | Notification preferences | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | not in `NotificationView.tsx` scope confirmed |
| 2o | 포인트 정책 편집 | Point policy editor | `ConfigView` (assumed, `point_cycle` config per `CLAUDE.md`) | `/admin/config` | unchanged | Dock/nav | n/a | Yes | admin | REAL_API | IMPLEMENTED_MATCH (not deeply re-verified this pass) | `CLAUDE.md` P-FEATURE-POINT-CYCLE-001 |
| 2p | 사용자 관리·초대 목록 | User invite list | not found (no invite feature) | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 2f |
| 2q | 가족 규칙 안내 | Family rules info page | none found as a dedicated info screen | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | not found |
| 2r | 가족 활동 로그 | Activity log | none found in FE (backend `login_log` domain exists but no FE list screen found) | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION (FE) | not found |
| 2s | PIN 최초 설정 | First-time PIN setup | not confirmed distinctly from 1u/1j | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION or overlapping with existing PIN flows (not deeply distinguished this pass) | — |
| 2t | 관리자 알림 발송 | Send announcement | not confirmed in `NotificationView` | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION (not deeply re-verified) | — |
| 2u | 일정 상세 보기 | Event detail | tied to missing 1g | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 1g |
| 2v | 앨범 업로드 진행 | Upload progress | tied to missing 1h | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 1h |
| 2w | 가족 초대 수락 | Accept family invite | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 2f |
| 2x | 미션 통계 대시보드 | Mission stats dashboard | `DashboardView` has some stats; dedicated stats view not confirmed | `/admin` (partial) | — | — | — | Yes | admin | REAL_API (partial) | IMPLEMENTED_ROUTE_MISMATCH or FUTURE_IMPLEMENTATION (ambiguous, not deeply re-verified) | `DashboardView.tsx` |
| 2y | 앨범 공유설정 | Album sharing | tied to missing 1h | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 1h |
| 2z | 프로필 편집 | Edit profile | `ProfileCard` appears view-only; edit action not confirmed | `/dashboard` (partial) | — | — | — | Yes | player | REAL_API (partial) | SCREEN_EXISTS_ROUTE_MISSING or IMPLEMENTED_VISUAL_MISMATCH (not deeply re-verified) | `ProfileCard.tsx` |
| 3a | 가족 캘린더 공유 | Calendar sharing | tied to missing 1g | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 1g |
| 3b | 미션 통계 필터 | Stats filter modal | tied to 2x | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 2x |
| 3c | 가족 게시판 | Community board | **none anywhere** — confirmed no such backend domain exists either (per the prior session's domain audit: `all_models.py` import list has no board/post model) | — | — | — | — | — | — | — | **NOT_PRODUCT_SCREEN today / FUTURE_IMPLEMENTATION** | cross-checked against backend domain list, not just FE |
| 3d | 댓글 작성 화면 | Write comment | tied to 3c | — | — | — | — | — | — | — | NOT_PRODUCT_SCREEN today / FUTURE_IMPLEMENTATION | same as 3c |
| 3e | 인기 게시글 모아보기 | Trending posts | tied to 3c | — | — | — | — | — | — | — | NOT_PRODUCT_SCREEN today / FUTURE_IMPLEMENTATION | same as 3c |
| 3f | 설정·언어 설정 | Language settings | none found (no i18n framework in `package.json`) | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | confirmed no i18n dependency |
| 3g | 설정·화면 테마 | Theme settings | none found (no theme-toggle store/logic found) | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | not found |
| 3h | 설정·계정 탈퇴 확인 | Delete account confirm | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | not found |
| 3i | 가족 초대 취소 | Cancel invite | tied to missing 2f/2p | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | same gap as 2f |
| 3j | 검색 전체 | Global search | none found | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | no search UI or endpoint referenced in FE |
| 3k | 위젯 갤러리 | Widget gallery (home customization) | none found — tied to missing 1b (홈) | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION | depends on 1b existing first |
| 3l | 바로가기 편집 | Shortcut/Dock editor | **none found — this is almost certainly the intended FE home for user-configurable Dock settings** (per PM's Wave 4 rule §7 "Dock은... 사용자 설정 계약을 따른다" and the prior task's `DOCK_EXISTING_CONTRACT_AUDIT.md` finding that no backend supports it yet) | — | — | — | — | — | — | — | FUTURE_IMPLEMENTATION — **explicitly blocked on the same backend gap already recorded in the prior repair task**, not something to build here | cross-referenced with `DOCK_EXISTING_CONTRACT_AUDIT.md` from the design-handoff repair session |
| 1z0–1z5 | (hidden/superseded drafts) | — | — | — | — | — | — | — | — | — | NOT_PRODUCT_SCREEN | `display:none`, superseded per `SOURCE_SCREEN_INVENTORY.md` |

## Summary counts

| Status | Count |
|---|---|
| IMPLEMENTED_MATCH | 15 |
| IMPLEMENTED_ROUTE_MISMATCH | 3 |
| IMPLEMENTED_VISUAL_MISMATCH | 2 |
| SCREEN_EXISTS_ROUTE_MISSING | 4 |
| MODAL_NO_ROUTE_REQUIRED | 4 |
| STATE_NO_ROUTE_REQUIRED | 2 |
| NOT_PRODUCT_SCREEN | 9 (incl. 6 hidden + 3c/3d/3e) |
| FUTURE_IMPLEMENTATION | 33 |

**Read this table as an honest routing/implementation-status snapshot, not a build plan.** Per the task's own explicit prohibitions, none of the `FUTURE_IMPLEMENTATION` rows are built in this task — they are documented so a later, properly-scoped implementation wave has an accurate starting point instead of rediscovering the same gaps.

## Minimum-scope route repair identified (carried into the final report)

Cross-referencing this matrix against Wave 2's audit, **the only concrete, evidence-backed "broken route" repair in scope for Wave 4 is the missing top-level 404/fallback route** (§1 of `MONGLE_ROUTE_AUDIT.md`). Every other gap in this matrix is either:
- a **known, already-PM-flagged, backend-blocked item** (Dock 4-slot configurability, 3l shortcut editor) — not to be hardcoded around, per explicit prohibition, or
- a **genuinely new/future feature** (calendar, album, board, search, widget gallery, onboarding, invites) — out of "최소 경로 복구" scope, per explicit prohibition against full screen rebuilds.

No canonical route rename (e.g. `/naran/doran` → `/mongle`) is adopted in this matrix, per task rule §7.11 — current valid routes are preserved as-is.
