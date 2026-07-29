#!/usr/bin/env python3
import csv
OUT = "/tmp/mongle-wave6-0ab/6.0B/e2e_coverage_map_v2.csv"

FIELDS = ["test_file","test_title","route","viewport","fixture_or_real","auth","family_context",
    "assertion","screenshot","console_error_check","storage","route_compatibility",
    "loading_empty_error_state","screen_mapping","visual_reconstruction_impact"]

rows = []
def add(**kw):
    missing = [f for f in FIELDS if f not in kw]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    rows.append(kw)

COMMON_SCREENSHOT = "only-on-failure(전역 설정)"

add(test_file="specs-mongle/01-shell.spec.ts", test_title="keeps the legacy dashboard inside the Mongle shell and allows a Family switch",
    route="/dashboard", viewport="5 projects(desktop 전용 assertion 일부 분기)", fixture_or_real="실제 API(loginAsFirstPlayer가 /api/auth/login 호출)",
    auth="필요(로그인)", family_context="필요(FamilySwitcher 조작)",
    assertion="mongle-shell testid 노출, 가족 옵션 수 확인, desktop에서만 미션관리 링크 노출 확인", screenshot=COMMON_SCREENSHOT,
    console_error_check="미확인(assert 없음)", storage="N/A", route_compatibility="N/A",
    loading_empty_error_state="N/A", screen_mapping="A2(Shell/Header) 간접 커버",
    visual_reconstruction_impact="재구성 시 FamilySwitcher/nav 마크업 변경되면 셀렉터 깨질 위험")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="presents Doran as an honest unavailable service entry point",
    route="/wagle", viewport="5 projects", fixture_or_real="fixture(doranPreview*) 렌더만 검증, 서비스 status 판정은 실제 FamilyContext 기반",
    auth="필요", family_context="필요", assertion="'와글와글' heading 노출만 확인", screenshot=COMMON_SCREENSHOT,
    console_error_check="미확인", storage="N/A", route_compatibility="N/A", loading_empty_error_state="disabled state 간접 커버",
    screen_mapping="A4", visual_reconstruction_impact="낮음")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="renders the responsive navigation landmark",
    route="/wagle", viewport="5 projects", fixture_or_real="N/A", auth="필요", family_context="불필요(nav 자체만)",
    assertion="nav 랜드마크 정확히 1개 존재", screenshot=COMMON_SCREENSHOT, console_error_check="미확인",
    storage="N/A", route_compatibility="N/A", loading_empty_error_state="N/A", screen_mapping="A2 Dock/nav",
    visual_reconstruction_impact="낮음")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="does not turn a direct Family URL into a permission grant",
    route="/family", viewport="5 projects", fixture_or_real="N/A(legacy 로그인 API 직접 호출)", auth="필요(player 4)",
    family_context="필요(권한 없음 케이스)", assertion="'권한이 없어요' heading 확인", screenshot=COMMON_SCREENSHOT,
    console_error_check="미확인", storage="N/A", route_compatibility="N/A", loading_empty_error_state="AccessBoundary forbidden state",
    screen_mapping="A2/family", visual_reconstruction_impact="권한 가드 로직 검증 — MUST_PRESERVE")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="renders the reviewed mapping-needed state without creating an Account",
    route="N/A(route intercept)", viewport="5 projects", fixture_or_real="API mock(page.route 403 강제)", auth="필요",
    family_context="N/A", assertion="'계정 연결이 필요해요' 텍스트 확인", screenshot=COMMON_SCREENSHOT, console_error_check="미확인",
    storage="N/A", route_compatibility="N/A", loading_empty_error_state="mapping_required state",
    screen_mapping="MongleAppShell state notice", visual_reconstruction_impact="낮음")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="shows a safe not-found page instead of a blank screen for an unregistered path",
    route="/this-path-does-not-exist", viewport="5 projects", fixture_or_real="N/A", auth="불필요", family_context="불필요",
    assertion="404 heading+복귀링크 확인", screenshot=COMMON_SCREENSHOT, console_error_check="미확인", storage="N/A",
    route_compatibility="N/A", loading_empty_error_state="404 state", screen_mapping="N/A(승인자료 대응 없음)",
    visual_reconstruction_impact="낮음")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="canonical /wagle and /family render directly, refresh preserved, no console error",
    route="/wagle,/family", viewport="5 projects", fixture_or_real="fixture(wagle)/실제(family)", auth="필요", family_context="필요",
    assertion="heading 확인 + reload 후 URL 유지 + console error 배열이 빈 배열임을 assert", screenshot=COMMON_SCREENSHOT,
    console_error_check="있음(핵심 assert)", storage="N/A", route_compatibility="canonical route 자체",
    loading_empty_error_state="N/A", screen_mapping="A4,A2", visual_reconstruction_impact="라우트 변경 시 반드시 재검증")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="internal Dock/nav clicks produce canonical URLs, never /naran/*",
    route="N/A", viewport="5 projects(desktop 외 4개는 test.skip — 보고된 baseline의 '4 intentional skipped' 정확한 원인, 코드: test.skip(testInfo.project.name !== 'desktop', ...))",
    fixture_or_real="N/A", auth="필요", family_context="필요", assertion="nav 클릭 후 URL이 canonical(/wagle,/family)인지 확인",
    screenshot=COMMON_SCREENSHOT, console_error_check="미확인", storage="N/A", route_compatibility="N/A",
    loading_empty_error_state="N/A", screen_mapping="A2 Dock", visual_reconstruction_impact="Dock 마크업 변경 시 셀렉터 위험")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="legacy /naran/doran and /naran/family redirect once, preserving query and hash, no Back-loop",
    route="/naran/doran,/naran/family", viewport="5 projects(뷰포트 폭 따라 assertion 분기 <701px vs >=701px)", fixture_or_real="N/A",
    auth="필요", family_context="필요", assertion="리다이렉트 target/query/hash 보존 + Back 1회 확인", screenshot=COMMON_SCREENSHOT,
    console_error_check="미확인", storage="N/A", route_compatibility="핵심 커버 대상", loading_empty_error_state="N/A",
    screen_mapping="N/A", visual_reconstruction_impact="라우트 별칭 정책 자체 — MUST_PRESERVE")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="legacy routes do not fall through to the 404 catch-all",
    route="/naran/doran,/naran/family", viewport="5 projects", fixture_or_real="N/A", auth="필요", family_context="필요",
    assertion="404 heading이 뜨지 않음을 확인(부정 assert)", screenshot=COMMON_SCREENSHOT, console_error_check="미확인",
    storage="N/A", route_compatibility="핵심 커버", loading_empty_error_state="N/A", screen_mapping="N/A",
    visual_reconstruction_impact="낮음(회귀 방지용)")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="canonical absent + valid legacy present: family preserved, canonical copy-forward occurs",
    route="N/A(localStorage 조작)", viewport="5 projects", fixture_or_real="N/A", auth="필요", family_context="필요",
    assertion="localStorage canonical/legacy 키 상태 직접 확인", screenshot=COMMON_SCREENSHOT, console_error_check="미확인",
    storage="핵심 커버(storage migration)", route_compatibility="N/A", loading_empty_error_state="N/A", screen_mapping="N/A",
    visual_reconstruction_impact="MUST_PRESERVE")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="canonical present + legacy present with a different value: canonical wins, legacy not overwritten",
    route="N/A", viewport="5 projects", fixture_or_real="N/A", auth="필요", family_context="필요",
    assertion="canonical 값 우선, legacy 값 불변 확인", screenshot=COMMON_SCREENSHOT, console_error_check="미확인",
    storage="핵심 커버", route_compatibility="N/A", loading_empty_error_state="N/A", screen_mapping="N/A",
    visual_reconstruction_impact="MUST_PRESERVE")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="canonical absent + invalid/inaccessible legacy: no copy-forward, no silent auto-select",
    route="N/A", viewport="5 projects", fixture_or_real="N/A", auth="필요", family_context="필요",
    assertion="잘못된 legacy 값으로 canonical 생성 안 됨 확인", screenshot=COMMON_SCREENSHOT, console_error_check="미확인",
    storage="핵심 커버", route_compatibility="N/A", loading_empty_error_state="가족 선택 필요 상태", screen_mapping="N/A",
    visual_reconstruction_impact="MUST_PRESERVE")

add(test_file="specs-mongle/01-shell.spec.ts", test_title="explicit logout clears both canonical and legacy keys for that account, no resurrection on next login",
    route="N/A", viewport="5 projects", fixture_or_real="N/A", auth="필요(로그아웃 포함)", family_context="필요",
    assertion="로그아웃 후 두 키 모두 삭제 + 재로그인 시 재생성 안 됨 확인", screenshot=COMMON_SCREENSHOT, console_error_check="미확인",
    storage="핵심 커버", route_compatibility="N/A", loading_empty_error_state="N/A", screen_mapping="N/A",
    visual_reconstruction_impact="MUST_PRESERVE")

LEGACY_NOTE = ("CURRENT_TEMPORARY: playwright.config.ts의 webServer가 docker-compose.phase0.yml을 참조하나 "
    "저장소에 해당 파일이 없음(ls로 확인, No such file or directory) — 이 config로는 현재 환경에서 실행 불가. "
    "테스트 코드 자체는 유효하나 실행 가능성은 phase0 스택 복원 여부에 달려 있음(NOT_VERIFIED as currently-passing)")

for f, title, route, screen in [
    ("specs/01-login.spec.ts", "캐릭터 선택 화면이 표시된다", "/", "A1"),
    ("specs/01-login.spec.ts", "PIN 입력 후 대시보드로 이동", "/", "A1"),
    ("specs/02-mission.spec.ts", "대시보드에서 미션 목록이 표시된다", "/dashboard", "A3"),
    ("specs/02-mission.spec.ts", "미션 제안 버튼이 표시된다", "/dashboard", "A3"),
    ("specs/03-admin.spec.ts", "관리자 로그인 버튼이 표시된다", "/", "A1(관리자 진입부)"),
    ("specs/03-admin.spec.ts", "관리자 ID/PW 폼이 표시된다", "/", "A1-S1 유사"),
    ("specs/03-admin.spec.ts", "관리자 로그인 후 /admin으로 이동", "/", "A5"),
    ("specs/04-flow.spec.ts", "플레이어 로그인 → 대시보드 → 로그아웃 → 홈 복귀", "/,/dashboard", "A1,A3"),
    ("specs/04-flow.spec.ts", "관리자 로그인 → /admin 접근 성공", "/,/admin", "A1,A5"),
]:
    add(test_file=f, test_title=title, route=route, viewport="1 project(playwright.config.ts, projects 미정의)",
        fixture_or_real="실제 API(추정, 상세 미열람)", auth="테스트별 상이(제목 참조)", family_context="N/A(레거시 경로)",
        assertion="상세 미열람(파일 존재 및 제목만 확인)", screenshot=COMMON_SCREENSHOT, console_error_check="미확인",
        storage="N/A", route_compatibility="N/A", loading_empty_error_state="N/A", screen_mapping=screen,
        visual_reconstruction_impact=LEGACY_NOTE)

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {len(rows)} rows")
