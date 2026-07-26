# 가족 플랫폼 디자인 구현 통합 정본 v1

## 0. 문서 메타데이터

- 상태: `DESIGN_IMPLEMENTATION_SOURCE_INTEGRATED / CONTRACT_EXACTNESS_PASS / CONTRACT_COMPLETENESS_PASS`
- 생성 기준일: 2026-07-26
- 디자인 정본: PM 승인 `family_platform_component_contract_v1.md`
- 기준 구현: `origin/dev @ 1dbbec5176138e4b8c00e42dd5fc9f6ad6b58eef`
- 적용 대상: 나란 공통 시각 foundation, Family User Shell, Admin Shell의 공통
  primitive, 도란 첫 화면 적용 지침
- 비적용 대상: Backend 권한·API·DB·migration·Outbox·credential·Push·WebSocket·
  사진 저장·운영 배포·PWA 설치 정책 및 마크포인트 업무 상태 변경
- 충돌 처리: 디자인 값은 디자인 규범 권위, 파일/구현 여부는 현재 구현 사실
  권위, 명칭·제품 정책은 제품 결정 권위만 사용한다. 축을 교차 대체하지 않는다.

### Output trace map

각 절의 규범/구체 사실은 다음 source class로만 역추적한다: §4–8·§11은
`PM_CONTRACT`, §6·§10의 visual reference는 `APPROVED_VISUAL`, §2·§12–13의
구조/이관 분석은 `CC_IMPLEMENTATION_SOURCE`, 현재 파일/route/API 관찰은
`CURRENT_ORIGIN_DEV`, 나란·도란·마크포인트 및 UI 동결은 `LATER_PM_DECISION`.
그 밖의 제안은 구현 지시가 아니라 근거가 있는 human gate 또는 신규 Task에서
측정할 항목으로 표기한다.

### 정본 사본 동일성

Drive에서 같은 제목의 계약 사본 두 개를 확인했다.

| Drive ID | 수정 시각 | 크기 | 본문 비교 |
| --- | --- | ---: | --- |
| `1LP0q1lTMzgfFCAiJUisb_KZihtLI_OmL` | 2026-07-24 00:02:18 | 21,191 B | `EQUIVALENT_COPIES` |
| `1sfAxl-eceYJi1JNhKGpTg4ltnJPUcCIY` | 2026-07-23 08:12:52 | 21,191 B | `EQUIVALENT_COPIES` |

CRLF/LF와 끝 줄바꿈을 정규화한 전체 본문은 동일했다. 본문을 읽은 첫 사본을
작업용 정본으로 사용한다.

## 1. 권위 체계

### 1.1 디자인 규범 권위

| 우선순위 | 출처 | 적용 범위 |
| ---: | --- | --- |
| 1 | PM component contract | token 값, component 계약, asset·SVG 사용 금지사항 |
| 2 | PM style guide HTML | 시각 적용 보조 기준 |
| 3 | PM style guide PNG | 시각 적용 보조 기준 |
| 4 | 승인 대표 화면 | hierarchy와 시각 방향 |
| 5 | 승인 브랜드·캐릭터·서비스 에셋 | 이미지 정체성과 허용 위치 |
| 6 | CC 구현 참조 | migration 구조, 상태 분석, 점진 이관 방식 |
| 7 | 과거 시안·prototype | 재사용 불가한 참고 관찰 |

### 1.2 현재 구현 사실 권위

| 우선순위 | 출처 | 적용 범위 |
| ---: | --- | --- |
| 1 | 현재 `origin/dev` 코드·OpenAPI | 존재 경로, route, component, API 타입 |
| 2 | 활성 Task 및 검증 결과 | 현재 작업 경계 |
| 3 | 최신 handoff | 전환 맥락 |
| 4 | CC 과거 코드 관찰 | 재검증 후보만 제공 |
| 5 | prototype | 구현 사실로 사용 금지 |

### 1.3 제품 결정 권위

| 우선순위 | 출처 | 적용 범위 |
| ---: | --- | --- |
| 1 | 이후 PM 명시 결정 | 나란·도란·마크포인트, UI 동결 및 SSOT 우선 |
| 2 | PM 승인 계약 | 제품/브랜드 사용 규칙 |
| 3 | 현재 canonical 프로젝트 문서 | 명시된 범위에서만 보조 |
| 4 | CC Decision Log | 권고, 확정 아님 |
| 5 | 임시 명칭·prototype | 제품 결정으로 사용 금지 |

확정 명칭은 플랫폼 **나란**, 대화 서비스 **도란**, 포인트 서비스
**마크포인트**다.

## 2. Source Coverage Matrix

`읽기`는 이번 통합 시 실제 내용을 읽었음을, `stale`은 현재 구현 사실로
재사용하지 않는다는 뜻이다.

| 소스 | ID 또는 경로 | 읽기 | 흡수 | 제외/이유 | stale/충돌 |
| --- | --- | --- | --- | --- | --- |
| PM component contract | `1LP0…OmL`, `1sfA…CIY` | 성공 | 아래 PM Contract Coverage Matrix의 항목별 분류 | 항목별 이유를 아래에 명시 | 사본 동일 |
| style guide HTML | `1sgtbXVHc_rlvIga9JD7j7OhJBFV7bNtK` | 성공 | 시각 방향 | 내장 이미지 바이트는 registry 항목 아님 | 없음 |
| style guide PNG | `1D8zLAusWZjS2bzob17X0g-4ra8vi92mg` | 성공 | 시각 방향 | 코드 값 추출 금지 | 없음 |
| approved chat screen | `1uXFTYGj0FH2e2HWJXqyt2hpoLJiUUWRp` | 성공 | hierarchy | mock text/pixel 복제 금지 | 없음 |
| approved screens | Drive asset folder | 성공 | hierarchy 참조 | mock 인물·문구 | 없음 |
| transparent pin assets | `1eAKDkLrrACW84-nwAnqgPSwe-q6nLBHF`, `1-jyeJTwX2uVybx9naTbPL0vxQCEhLAAE` | 성공 | §6 | 미반입 | identity 후보 중복 |
| CC README | `1ekrFS2PmCIKxqT2hqqT8sl-wQvzKSPXe` | 성공 | source 성격 | 과거 branch 기준 | stale |
| CC 01_PRODUCT_VISION | `1AhD_QEoy-K3fOTBFRfaadgKOtQ7prM_N` | 성공 | 서비스/모듈 분리 | 과거 route 주장 | stale |
| CC 02_PLATFORM_IA | `1mZopiuTabtWF0d4uY75bRcwOHE4gU0lB` | 성공 | User/Admin 분리, module 확장 | 명칭·탭 권고 | decision stale |
| CC 03_DESIGN_PRINCIPLES | `1eoPAY3JdIzIvi8EjIsmeRzd4BwGJqJdX` | 성공 | 점진 이관·접근성 | 과거 CSS 값 | design conflict |
| CC 04_DESIGN_TOKENS | `1y4BnS6l9gESKdSI_CfumBErKAW9FL0r3` | 성공 | alias migration | 값·chat color | design conflict |
| CC 05_SHELL_AND_NAVIGATION | `1h0gyf35-EF-LoOYaY8IU5-eP7Io8KmDI` | 성공 | shell 분리·safe area | 4탭 확정 주장 | decision stale |
| CC 06_COMPONENT_CONTRACTS | `1sSXAB_TG_4m__oVN4rDPc3ITwGPHpE6q` | 성공 | primitive inventory | props·값 완성 계약 | partial conflict |
| CC 07_SCREEN_SPECIFICATIONS | `1GAEu5hjWnovKIiuLfznXTPlnNTOnz4tL` | 성공 | 상태/조합 | Future/mock 사실 | stale |
| CC 07b_STATE_MATRIX | `1SOD_OKG0SxEolepk1XbIALlRVR2zU3wy` | 성공 | 상태 분류 방법 | 화면 구현 현황 | stale |
| CC 08_RESPONSIVE_IOS_GUIDE | `1U1F9BS8Kg85sCfkFjEVZtNx-ltswXQVy` | 성공 | safe area/dvh/keyboard | 과거 ChatModal 측정값 | current recheck 필요 |
| CC 09_ACCESSIBILITY_GUIDE | `1zeXXOsnQG0Bmph_n4bXHcm6fnjmmBr-m` | 성공 | focus/label/motion | 과거 문제 위치 | stale |
| CC 10_MIGRATION_MAP | `1uO3PELspgwDhiTG_zFq-_l6ZLRRYzfop` | 성공 | wave 방식 | 과거 wave 번호 | superseded naming |
| CC 11_DECISION_LOG | `1yFhDTfilK2ruvd7sdKUftqwaWYpKG39_` | 성공 | §13 재정합 | 권고를 확정으로 승격 금지 | decision stale |
| CC FINAL_REPORT | `1PZ3wZpb5BWK3srHmGGn3E4mtOjfftLBb` | 성공 | stale 위험 목록 | 과거 commit/완료 선언 | stale |
| CC prototype | `prototype/index.dc.html`, `10JzCfgSL6DndU6xC8wq_gn6ijqmpKspR` | 성공 | 화면/상태 후보 | mock, emoji, hard-code | design conflict |
| current code | `origin/dev` | 성공 | §§7–10 | 구현 지침으로 자동 승격 금지 | current |

### PM Contract Coverage Matrix

각 행은 PM contract의 독립 계약 단위다. `CURRENT_CODE_MAPPING_ADDED`는 target
contract가 현재 코드에 존재한다는 뜻이 아니라 mapping 조사 항목을 추가했다는 뜻이다.

| PM unit | 분류 | 통합 위치 또는 이유 |
| --- | --- | --- |
| Button | `INTEGRATED_VERBATIM` | §8.1 |
| IconButton | `INTEGRATED_VERBATIM` | §8.2 |
| Card | `INTEGRATED_VERBATIM` | §8.3 |
| Badge / StatusChip | `INTEGRATED_VERBATIM` | §8.4 |
| Avatar | `INTEGRATED_VERBATIM` | §8.5 |
| PageHeader | `INTEGRATED_NORMALIZED` | §8.6; no PM TS interface exists |
| HeroBanner | `INTEGRATED_VERBATIM` | §8.7 |
| ServiceTile | `INTEGRATED_VERBATIM` | §8.8 |
| ActivityList / ActivityRow | `INTEGRATED_VERBATIM` | §8.9 |
| BottomNavigation | `INTEGRATED_VERBATIM` | §8.10 |
| PointHero | `INTEGRATED_NORMALIZED` | §8.11; anatomy-only PM contract |
| MetricSummary | `INTEGRATED_VERBATIM` | §8.12 |
| WeekSelector | `INTEGRATED_NORMALIZED` | §8.13; behavior-only PM contract |
| MissionRow | `INTEGRATED_VERBATIM` | §8.14 |
| PointHistoryRow | `INTEGRATED_NORMALIZED` | §8.15; behavior-only PM contract |
| ChatHeader | `INTEGRATED_NORMALIZED` | §8.16; anatomy-only PM contract |
| MessageBubble | `INTEGRATED_VERBATIM` | §8.17 |
| DateDivider / UnreadDivider | `INTEGRATED_NORMALIZED` | §8.18; behavior-only PM contract |
| PhotoMessage | `INTEGRATED_NORMALIZED` | §8.19; behavior-only PM contract |
| ChatComposer | `INTEGRATED_VERBATIM` | §8.20 |
| AdminSidebar | `INTEGRATED_NORMALIZED` | §8.21; behavior-only PM contract |
| FilterBar | `INTEGRATED_NORMALIZED` | §8.22; anatomy-only PM contract |
| AdminMetricCard | `INTEGRATED_NORMALIZED` | §8.23; behavior-only PM contract |
| DataTable | `INTEGRATED_VERBATIM` | §8.24 |
| PointAdjustmentDialog | `INTEGRATED_NORMALIZED` | §8.25; behavior-only PM contract |
| Dialog | `INTEGRATED_NORMALIZED` | §8.26 |
| Toast | `INTEGRATED_NORMALIZED` | §8.27 |
| Loading / Skeleton | `INTEGRATED_NORMALIZED` | §8.28 |
| EmptyState | `INTEGRATED_NORMALIZED` | §8.29 |
| ErrorState | `INTEGRATED_NORMALIZED` | §8.30 |
| Responsive / iOS | `INTEGRATED_NORMALIZED` | §7, §12 |
| Accessibility | `INTEGRATED_NORMALIZED` | §11 |
| Visual Regression | `INTEGRATED_VERBATIM` | §11.1 |
| Implementation Prohibitions | `INTEGRATED_VERBATIM` | §15 |
| Completion Evidence | `INTEGRATED_VERBATIM` | §16 |
| Recursive Validation | `INTEGRATED_NORMALIZED` | §17 |

## 3. Conflict Register

| 유형 | 충돌 | 출처 A / B | 적용 축 | 해결 | PM 확인 |
| --- | --- | --- | --- | --- | --- |
| `DESIGN_VALUE_CONFLICT` | CC indigo/pink chat·14px radius vs PM token·24px card | CC 04/06 / PM contract | 디자인 규범 | PM 값만 normative | 아니오 |
| `CURRENT_CODE_STALENESS` | CC는 도란을 Future로 서술 | CC 01/07 / current OpenAPI·`/naran/doran` | 구현 사실 | current API/route만 사실로 기록 | 아니오 |
| `PRODUCT_DECISION_STALENESS` | 플랫폼명 미확정 | CC 02/11 / 이후 PM | 제품 결정 | 나란·도란·마크포인트 사용 | 아니오 |
| `TERMINOLOGY_STALENESS` | 마크 포인트 잔치/가족 플랫폼 임시 명칭 | CC / 이후 PM | 제품 결정 | 마크포인트·나란으로 대체 | 아니오 |
| `IMPLEMENTATION_SCOPE_CONFLICT` | CC가 Shell 전면 wave를 권고 | CC 10 / 현재 thin slice | 제품 결정 | 공통 foundation부터 점진 적용; 일괄 재작성 금지 | 아니오 |
| `ASSET_IDENTITY_CONFLICT` | 투명 pin PNG 두 개, 역할 우열 미확정 | Drive assets | 디자인 규범 | 둘 다 후보; 반입 전 정본 asset 선택 필요 | 예 |

## 4. 제품과 브랜드 원칙

- 세련됨 70 / 친근함 30. Surface 약 70, brand purple 약 20, 의미색 약 10의
  비중을 따른다. 이는 임의 팔레트 확장의 근거가 아니다.
- 나란은 플랫폼 표면, 도란은 대화 서비스, 마크포인트는 포인트 서비스다.
- 캐릭터/브랜드 이미지는 정서·hero·empty·onboarding용이다. 한 화면의 큰
  캐릭터 영역은 하나만 두며 텍스트/버튼 위에 겹치지 않는다.
- Back, Send, Bell 같은 조작은 outline SVG이고 emoji가 아니다.
- 핀 로고는 login hero, app icon, 마크포인트 영역 외의 작은 조작 아이콘으로
  사용하지 않는다.
- User/Admin은 token과 primitive는 공유하되 navigation, 정보 밀도, 업무 UX는
  분리한다.

## 5. Semantic Design Tokens

아래 값은 PM contract의 normative 값이다. 화면 컴포넌트에서 직접 hex/rgb,
임의 shadow, 새 시각명 token, 무제한 z-index를 사용하지 않는다.

```css
--color-brand-700: #4726C7; --color-brand-600: #5835DF;
--color-brand-500: #6B46F2; --color-brand-400: #8B6DF5;
--color-brand-200: #D9CCFF; --color-brand-100: #EEE8FF;
--color-brand-50: #F8F5FF;
--color-ink-950: #12172F; --color-ink-900: #171D3A;
--color-ink-700: #434A68; --color-ink-500: #757C98;
--color-line: #E8E6F2; --color-canvas: #F7F6FC;
--color-surface: #FFFFFF; --color-surface-soft: #FBFAFF;
--color-success: #2FBE78; --color-warning: #F3A72B;
--color-danger: #EF4665; --color-reward: #F1B83A;
--color-chat-own: #6944EF; --color-chat-other: #F3F0FF;
--space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
--space-5: 20px; --space-6: 24px; --space-8: 32px;
--space-10: 40px; --space-12: 48px;
--radius-control: 16px; --radius-card: 24px;
--radius-hero: 28px; --radius-dialog: 28px; --radius-pill: 999px;
--shadow-sm: 0 4px 14px rgb(70 47 158 / 6%);
--shadow-md: 0 14px 38px rgb(70 47 158 / 10%), 0 2px 8px rgb(70 47 158 / 6%);
--size-touch-min: 44px;
--duration-quick: 160ms; --duration-standard: 240ms;
--layer-base: 0; --layer-sticky: 20; --layer-overlay: 100;
--layer-dialog: 120; --layer-toast: 160;
```

Typography: Display 40/48 700, Page 30/38 700, Section 22/30 700, Card
17/24 700, Body 16/26 400, Body Strong 16/24 600, Meta 13/19, Label 13/18
700; 수치는 tabular alignment를 사용한다. Layer token과 interaction duration은
PM contract에서 이미 확정된 normative 값이다.

Legacy token은 즉시 삭제하지 않는다. 먼저 semantic alias로 연결하고 소비처를
이관하며, 실제 참조 0건을 검증한 뒤에만 제거한다.

## 6. Asset Registry Contract

코드 반입 전에는 Drive 원본만 registry source다. 현재 `origin/dev`에는
`frontend/src/assets/icons`와 `frontend/src/assets/logos`가 존재하지만, 새 registry
파일 경로는 아직 확정하지 않는다.

| 확인한 asset | 포맷 | 권장 역할 | 허용/금지 | alt·변형 규칙 |
| --- | --- | --- | --- | --- |
| `family_platform_pin_logo_transparent_1024.png` (`1eAK…BHF`) | transparent RGBA PNG, 1024×1024 | 보라색 핀 로고 | login hero/app icon/마크포인트만; Back/Send 금지 | 의미 있으면 제품명 alt, CSS filter·비율변경 금지 |
| `brand_pin_logo_transparent.png` (`1-jye…AAE`) | transparent RGBA PNG, 2048×2048 | 보라색 핀 로고 | 위와 동일 | 위와 동일 |
| Drive 표시명이 공백인 `           .png` (`1cPp5FbJ3y1Fn5rJP8xvF2uQxjrZVXORP`) | transparent RGBA PNG, 2048×1465 | 가족 대화 캐릭터 그룹 | 대화 hero, Empty State, onboarding; 모든 카드 반복·가족 profile 대체 금지 | 장식이면 alt="", 정보성이면 목적 alt; 색·광택·표정·비율 CSS 변경 금지 |
| `screen_family_chat_approved.png` (`1uXF…WRp`) | PNG | visual reference | 코드 UI asset로 직접 사용 금지 | alt 불필요; mock 복제 금지 |
| `screen_family_home_approved.png`, `screen_login_approved.png`, `screen_point_festival_approved.png`, `screen_admin_point_approved.png` | PNG | 대표 화면 reference | 코드 UI asset로 직접 사용 금지 | hierarchy만 참조 |

기능 SVG는 하나의 공통 outline set(Home, Back, Bell, Settings, Edit, Delete,
Attach, Camera, Send)로 구현한다. stroke 1.75–2, round cap/join, navigation
24px, inline 20px, status 16px를 따른다. 서비스 아이콘 방향은 저채도 라일락
3D/embossed 단순 실루엣이며, 마크포인트=핀 로고, 가족 일정=Calendar + Heart,
앨범=Landscape Frame, 할 일=Checklist다. 얼굴 달린 시계·보물상자·금화 더미·가족
인형 시리즈는 금지한다. 승인 SVG 개별 원본은 이번 조사에서 관찰되지 않아 구체
파일명은 확정하지 않는다.

두 핀 파일은 모두 alpha와 시각 내용(동일 pin character + confetti)을 확인했다.
해상도만 다르므로 코드 반입용 canonical variant를 파일명만으로 선정하지 않는다.
`ASSET_SELECTION_HUMAN_GATE`: 1024 또는 2048 master 선택이 필요하다. 이는
family chat character asset의 누락이 아니라 pin delivery variant 선택 문제다.

## 7. Shell and Responsive Foundation

현재 구현 사실: `NaranAppShell`은 `frontend/src/platform/shell/`에 있으며
`100dvh`, safe-area, desktop sidebar와 mobile bottom navigation을 이미 사용한다.
`AdminLayout`은 별도 `frontend/src/pages/AdminDashboard/`에 있다. 이는 현 상태
관찰이며 디자인 완료 선언이 아니다.

추가 current-code inventory: CSS Modules는 `NaranAppShell.module.css`와
`PlatformPages.module.css`에서 확인했고, existing `Button`, `Toast`, `AppIcon`은
각각 `frontend/src/shared/components/` 아래에 있다. `AppIcon`은 현재 PNG/SVG
asset을 동적으로 읽되 emoji fallback도 가진다; 따라서 platform 기능 아이콘에는
그 fallback을 새로 의존하지 않는다. Doran route는 `App.tsx`에서
`/naran/doran`으로 Naran Shell 안에 연결되어 있고, generated API type은
`frontend/src/generated/openapi.d.ts`에 있다.

- `FamilyUserShell` 역할은 현 `NaranAppShell`을 기준으로 한다: safe top →
  PageHeader → scroll content → Bottom Navigation.
- `FamilyUserShell`은 이 문서가 요구하는 새 파일명이나 rename이 아니다. 현
  `NaranAppShell`을 future implementation에서 평가할 역할명이며, rename·전역
  replacement는 별도 승인 없이는 금지한다.
- `AdminShell`은 분리 유지한다. 공통 token/primitive만 공유하며 User navigation을
  강제 이식하지 않는다.
- mobile baseline은 390×844, 320px에서 overflow 없음, 768px tablet, 1280px admin
  desktop을 검토한다. iPhone 375–430px, iPad 768/834/1024px도 점검 범위다.
- top padding은 `max(16px, env(safe-area-inset-top))` 형태, bottom navigation과
  composer는 bottom safe-area를 포함한다. `100dvh` fallback과 visual viewport/
  keyboard 정책은 구현 시 실제 브라우저 검증으로 확정한다.
- Chat composer는 scroll content와 분리해 키보드·home indicator에 가려지지 않게
  하며, system Back/화면 Back은 room에서 목록으로 복귀한다.

## 8. Core Component Contracts

각 표의 `현재 후보`는 존재 여부만 확인한 후보이며 재사용 확정은 아니다. PM/CC에
없는 완성 props를 만들지 않는다.

| 컴포넌트 | 책임·상태 | 규범/token·접근성 | 현재 후보 / 신규 |
| --- | --- | --- | --- |
| Button | primary/secondary/danger/ghost, disabled/loading | 44px, focus-visible, label 유지 | `shared/components/Button`; 확장 필요 |
| IconButton | 단일 SVG action | aria-label, 44px, outline SVG | 신규 필요 |
| Avatar | 사진 또는 initials | 사진 alt, 원형 crop, 역할 의미를 색만으로 표현 금지 | ChatModal/여러 local Avatar; 공통화 검토 |
| Badge/StatusChip | count·status·point | 텍스트+색, tabular number | 신규 계약 필요 |
| Card | surface container | card radius/shadow token만 | 신규 primitive 검토 |
| Dialog | confirmation/short interaction | role dialog, focus trap, Esc/복귀 | 현 modal 패턴; 접근성 보강 필요 |
| Toast | success/error/info | status/alert role, 닫기, motion 감소 | shared Toast/Container 존재 |
| Empty/Loading/Error | 명확한 다음 행동 | `aria-busy`, 재시도, 상태 copy | 신규 공통 state surface |
| PageHeader | back/avatar + title/subtitle + 최대 2 actions | safe top, long title, SVG actions | 신규 필요 |
| ChatHeader | back + room name + participant summary + action | small textual status, avatar stack ≤4+N | 신규 필요 |
| BottomNavigation | User service navigation | icon+label, active는 색 단독 금지 | Naran mobileNav 후보; 재구성 필요 |
| RoomItem | room title/type/preview/activity/unread/access state | long text truncate, unread text alternative | 신규 필요 |
| MessageBubble | own/other text state | mobile max 78%, tablet 64%, semantic chat colors | 신규 필요 |
| ServiceActionCard | service event 정보, display minimum/action | JSON raw 노출 금지, 일반 bubble 금지 | 신규 필요 |
| ChatComposer | text send/pending/failed/retry | 16px input, IME, empty/duplicate send 방지 | 신규 필요 |

`pressed`, `focus`, `read-only`, `loading`, `empty`, `error`, `disabled`는 각
component가 지원해야 하는 상태 범주다. 구체 DOM props와 service action payload
mapping은 실제 API adapter 단계에서 OpenAPI와 함께 확정한다.

| component group | 기본/variant | loading·empty·error·disabled | pressed·focus·read-only |
| --- | --- | --- | --- |
| Button / IconButton | primary·secondary·danger·ghost / icon action | loading text 유지, disabled 사유 | pressed feedback, focus-visible |
| Avatar / Badge / Card | photo/initial, status/count/point, surface | fallback/unknown state를 text로 설명 | Card가 button이면 focus/pressed 적용 |
| Dialog / Toast | confirmation, info/success/error | dialog action disabled; toast error alert | focus trap/return; toast close focus |
| Empty / Loading / Error | state surface | 각 상태 자체가 primary state | retry focus, disabled retry 방지 |
| Header / BottomNavigation | normal/long-title/selected | access unavailable은 state surface로 위임 | back/action focus, active non-color cue |
| Room / Message / Service / Composer | DIRECT/GROUP/SERVICE, own/other, service card, send | history/list loading·empty·error; SERVICE read-only; send disabled/pending/failed | selected/focus, retry focus, IME send rules |

이 표는 상태 범주와 접근성 책임을 고정할 뿐, 존재하지 않는 prop·event·API field를
계약으로 추가하지 않는다.

PM contract 또는 CC에 없는 TypeScript prop 이름·필드·payload shape는 이 문서에서
정의하지 않는다. 그 정보가 필요한 구현은 추측 승인이 아니라 실제
`CURRENT_ORIGIN_DEV` OpenAPI/adapter 계약을 먼저 읽어야 한다.

### 8.1 Button

#### A. PM Target Contract

`type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'`; `type ButtonSize = 'sm' | 'md' | 'lg'`;
`ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> { variant?; size?; loading?; leadingIcon?; trailingIcon?; }`.
기본 `type="button"`, 화면/Dialog당 primary 1개, loading width 유지·중복 클릭 차단·`aria-busy=true`, md 48px와 sm touch hit area 44px가 규범이다.

#### B. Current origin/dev Mapping

후보는 `frontend/src/shared/components/Button/Button.tsx`; 현 variant는 `primary | ghost | dangerSm`뿐이며 size/loading/icon target interface와 다르다.

#### C. Migration Rule

Adapter/소비처 단위 확장만 허용하며 rename·기존 variant 제거는 모든 소비처 mapping과 참조 0건 확인 전 금지다.

### 8.2 IconButton

#### A. PM Target Contract

`IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> { label: string; icon: React.ReactNode; tone?: 'neutral' | 'brand' | 'danger'; badgeCount?: number; }`. `aria-label`은 필수이고 의미가 불명확하면 Tooltip을 제공하며 delete는 과도하게 강조하지 않는다.

#### B. Current origin/dev Mapping

공통 후보는 없고 local button과 `AppIcon`이 분산돼 있다.

#### C. Migration Rule

신규 primitive를 Adapter로 도입하고 기존 local button은 소비처 단위로만 이관한다.

### 8.3 Card

#### A. PM Target Contract

`type CardVariant = 'section' | 'interactive' | 'metric' | 'hero'`; section은 border/shadow-sm 선택, interactive는 hover/focus/pressed, metric은 tabular numeric/최소폭, hero는 페이지당 하나·brand gradient 가능이다. 모든 box를 Card로 만들지 않는다.

#### B. Current origin/dev Mapping

공통 Card는 확인되지 않았고 CSS Module의 local surface가 후보다.

#### C. Migration Rule

신규 primitive; divider가 맞는 행에는 Card를 만들지 않으며 전면 wrapper 교체를 금지한다.

### 8.4 Badge / StatusChip

#### A. PM Target Contract

`type StatusTone = 'brand' | 'success' | 'warning' | 'danger' | 'neutral'`; 완료·진행 중·승인 대기·잠김 같은 text를 포함하고 색 단독 구분 및 한 행 Badge 2개 초과를 금지한다.

#### B. Current origin/dev Mapping

local badge styles가 있으나 공통 primitive는 확인되지 않았다.

#### C. Migration Rule

신규 primitive를 Adapter로 연결하며 status 의미/업무 state를 변경하지 않는다.

### 8.5 Avatar

#### A. PM Target Contract

`AvatarProps { src?: string; alt: string; fallback: string; size?: 28 | 36 | 44 | 56 | 72; status?: 'online' | 'offline' | 'locked'; }`; 가족 사진 또는 initials만, 실제 의미 없는 online dot과 장식 캐릭터의 profile 대체는 금지다.

#### B. Current origin/dev Mapping

ChatModal과 여러 화면에 local Avatar가 있다.

#### C. Migration Rule

공통 Adapter를 추가할 수 있으나 existing local Avatar rename/remove는 참조 0건 전 금지다.

### 8.6 PageHeader

#### A. PM Target Contract

Avatar/Back + Title/Subtitle + Actions 구조, mobile action 최대 2개, 99+ notification badge, 긴 제목 2행 허용 및 action 영역 침범 금지다.

#### B. Current origin/dev Mapping

Naran header는 `platform/shell/NaranAppShell.tsx`에 있으나 target PageHeader는 별도 component로 없다.

#### C. Migration Rule

신규 component를 Adapter로 도입하고 shell을 rename하지 않으며 소비처별 적용한다.

### 8.7 HeroBanner

#### A. PM Target Contract

`HeroBannerProps { eyebrow?: string; title: string; description?: string; action?: React.ReactNode; asset?: React.ReactNode; tone?: 'brand' | 'soft'; }`; 브랜드/핵심 경험은 한 번만 강조, image 35–45%·text 55–65%, small screen에서 image가 text를 가리지 않으며 decorative asset alt는 빈 문자열이다.

#### B. Current origin/dev Mapping

공통 HeroBanner는 확인되지 않았다.

#### C. Migration Rule

신규 primitive; 승인 투명 asset만 registry Adapter로 전달한다.

### 8.8 ServiceTile

#### A. PM Target Contract

`ServiceTileProps { title: string; description: string; icon: React.ReactNode; status?: 'active' | 'coming-soon' | 'disabled'; onActivate?: () => void; }`; coming-soon은 lock emoji 대신 `준비 중` badge, disabled는 4.5:1 대비/비클릭 명시, tile button 내부 중첩 button 금지다.

#### B. Current origin/dev Mapping

Naran navigation은 있으나 ServiceTile은 없다.

#### C. Migration Rule

신규 component; service 권한/API state를 UI가 추측하지 않는다.

### 8.9 ActivityList / ActivityRow

#### A. PM Target Contract

`ActivityItem { id: string; icon: React.ReactNode; title: string; description?: string; timestamp: string; reward?: number; }`; 한 Section Card 안 divider, reward 우측 고정·부호 명시, empty와 더보기 제공이다.

#### B. Current origin/dev Mapping

공통 activity component는 확인되지 않았다.

#### C. Migration Rule

신규 component; mock activity를 제품 사실로 승격하지 않는다.

### 8.10 BottomNavigation

#### A. PM Target Contract

`type NavId = 'home' | 'points' | 'chat' | 'profile'`; 기본 4개 최대 5개, active icon+label 모두 brand, inactive label 숨김 금지, safe area 포함·scroll 임의 숨김 금지다.

#### B. Current origin/dev Mapping

`NaranAppShell`의 mobileNav는 존재하나 target NavId/visual contract와 다르다.

#### C. Migration Rule

navigation policy D2가 open이므로 target을 즉시 전면 교체하지 않는다.

### 8.11 PointHero

#### A. PM Target Contract

Service identity + Avatar/Name/Level + Point + Progress + Secondary action; point와 next-level progress 결합, logout primary CTA 금지, level 중복 표기 금지다.

#### B. Current origin/dev Mapping

마크포인트 UserDashboard local profile/metric UI가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; 업무 의미 보존, adapter로 점진 이관한다.

### 8.12 MetricSummary

#### A. PM Target Contract

`MetricItem { label: string; value: string; tone?: 'brand' | 'success' | 'danger' | 'neutral'; }`; 3 metric은 하나의 summary container, 숫자 폭 변화에도 안정적이어야 한다.

#### B. Current origin/dev Mapping

UserDashboard local stat UI가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; point 계산/label 의미를 바꾸지 않는다.

### 8.13 WeekSelector

#### A. PM Target Contract

월~일 7개, touch 44px, 선택일 filled brand, 오늘 text/small indicator, 선택=오늘 중복 badge 금지, `ko-KR`과 timezone 명시다.

#### B. Current origin/dev Mapping

현재 week selector는 UserDashboard local component/CSS에 있다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; 날짜 계산을 CSS migration으로 변경하지 않는다.

### 8.14 MissionRow

#### A. PM Target Contract

`MissionRowProps { title: string; description?: string; reward: number; status: 'complete' | 'in-progress' | 'pending-approval' | 'not-started'; progress?: { current: number; total: number }; action?: React.ReactNode; }`; Icon→Content/Progress→Reward/Status/Action anatomy, 취소선만 완료 표현 금지, progress/status 모순 금지, CTA 과강조 금지다.

#### B. Current origin/dev Mapping

UserDashboard 및 Admin mission local UI가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; backend status enum을 target display enum으로 억지 변경하지 않는다.

### 8.15 PointHistoryRow

#### A. PM Target Contract

증가/감소 부호 필수, 감소는 danger text만 사용하고 full red background 금지, detail은 expand 또는 separate route다.

#### B. Current origin/dev Mapping

point history local UI가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; data/API 변경 없이 visual Adapter만 적용한다.

### 8.16 ChatHeader

#### A. PM Target Contract

Back, family room name, participant summary, optional actions; connection은 small label, avatar stack 최대 4명+`+N`, large green pill 금지다.

#### B. Current origin/dev Mapping

current Doran landing에는 없고 ChatModal header는 1:1 legacy candidate다.

#### C. Migration Rule

`CANONICAL_CONTRACT`이며 Doran usage에서 신규 필요; legacy ChatModal을 다자 room 계약으로 rename하지 않는다.

### 8.17 MessageBubble

#### A. PM Target Contract

`MessageBubbleProps { direction: 'incoming' | 'outgoing'; sender?: { name: string; avatar?: string }; timestamp: string; readState?: 'sending' | 'sent' | 'read' | 'failed'; grouped?: 'first' | 'middle' | 'last' | 'single'; children: React.ReactNode; }`; incoming neutral/lilac, outgoing brand, mobile 78%/tablet 64%, text+icon state와 overflow 방지가 규범이다.

#### B. Current origin/dev Mapping

legacy ChatModal local message presentation만 존재한다.

#### C. Migration Rule

Doran adapter와 함께 신규 생성; payload/participant field는 OpenAPI를 읽어 연결한다.

### 8.18 DateDivider / UnreadDivider

#### A. PM Target Contract

Date는 neutral, unread는 brand text+line `여기부터 안 읽음`, message와 구별되도록 `role="separator"`다.

#### B. Current origin/dev Mapping

공통 divider는 확인되지 않았다.

#### C. Migration Rule

신규 필요; unread semantics는 backend read state가 source다.

### 8.19 PhotoMessage

#### A. PM Target Contract

thumbnail aspect ratio 보존, upload skeleton/progress, failure retry, image alt 또는 file description 지원이다.

#### B. Current origin/dev Mapping

현재 Doran thin slice 범위 밖이며 photo storage/attachment API는 이 문서 비적용 범위다.

#### C. Migration Rule

`DEFERRED_WITH_REASON`: attachment backend가 별도 승인될 때만 adapter를 설계한다.

### 8.20 ChatComposer

#### A. PM Target Contract

`ChatComposerProps { value: string; disabled?: boolean; sending?: boolean; attachmentEnabled?: boolean; onChange(value: string): void; onSend(): void; onAttach?(): void; }`; Attachment/Input/Send 단일 surface, iOS keyboard/home indicator 보호, mobile/desktop Enter 분리, empty/duplicate/sending retap 차단이다.

#### B. Current origin/dev Mapping

Doran composer는 없고 legacy ChatModal candidate가 있다.

#### C. Migration Rule

도란 text-only first usage에서 신규 필요; attachmentEnabled는 false이며 photo consumer는 deferred다.

### 8.21 AdminSidebar

#### A. PM Target Contract

neutral ink/white + brand active accent 가능, active는 background+text+indicator, `관리자 모드` 명시가 규범이다.

#### B. Current origin/dev Mapping

`pages/AdminDashboard` Sidebar가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; AdminShell을 UserShell로 합치지 않는다.

### 8.22 FilterBar

#### A. PM Target Contract

User segment + Date + Type/Status + optional Search, mobile bottom sheet 가능, reset과 optional applied-count badge 제공이다.

#### B. Current origin/dev Mapping

admin view별 local filters가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; filter query/API 의미 변경 금지다.

### 8.23 AdminMetricCard

#### A. PM Target Contract

current range/baseline 명시, tabular amount/point, semantic color는 number 또는 small icon에 제한한다.

#### B. Current origin/dev Mapping

admin metric local card가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; metrics calculation을 변경하지 않는다.

### 8.24 DataTable

#### A. PM Target Contract

`Column<T> { id: string; header: string; cell(row: T): React.ReactNode; align?: 'left' | 'center' | 'right'; width?: number | string; }`; sticky header 명시, Edit/Delete IconButton label, loading/empty/error/pagination, 기본 user/reason/amount/time/creator/manage columns, mobile card/priority columns 규칙이다.

#### B. Current origin/dev Mapping

admin tables/list가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; table data contracts와 pagination을 새로 창작하지 않는다.

### 8.25 PointAdjustmentDialog

#### A. PM Target Contract

target user/amount/reason 재확인, deduction은 normal primary CTA이고 delete가 아님, negative input을 UI/API에서 이중 처리 금지, success Toast+list refresh state 제공이다.

#### B. Current origin/dev Mapping

admin point adjustment UI가 후보다.

#### C. Migration Rule

`DEFERRED_CONSUMER`; amount sign/API payload를 변경하지 않는다.

### 8.26 Dialog

#### A. PM Target Contract

`role="dialog"`, `aria-modal="true"`, labelled title, focus trap/initial focus/ESC/backdrop policy, iPhone complex form은 bottom sheet 가능이다.

#### B. Current origin/dev Mapping

local modal patterns은 있으나 target accessibility contract와 차이가 있다.

#### C. Migration Rule

Adapter를 새로 추가하고 existing modal 일괄 rename/remove를 금지한다.

### 8.27 Toast / Inline Alert

#### A. PM Target Contract

success/error/info 구분, important error는 Toast만으로 끝내지 않고 Inline Alert 병행, stack 최대 3, auto-dismiss 4–6초, 읽어야 할 error는 manual close다.

#### B. Current origin/dev Mapping

shared Toast/ToastContainer와 store가 존재한다.

#### C. Migration Rule

소비처 단위 adapter 확장; 기존 timeout/type semantics 제거 전 reference audit이 필요하다.

### 8.28 Loading / Skeleton

#### A. PM Target Contract

layout size 유지로 CLS 방지, infinite shimmer 금지/reduce-motion, page spinner보다 section skeleton 우선이다.

#### B. Current origin/dev Mapping

공통 Skeleton은 확인되지 않았다.

#### C. Migration Rule

신규 state primitive; data fetching behavior를 변경하지 않는다.

### 8.29 EmptyState

#### A. PM Target Contract

title, description, 가능한 next action 하나; character illustration은 empty state 전체에서 하나, `데이터 없음` 단독 문구 금지다.

#### B. Current origin/dev Mapping

local empty text는 있으나 common component는 확인되지 않았다.

#### C. Migration Rule

신규 primitive; family character asset은 §6 허용 위치에서만 사용한다.

### 8.30 ErrorState

#### A. PM Target Contract

무엇이 실패했는지, retry 가능 여부, data preservation 여부를 알리고 기술 error code만 노출하지 않는다.

#### B. Current origin/dev Mapping

Naran shell state notice와 local error handling이 후보다.

#### C. Migration Rule

신규 primitive/adapter; backend error policy를 UI가 재정의하지 않는다.

## 9. State Matrix

### 9.1 공통 디자인 상태

| 상태 | 표현 원칙 |
| --- | --- |
| Default | 정상 surface와 primary action |
| Loading | text 또는 skeleton, `aria-busy` |
| Empty | 이유와 가능한 다음 행동 |
| Error | 원인 범주와 재시도/이동 |
| Disabled | 행동 불가 이유를 텍스트로 병기 |
| Focus / Pressed | focus-visible, 비색상 pressed feedback |
| Read-only | 입력을 감추거나 이유를 설명 |

### 9.2 Doran Application Mapping — 전역 디자인 계약이 아닌 Thin Slice 예시

| Doran 상태 | UI 처리 |
| --- | --- |
| room list loading / empty | loading/empty state surface |
| no selected room / empty history | 선택 안내 또는 history empty |
| permission denied / subscription inactive / session expired | Naran Shell의 실제 상태 메시지와 다음 행동 |
| onboarding failure | 실패 이유와 재시도 |
| send pending / confirmed / failed / retry | 확정 전 pending, 실패 재시도, client 중복 방지 |
| SERVICE read-only | composer 대신 읽기 전용 설명 |
| stale room response | 선택 room identity가 일치할 때만 반영 |

## 10. Screen Composition

공통 조합은 Shell → Header → scroll content → state surface → primary action →
Bottom Navigation이다. 승인 화면은 hierarchy 기준일 뿐 mock 이름, 메시지, 우연한
pixel, 오탈자, 비현실 간격을 복제하지 않는다.

도란 첫 적용은 Room 목록(DIRECT/GROUP/SERVICE), history, unread/read, composer,
SERVICE_ACTION, mobile 목록↔room 전환과 wide viewport split을 포함한다. SERVICE는
일반 사용자 대화로 오해되지 않도록 card와 read-only treatment를 사용한다. 현재
`origin/dev`의 `DoranLanding.tsx`는 안내 화면이며, 전용 worktree의 미커밋 prototype은
승인 시각 기준이 아니다.

## 11. Accessibility and Interaction

- touch target 최소 44px, interactive element 중첩 금지
- `:focus-visible`, 아이콘 `aria-label`, loading `aria-busy`, 오류/성공 상태 text
- 본문 16px 규범, 한글 IME 중 Enter/전송 동작 분리, iOS input 16px
- reduced motion, 대비, 색+텍스트 상태, numeric tabular alignment
- screen-reader announcement는 전송/실패/read state를 문장으로 제공
- 긴 제목·긴 메시지·두 자리 이상 unread·keyboard·safe area·system Back을 검증한다

### 11.1 Visual Regression Contract

승인 목업 지정 → 동일 viewport 구현 캡처 → 나란히 비교 → Delta Table 작성 →
token/component 수준 수정 → 재캡처 → 기능·접근성 회귀 확인 순서를 따른다. 목표는
pixel 100% 복제가 아니라 시각 유사도 90% 이상과 사용성·접근성 개선이다.

| Delta Table 축 | 반드시 비교할 항목 |
| --- | --- |
| 1 | 전체 콘텐츠 폭·정렬 |
| 2 | Header 높이·safe area |
| 3 | typography 크기·행간 |
| 4 | surface 색·border·shadow |
| 5 | spacing rhythm |
| 6 | card radius |
| 7 | 아이콘 스타일·크기 |
| 8 | 상태 표현 |
| 9 | Bottom Navigation / Composer 위치 |
| 10 | 긴 텍스트·loading·empty·error |

### 11.2 Implementation Prohibitions and Completion Evidence

금지: 화면 전체를 이미지로 렌더링, 모든 surface purple gradient, 임의 CSS/breakpoint,
emoji 기능 아이콘, 새 얼굴 캐릭터 series, point/mission/deduction/admin 의미 변경,
User/Admin 강제 통합, 없는 family room/Push 완료 선언, 테스트 없는 동시 이관, 전면
재작성. 완료 증거에는 수정 파일, token, 신규/현행화 component, 지원 상태, 동일
viewport screenshot, Delta Table, keyboard/touch/screen reader, iPhone small/standard,
iPad/Admin desktop, 자동화 또는 안전한 수동 검증, 기존 기능·data 의미 보존 증거가
포함되어야 한다.

## 12. Migration Guidance

| 논리 순서 | 현재 분류 | 구현 원칙 |
| --- | --- | --- |
| 현재 화면 fixture | `REQUIRED_FOR_CURRENT_DORAN_SLICE` | UI 변경 전 시각 기준 확보 |
| token foundation | `REQUIRED_FOR_CURRENT_DORAN_SLICE` | alias 우선, legacy 삭제 금지 |
| iOS layout foundation | `REQUIRED_FOR_CURRENT_DORAN_SLICE` | safe-area/dvh/keyboard 검증 |
| core primitives | `REQUIRED_FOR_CURRENT_DORAN_SLICE` | 공통 contract 먼저 |
| Family Shell alignment | `PARTIALLY_COMPLETE` | existing Naran Shell 점진 정렬 |
| Doran first application | `REQUIRED_FOR_CURRENT_DORAN_SLICE` | static PM gate 후 API |
| 마크포인트 점진 이관 | `DEFERRED` | 업무 의미 보존 |
| Admin 점진 이관 | `DEFERRED` | shell 분리 유지 |
| legacy cleanup | `DEFERRED` | reference 0건 검증 후만 |
| CC Future chat migration | `SUPERSEDED` | 실제 Doran API/route 존재로 재계획 |

기존 화면을 한 번에 재작성하지 않는다. CC Wave 번호는 현재 프로젝트 Phase 번호가 아니다.
토큰 foundation은 한 future Task에서 measured consumer 단위로 적용한다. 본 문서는
`global.css`, CSS Module, shell, asset을 지금 수정하라는 명령이 아니며, 임시 Doran
UI를 reset/clean/stash/delete/commit할 근거도 제공하지 않는다.

## 13. Decision Reconciliation

| CC ID | 원래 권고 | 이후 PM 결정 | 상태 | 적용 규칙 |
| --- | --- | --- | --- | --- |
| D1 | home-first | 명시 확정 없음 | `STILL_OPEN` | 도란 thin slice가 첫 진입 정책을 바꾸지 않음 |
| D2 | mobile 4 tabs | 명시 확정 없음 | `STILL_OPEN` | 현 Naran navigation을 일괄 교체하지 않음 |
| D3 | 임시 Family Platform | 나란 확정 | `SUPERSEDED_BY_LATER_PM_DECISION` | 나란 사용 |
| D4 | platform tone + point game tone | 마크포인트와 플랫폼 분리, PM asset 규칙 | `CONFIRMED_BY_LATER_PM_DECISION` | point asset은 point 영역만 |
| D5 | Minecraft asset을 point로 한정 | 명시 확정 없음 | `STILL_OPEN` | 현재 asset 제거·확대 금지 |
| D6 | shared primitive, separate UX | PM contract와 현재 shell 분리 | `CONFIRMED_BY_LATER_PM_DECISION` | User/Admin 강제 통합 금지 |
| D7 | independent chat route | `/naran/doran` 및 Doran task 확정 | `CONFIRMED_BY_LATER_PM_DECISION` | 도란은 Naran shell route |
| D8 | iPad bottom nav | 명시 확정 없음 | `STILL_OPEN` | tablet layout만 검증, rail 도입 금지 |
| D9 | light only, dark token reserve | 명시 확정 없음 | `STILL_OPEN` | dark mode 구현/약속 금지 |
| D10 | home service grid | 명시 확정 없음 | `STILL_OPEN` | 신규 모듈 navigation 정책 창작 금지 |

## 14. Codex Implementation Checklist

- [x] 디자인 정본 사본 동일성 확인
- [x] 세 권위 축 분리
- [x] 모든 CC source coverage 기록
- [x] current `origin/dev` 구현 사실 재검증
- [x] 신규 hex/rgb·임의 shadow·emoji 기능 아이콘 금지 기록
- [x] 확인된 asset만 기록
- [x] common primitive와 CSS Modules 점진 이관 기록
- [x] legacy token 즉시 삭제 및 User/Admin 강제 통합 금지
- [x] safe-area/dvh/keyboard와 공통/Doran 상태 분리
- [x] mock 사실의 제품 승격 금지
- [x] CC Decision 재정합
- [x] 오작업 방지 범위와 비적용 범위 기록

## 15. 명시적 비적용 범위

이 문서는 Doran Backend 권한, WebSocket, Push, DB schema, migration, service
credential, Outbox 운영, 사진 저장, 실제 API endpoint 계약, 마크포인트 업무 상태
변경, 운영 배포, PWA 설치 정책을 새로 정의하거나 기존 canonical 문서를 덮어쓰지 않는다.

## 16. Completion Evidence Contract

화면 또는 component 이관 완료 보고에는 수정 파일, 소비 token, 신규/현행화 component,
지원 상태 목록, 동일 viewport screenshot, Delta Table, keyboard/touch/screen reader
확인, iPhone small/standard·iPad·Admin desktop 결과, 자동화 또는 안전한 수동 검증,
기존 기능과 data 의미 보존 증거를 포함한다. 이 목록은 완료 선언의 최소 증거이며,
테스트를 생략하거나 API/권한 변경을 허용하는 근거가 아니다.

## 17. Correction Recursive Validation Evidence

### Pass 1 — Token Exactness

- 발견 결함: 합쳐진 hero/dialog radius 이름은 PM token이 아니고 radius hero/dialog,
  duration, layer token이 누락됐다.
- 수정 파일·절: 이 파일 §5.
- 수정 전: 합쳐진 hero/dialog radius 선언 및 layer 미확정 선언.
- 수정 후: `--radius-hero`, `--radius-dialog`, duration 2개와 layer 5개를 PM
  contract의 이름·값으로 수록하고 layer 확정 사실을 기록.
- 재검증: 기계 비교 `TOKEN_NAME_DIFF=0`, `TOKEN_VALUE_DIFF=0`,
  `TOKEN_FORBIDDEN_EXTRA=0`.

### Pass 2 — Contract Completeness

- 발견 결함: PM component contract를 포괄 행 하나로 처리해 platform, point,
  admin, feedback, cross-cutting 계약이 누락됐다.
- 수정 파일·절: §2 PM Contract Coverage Matrix, §8.1–§8.30, §11.1–§11.2.
- 수정 전: PM contract 전체를 포괄 흡수라고만 선언.
- 수정 후: 각 단위를 허용된 classification 중 하나로 분류하고 target/current/
  migration 분리를 추가.
- 재검증: `CONTRACT_COMPONENT_UNCLASSIFIED=0`,
  `CONTRACT_SECTION_UNCLASSIFIED=0`.

### Pass 3 — Implementation Safety

- 발견 결함: target interface 요약이 current code 재사용 판단으로 오독될 수 있었다.
- 수정 파일·절: §8.1–§8.30.
- 수정 전: 표 중심의 후보/신규 요약.
- 수정 후: 모든 component에 A. PM Target Contract, B. Current origin/dev Mapping,
  C. Migration Rule을 기록하고 adapter·consumer-unit·rename/remove 금지 조건을 명시.
- 재검증: 전면 교체, 일괄 rename, 추측 삭제, backend/API 변경 지시 0건.

### Pass 4 — Hallucination and Reverse Trace

- 발견 결함: 가족 대화 캐릭터 asset 원본과 pin 후보의 실체 검증이 부족했다.
- 수정 파일·절: §6.
- 수정 전: character asset은 inventory에 없고 pin은 filename만으로 후보 처리.
- 수정 후: 실제 Drive character group ID/포맷/크기/alpha/허용·금지 위치를 기록하고,
  pin 후보도 1024/2048 RGBA와 시각 내용을 비교해 human gate로 남김.
- 재검증: false coverage claim 0, unsupported decision marker 0,
  unresolved asset omission 0.
