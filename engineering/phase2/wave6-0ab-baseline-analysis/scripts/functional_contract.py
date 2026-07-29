#!/usr/bin/env python3
import csv
OUT = "/tmp/mongle-wave6-0ab/6.0B/functional_contract_matrix.csv"

rows = [
 # A1 로그인
 dict(screen="A1", function="Player profile fetch(GET /api/players)", classification="MUST_PRESERVE",
   evidence="pages/Auth/api/authApi.ts 존재 확인(파일 리스트), pages/Auth/components/PlayerSelectView.tsx 소비 — CLAUDE.md 컨텍스트상 실제 백엔드 endpoint"),
 dict(screen="A1", function="Player selection → PIN flow(select→pin 2-step)", classification="MUST_PRESERVE",
   evidence="pages/Auth/index.tsx: Mode='select'|'pin'|'admin' state machine 코드 직접 확인"),
 dict(screen="A1", function="PIN error / locked-state 표시(5회 실패 잠금)", classification="MUST_PRESERVE",
   evidence="승인자료 A1 스크린 자체가 이 상태를 명시(지호 카드), CLAUDE.md Phase1 auth 도메인에 locked player 로직 명시 존재 — 코드 상세는 NOT_VERIFIED(PinInputView.tsx 미상세열람)"),
 dict(screen="A1", function="Admin entry(관리자 로그인 별도 모드)", classification="MUST_PRESERVE",
   evidence="pages/Auth/index.tsx Mode='admin' + AdminLoginView.tsx 컴포넌트 존재 확인"),
 dict(screen="A1", function="Abort-cancellation on player fetch(AbortController)", classification="NOT_VERIFIED",
   evidence="CLAUDE.md 프로젝트 규칙상 필수 패턴으로 문서화되어 있으나 이번 세션에서 authApi.ts 소스 직접 열람은 하지 않음(정적 파일 존재만 확인)"),
 dict(screen="A1", function="세션 생성 + redirect(로그인 성공 시 role별 분기)", classification="MUST_PRESERVE",
   evidence="pages/Auth/index.tsx: isLoggedIn && <Navigate to={isAdmin?'/admin':'/dashboard'}/> 코드 직접 확인"),
 dict(screen="A1", function="Accessibility(스크린리더 라벨 등)", classification="NOT_VERIFIED",
   evidence="컴포넌트 상세 미열람"),
 dict(screen="A1", function="순수 ID/PW 로그인 폼(승인자료 A1-S1)", classification="KNOWN_GAP",
   evidence="현재 구현에는 select→pin 경로와 admin ID/PW 경로만 있고, '일반 계정'용 ID/PW 로그인 폼은 관측되지 않음 — 승인자료 A1-S1이 요구하는 화면과 정확히 대응하는 현재 화면 없음"),

 # A2 홈/Shell
 dict(screen="A2", function="Account Context(로그인 계정 식별)", classification="MUST_PRESERVE",
   evidence="useAuthStore(token/player/isAdmin) — App.tsx/MongleAppShell.tsx에서 직접 소비 확인"),
 dict(screen="A2", function="Family Context(활성 가족 로드/전환)", classification="MUST_PRESERVE",
   evidence="useFamilyContextStore.ts + FamilyContextLoader.tsx: load()/selectFamily()/reset() 코드 직접 확인, canonical storage key mongle.activeFamily.{accountId} 확인"),
 dict(screen="A2", function="Header(브랜드+FamilySwitcher+계정영역+로그아웃)", classification="MUST_PRESERVE",
   evidence="MongleAppShell.tsx header 블록 코드 직접 확인"),
 dict(screen="A2", function="Dock/desktop nav(서비스별 가시성 필터: hasFamily/hasPermission)", classification="MUST_PRESERVE",
   evidence="MongleAppShell.tsx navItems 배열의 visible 조건(hasFamily, hasPermission('family.read') 등) 코드 직접 확인"),
 dict(screen="A2", function="Service eligibility(doran/family 권한 기반 노출)", classification="MUST_PRESERVE",
   evidence="serviceStatus('doran'), hasPermission('family.read') 등 코드 직접 확인"),
 dict(screen="A2", function="Logout(canonical+legacy storage key 동시 제거)", classification="MUST_PRESERVE",
   evidence="specs-mongle/01-shell.spec.ts 'explicit logout clears both canonical and legacy keys' 테스트로 명세·검증됨"),
 dict(screen="A2", function="Storage 계약(canonical 우선, legacy read-only fallback, invalid legacy 무시)", classification="MUST_PRESERVE",
   evidence="useFamilyContextStore.ts canonicalStorageKey/legacyStorageKey 함수 + specs-mongle 5개 테스트로 코드 레벨 검증"),
 dict(screen="A2", function="safe-area 처리(노치/홈인디케이터 대응)", classification="NOT_VERIFIED",
   evidence="MongleAppShell.module.css 상세 미열람"),
 dict(screen="A2", function="가족 홈 화면 자체(GreetingHeader/PromoCard/ActivityCard/ServiceGrid)", classification="MISSING",
   evidence="/family 라우트(FamilyLanding.tsx)는 이름+관계만 표시하는 텍스트 스텁 — 승인 A2가 요구하는 어떤 zone도 구현되어 있지 않음(코드 직접 확인, 15줄 전체 열람)"),

 # A3 마크포인트
 dict(screen="A3", function="Points/미션 조회 및 상태(mission list, status)", classification="MUST_PRESERVE",
   evidence="dashboardApi.ts: MissionResponse, DailyPointResponse 등 실제 인터페이스 정의 확인(백엔드 연동, fixture 아님)"),
 dict(screen="A3", function="Deduction(차감) 조회", classification="MUST_PRESERVE", evidence="dashboardApi.ts DeductionResponse 인터페이스 확인"),
 dict(screen="A3", function="Level(레벨 시스템)", classification="MUST_PRESERVE",
   evidence="CLAUDE.md Phase7 P7-PATCH-005 LEVEL-001(level_tiers 테이블, total_earned 물리화) — 백엔드 구현 기록 존재, FE 상세는 NOT_VERIFIED(ExpBar.tsx 등 미상세열람)"),
 dict(screen="A3", function="Cheer(응원 메시지)", classification="MUST_PRESERVE", evidence="dashboardApi.ts CheerResponse 확인, CheerModal.tsx 파일 존재"),
 dict(screen="A3", function="승인 플로우(미션 승인/거절)", classification="MUST_PRESERVE",
   evidence="CLAUDE.md Phase2/Phase7(P7-PATCH-002 proposed 미션 거절 버그수정 기록) — 실제 운영 이력 존재하는 핵심 기능"),
 dict(screen="A3", function="필터/데이터 새로고침/에러 처리", classification="NOT_VERIFIED", evidence="hooks/useDashboard.ts 상세 미열람"),
 dict(screen="A3", function="포인트 사이클 요약(daily/weekly/...)", classification="MUST_PRESERVE",
   evidence="dashboardApi.ts PointCycleSummary 인터페이스 확인, CLAUDE.md P-FEATURE-POINT-CYCLE-001 기록"),

 # A4 와글와글
 dict(screen="A4", function="Doran 구독 자격 확인(family.services에서 doran status)", classification="MUST_PRESERVE",
   evidence="DoranLanding.tsx: serviceStatus, pageState='disabled' when status!=='active' — 코드 직접 확인"),
 dict(screen="A4", function="Room 선택(query param 기반, ?room=id)", classification="MUST_PRESERVE",
   evidence="DoranLanding.tsx useSearchParams/selectRoom 코드 직접 확인"),
 dict(screen="A4", function="Desktop auto-selection(≥701px 첫 룸 자동 선택, 1회만)", classification="CURRENT_TEMPORARY",
   evidence="DoranLanding.tsx didAutoSelectRef 코드 직접 확인 + 코드 주석 자체가 'PM 정책' 표현 사용 — PM 재확인 전까지 임시 정책으로 간주"),
 dict(screen="A4", function="Query rewriting(뒤로가기 시 pushedSelectionRef 분기)", classification="CURRENT_TEMPORARY",
   evidence="DoranLanding.tsx handleBack 코드 직접 확인, 명세 문서(FAMILY_PLATFORM_DESIGN_IMPLEMENTATION_SOURCE_V1 등)와 1:1 대조 안 됨"),
 dict(screen="A4", function="Message state(전송 pending/failed/retry)", classification="FIXTURE_ONLY",
   evidence="DoranLanding.tsx Conversation: handleSend은 window.setTimeout(...,500)으로 항상 'failed' 하드코드 — 실제 API 호출 없음, 코드 직접 확인"),
 dict(screen="A4", function="Composer(입력/전송/읽기전용)", classification="FIXTURE_ONLY",
   evidence="isReadOnly = room.kind==='SERVICE'만 로컬 판정, 실제 서버 검증 없음"),
 dict(screen="A4", function="Loading/empty/unavailable 3-state", classification="FIXTURE_ONLY",
   evidence="pageState는 실제로 previewState 쿼리파라미터로만 도달 가능(resolvePreviewPageState) — 실제 데이터 유무로 자연 도달하는 경로 아님, DEV 전용 안내문구('UX Gate 미리보기') 코드 직접 확인"),
 dict(screen="A4", function="Fixture vs 실제 API 경계", classification="FIXTURE_ONLY",
   evidence="platform/doran/preview/*.ts 전체가 하드코드 상수 — GROUP/DIRECT/SERVICE 3종 kind 데이터 전부 fixture, 실제 /api/families/{family_id}/doran 호출 코드 없음(App 전체에서 'doran' 관련 fetch 호출 grep 결과 preview 폴더 외 미발견)"),
 dict(screen="A4", function="GROUP 메시징(승인자료 A4의 실제 대상)", classification="FIXTURE_ONLY",
   evidence="doranPreviewRooms 중 kind='GROUP'인 항목이 UI로 렌더링되나 실제 백엔드 연동 없음 — 승인자료가 요구하는 '기능'은 아직 시각적 뼈대만 존재"),

 # A5 관리자 포인트
 dict(screen="A5", function="Admin auth/RBAC", classification="MUST_PRESERVE",
   evidence="App.tsx AdminProtectedRoute(isLoggedIn && isAdmin) 코드 직접 확인, CLAUDE.md get_current_admin 의존성 기록"),
 dict(screen="A5", function="Point data 조회", classification="MUST_PRESERVE", evidence="adminApi.ts 존재 확인(파일 리스트), PointView.tsx가 usePointView 훅으로 소비"),
 dict(screen="A5", function="필터(플레이어별)", classification="MUST_PRESERVE", evidence="PointView.tsx import에 PlayerPointSummary 컴포넌트 확인"),
 dict(screen="A5", function="행 액션(편집/삭제) + 다이얼로그", classification="MUST_PRESERVE",
   evidence="PointView.tsx import: AddDeductionModal, EditDeductionModal 존재 확인 — 승인자료(A5)에는 이 다이얼로그의 시각 이미지가 없어(SOURCE_MISSING) 현재 구현이 승인 시각보다 기능적으로 앞서 있음"),
 dict(screen="A5", function="Pagination", classification="NOT_VERIFIED", evidence="usePointView.ts 상세 미열람"),
 dict(screen="A5", function="Loading/error 상태 + mutation", classification="NOT_VERIFIED", evidence="usePointView.ts 상세 미열람"),
 dict(screen="A5", function="Permission boundary(사이드바 6항목 중 승인자료엔 5개 화면 없음)", classification="APPROVED_SOURCE_GAP",
   evidence="AdminDashboard/views/에 ChatView/ConfigView/DashboardView/FeedbackView/MissionView/NotificationView/PlayerView/PointView 8개 View 존재 — 승인자료(A5)는 이 중 PointView 1개만 시각화되어 있음"),
]

fieldnames = ["screen","function","classification","evidence"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {len(rows)} rows")
