#!/usr/bin/env python3
import csv
OUT = "/tmp/mongle-wave6-0ab/6.0B/screen_component_gap_matrix_v2.csv"

rows = [
 dict(screen_id="A1", approved_zone="ProfileSelectorCard(3 PlayerCard)", current_route="/", current_component="pages/Auth/components/PlayerSelectView.tsx",
   current_file="frontend/src/pages/Auth/components/PlayerSelectView.tsx", approved_measurement="78px 아바타, 999px pill 레벨배지, 44px chevron 버튼(단 38px 관측)",
   current_implementation="NOT_VERIFIED(상세 미열람, 파일 존재만 확인)", visual_delta="NOT_VERIFIED", functional_dependency="GET /api/players",
   token_dependency="브랜드 accent, ink, muted 텍스트", asset_dependency="아바타 이니셜(사진 없음, 승인자료와 동일 패턴 추정)",
   reuse_decision_candidate="PlayerCard(이미 자체 컴포넌트로 존재: Auth/components/PlayerCard.tsx)", change_risk="MEDIUM",
   pm_decision="시각 재구성 범위", expected_test="specs/01-login.spec.ts 확장", expected_screenshot="A1 desktop/mobile",
   gap_classification="PARTIAL(구조적으로 대응 컴포넌트 존재, 시각 1:1 일치 여부 NOT_VERIFIED)"),
 dict(screen_id="A1", approved_zone="AdminEntryRow(관리자 로그인 링크)", current_route="/", current_component="pages/Auth/index.tsx(Mode='admin' 전환)",
   current_file="frontend/src/pages/Auth/index.tsx, components/AdminLoginView.tsx", approved_measurement="하단 고정 행, gear 아이콘+관리자로그인 텍스트",
   current_implementation="별도 전체화면 모드 전환(AdminLoginView)으로 구현 — 승인자료는 같은 화면 하단 링크 형태", visual_delta="MATERIAL_VISUAL_DELTA(추정, 화면전환 방식 자체가 다름)",
   functional_dependency="POST /api/auth/admin/login", token_dependency="N/A", asset_dependency="N/A",
   reuse_decision_candidate="N/A", change_risk="LOW(기능은 이미 존재, 진입 UX만 상이)", pm_decision="진입 UX를 승인자료의 인라인 링크 형태로 맞출지",
   expected_test="N/A", expected_screenshot="A1 admin-entry", gap_classification="PARTIAL"),
 dict(screen_id="A1", approved_zone="A1-S1(순수 ID/PW 로그인 폼)", current_route="N/A(대응 라우트 없음)", current_component="없음",
   current_file="N/A", approved_measurement="LoginFormPanel, TextField x2, PrimaryButton 등(HTML_STRUCTURE_EXTRACTION 참조)",
   current_implementation="없음 — 현재는 select→pin 또는 admin ID/PW 뿐, '일반 계정' ID/PW 로그인 없음", visual_delta="NOT_COMPARABLE(구현 자체 없음)",
   functional_dependency="APPROVED_SOURCE_GAP 아님(현재 제품이 이 로그인 방식을 아예 채택하지 않았을 가능성) — PM 확인 필요", token_dependency="N/A", asset_dependency="N/A",
   reuse_decision_candidate="N/A", change_risk="UNKNOWN(신규 기능이 될 수도, 폐기된 설계일 수도 있음)",
   pm_decision="A1-S1을 실제로 구현할지, 승인자료의 참고용 대안일 뿐인지", expected_test="N/A", expected_screenshot="N/A",
   gap_classification="MISSING"),

 dict(screen_id="A2", approved_zone="전체(GreetingHeader+PromoCard+ActivityCard+ServiceGrid+Dock)", current_route="/family",
   current_component="platform/pages/FamilyLanding.tsx", current_file="frontend/src/platform/pages/FamilyLanding.tsx(15줄 전체 열람)",
   approved_measurement="MEASUREMENT_TABLE_V2 category A/B/C/D 다수", current_implementation="가족명+관계 텍스트만 표시하는 스텁(15줄), 위 5개 zone 중 어느 것도 미구현",
   visual_delta="MATERIAL_VISUAL_DELTA(사실상 100% 미구현)", functional_dependency="useFamilyContextStore(활성 가족만)",
   token_dependency="전체(A2 관련 모든 색/spacing/typography 후보)", asset_dependency="Hero illustration(SOURCE_MISSING), 서비스타일 아이콘(SOURCE_MISSING)",
   reuse_decision_candidate="N/A(아직 컴포넌트 없음)", change_risk="HIGH(신규 구현 규모가 큼)",
   pm_decision="A2를 /family에 구현할지, 별도 라우트를 신설할지, MongleAppShell의 기존 Dock/Header와 어떻게 통합할지",
   expected_test="specs-mongle 신규 스펙 필요", expected_screenshot="A2 mobile", gap_classification="MISSING"),
 dict(screen_id="A2", approved_zone="BottomDock(4탭: 홈/포인트잔치/대화/나)", current_route="전역(MongleAppShell)",
   current_component="platform/shell/MongleAppShell.tsx(mobileNav)", current_file="frontend/src/platform/shell/MongleAppShell.tsx:131-154",
   approved_measurement="grid(4,1fr), 아이콘+라벨, active=보라 필채움+bold", current_implementation="현재는 3항목(마크포인트/와글와글/가족)만, 아이콘 없이 라벨텍스트만(코드 주석: ASSET_GAP_BOTTOM_DOCK_ICONS로 아이콘 의도적 보류)",
   visual_delta="MATERIAL_VISUAL_DELTA(코드 자체가 자인함)", functional_dependency="hasFamily/hasPermission 필터(승인자료는 필터 개념 없음, 고정 4탭)",
   token_dependency="브랜드 accent(active pill)", asset_dependency="9종 승인 아이콘 asset 없음(SOURCE_MISSING, 코드 주석과 일치)",
   reuse_decision_candidate="N/A", change_risk="MEDIUM", pm_decision="PM_DECISION_REQUIRED_BOTTOM_DOCK_ROUTE(코드 주석에 이미 명시된 미해결 항목) — '홈'/'나' 대응 route 신설 여부",
   expected_test="specs-mongle/01-shell.spec.ts 확장", expected_screenshot="Dock mobile", gap_classification="PARTIAL"),

 dict(screen_id="A3", approved_zone="ProfileSummaryCard+MissionListCard", current_route="/dashboard",
   current_component="pages/UserDashboard/index.tsx + components/ProfileCard.tsx, MissionList.tsx", current_file="frontend/src/pages/UserDashboard/components/{ProfileCard,MissionList}.tsx",
   approved_measurement="MEASUREMENT_TABLE_V2 A3 rows(그라디언트 카드, 64% 진행바, 3분할 통계 등)", current_implementation="NOT_VERIFIED(상세 미열람, 레거시 CSS Module 존재 확인만)",
   visual_delta="NOT_VERIFIED", functional_dependency="dashboardApi(MissionResponse/DailyPointResponse — 실 API)",
   token_dependency="레거시 global.css 최초 토큰(§1-15) 사용 추정, 승인 토큰과 미대조", asset_dependency="미션 아이콘(승인=flat icon, 현재 구현은 NOT_VERIFIED)",
   reuse_decision_candidate="MissionList/ProfileCard(레거시 컴포넌트, 재구성 시 승격 여부는 2번째 consumer 필요)", change_risk="MEDIUM(기능 보존 필수, 시각만 재구성 대상)",
   pm_decision="레거시 UserDashboard 전체를 승인 A3 시각으로 재구성할 범위와 순서", expected_test="specs/02-mission.spec.ts", expected_screenshot="A3 mobile",
   gap_classification="PARTIAL(기능 MATCH 추정, 시각 대조는 NOT_VERIFIED)"),

 dict(screen_id="A4", approved_zone="MessageTimeline+Composer(단일 GROUP 룸)", current_route="/wagle",
   current_component="platform/pages/DoranLanding.tsx > Conversation", current_file="frontend/src/platform/pages/DoranLanding.tsx",
   approved_measurement="MEASUREMENT_TABLE_V2 F 카테고리 전체", current_implementation="구조적으로 대응하는 컴포넌트 세트 이미 존재(MessageBubble/DateDivider/UnreadDivider/ChatComposer), 단 fixture 데이터",
   visual_delta="MINOR_RENDERING_NOISE로 추정(TIER1 A4 판정 참조, 구조 이미 근접)", functional_dependency="**FIXTURE_ONLY** — 실제 /api/families/{family_id}/doran 연동 없음",
   token_dependency="--color-chat-own/--color-chat-other(이미 EXACT_MATCH)", asset_dependency="사진 첨부 placeholder(승인=텍스처, 현재=NOT_VERIFIED)",
   reuse_decision_candidate="10개 doran/components(단일 consumer, COMPONENT_REUSE_MATRIX 참조)", change_risk="HIGH(fixture→실제 API 전환이 최대 리스크 항목)",
   pm_decision="실제 백엔드 연동 시점(Doran API 계약은 절대 변경 금지 대상 — /api/families/{family_id}/doran)", expected_test="specs-mongle 확장 필요(현재는 UI 렌더링만 검증, 실 전송 없음)",
   expected_screenshot="A4 mobile", gap_classification="PARTIAL(시각 구조 근접, 기능은 FUNCTION_BLOCKER 수준 — 실동작 없음)"),
 dict(screen_id="A4", approved_zone="Room List(승인자료엔 없음)", current_route="/wagle(room 미선택 상태)", current_component="platform/pages/DoranLanding.tsx(aside.roomList)",
   current_file="frontend/src/platform/pages/DoranLanding.tsx:227-253", approved_measurement="SOURCE_MISSING(승인자료에 이 화면 자체가 없음)",
   current_implementation="GROUP/DIRECT/SERVICE 3종 kind의 RoomItem 리스트 이미 구현(fixture)", visual_delta="NOT_COMPARABLE(승인 대상 없음)",
   functional_dependency="FIXTURE_ONLY", token_dependency="NOT_VERIFIED", asset_dependency="NOT_VERIFIED",
   reuse_decision_candidate="RoomItem(단일 consumer)", change_risk="MEDIUM", pm_decision="현재 구현이 승인자료보다 앞서 나간 Room List/DIRECT/SERVICE 범위를 그대로 승인할지, 승인자료 범위(GROUP 단일룸)로 축소할지",
   expected_test="specs-mongle 확장", expected_screenshot="N/A(승인 없음)", gap_classification="EXTRA_CURRENT_UI"),

 dict(screen_id="A5", approved_zone="AdminSidebar+StatCardRow+DeductionDataTable", current_route="/admin/*",
   current_component="pages/AdminDashboard/views/PointView/PointView.tsx", current_file="frontend/src/pages/AdminDashboard/views/PointView/PointView.tsx",
   approved_measurement="MEASUREMENT_TABLE_V2 G 카테고리 전체(300px sidebar, 6열 테이블 등)", current_implementation="usePointView 훅 + PlayerPointSummary/DeductionList/Add·EditDeductionModal 컴포넌트로 이미 구현 확인(다이얼로그는 승인자료보다 앞서 있음 — SOURCE_MISSING이었던 다이얼로그가 현재 구현엔 존재)",
   visual_delta="NOT_VERIFIED(시각 상세 미대조, TIER1은 HTML vs PNG만 비교했고 현재 코드의 실제 렌더 결과는 미캡처)", functional_dependency="adminApi(실 API)",
   token_dependency="--admin-sidebar-bg:#1e1b4b(다크) vs 승인 #FBFAFE(라이트) — TOKEN_CONFLICT 확인됨", asset_dependency="N/A",
   reuse_decision_candidate="AdminDashboard/components/{Sidebar,StatCard}(문서 근거, 이번 세션 미재확인)", change_risk="HIGH(다크→라이트 사이드바 전면 재구성 필요 가능성)",
   pm_decision="레거시 다크 admin sidebar를 승인 라이트 톤으로 전환할지, 관리자 화면은 별도 브랜드 톤을 유지할지(제품 결정)",
   expected_test="specs/03-admin.spec.ts", expected_screenshot="A5 desktop", gap_classification="PARTIAL(기능 우위, 시각 TOKEN_CONFLICT)"),
]

fieldnames = ["screen_id","approved_zone","current_route","current_component","current_file","approved_measurement",
  "current_implementation","visual_delta","functional_dependency","token_dependency","asset_dependency",
  "reuse_decision_candidate","change_risk","pm_decision","expected_test","expected_screenshot","gap_classification"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {len(rows)} rows")
