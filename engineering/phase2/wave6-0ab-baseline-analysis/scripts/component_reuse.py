#!/usr/bin/env python3
import csv
OUT = "/tmp/mongle-wave6-0ab/6.0B/component_reuse_matrix_v2.csv"

rows = [
 dict(component="shared/components/Avatar", consumers="4(ChatHeader, MessageBubble, RoomItem, DoranLanding — grep-verified)",
   props_api="alt/fallback/size/className(관측, 상세 props 인터페이스 미열람)", states_variants="fallback 이니셜 문자 지원(승인 A1/A3의 이니셜 아바타 패턴과 구조적으로 대응)",
   styling_source="Avatar.module.css", accessibility="NOT_VERIFIED", approved_screen_match="A1/A2/A3/A4/EXTRA-01 전 화면의 원형 이니셜 아바타 패턴과 대응 후보",
   functional_coupling="낮음(순수 표시 컴포넌트로 추정)", extraction_risk="LOW(이미 4곳 소비, 승격 조건 충족)",
   expected_wave="6.1(승인 아바타 크기/색 규칙 반영 시 우선 후보)", test_coverage="NOT_VERIFIED(전용 테스트 없음, e2e 간접 커버만)",
   classification="REUSE_AS_IS"),
 dict(component="shared/components/Button", consumers="0(grep 결과 현재 소비처 없음)", props_api="variant: primary|ghost|dangerSm(코드 확인)",
   states_variants="3 variant만 존재, 승인자료의 primary/outline pill 버튼 다양성(A1-S1 등)과 매핑 미검증",
   styling_source="Button.module.css", accessibility="NOT_VERIFIED", approved_screen_match="A1-S1 PrimaryLoginButton/SecondaryButton, A5 차감추가버튼 후보",
   functional_coupling="없음(미사용)", extraction_risk="LOW(이미 primitive로 존재하나 채택 전)",
   expected_wave="6.1(A1-S1/A5 버튼 구현 시 최우선 채택 후보)", test_coverage="NOT_VERIFIED", classification="REUSE_AS_IS(단, 현재 실사용 0건이므로 두 번째 이상 consumer 확보 전에는 검증 부족)"),
 dict(component="shared/components/Card", consumers="1(ServiceActionCard만)", props_api="NOT_VERIFIED(상세 미열람)",
   states_variants="NOT_VERIFIED", styling_source="Card.module.css", accessibility="NOT_VERIFIED",
   approved_screen_match="A2/A3/A5의 반복 카드 패턴(ProfileSummaryCard/RecentActivityCard/StatCard 등) 후보",
   functional_coupling="낮음", extraction_risk="MEDIUM(단일 consumer라 일반화 정도 미검증)",
   expected_wave="6.1 이후(2번째 consumer 확보 후 재평가)", test_coverage="NOT_VERIFIED",
   classification="SCREEN_LOCAL_KEEP(단일 consumer, 브리프 규칙상 지금 승격 권고 불가)"),
 dict(component="shared/components/IconButton", consumers="2(ChatComposer, ChatHeader)", props_api="NOT_VERIFIED",
   states_variants="NOT_VERIFIED", styling_source="IconButton.module.css", accessibility="NOT_VERIFIED",
   approved_screen_match="A1 chevron 버튼, A4 첨부/카메라 버튼, A5 편집/삭제 아이콘 버튼 후보",
   functional_coupling="낮음", extraction_risk="LOW(2번째 consumer 확보됨)", expected_wave="6.1",
   test_coverage="NOT_VERIFIED", classification="REUSE_AS_IS"),
 dict(component="shared/components/MainLogo", consumers="1(Auth/PlayerSelectView.tsx)", props_api="NOT_VERIFIED",
   states_variants="NOT_VERIFIED", styling_source="MainLogo.module.css", accessibility="NOT_VERIFIED",
   approved_screen_match="A1/A2/A3/A4/A5 전 화면의 반복 로고 워터마크와 대응 후보(단, 승인자료 로고 에셋 자체와 현재 구현 로고 에셋이 동일 파일인지 NOT_VERIFIED)",
   functional_coupling="낮음", extraction_risk="MEDIUM(단일 consumer)", expected_wave="6.1 이후(2번째 consumer 확보 후 재평가)",
   test_coverage="NOT_VERIFIED", classification="SCREEN_LOCAL_KEEP"),
 dict(component="shared/components/Toast + ToastContainer", consumers="App.tsx 전역 마운트(ToastContainer) — 다수 페이지의 개별 토스트 트리거는 NOT_VERIFIED(전수 미확인)",
   props_api="NOT_VERIFIED", states_variants="success/error 등 추정(CLAUDE.md 문서 근거)", styling_source="Toast.module.css/ToastContainer.module.css",
   accessibility="NOT_VERIFIED", approved_screen_match="승인자료에는 토스트/알림 배너 화면이 없음(N/A)",
   functional_coupling="낮음(전역 상태 스토어 useToastStore 경유)", extraction_risk="LOW(이미 전역 승격 완료 상태)",
   expected_wave="해당 없음(이미 공용화 완료)", test_coverage="NOT_VERIFIED", classification="REUSE_AS_IS"),
 dict(component="platform/doran/components/* (ChatHeader/RoomItem/MessageBubble/DateDivider/UnreadDivider/ChatComposer/ServiceActionCard/LoadingState/EmptyState/ErrorState, 10개)",
   consumers="1개 파일(DoranLanding.tsx)뿐 — barrel import grep으로 확인, 10개 컴포넌트 전부 동일 단일 소비처",
   props_api="NOT_VERIFIED(개별 상세 미열람)", states_variants="Wave 6.0B 코드 주석으로 볼 때 승인 A4 시각 규범을 이미 상당 부분 반영 시도된 상태로 추정",
   styling_source="각 컴포넌트별 .module.css", accessibility="NOT_VERIFIED",
   approved_screen_match="A4(가족 대화)와 직접 대응 — 이미 컴포넌트 단위로 잘게 쪼개져 있어 구조적으로는 재사용 준비가 되어 있음",
   functional_coupling="중간(DoranLanding의 fixture 데이터 구조에 결합)", extraction_risk="MEDIUM(단일 consumer라 브리프 규칙상 지금 전역 승격 대상 아님 — 이미 platform/doran 내부로는 응집되어 있어 사실상 도메인-로컬 shared로 볼 수 있음)",
   expected_wave="6.1(Room List 화면이 신설되면 자연히 2번째 consumer 발생 가능)", test_coverage="specs-mongle/01-shell.spec.ts가 간접적으로 렌더링을 검증(하지만 컴포넌트 단위 직접 테스트는 아님)",
   classification="REUSE_WITH_VARIANT(도메인 내부에서는 이미 재사용 가능 구조, 전역 shared 승격은 아직 근거 부족)"),
 dict(component="shared/components/PhotoUpload", consumers="NOT_VERIFIED(이번 세션에서 grep 미수행, CLAUDE.md 문서상 PlayerManager+CheerEditor 2곳 사용 기록)",
   props_api="NOT_VERIFIED", states_variants="NOT_VERIFIED", styling_source="PhotoUpload.module.css",
   accessibility="NOT_VERIFIED", approved_screen_match="승인자료에는 사진 업로드 UI 자체가 없음(A4의 사진 3장은 placeholder이지 업로드 폼 아님) — N/A",
   functional_coupling="NOT_VERIFIED", extraction_risk="LOW(문서상 이미 2 consumer)", expected_wave="해당 없음(레거시 AdminDashboard 전용 기능으로 추정)",
   test_coverage="NOT_VERIFIED", classification="REUSE_AS_IS(CLAUDE.md 문서 근거, 이번 세션 코드 재검증은 하지 않음 — NOT_VERIFIED 표시 유지)"),
 dict(component="AdminDashboard/components/* (AdminModal/AdminToast/CycleIndicator/DateSelector/MobileDrawer/MobileHeader/PlayerBadge/PlayerTab/Sidebar/StatCard — CLAUDE.md 문서 근거)",
   consumers="NOT_VERIFIED(이번 세션 grep 미수행)", props_api="NOT_VERIFIED", states_variants="NOT_VERIFIED",
   styling_source="각 .module.css(문서 근거)", accessibility="NOT_VERIFIED",
   approved_screen_match="A5(관리자 포인트 관리)의 AdminSidebar/StatCard/DataTable과 명칭·역할 대응 후보 — 단, 승인자료의 라이트 톤 sidebar와 현재 구현의 다크 sidebar(--admin-sidebar-bg:#1e1b4b) 간 시각 불일치 확인됨(TOKEN_IMPLEMENTATION_AUDIT_V2 참조)",
   functional_coupling="NOT_VERIFIED", extraction_risk="MEDIUM(시각 재구성 필요, 기능 결합도 미검증)", expected_wave="6.1",
   test_coverage="specs/03-admin.spec.ts(3 tests, 실행 가능 여부는 phase0 compose 의존 — E2E_COVERAGE_MAP 참조)",
   classification="REUSE_WITH_VARIANT(명칭은 대응하나 시각 톤 전면 재구성 필요 추정)"),
]

fieldnames = ["component","consumers","props_api","states_variants","styling_source","accessibility",
  "approved_screen_match","functional_coupling","extraction_risk","expected_wave","test_coverage","classification"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {len(rows)} rows")
