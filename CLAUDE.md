# CLAUDE.md — 프로젝트 컨텍스트 (매 세션 필독)

> **프로젝트:** 마인크래프트 포인트 잔치 — 모던 스택 마이그레이션
> **최종 갱신:** 2026-03-31 | Phase 3 완료, Phase 4 설계 대기
> **이 파일은 프로젝트의 SSOT입니다. 매 세션 시작 시 반드시 읽으세요.**

---

## 1. 프로젝트 개요

가족용 포인트 관리 웹 서비스를 바닐라 JS + Firebase에서 React + FastAPI + PostgreSQL로 마이그레이션합니다.

| As-Is | To-Be |
|---|---|
| 바닐라 JS (3개 HTML) | React (Vite + TypeScript) |
| Firebase RTDB | PostgreSQL 16.9 LTS |
| Firebase Hosting | Docker 3-Tier (Synology NAS) |
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
- **AbortController**: useEffect 내 API 호출 시 cleanup에 abort() 필수 (Race Condition 방지)

### 인프라
- **Docker 3-Tier**: Frontend(Nginx) / Backend(FastAPI) / DB(PostgreSQL) 분리
- **개발**: `docker-compose.yml` (볼륨 마운트, 핫 리로드)
- **운영**: `docker-compose.prod.yml` (이미지 기반, NAS 경로)

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
├── .env
├── .gitignore
├── docker-compose.yml           # 개발용
├── docker-compose.prod.yml      # 운영용 (Synology NAS)
├── deploy.sh                    # OrbStack → NAS 배포
│
├── database/
│   └── init.sql                 # 11 테이블 + Seed (level.thresholds 포함)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI 앱 + 라우터 등록 (10개)
│       ├── config.py            # pydantic-settings
│       ├── database.py          # AsyncSession
│       ├── models/
│       │   ├── base.py          # Base + Mixin
│       │   └── all_models.py    # Junction Hub (10개 모델)
│       └── domains/
│           ├── auth/            # ✅ Phase 1
│           ├── player/          # ✅ Phase 1 + Phase 3 PATCH 추가
│           │   ├── router.py    # GET + PATCH
│           │   ├── service.py   # get_players + update_player
│           │   ├── schema.py    # PlayerListItem + PlayerUpdate
│           │   └── models.py
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
│       ├── App.tsx              # Router + ProtectedRoute + data-domain 래퍼
│       ├── styles/
│       │   ├── reset.css
│       │   └── global.css       # CSS Variables + 테마 격리
│       ├── shared/
│       │   ├── api/httpClient.ts
│       │   ├── stores/useAuthStore.ts
│       │   └── components/Button/
│       └── pages/
│           ├── Auth/            # ✅ Phase 1
│           │   ├── index.tsx
│           │   ├── Auth.module.css
│           │   ├── components/
│           │   ├── hooks/
│           │   └── api/
│           └── UserDashboard/   # ✅ Phase 3
│               ├── index.tsx
│               ├── UserDashboard.module.css
│               ├── components/
│               │   ├── DateSelector.tsx
│               │   ├── ProfileCard.tsx
│               │   ├── StoryCards.tsx
│               │   ├── MissionList.tsx
│               │   ├── MissionProposal.tsx
│               │   ├── FeedbackSection.tsx
│               │   ├── DeductionAccordion.tsx
│               │   ├── RankingView.tsx
│               │   ├── BottomNav.tsx
│               │   ├── StatDetailModal.tsx
│               │   ├── CheerModal.tsx
│               │   ├── ExpBar.tsx
│               │   ├── MissionProgressBar.tsx
│               │   └── ConfettiEffect.tsx
│               ├── hooks/
│               │   └── useDashboard.ts
│               └── api/
│                   └── dashboardApi.ts
│
└── _legacy/                     # ✅ Phase 1에서 이동 완료
    ├── index.html
    ├── user.html
    ├── admin.html
    ├── styles.css
    └── ...
```

---

## 6. 도메인 매핑 (Firebase → PostgreSQL)

| # | Firebase 노드 | BE 도메인 | DB 테이블 | Phase |
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

**mc_party_data** (레거시) → players + daily_points로 흡수, 별도 테이블 없음.

---

## 7. Phase 현황

| Phase | 초점 | 상태 |
|---|---|---|
| **1** | **Scaffolding + Auth** | **✅ 완료** |
| **2** | **Core Domains BE (8개 도메인 CRUD)** | **✅ 완료** |
| **3** | **User Dashboard FE (user.html 마이그레이션)** | **✅ 완료** |
| 4 | Admin Dashboard BE+FE (RBAC, 미션관리) | 대기 |
| 5 | Home Page + Legacy (index.html 다크테마) | 대기 |
| 6 | Data Migration + E2E (Firebase→PostgreSQL ETL) | 대기 |
| 7 | Production Deploy (NAS 배포, DNS, SSL) | 대기 |

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

## 11. 잔여 사항

| # | 항목 | 상태 | 비고 |
|---|---|---|---|
| 1 | ~~Phase 4-A CSS 레거시 클래스 제거~~ | **Close (해당 없음)** | Outlook Hub 프로젝트 이슈가 혼입된 것. mc-point-festival에 대상 파일(System/AdminSystem, Credit, RawData) 미존재 확인 (2026-03-31) |
| 2 | Docker socket 권한 이슈 | 해결 가이드 전달 | 방안 A 권장: 호스트에서 직접 pytest 실행 (venv + DB 포트 포워딩). Phase 4 병행 확인 가능 |
| 3 | B-5 global.css 변경 이력 확인 | PM 수동 확인 대기 | Git 초기화 후 diff — 코드 결함 아님, WARNING 수준 |

---

## 12. Phase 4 Task 목록 (다음)

> Phase 4 설계 미착수. 아래는 CLAUDE.md v2 기준 Phase 정의입니다.
> **Phase 4: Admin Dashboard BE+FE (RBAC, 미션관리)**

---

## 13. 보고 형식

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

## 14. 주의사항

- **설계서에 없는 파일을 임의로 생성하지 마세요.** 실행 프롬프트에 명시된 파일만 생성합니다.
- **전역 CSS 파일을 추가하지 마세요.** global.css, reset.css 외 전역 스타일 금지.
- **router.py에 로직을 넣지 마세요.** service.py로 위임만 합니다.
- **Python import 순서**: stdlib → third-party → local (isort 규칙)
- **TypeScript strict mode** 호환 코드만 작성합니다.
- **useEffect 내 API 호출 시 AbortController cleanup 필수.**
- **인라인 style={{}} 5개/파일 초과 금지.** CSS Module로 이관합니다.

### Phase별 제약
- Phase 1~3: ✅ 완료 (수정 시 PM 승인 필요)
- Phase 4: Admin Dashboard — BE RBAC + FE admin.html 마이그레이션
