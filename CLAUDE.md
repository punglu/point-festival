# CLAUDE.md — 프로젝트 컨텍스트 (매 세션 필독)

> **프로젝트:** 마인크래프트 포인트 잔치 — 모던 스택 마이그레이션
> **최종 갱신:** 2026-04-05 | Phase 7 진행중 — v1.0.0 운영 배포 완료, 운영 패치 진행중
> **이 파일은 프로젝트의 SSOT입니다. 매 세션 시작 시 반드시 읽으세요.**

---

## 1. 프로젝트 개요

가족용 포인트 관리 웹 서비스입니다.

| As-Is | To-Be |
|---|---|
| 바닐라 JS (3개 HTML) | React (Vite + TypeScript) |
| Data store | PostgreSQL 16.9 LTS |
| Hosting | Docker 3-Tier (Synology NAS) |
| 전역 CSS 1개 (1,589줄) | CSS Modules 캡슐화 |
| PIN 평문 | bcrypt 해시 + JWT |

---

## 2. 멀티 에이전트 R&R

| 역할 | 담당 | 행동 규칙 |
|---|---|---|
| PM (User) | 최종 의사결정 | — |
| Claude Web | Main Architect | 설계서 + 실행 프롬프트 생성 |
| Gemini | Auditor | 설계 감사, Pass/Fail 판정 |
| **Claude Code (본인)** | **Developer** | **설계서대로 코드 생성, 빌드 검증** |
| Codex | QA Engineer | 정적 분석, 체크리스트 검증 |

---

## 3. 아키텍처 철칙 (위반 시 QA Fail)

### Backend (FastAPI)
- **Thin Controller**: `router.py`에 비즈니스 로직 0줄. 모든 검증/처리는 `service.py`로 위임
- **SQL Annotation**: `service.py` 핵심 함수 상단에 RAW SQL 주석 필수
- **Junction Architecture**: `app/models/all_models.py`는 import만 수행 (코드 없음)
- **Soft Delete**: 물리 삭제 금지, `deleted_at` 컬럼 + `SoftDeleteMixin` 사용
- **문자열 기반 FK**: `ForeignKey("players.id")` 형식 (순환 참조 방지)
- **Vertical Domain Slicing**: `app/domains/[도메인명]/` 하위에 router/service/schema/models 응집

#### Soft Delete 예외 모델
- `AppConfig`: 설정 키-값이므로 삭제 이력 불필요
- `LoginLog`: 로그성 데이터, 물리 삭제 허용

#### sync def 헬퍼 허용
- 순수 계산 함수(DB 미접근)는 `async` 없이 `def` 허용 (예: 포인트 계산)

### Frontend (React)
- **1 Page = 1 Directory**: `src/pages/[도메인명]/` 하위 수직 응집
- **수평 구조 금지**: `src/components/`, `src/hooks/` 등 전역 디렉토리 생성 금지
- **CSS Modules 강제**: 모든 스타일은 `.module.css` (global.css, reset.css만 예외). 인라인 style={{}} 최소화 (파일당 5개 미만)
- **Shared 승격 규칙**: 2개+ 페이지에서 사용될 때만 `src/shared/`로 이동
- **테마 격리**: `[data-domain]` 속성 기반 CSS Variable 분기 (다크/라이트)
- **AbortController**: useEffect 내 API 호출 시 cleanup에 abort() 필수. 폼 제출 API 호출에도 signal 전달 필수 (Race Condition 방지)

### 인프라
- **Docker 3-Tier**: Frontend(Nginx) / Backend(FastAPI) / DB(PostgreSQL) 분리
- **개발**: `docker-compose.yml` (볼륨 마운트, 핫 리로드)
- **운영**: `docker-compose.prod.yml` (이미지 기반, NAS 경로)
- **배포**: `deploy.sh`는 빌드+전송만 (크로스 빌드 `buildx amd64` + SSH 파이프). NAS 컨테이너 재시작은 PM 수동

---

## 4. 기술 스택 (버전 고정)

| 레이어 | 기술 | 버전 |
|---|---|---|
| Frontend | React + Vite + TypeScript | Vite 6.x, React 18/19 |
| State | Zustand | 5.x |
| HTTP | Axios | 1.x |
| Routing | React Router | 6.x |
| CSS | CSS Modules | built-in |
| Backend | FastAPI | 0.115.x |
| ORM | SQLAlchemy (Async) | 2.0.x |
| Auth | python-jose + bcrypt | — |
| DB | PostgreSQL | **16.9** LTS |
| Container | Docker Compose | 3.9 |
| Dev Runtime | OrbStack (macOS) | — |
| Prod Runtime | Synology NAS Container Manager | — |

---

## 5. 프로젝트 구조

```
mc-point-festival/
├── CLAUDE.md                    ← 이 파일
├── docs/CLAUDE.md               # CLAUDE.md 사본 (문서 보관용)
├── .env
├── .gitignore
├── docker-compose.yml           # 개발용
├── docker-compose.prod.yml      # 운영용 (Synology NAS)
├── deploy.sh                    # OrbStack → NAS 배포
├── tests/api/e2e_scenario_test.py    # E2E API 시나리오 테스트 (v1)
├── tests/api/e2e_scenario_test_v2.py # E2E API 시나리오 테스트 (v2)
├── wrapper.py                   # 테스트 래퍼
├── favicon-assets/              # 파비콘 원본 이미지 (11종)
└── logo-assets/                 # 로고 원본 이미지 (5종)
│
├── database/
│   └── init.sql                 # 12 테이블 + Seed (admin_auth 포함)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI 앱 + 라우터 등록
│       ├── config.py            # pydantic-settings
│       ├── database.py          # AsyncSession
│       ├── dependencies.py      # 앱 레벨 공통 의존성 (REFACTORING_0404 신규)
│       ├── models/
│       │   ├── base.py          # Base + Mixin
│       │   └── all_models.py    # Junction Hub (11개 모델)
│       └── domains/
│           ├── auth/            # ✅ Phase 1 + Phase 5
│           │   ├── router.py    # POST /login + POST /admin/login
│           │   ├── service.py   # authenticate_player + authenticate_admin
│           │   ├── schema.py    # LoginRequest/Response + AdminLoginRequest/Response
│           │   ├── models.py    # PlayerAuth + AdminAuth
│           │   └── dependencies.py  # get_current_user(player) + get_current_admin
│           ├── player/          # ✅ Phase 1 + Phase 3 PATCH 추가
│           ├── admin/           # ✅ Phase 4
│           │   └── router.py    # /api/admin/* 집합 라우터 (get_current_admin 보호)
│           ├── mission/         # ✅ Phase 2
│           ├── cheer/           # ✅ Phase 2
│           ├── feedback/        # ✅ Phase 2
│           ├── deduction/       # ✅ Phase 2
│           ├── daily_point/     # ✅ Phase 2
│           ├── notification/    # ✅ Phase 2
│           ├── config/          # ✅ Phase 2
│           └── login_log/       # ✅ Phase 2
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── src/
│       ├── main.tsx
│       ├── App.tsx              # Router + ProtectedRoute + AdminProtectedRoute
│       ├── styles/
│       │   ├── reset.css
│       │   └── global.css       # CSS Variables + 테마 격리
│       ├── shared/
│       │   ├── api/httpClient.ts
│       │   ├── stores/
│       │   │   ├── useAuthStore.ts     # setLogin + adminLogin + logout
│       │   │   └── useToastStore.ts    # Toast 전역 상태 (REFACTORING_0404 신규)
│       │   ├── utils/
│       │   │   ├── compressImage.ts    # Canvas 기반 이미지 압축 (200px, JPEG 75%)
│       │   │   └── favicon.ts          # 파비콘 동적 전환 유틸 (REFACTORING_0404 신규)
│       │   └── components/
│       │       ├── Button/
│       │       ├── PhotoUpload/        # 재사용 사진 업로드 컴포넌트
│       │       └── Toast/              # ToastContainer (REFACTORING_0404 신규)
│       └── pages/
│           ├── Auth/            # ✅ Phase 1 + Phase 5 (Login Hub 리팩토링)
│           │   ├── index.tsx    # 3모드 허브 (select/pin/admin)
│           │   ├── Auth.module.css
│           │   ├── components/
│           │   │   ├── PlayerSelectView.tsx   # 캐릭터 카드 그리드
│           │   │   ├── PlayerCard.tsx         # 사진/이니셜 폴백 카드
│           │   │   ├── PinInputView.tsx       # PIN 입력 화면
│           │   │   ├── AdminLoginView.tsx     # ID/PW 관리자 로그인
│           │   │   ├── LoginOverlay.tsx       # (레거시 유지)
│           │   │   ├── PinInput.tsx
│           │   │   └── PlayerSelector.tsx
│           │   ├── hooks/useAuth.ts
│           │   └── api/authApi.ts             # login + adminLogin + getPlayers(signal)
│           ├── UserDashboard/   # ✅ Phase 3
│           │   ├── index.tsx
│           │   ├── UserDashboard.module.css
│           │   ├── components/
│           │   │   ├── DateSelector.tsx
│           │   │   ├── ProfileCard.tsx
│           │   │   ├── StoryCards.tsx
│           │   │   ├── MissionList.tsx
│           │   │   ├── MissionProposal.tsx
│           │   │   ├── FeedbackSection.tsx
│           │   │   ├── DeductionAccordion.tsx
│           │   │   ├── RankingView.tsx
│           │   │   ├── BottomNav.tsx
│           │   │   ├── StatDetailModal.tsx
│           │   │   ├── CheerModal.tsx
│           │   │   ├── ExpBar.tsx
│           │   │   ├── MissionProgressBar.tsx + MissionProgressBar.module.css
│           │   │   └── ConfettiEffect.tsx
│           │   ├── hooks/useDashboard.ts
│           │   └── api/dashboardApi.ts
│           └── AdminDashboard/  # ✅ Phase 4 + REFACTORING_0404 전면 개편
│               ├── index.tsx
│               ├── AdminLayout.tsx + AdminLayout.module.css  # 레이아웃 래퍼
│               ├── types/admin.types.ts
│               ├── constants/admin.constants.ts
│               ├── api/adminApi.ts
│               ├── hooks/
│               │   ├── useAdminAuth.ts
│               │   ├── useAdminData.ts
│               │   ├── useAdminToast.ts
│               │   └── useCycle.ts
│               ├── components/              # AdminDashboard 내 공유 컴포넌트
│               │   ├── AdminModal/
│               │   ├── AdminToast/
│               │   ├── CycleIndicator/
│               │   ├── DateSelector/
│               │   ├── MobileDrawer/
│               │   ├── MobileHeader/
│               │   ├── PlayerBadge/
│               │   ├── PlayerTab/
│               │   ├── Sidebar/
│               │   └── StatCard/
│               └── views/                   # View 단위 수직 응집 (REFACTORING_0404)
│                   ├── DashboardView/
│                   │   ├── DashboardView.tsx + DashboardView.module.css
│                   │   └── components/      # PlayerStatusCard, MissionRanking, etc.
│                   ├── MissionView/
│                   │   ├── MissionView.tsx + MissionView.module.css
│                   │   ├── components/      # MissionCard, MissionCardEdit, BatchCopyModal, etc.
│                   │   └── hooks/
│                   ├── PlayerView/
│                   │   ├── PlayerView.tsx + PlayerView.module.css
│                   │   ├── components/      # PlayerProfileCard, AddPlayerModal, LoginLogTable, etc.
│                   │   └── hooks/usePlayerView.ts
│                   ├── PointView/
│                   │   ├── PointView.tsx + PointView.module.css
│                   │   ├── components/      # PlayerPointSummary, DeductionList, AddDeductionModal, etc.
│                   │   └── hooks/usePointView.ts
│                   ├── FeedbackView/
│                   │   └── FeedbackView.tsx + FeedbackView.module.css
│                   ├── NotificationView/
│                   │   ├── NotificationView.tsx + NotificationView.module.css
│                   │   └── components/      # NotificationFilter, NotificationItem
│                   └── ConfigView/
│                       ├── ConfigView.tsx + ConfigView.module.css
│                       ├── components/
│                       └── hooks/
│
└── _legacy/                     # ✅ Phase 1에서 이동 완료
    ├── index.html
    ├── user.html
    ├── admin.html
    ├── styles.css
    └── ...
```

---

## 6. 도메인 매핑

| # | Source node | BE 도메인 | DB 테이블 | Phase |
|---|---|---|---|---|
| 1 | mc_players | player | players | ✅ 1 |
| 2 | mc_player_auth | auth | player_auth | ✅ 1 |
| 3 | mc_mission_data | mission | missions | ✅ 2 |
| 4 | mc_cheer_msgs | cheer | cheer_messages | ✅ 2 |
| 5 | mc_feedbacks | feedback | feedbacks, feedback_replies | ✅ 2 |
| 6 | mc_deductions | deduction | deductions | ✅ 2 |
| 7 | mc_daily_points | daily_point | daily_points | ✅ 2 |
| 8 | mc_notifications | notification | notifications | ✅ 2 |
| 9 | mc_config | config | app_configs | ✅ 2 |
| 10 | mc_login_logs | login_log | login_logs | ✅ 2 |
| 11 | — (신규) | auth | admin_auth | ✅ 5 |

**mc_party_data** (레거시) → players + daily_points로 흡수, 별도 테이블 없음.

---

## 7. Phase 현황

| Phase | 초점 | 상태 |
|---|---|---|
| **1** | **Scaffolding + Auth** | **✅ 완료** |
| **2** | **Core Domains BE (8개 도메인 CRUD)** | **✅ 완료** |
| **3** | **User Dashboard FE (user.html 마이그레이션)** | **✅ 완료** |
| **4** | **Admin Dashboard BE+FE (RBAC, 미션관리)** | **✅ 완료** |
| **5** | **Login Hub + Admin 인증 분리** | **✅ 완료** |
| 6 | Home Page + Legacy (index.html 다크테마) | 대기 |
| **7** | **프로덕션 배포 준비 + 운영 패치** | **🚀 진행중** |

---

## 8. Phase 1 완료 Task 목록 (아카이브)

| Task ID | 작업 | 상태 |
|---|---|---|
| P1-001 ~ P1-010 | Docker 인프라, DB, BE/FE 보일러플레이트, Auth 도메인, 빌드 검증 | ✅ 전체 완료 |

**QA 결과:** Codex 34/34 PASS (블로커 0)

---

## 9. Phase 2 완료 Task 목록 (아카이브)

| Task ID | 작업 | 상태 |
|---|---|---|
| P2-001 ~ P2-011 | 8개 도메인 CRUD + all_models + main.py 라우터 + 빌드 검증 | ✅ 전체 완료 |
| P2-FIX | Thin Controller 핫픽스, 미션 상태 머신, 포인트 엔진 Row Lock | ✅ 완료 |

**QA 결과:** Codex 38/38 PASS (블로커 0)

### Phase 2 주요 보강 사항
- **Thin Controller**: 9개 라우터 전체 HTTPException 제거, service 위임 완료
- **미션 상태 머신**: `ROLE_TRANSITIONS` 역할별 전이 맵 (player/admin)
- **포인트 엔진**: `adjust_daily_point` 서버 측 계산 + `with_for_update()` Row Lock

---

## 10. Phase 3 완료 Task 목록 (아카이브)

### Step 1: Pixel-perfect Baseline
| Task ID | 작업 | 상태 |
|---|---|---|
| P3-001 | init.sql Seed (level.thresholds) | ✅ 완료 |
| P3-002 | App.tsx (ProtectedRoute + 라우트 변경) | ✅ 완료 |
| P3-003 | Player PATCH 엔드포인트 (상태 메시지 수정) | ✅ 완료 |
| P3-004 | dashboardApi.ts (7개 API + 6개 타입) | ✅ 완료 |
| P3-005 | useDashboard.ts (병렬 로드 + 레벨 임계치 BE 연동) | ✅ 완료 |
| P3-006 | UserDashboard.module.css (35개+ 클래스) | ✅ 완료 |
| P3-007 | 컴포넌트 11개 생성 | ✅ 완료 |
| P3-008 | index.tsx 엔트리 조립 | ✅ 완료 |
| P3-009 | 빌드 검증 | ✅ 완료 |

### Step 2: v2 Overhaul
| Task ID | 작업 | 상태 |
|---|---|---|
| P3-010 | ExpBar.tsx + ProfileCard 통합 | ✅ 완료 |
| P3-011 | MissionProgressBar.tsx + MissionList 통합 | ✅ 완료 |
| P3-012 | ConfettiEffect.tsx + 승인 트리거 | ✅ 완료 |
| P3-013 | StoryCards "+" 카드 제거 | ✅ 완료 |
| P3-014 | CSS v2 오버라이드 (픽셀 스타일, 코인 아이콘) | ✅ 완료 |
| P3-015 | 빌드 검증 | ✅ 완료 |

### 핫픽스 (Gemini 조건 이행)
| Task ID | 작업 | 상태 |
|---|---|---|
| P3-FIX-1 | StatDetailModal 인라인 스타일 → CSS Module 이관 | ✅ 완료 |
| P3-FIX-2 | useDashboard AbortController 적용 | ✅ 완료 |
| P3-FIX-3 | 빌드 재검증 | ✅ 완료 |

**Gemini 감사:** PASS (조건 이행 후)
**QA 결과:** Codex 39/40 PASS (WARNING 1: B-5 Git 환경 부재 — 코드 결함 아님)

### Phase 3 확립된 패턴
- **Auth Guard**: `ProtectedRoute` 컴포넌트 — `isLoggedIn` 검사 + `<Navigate to="/" replace />`
- **BE 설정 연동**: `app_configs` DB Seed → `GET /api/configs/{key}` → FE 동적 로드 + 폴백
- **AbortController**: useEffect 내 API 병렬 호출 시 cleanup abort 패턴
- **CSS Module 인라인 제한**: style={{}} 파일당 5개 미만 (초과 시 즉시 이관)
- **BottomNav Local 유지**: Admin과 기능/링크 상이하므로 Shared 승격 안 함

---

## 11. Phase 4 완료 Task 목록 (아카이브)

| Task ID | 작업 | 상태 |
|---|---|---|
| P4-001 ~ P4-N | Admin Dashboard BE (admin 집합 라우터, RBAC) | ✅ 완료 |
| P4-N+1 ~ P4-M | Admin Dashboard FE (9개 컴포넌트, AdminDashboard.module.css) | ✅ 완료 |
| P4-FIX-1 | init.sql is_locked 컬럼 / healthcheck / CSS Module 이관 | ✅ 완료 |

**QA 결과:** Codex PASS (P4-FIX-1 핫픽스 후)

### Phase 4 확립된 패턴
- **Admin 집합 라우터**: `admin/router.py`가 각 도메인 service를 직접 import해 `/api/admin/*` 제공
- **RBAC**: `get_current_admin` 의존성으로 admin_auth 토큰 전용 보호 (Phase 5 hotfix에서 확정)
- **AdminProtectedRoute**: `isLoggedIn && isAdmin` 검사 + `<Navigate to="/" replace />`

---

## 12. Phase 5 완료 Task 목록 (아카이브)

### Step 1: BE — Admin 인증 기반 구축
| Task ID | 작업 | 상태 |
|---|---|---|
| P5-001 | init.sql: admin_auth 테이블 + Seed (dad/mom, bcrypt) | ✅ 완료 |
| P5-002 | AdminAuth 모델 (SoftDeleteMixin) | ✅ 완료 |
| P5-003 | AdminLoginRequest / AdminLoginResponse 스키마 | ✅ 완료 |
| P5-004 | authenticate_admin 서비스 (RAW SQL 주석, bcrypt 검증) | ✅ 완료 |
| P5-005 | POST /api/auth/admin/login 라우트 | ✅ 완료 |
| P5-006 | all_models.py AdminAuth import 추가 | ✅ 완료 |
| P5-007 | Step 1 빌드 검증 | ✅ 완료 |

### Step 2: FE — Login Hub
| Task ID | 작업 | 상태 |
|---|---|---|
| P5-008 | authApi.ts: adminLogin 함수 + AdminLoginResponse 타입 | ✅ 완료 |
| P5-009 | useAuthStore: adminDisplayName + adminLogin 액션 | ✅ 완료 |
| P5-010 | PlayerCard.tsx (사진/이니셜 폴백, 클릭 콜백) | ✅ 완료 |
| P5-011 | PlayerSelectView.tsx (카드 그리드, 관리자 링크, AbortController) | ✅ 완료 |
| P5-012 | PinInputView.tsx (기존 PinInput 재사용, 뒤로가기) | ✅ 완료 |
| P5-013 | AdminLoginView.tsx (ID/PW 폼, AbortController) | ✅ 완료 |
| P5-014 | Auth/index.tsx: 3모드 허브 리팩토링 (select/pin/admin) | ✅ 완료 |
| P5-015 | Auth.module.css: Login Hub 클래스 14개 추가 | ✅ 완료 |
| P5-016 | Step 2 빌드 검증 | ✅ 완료 |

### 핫픽스 (Codex QA FAIL 4건)
| Task ID | 작업 | 상태 |
|---|---|---|
| P5-FIX-1 | JWT payload sub 수정: `admin.username` → `str(admin.id)` | ✅ 완료 |
| P5-FIX-2 | dependencies.py: get_current_user role 체크 + get_current_admin 신규 | ✅ 완료 |
| P5-FIX-3 | admin/router.py: get_admin_user → get_current_admin 전체 교체 | ✅ 완료 |
| P5-FIX-4 | mission/, AdminDashboard/ origin/dev 롤백 (범위 초과 복원) | ✅ 완료 |
| P5-FIX-5 | authApi.getPlayers + PlayerSelectView에 AbortController signal 전달 | ✅ 완료 |

**QA 결과:** Codex 79/80 PASS (WARNING 1: E-4 dependencies.py 의도적 변경 — hotfix 필수 수정)

### Phase 5 확립된 패턴
- **JWT 토큰 완전 격리**: Player(`role="player"`, `sub=str(player.id)`) / Admin(`role="admin"`, `sub=str(admin_auth.id)`)
- **get_current_user**: `role != "player"` 시 401. Player 전용 엔드포인트 보호
- **get_current_admin**: `role != "admin"` 시 401 → admin_auth 테이블 id 조회. Admin 전용 엔드포인트 보호
- **Login Hub 3모드**: `select`(캐릭터 선택) → `pin`(PIN 입력) / `admin`(ID/PW 폼). 뒤로가기 시 select 복귀
- **AdminAuth**: admin_auth 테이블, SoftDeleteMixin, bcrypt 해시. PIN 인증과 완전 분리
- **AbortController 확장**: useEffect뿐 아니라 폼 제출 API 호출(`abortRef.current`)에도 적용

---

## 13. Phase 5 이후 핫픽스 (2026-04-03)

### P-FEATURE-POINT-CYCLE-001 — 포인트 사이클 기능
| 작업 | 상태 |
|---|---|
| ConfigManager `point_cycle` 키: textarea → select 드롭다운 (daily/weekly/monthly/quarterly/yearly) | ✅ 완료 |
| `useDashboard` `cycleSummary` 반환 + `UserDashboard/index.tsx` 적용 | ✅ 완료 |
| `UserDashboard.module.css` `.cycleLabel` 추가 (파란 배지) | ✅ 완료 |

### P-HOTFIX-ADMIN-VIEWS-002 / PATCH-003 — Admin Dashboard UI 전면 개편
| 작업 | 상태 |
|---|---|
| `DashboardView`: 오늘 날짜 고정 + 전체 플레이어 집계 (totalPoints/completedCount/pendingCount/totalCount) | ✅ 완료 |
| `DashboardView`: 플레이어 요약 `<table>` (레벨/포인트/완료율 pill), 모바일 카드 전환 (`data-label` 패턴) | ✅ 완료 |
| `DashboardView`: 컬러 스탯 카드 4종 (indigo/green/amber/purple) | ✅ 완료 |
| AdminHeader에서 `PlayerFilterBar` 제거 → 각 View 로컬로 이동 | ✅ 완료 |
| 5개 View CSS 데드코드 제거 (콜로케이션 정리) | ✅ 완료 |
| `PointManager` 차감 목록: `.deductionCard` 카드형 (왼쪽 red border) | ✅ 완료 |
| `nginx.conf` `index.html` no-cache 헤더 추가 (브라우저 캐시 버그 방지) | ✅ 완료 |

### P-HOTFIX-ADMIN-POLISH-004 — 사진 업로드 + 시각 폴리시
| 작업 | 상태 |
|---|---|
| `shared/utils/compressImage.ts` 신규 (Canvas, 200px, JPEG 75%) | ✅ 완료 |
| `shared/components/PhotoUpload/` 신규 (호버 오버레이, 파일 선택, base64 콜백) | ✅ 완료 |
| `PlayerManager` 수정 모달: PhotoUpload 통합, 기존 photo 로드 | ✅ 완료 |
| `CheerEditor` dad/mom 행: PhotoUpload 통합, 변경 즉시 `adminApi.updateConfig('photos.{key}', b64)` 저장 | ✅ 완료 |
| `adminApi.ts` `PlayerItem.photo?: string | null` 추가 | ✅ 완료 |
| `DashboardView.module.css` 스탯 카드 `linear-gradient` + `::before` 라디얼 하이라이트 + hover lift | ✅ 완료 |
| `DashboardView.module.css` `levelPill`/`pointPill` 그라디언트 + `box-shadow` | ✅ 완료 |
| `Sidebar.module.css` `linear-gradient(180deg, #F8F7FF → #EEF2FF)` + brand 섹션 subtle gradient | ✅ 완료 |
| `AdminHeader.module.css` `linear-gradient(90deg, #FAFAFF → #F5F5FF)` | ✅ 완료 |

### 핫픽스에서 확립된 패턴
- **Photo 저장 방식**: Base64 → DB 직접 저장 (`players.photo TEXT`, `app_configs`의 `photos.dad`/`photos.mom` 키). 파일 서버 불필요
- **DashboardView 집계 전략**: `selectedPlayerId` 무시, 항상 오늘(`TODAY = new Date().toISOString().slice(0,10)`) + 전체 플레이어 집계로 어드민 오버뷰 제공
- **PlayerFilterBar 위치**: AdminHeader에 없음. 각 View 최상단 로컬 배치
- **mobile table→card**: `thead { display:none }` + `td::before { content: attr(data-label) }` 패턴
- **PhotoUpload Shared 승격 조건 충족**: PlayerManager + CheerEditor 2곳 사용 → `src/shared/components/PhotoUpload/` 배치 정당

---

## 14. REFACTORING_0404 (2026-04-04)

### 주요 변경 범위
| 영역 | 변경 내용 |
|---|---|
| AdminDashboard FE | 평면 `components/` → `views/[ViewName]/` 수직 응집 구조로 전면 개편 |
| AdminDashboard FE | `AdminLayout.tsx` 레이아웃 래퍼 신규, `types/`, `constants/` 디렉토리 추가 |
| AdminDashboard FE | 공유 훅 4종 신규: `useAdminAuth`, `useAdminData`, `useAdminToast`, `useCycle` |
| shared/ | `Toast/ToastContainer` + `useToastStore` 신규 |
| shared/ | `utils/favicon.ts` 신규 (파비콘 동적 전환) |
| BE | `backend/app/dependencies.py` 앱 레벨 공통 의존성 파일 신규 |
| 루트 | `e2e_scenario_test.py`, `e2e_scenario_test_v2.py`, `wrapper.py` 추가 |
| 루트 | `favicon-assets/` (11종), `logo-assets/` (5종) 추가 |
| UserDashboard | `MissionProgressBar.module.css` 분리, CSS 전면 개편 |
| Auth | `Auth.module.css` 대규모 개편 (로그인 화면 UI 개선) |

### REFACTORING_0404에서 확립된 패턴
- **Views 수직 응집**: AdminDashboard는 `views/[ViewName]/` 단위로 컴포넌트+훅+CSS 응집. 각 View는 독립 디렉토리 유지
- **AdminDashboard 내부 Shared**: 2개+ View에서 쓰이는 컴포넌트는 `AdminDashboard/components/`로 승격 (전역 `src/shared/`와 구분)
- **Toast 시스템**: `useToastStore` (Zustand) + `ToastContainer` (shared). admin/user 양쪽에서 활용 가능
- **Favicon 유틸**: `shared/utils/favicon.ts`로 이벤트/일반 파비콘 동적 전환
- **AdminLayout 분리**: 레이아웃(Sidebar+Header) 관심사를 `AdminLayout.tsx`로 분리, `index.tsx`는 라우팅/상태만 담당

---

## 15. Phase 5 이후 핫픽스 (2026-04-05) — 추가 기능

### P-FEATURE-CHAT-001 — 채팅 시스템
| 작업 | 상태 |
|---|---|
| `chat_messages` 테이블 신규 (init.sql) | ✅ 완료 |
| `chat/` 도메인 신규 (models/schema/service/router) | ✅ 완료 |
| `GET /api/chat/partners`, `GET /api/chat/history/{id}`, `POST /api/chat/send`, `GET /api/chat/unread` | ✅ 완료 |
| `get_current_chat_user` 의존성 신규 — player/admin 토큰 모두 허용 | ✅ 완료 |
| `shared/components/ChatModal/` 신규 (embedded/overlay 모드, 15s 폴링) | ✅ 완료 |
| `AdminDashboard/views/ChatView/` 신규 (embedded ChatModal) | ✅ 완료 |
| `UserDashboard/index.tsx` — 헤더 💬 버튼 + unread 배지 + ChatModal 통합 | ✅ 완료 |
| `MobileHeader` — 채팅 미읽음 폴링 (admin/player 공통) | ✅ 완료 |

### P-FEATURE-ADMIN-CHAT-LINK — Admin → Chat 연결
| 작업 | 상태 |
|---|---|
| `admin_auth`에 `player_id` 컬럼 추가 (players FK) | ✅ 완료 |
| players 테이블에 아빠(id=3)/엄마(id=4) 레코드 추가 (init.sql 정비에서 확정) | ✅ 완료 |
| admin JWT payload에 `player_id` claim 포함 | ✅ 완료 |
| `useAuthStore` — `adminPlayerId` 상태 추가 | ✅ 완료 |
| `관리자(id=3)` soft-delete (레거시 PIN admin 비활성화) | ✅ 완료 |

#### 확립된 패턴
- **get_current_chat_user**: player(`sub`=player_id) / admin(`player_id` claim) 모두 허용. chat 전용 의존성
- **admin_auth.player_id**: admin 계정의 players 테이블 연결 키. JWT에 포함되어 FE에서 chat에 활용
- **ChatModal embedded 모드**: `embedded=true` prop → overlay 없이 div 내 렌더링 (AdminDashboard ChatView)

### P-FEATURE-PLAYER-VISIBILITY-001 — 로그인 페이지 노출 제어
| 작업 | 상태 |
|---|---|
| `players.is_visible BOOLEAN NOT NULL DEFAULT TRUE` 컬럼 추가 | ✅ 완료 |
| `PlayerListItem` 스키마에 `is_visible` 추가 | ✅ 완료 |
| `PlayerVisibilityRequest` 스키마 신규 | ✅ 완료 |
| `set_player_visibility` 서비스 신규 | ✅ 완료 |
| `get_player_list(visible_only=False)` 파라미터 추가 | ✅ 완료 |
| `GET /api/players` (로그인 페이지) — `visible_only=True` 적용 | ✅ 완료 |
| `GET /api/admin/players` — 모든 플레이어 반환 (is_visible 무관) | ✅ 완료 |
| `PATCH /api/admin/players/{id}/visibility` 엔드포인트 신규 | ✅ 완료 |
| Admin `types/admin.types.ts` `Player.is_visible` 추가 | ✅ 완료 |
| `adminApi.setPlayerVisibility()` 추가 | ✅ 완료 |
| `PlayerProfileCard` — "로그인 숨김/노출" 버튼 + `hiddenBadge` 뱃지 추가 | ✅ 완료 |

#### 확립된 패턴
- **is_locked vs is_visible**: `is_locked`=로그인 차단(인증 단계), `is_visible`=카드 노출 여부(로그인 페이지 렌더링 단계). 완전 독립적으로 작동
- **로그인 페이지 필터링**: BE에서 `visible_only=True`로 처리. FE 필터링 없음
- **Admin은 is_visible 무시**: `/api/admin/players`는 숨긴 플레이어도 표시하여 관리 가능

### P-HOTFIX-CYCLE-INTEGRITY-001 — 주기 기반 미션 생명주기 정합성
| 작업 | 상태 |
|---|---|
| `get_cycle_range()` 주기 유틸 함수 (daily/weekly/biweekly/monthly/quarterly/yearly 지원) | ✅ 완료 |
| `expire_stale_missions()` Lazy Expiry — 이전 주기 active/pending 미션 자동 failed | ✅ 완료 |
| Admin 대시보드 미션 조회 시 Lazy Expiry 트리거 (`admin_list_missions`) | ✅ 완료 |
| `get_missions_admin` date_from/date_to optional 파라미터 추가 | ✅ 완료 |
| `useAdminData` → 주기 범위로 미션 조회 (스탯 카드 범위 통일) | ✅ 완료 |
| 주기 변경 가드 A: 주기 진행 중 잠금 | ✅ 완료 |
| 주기 변경 가드 B: 활성 반복 미션 의존성 잠금 | ✅ 완료 |
| ConfigView 잔여일 뱃지 + 에러 토스트 | ✅ 완료 |

#### 확립된 패턴
- **Lazy Expiry**: cron 없이 조회 시점에 만료 처리. `expire_stale_missions(db, cycle_start_date)` — 현재 주기 시작일 이전 active/pending 미션 → failed
- **주기 변경 2중 가드**: (A) 주기 진행 중 변경 불가 + (B) 활성 반복 미션 존재 시 변경 불가
- **get_cycle_range**: daily/weekly/biweekly/monthly/quarterly/yearly 지원. 미지원 값은 weekly 폴백
- **설계 예외**: `mission/service.py`에서 `app_configs` 읽기 전용 조회 허용 (PM 승인, Vertical Domain 예외)
- **스탯 카드 범위 통일**: `useAdminData`의 getMissions가 `date_from: cycle.startDate, date_to: cycle.endDate`로 주기 범위 제한됨

### P-HOTFIX-DASHBOARD-DETAIL-001 — DashboardView 카드 상세 + 밸런싱
| 작업 | 상태 |
|---|---|
| 스탯 카드 순서 변경: 총 발행 → 활성 → 승인대기 → 완료 | ✅ 완료 |
| 스탯 카드 탭화: 클릭 시 하단 상세 테이블 토글 (같은 카드 재클릭 시 닫힘) | ✅ 완료 |
| CardDetailTable.tsx 신규: 4모드 (points/active/pending/completed) | ✅ 완료 |
| points 모드: 일자×플레이어 아코디언, 배정 대비 완료 비교 (달성률%) | ✅ 완료 |
| active/pending/completed 모드: flat 테이블 (일자/이름/미션명/포인트/상태) | ✅ 완료 |
| 플레이어 필터 셀렉트 (각 모드 공통) | ✅ 완료 |
| 모바일 카드 전환: thead 숨김 + data-label 패턴 | ✅ 완료 |
| BalanceSection.tsx 신규: 플레이어별 밸런싱 카드 + 포인트 비교 바 | ✅ 완료 |

#### 확립된 패턴
- **스탯 카드 탭 패턴**: selectedCard 상태로 1개 CardDetailTable 영역을 4모드로 전환
- **아코디언 그룹 집계**: missions[]를 date+player_id로 groupBy → 배정건수/포인트 vs 완료건수/포인트
- **밸런싱 대상**: players에서 role='player'만 필터. 아빠/엄마(role='admin') 제외
- **기존 모달 제거**: ActiveMissionDetailModal, PendingApprovalModal, CompletedMissionsModal, PointHistoryModal → 인라인 CardDetailTable로 대체. 모달 파일은 보존

### P-HOTFIX-DASHBOARD-DETAIL-002 — 밸런싱 카드 개선 + 세로 바 + 주기 배너
| 작업 | 상태 |
|---|---|
| BalanceSection 카드: 3셀 1행 → 2행 분리 (미션 현황 / 포인트 현황) + 구분선 + 서브 라벨 | ✅ 완료 |
| BalanceSection 카드: 셀 배경색 적용 (statCell → background-secondary) | ✅ 완료 |
| BalanceSection 포인트 밸런스 비교: 가로 바 → 세로 바 차트 (4인 막대) | ✅ 완료 |
| DashboardView: 글로벌 주기 배너 (타이틀 우측 cycleBadge) | ✅ 완료 |
| DashboardView: 스탯 카드 총 발행 포인트에서 "이번 주기" 서브 라벨 제거 | ✅ 완료 |
| BalanceSection: 섹션 타이틀 + 비교 차트에 "집계: 기간" 표기 | ✅ 완료 |

#### 확립된 패턴 (DETAIL-002)
- **글로벌 주기 배너**: 개별 컴포넌트가 주기를 각자 표기하지 않고, 대시보드 최상단에 1회 표기. 하위 섹션은 "집계: 기간"으로 참조
- **밸런싱 카드 2행 분리**: 건수(미션 현황)와 포인트(포인트 현황)를 구분선으로 분리. 서브 라벨 + 셀 배경으로 시각 구분
- **세로 바 차트**: 4인 이하 비교에서 가로 바보다 직관적. 2그룹(배정/획득) 나란히 배치
- **pendingPoints 계산**: `assignedPoints - donePoints` (active/pending_approval 합산 아님. Lazy Expiry 적용 후 현재 주기 내에서 정확)

---

## 16. Phase 7 Task 목록 (진행중)

### 인프라/배포 환경

| Task ID | 작업 | 상태 |
|---|---|---|
| P7-INFRA-001 | 레거시 정리: `public/`, `_legacy/`, `nas-deploy/`, `frontend/media/` 삭제 | ✅ 완료 |
| P7-INFRA-002 | `.gitignore`: `favicon-assets/`, `logo-assets/` 추가 (git rm --cached) | ✅ 완료 |
| P7-INFRA-003 | `docker-compose.yml`: `image:` 태그 명시 (`mc-backend/mc-frontend:latest`), version 제거 | ✅ 완료 |
| P7-INFRA-004 | `docker-compose.prod.yml`: B방식 (image 기반, NAS bind mount, `init.sql` 마운트) | ✅ 완료 |
| P7-INFRA-005 | `deploy.sh`: Mac 크로스 빌드(`buildx amd64`) → SSH 파이프 전송. NAS 컨테이너 재시작은 수동 | ✅ 완료 |
| P7-INFRA-006 | `reset-history.sh`: 이력 데이터 초기화 스크립트 (계정/설정 유지) | ✅ 완료 |
| P7-INFRA-007 | `.env.production.template` 신규 생성 | ✅ 완료 |

### 보안

| Task ID | 작업 | 상태 |
|---|---|---|
| P7-SEC-001 | `nginx.conf`: `server_tokens off`, 보안 헤더 6종, dotfile/.map 차단 | ✅ 완료 |
| P7-SEC-002 | `main.py`: `ENVIRONMENT=production` 시 Swagger 비활성화 (`_is_prod` 분기) | ✅ 완료 |
| P7-SEC-003 | `main.py`: 글로벌 예외 핸들러 (스택 트레이스 노출 방지) | ✅ 완료 |
| P7-SEC-004 | `config.py`: CORS 프로덕션 도메인 추가, `ENVIRONMENT` 필드 추가 | ✅ 완료 |
| P7-SEC-005 | `App.tsx`: `AdminProtectedRoute` — Player 로그인 시 `/` → `/dashboard` 리다이렉트 | ✅ 완료 |

### DB 정합성

| Task ID | 작업 | 상태 |
|---|---|---|
| P7-DB-001 | `init.sql`: `admin_auth player_id` 버그 수정 (4,5 → 3,4) | ✅ 완료 |
| P7-DB-002 | `init.sql`: `player_auth` 아빠(3)/엄마(4) 항목 추가 | ✅ 완료 |
| P7-DB-003 | `init.sql`: `docker-compose.prod.yml`에 마운트 추가 (최초 기동 시 자동 실행) | ✅ 완료 |

### 버전 관리

| 항목 | 내용 |
|---|---|
| `v1.0.0` 태그 | 포인트 페스티발 2.0 초기 릴리즈 (2026-04-05) |
| `prd` 브랜치 | 프로덕션 배포 전용 브랜치 |
| `dev` 브랜치 | 개발 메인 브랜치 |

### NAS 환경 정보

| 항목 | 값 |
|---|---|
| SSH | `ssh -p 5422 starbee@192.168.1.57` |
| 프로젝트 경로 | `/volume3/V3_APPL/PJT/point-festival` |
| pgdata 경로 | `/volume3/V3_APPL/PJT/point-festival/pgdata` |
| docker 권한 | `sudo` 필요 (또는 `synogroup --member docker starbee`) |
| 서비스 포트 | `:3000` (Nginx → frontend) |
| 관리자 계정 | `dad` / `admin1234`, `mom` / `admin1234` |

### 운영 패치 (진행중)

| Task ID | 작업 | 상태 |
|---|---|---|
| P7-PATCH-001 | Admin DashboardView: 플레이어별 배정 미션 수 + 획득 예정 포인트 표시 (밸런싱) | 🔄 진행중 |

### Phase 7 확립된 패턴
- **2단계 배포**: deploy.sh(Mac)는 빌드+전송만 수행. NAS 컨테이너 재시작은 PM이 SSH 접속 후 수동 실행
- **크로스 빌드**: Mac ARM → NAS AMD64이므로 `docker buildx build --platform linux/amd64` 필수. `docker-compose build` 사용 금지
- **SSH 파이프 전송**: Synology SFTP chroot로 `scp` 절대경로 불가 → `cat file | ssh "cat > path"` 방식
- **NAS sudo 필수**: docker 그룹 미등록 → 모든 docker 명령에 `sudo` 접두
- **docker tag 필수**: 로컬 빌드명 `mc-point-festival-backend` → prod 참조명 `mc-backend`로 태깅
- **pgdata 보존**: `docker-compose down`은 컨테이너만 삭제. bind mount `pgdata/`는 유지됨. `init.sql`은 `pgdata/`가 빈 경우에만 실행
- **init.sql 마운트 필수**: `docker-compose.prod.yml`에 `./database/init.sql:/docker-entrypoint-initdb.d/01-init.sql` 없으면 최초 기동 시 빈 DB

---

## 17. 잔여 사항

| # | 항목 | 상태 | 비고 |
|---|---|---|---|
| 1 | ~~Phase 4-A CSS 레거시 클래스 제거~~ | **Close (해당 없음)** | Outlook Hub 프로젝트 이슈 혼입. mc-point-festival 미존재 확인 (2026-03-31) |
| 2 | Docker socket 권한 이슈 | ✅ 해결 | NAS: `sudo` 방식 확정. 또는 `synogroup --member docker starbee` 후 재로그인 |
| 3 | B-5 global.css 변경 이력 확인 | PM 수동 확인 대기 | Git 초기화 후 diff — 코드 결함 아님, WARNING 수준 |
| 4 | ~~P4 missions/{id}/status 라우트 롤백~~ | **Close (재적용 완료)** | P5 hotfix 오귀인으로 롤백됐으나 2026-03-31 재적용 확정. mission/schema+service+admin/router 복원 |

---

## 18. Phase 6 Task 목록 (대기)

> Phase 6 설계 미착수.
> **Phase 6: Home Page + Legacy (index.html 다크테마 마이그레이션)**

---

## 19. 보고 형식

### 작업 시작
```
제목: [작업명]
수행자: Claude Code
일시: [YYYY-MM-DD HH:MM]
Task ID: [PX-XXX]
상태: TODO → 진행중
목표: [한 줄 설명]
```

### 작업 완료
```
총소요시간: XX분
Task ID: [PX-XXX]
상태: 진행중 → 완료
생성/수정 파일: [경로 목록]
```

---

## 20. 주의사항

- **설계서에 없는 파일을 임의로 생성하지 마세요.** 실행 프롬프트에 명시된 파일만 생성합니다.
- **전역 CSS 파일을 추가하지 마세요.** global.css, reset.css 외 전역 스타일 금지.
- **router.py에 로직을 넣지 마세요.** service.py로 위임만 합니다.
- **Python import 순서**: stdlib → third-party → local (isort 규칙)
- **TypeScript strict mode** 호환 코드만 작성합니다.
- **useEffect 내 API 호출 시 AbortController cleanup 필수.**
- **폼 제출 API 호출에도 AbortController signal 전달 필수.** (AdminLoginView 패턴 참조)
- **인라인 style={{}} 5개/파일 초과 금지.** CSS Module로 이관합니다.

### Phase별 제약
- Phase 1~5: ✅ 완료 (수정 시 PM 승인 필요)
- Phase 6: Home Page — index.html 다크테마 마이그레이션
