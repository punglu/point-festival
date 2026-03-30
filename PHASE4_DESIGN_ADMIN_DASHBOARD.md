# Phase 4 설계서 — Admin Dashboard BE+FE

> **작성자:** Claude Web (Main Architect)
> **작성일:** 2026-03-31
> **대상 프로젝트:** 마인크래프트 포인트 잔치 — 모던 스택 마이그레이션
> **선행 조건:** Phase 1~3 완료 (CLAUDE.md v4 참조)
> **다음 단계:** Gemini 감사 → Claude Code 실행 → Codex QA

---

## 0. 설계 결정사항 요약

| 항목 | 결정 |
|---|---|
| Admin 인증 | JWT `is_admin` claim 추가 (Phase 1 auth 확장) |
| Step 분리 | Step 1 BE(RBAC + API 보강) → Step 2 FE(Admin 페이지) |
| Admin 테마 | 라이트 모드 (`[data-domain="admin"]` CSS Variable 분기) |
| Admin 진입 | ① UserDashboard BottomNav `onLongPress` ② `/admin` URL 직접 접근 |
| 미션 복제 | 전일 미션 → 오늘 복사, 포인트 수정 가능 옵션 포함 |

### 기능 범위 (8개)

| # | 기능 | BE 신규/보강 | FE 신규 |
|---|---|---|---|
| 1 | 미션 CRUD + 상태 관리 | 보강 (admin 상태 전이) | ✅ |
| 2 | 미션 복제 (전일→오늘) | **신규** | ✅ |
| 3 | 포인트 차감/동기화 | 기존 사용 | ✅ |
| 4 | 응원 메시지 작성 | 기존 사용 | ✅ |
| 5 | 플레이어 관리 (사진/정보) | 보강 (photo 업로드) | ✅ |
| 6 | 알림 관리 | 기존 사용 | ✅ |
| 7 | 피드백 조회/답글 | 기존 사용 | ✅ |
| 8 | 설정 관리 | 기존 사용 | ✅ |

---

## 1. Step 1: BE — RBAC + API 보강

### 1.1 인증/인가 확장

#### 1.1.1 DB 변경: `player_auth` 테이블에 `is_admin` 컬럼 추가

```sql
-- init.sql 추가
ALTER TABLE player_auth ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE;

-- Seed: 부모 계정을 admin으로 설정 (기존 Seed 수정)
-- 예: player_id가 'dad', 'mom'인 경우
UPDATE player_auth SET is_admin = TRUE WHERE player_id IN ('dad', 'mom');
```

> **주의:** init.sql은 Docker 최초 실행 시에만 적용됩니다. 기존 환경에서는 마이그레이션 SQL을 별도 실행해야 합니다.

#### 1.1.2 모델 변경: `app/domains/auth/models.py`

```python
# PlayerAuth 모델에 is_admin 추가
is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

#### 1.1.3 JWT Payload 확장: `app/domains/auth/service.py`

```python
# 토큰 생성 시 is_admin claim 추가
def create_access_token(player_id: str, is_admin: bool) -> str:
    payload = {
        "sub": player_id,
        "is_admin": is_admin,  # ← 추가
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

#### 1.1.4 RBAC 미들웨어: `app/domains/auth/dependencies.py` (신규)

```python
# -- 의존성 함수 (FastAPI Depends) --
# GET /api/... → get_current_user (기존)
# Admin 전용 API → get_admin_user (신규)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """JWT 디코딩 → player_id + is_admin 반환"""
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return {"player_id": payload["sub"], "is_admin": payload.get("is_admin", False)}

async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Admin 권한 검증 — is_admin=False이면 403"""
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

> **Thin Controller 원칙:** HTTPException은 dependencies.py(미들웨어 레이어)에서만 발생. router.py에는 넣지 않음.

#### 1.1.5 기존 auth router 보강: 로그인 응답에 `is_admin` 포함

```python
# POST /api/auth/login 응답 스키마 확장
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player_id: str
    player_name: str
    is_admin: bool  # ← 추가
```

---

### 1.2 미션 복제 API (신규)

#### 엔드포인트

```
POST /api/missions/clone
```

#### 요청 스키마

```python
class MissionCloneRequest(BaseModel):
    source_player_id: str          # 대상 플레이어
    source_date: str               # 복제 원본 날짜 (YYYY-MM-DD)
    target_date: str               # 복제 대상 날짜 (YYYY-MM-DD)
    point_overrides: dict[str, int] | None = None
    # key: 원본 mission_id, value: 변경할 포인트
    # None이면 원본 포인트 그대로 복제
```

#### 서비스 로직 (`mission/service.py`)

```python
async def clone_missions(
    db: AsyncSession,
    request: MissionCloneRequest,
    admin_user: dict
) -> list[Mission]:
    """
    -- RAW SQL 참조 --
    SELECT * FROM missions
    WHERE player_id = :source_player_id
      AND mission_date = :source_date
      AND deleted_at IS NULL;

    INSERT INTO missions (id, player_id, mission_date, text, point, status, sender, msg, "order", created_at)
    VALUES (:new_id, :player_id, :target_date, :text, :point, 'active', :sender, :msg, :order, NOW());
    """
    # 1. source_date의 미션 조회
    # 2. target_date에 동일 미션 생성 (status='active'로 초기화)
    # 3. point_overrides가 있으면 해당 미션의 포인트 변경
    # 4. 생성된 미션 목록 반환
```

#### 응답

```python
class MissionCloneResponse(BaseModel):
    cloned_count: int
    missions: list[MissionItem]
```

---

### 1.3 플레이어 관리 API 보강

#### 1.3.1 플레이어 정보 수정 확장: `PATCH /api/players/{player_id}`

기존 Phase 3에서 `statusMsg`만 수정 가능했던 것을 확장:

```python
class PlayerUpdateAdmin(BaseModel):
    name: str | None = None
    status_msg: str | None = None
    photo: str | None = None       # Base64 이미지 (신규)
```

> **Admin 전용:** `Depends(get_admin_user)` 적용. 일반 Player는 기존 `PlayerUpdate` (statusMsg만) 유지.

#### 1.3.2 플레이어 잠금/해제 (신규)

```
PATCH /api/players/{player_id}/lock
```

```python
class PlayerLockRequest(BaseModel):
    is_locked: bool  # True=잠금, False=해제
```

> **구현:** `players` 테이블에 `is_locked` 컬럼 추가 (Boolean, default=False).
> 잠긴 플레이어는 로그인 시 차단 (auth/service.py에서 검증).

---

### 1.4 Admin 전용 라우터 등록

#### `app/domains/admin/router.py` (신규 도메인)

```python
"""
Admin 전용 집합 라우터.
각 도메인의 기존 서비스를 재사용하되, Admin 권한 검증(get_admin_user)을 적용.
비즈니스 로직은 각 도메인의 service.py에 위임 (Thin Controller 원칙).
"""

# Admin 라우터에서 호출하는 기존 서비스:
# - mission/service.py → create_mission, update_mission, delete_mission, clone_missions
# - deduction/service.py → create_deduction
# - daily_point/service.py → adjust_daily_point
# - cheer/service.py → create_or_update_cheer
# - player/service.py → update_player_admin, lock_player
# - notification/service.py → create_notification, mark_as_read
# - feedback/service.py → create_reply
# - config/service.py → update_config
```

#### 라우트 목록

| Method | Path | 기능 | 기존/신규 |
|---|---|---|---|
| POST | `/api/admin/missions` | 미션 생성 | 기존 service 재사용 |
| PATCH | `/api/admin/missions/{id}` | 미션 수정 | 기존 service 재사용 |
| DELETE | `/api/admin/missions/{id}` | 미션 삭제 (soft) | 기존 service 재사용 |
| PATCH | `/api/admin/missions/{id}/status` | 미션 상태 변경 (admin 전이) | 기존 service 재사용 |
| POST | `/api/admin/missions/clone` | 미션 복제 | **신규 service** |
| POST | `/api/admin/deductions` | 포인트 차감 | 기존 service 재사용 |
| POST | `/api/admin/daily-points/adjust` | 포인트 동기화 | 기존 service 재사용 |
| PUT | `/api/admin/cheers/{date}` | 응원 메시지 작성 | 기존 service 재사용 |
| PATCH | `/api/admin/players/{id}` | 플레이어 정보 수정 | 보강 service |
| PATCH | `/api/admin/players/{id}/lock` | 플레이어 잠금/해제 | **신규 service** |
| POST | `/api/admin/notifications` | 알림 생성 | 기존 service 재사용 |
| POST | `/api/admin/feedbacks/{id}/replies` | 피드백 답글 | 기존 service 재사용 |
| GET | `/api/admin/configs` | 설정 목록 조회 | 기존 service 재사용 |
| PUT | `/api/admin/configs/{key}` | 설정 수정 | 기존 service 재사용 |

> **모든 `/api/admin/*` 라우트에 `Depends(get_admin_user)` 적용.**

---

### 1.5 DB 변경 총괄

| 테이블 | 변경 | 내용 |
|---|---|---|
| `player_auth` | ALTER | `is_admin BOOLEAN NOT NULL DEFAULT FALSE` 추가 |
| `players` | ALTER | `is_locked BOOLEAN NOT NULL DEFAULT FALSE` 추가 |

> **init.sql 수정 범위:** 위 2개 컬럼 추가 + admin Seed 데이터.

---

### 1.6 Step 1 파일 목록

| # | 경로 | 작업 | 상태 |
|---|---|---|---|
| 1 | `database/init.sql` | `player_auth.is_admin`, `players.is_locked` 컬럼 + Seed | 수정 |
| 2 | `backend/app/domains/auth/models.py` | `is_admin` 필드 추가 | 수정 |
| 3 | `backend/app/domains/auth/schema.py` | `LoginResponse.is_admin` 추가 | 수정 |
| 4 | `backend/app/domains/auth/service.py` | JWT payload에 `is_admin` 포함 | 수정 |
| 5 | `backend/app/domains/auth/dependencies.py` | `get_current_user`, `get_admin_user` | **신규** |
| 6 | `backend/app/domains/player/models.py` | `is_locked` 필드 추가 | 수정 |
| 7 | `backend/app/domains/player/schema.py` | `PlayerUpdateAdmin`, `PlayerLockRequest` 추가 | 수정 |
| 8 | `backend/app/domains/player/service.py` | `update_player_admin`, `lock_player` 추가 | 수정 |
| 9 | `backend/app/domains/mission/schema.py` | `MissionCloneRequest`, `MissionCloneResponse` 추가 | 수정 |
| 10 | `backend/app/domains/mission/service.py` | `clone_missions` 추가 | 수정 |
| 11 | `backend/app/domains/admin/` | **신규 도메인 디렉토리** | **신규** |
| 12 | `backend/app/domains/admin/__init__.py` | 빈 파일 | **신규** |
| 13 | `backend/app/domains/admin/router.py` | Admin 집합 라우터 | **신규** |
| 14 | `backend/app/main.py` | admin router 등록 | 수정 |
| 15 | `backend/app/models/all_models.py` | 변경 없음 (기존 모델 수정만) | — |

**Step 1 완료 조건:**
- `py_compile` 전체 PASS
- 기존 API 회귀 없음 (기존 라우트 동작 유지)
- `/api/admin/*` 라우트 is_admin=False → 403 반환 확인

---

## 2. Step 2: FE — Admin Dashboard 페이지

### 2.1 디렉토리 구조

```
frontend/src/pages/AdminDashboard/
├── index.tsx                    # Admin 페이지 엔트리
├── AdminDashboard.module.css    # Admin 전용 스타일
├── components/
│   ├── AdminNav.tsx             # Admin 탭 네비게이션
│   ├── MissionManager.tsx       # 미션 CRUD + 상태 관리
│   ├── MissionCloneModal.tsx    # 미션 복제 모달 (포인트 수정 가능)
│   ├── PointManager.tsx         # 포인트 차감/동기화
│   ├── CheerEditor.tsx          # 응원 메시지 작성
│   ├── PlayerManager.tsx        # 플레이어 관리 (사진/정보/잠금)
│   ├── NotificationManager.tsx  # 알림 관리
│   ├── FeedbackViewer.tsx       # 피드백 조회/답글
│   └── ConfigManager.tsx        # 설정 관리
├── hooks/
│   └── useAdmin.ts              # Admin 데이터 로드 + 상태 관리
└── api/
    └── adminApi.ts              # Admin API 호출 레이어
```

### 2.2 라우트 변경: `App.tsx`

```tsx
// 기존
<Route path="/admin" element={<div>Phase 4 placeholder</div>} />

// 변경
<Route
  path="/admin"
  element={
    <AdminProtectedRoute>
      <AdminDashboard />
    </AdminProtectedRoute>
  }
/>
```

#### AdminProtectedRoute 컴포넌트

```tsx
/**
 * Admin 전용 보호 라우트.
 * 조건: isLoggedIn + isAdmin
 * 미충족 시: / (Auth 페이지)로 리다이렉트
 */
function AdminProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, isAdmin } = useAuthStore();

  if (!isLoggedIn || !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
```

#### useAuthStore 확장

```typescript
// shared/stores/useAuthStore.ts에 isAdmin 상태 추가
interface AuthState {
  isLoggedIn: boolean;
  playerId: string | null;
  playerName: string | null;
  isAdmin: boolean;           // ← 추가
  token: string | null;
  login: (response: LoginResponse) => void;
  logout: () => void;
}
```

### 2.3 Admin 진입점

#### 방법 1: UserDashboard BottomNav onLongPress

```tsx
// UserDashboard/components/BottomNav.tsx 수정
// 기존: Phase 4 placeholder로 이관 예정이었던 onLongPress
// 변경: /admin으로 네비게이트

const handleLongPress = () => {
  if (isAdmin) {
    navigate('/admin');
  }
};

// 3초 롱프레스 감지
const longPressTimer = useRef<NodeJS.Timeout | null>(null);

const onTouchStart = () => {
  longPressTimer.current = setTimeout(handleLongPress, 3000);
};

const onTouchEnd = () => {
  if (longPressTimer.current) {
    clearTimeout(longPressTimer.current);
  }
};
```

#### 방법 2: /admin URL 직접 접근

```
AdminProtectedRoute가 isAdmin을 검증하므로,
일반 Player가 /admin에 접근하면 자동으로 / 로 리다이렉트.
Admin 계정으로 로그인 후 /admin 직접 이동 가능.
```

### 2.4 컴포넌트 상세

#### 2.4.1 AdminNav.tsx — 탭 네비게이션

```
┌─────────────────────────────────────────────┐
│  [미션] [포인트] [응원] [플레이어] [더보기▾] │
└─────────────────────────────────────────────┘
           └── 알림 / 피드백 / 설정
```

- 상단 탭 바 (5개 메인 + 더보기 드롭다운)
- 모바일: 가로 스크롤 가능
- 활성 탭 하이라이트

#### 2.4.2 MissionManager.tsx — 미션 CRUD + 상태

```
┌──────────────────────────────────────┐
│ 플레이어 선택: [손유비▾]  날짜: [◀ 2026-03-31 ▶] │
├──────────────────────────────────────┤
│ + 미션 추가                    [복제] │
├──────────────────────────────────────┤
│ ☐ 숙제하기         10P   active     │
│   [수정] [삭제] [승인] [실패]        │
├──────────────────────────────────────┤
│ ☐ 방 청소          15P   completed  │
│   [수정] [삭제]                      │
└──────────────────────────────────────┘
```

**기능:**
- 플레이어 선택 드롭다운
- 날짜 네비게이션 (좌우 화살표)
- 미션 추가 폼 (text, point, sender, msg)
- 미션 수정 (인라인 편집)
- 미션 삭제 (soft delete, 확인 모달)
- 상태 변경 버튼 (admin 전이: active→completed, active→failed, completed→active)
- **복제 버튼** → MissionCloneModal 열기

#### 2.4.3 MissionCloneModal.tsx — 미션 복제

```
┌─────────────────────────────────────────┐
│ 미션 복제                          [✕] │
├─────────────────────────────────────────┤
│ 원본 날짜: 2026-03-30                   │
│ 대상 날짜: 2026-03-31                   │
├─────────────────────────────────────────┤
│ ☑ 숙제하기       [10] P ← 수정 가능    │
│ ☑ 방 청소        [15] P ← 수정 가능    │
│ ☐ 독서 (30분)    [20] P                │
├─────────────────────────────────────────┤
│ 선택된 미션: 2개                        │
│            [복제 실행]                  │
└─────────────────────────────────────────┘
```

**기능:**
- 전일 미션 목록 표시 (체크박스로 선택)
- 각 미션의 포인트를 인라인 수정 가능 (input number)
- 선택한 미션만 오늘 날짜로 복제
- 복제 후 MissionManager 목록 자동 갱신

#### 2.4.4 PointManager.tsx — 포인트 차감/동기화

```
┌──────────────────────────────────────┐
│ 플레이어 선택: [손유비▾]             │
├──────────────────────────────────────┤
│ 현재 보유 포인트: 280P               │
├──────────────────────────────────────┤
│ 💸 포인트 차감                       │
│ 금액: [    ] P                       │
│ 사유: [간식______]                   │
│ [차감하기]                           │
├──────────────────────────────────────┤
│ 차감 이력                            │
│ 2026-03-30  -50P  장난감             │
│ 2026-03-28  -30P  간식              │
└──────────────────────────────────────┘
```

#### 2.4.5 CheerEditor.tsx — 응원 메시지

```
┌──────────────────────────────────────┐
│ 날짜: [◀ 2026-03-31 ▶]              │
├──────────────────────────────────────┤
│ 아빠 메시지:                         │
│ [오늘도 화이팅!_________________]    │
├──────────────────────────────────────┤
│ 엄마 메시지:                         │
│ [잘하고 있어!__________________]     │
├──────────────────────────────────────┤
│ [저장]                               │
└──────────────────────────────────────┘
```

#### 2.4.6 PlayerManager.tsx — 플레이어 관리

```
┌──────────────────────────────────────┐
│ 플레이어 목록                        │
├──────────────────────────────────────┤
│ [📷] 손유비  280P  상태: 활성   [수정] │
│ [📷] 형제1   150P  상태: 활성   [수정] │
│ [📷] 형제2   200P  상태: 잠금🔒 [해제] │
├──────────────────────────────────────┤
│ 수정 모달:                           │
│ 이름: [손유비_____]                  │
│ 사진: [업로드]  [미리보기]           │
│ 상태 메시지: [오늘 행복!___]         │
│ [저장] [잠금/해제]                   │
└──────────────────────────────────────┘
```

#### 2.4.7 NotificationManager.tsx — 알림 관리

```
┌──────────────────────────────────────┐
│ 알림 목록                      [+추가] │
├──────────────────────────────────────┤
│ 🔔 미션 승인 요청 — 손유비  미읽음   │
│ 🔔 미션 제안 — 형제1        읽음     │
│ [읽음 처리] [삭제]                   │
└──────────────────────────────────────┘
```

#### 2.4.8 FeedbackViewer.tsx — 피드백 조회/답글

```
┌──────────────────────────────────────┐
│ 플레이어: [전체▾]  날짜: [◀ ▶]      │
├──────────────────────────────────────┤
│ 손유비 (2026-03-31)                  │
│ "오늘 숙제가 너무 많았어요"          │
│   ↳ 아빠: "내일은 줄여줄게!"        │
│   ↳ [답글 작성...]                   │
├──────────────────────────────────────┤
│ 형제1 (2026-03-31)                   │
│ "미션 재밌었어요!"                   │
│   ↳ [답글 작성...]                   │
└──────────────────────────────────────┘
```

#### 2.4.9 ConfigManager.tsx — 설정 관리

```
┌──────────────────────────────────────┐
│ 설정 관리                            │
├──────────────────────────────────────┤
│ level.thresholds:                    │
│ [JSON 편집기]                        │
│                                      │
│ 부모 사진:                           │
│ 아빠 [📷 업로드]                     │
│ 엄마 [📷 업로드]                     │
├──────────────────────────────────────┤
│ [저장]                               │
└──────────────────────────────────────┘
```

---

### 2.5 API 레이어: `adminApi.ts`

```typescript
// Admin API 호출 함수 목록
// 모든 함수는 signal: AbortSignal 파라미터를 지원

// 미션
createMission(data, signal?)
updateMission(id, data, signal?)
deleteMission(id, signal?)
updateMissionStatus(id, status, signal?)
cloneMissions(data, signal?)

// 포인트
createDeduction(data, signal?)
adjustDailyPoint(data, signal?)

// 응원
updateCheer(date, data, signal?)

// 플레이어
updatePlayerAdmin(id, data, signal?)
lockPlayer(id, isLocked, signal?)

// 알림
getNotifications(signal?)
createNotification(data, signal?)
markNotificationRead(id, signal?)

// 피드백
getFeedbacks(playerId?, date?, signal?)
createReply(feedbackId, data, signal?)

// 설정
getConfigs(signal?)
updateConfig(key, value, signal?)
```

### 2.6 커스텀 훅: `useAdmin.ts`

```typescript
/**
 * Admin 페이지 전체 데이터 관리 훅.
 * - 플레이어 목록 로드
 * - 활성 탭 상태
 * - 선택된 플레이어/날짜 상태
 * - AbortController 적용 (useEffect cleanup)
 */
interface UseAdminReturn {
  players: Player[];
  selectedPlayerId: string | null;
  selectedDate: string;
  activeTab: AdminTab;
  setSelectedPlayerId: (id: string) => void;
  setSelectedDate: (date: string) => void;
  setActiveTab: (tab: AdminTab) => void;
  loading: boolean;
  error: string | null;
}
```

### 2.7 CSS: `AdminDashboard.module.css`

- `[data-domain="admin"]` 기반 라이트 테마 변수 (UserDashboard와 동일 톤)
- Admin 전용 레이아웃 (탭 바, 관리 카드, 모달)
- 모바일 반응형 (min-width 기반)
- **인라인 style={{}} 5개/파일 미만 준수**

### 2.8 App.tsx 변경 사항

```tsx
// 1. AdminProtectedRoute 추가
// 2. /admin 라우트를 placeholder → AdminDashboard로 교체
// 3. data-domain="admin" 래퍼 적용
```

---

### 2.9 Step 2 파일 목록

| # | 경로 | 작업 |
|---|---|---|
| 1 | `frontend/src/pages/AdminDashboard/index.tsx` | **신규** |
| 2 | `frontend/src/pages/AdminDashboard/AdminDashboard.module.css` | **신규** |
| 3 | `frontend/src/pages/AdminDashboard/components/AdminNav.tsx` | **신규** |
| 4 | `frontend/src/pages/AdminDashboard/components/MissionManager.tsx` | **신규** |
| 5 | `frontend/src/pages/AdminDashboard/components/MissionCloneModal.tsx` | **신규** |
| 6 | `frontend/src/pages/AdminDashboard/components/PointManager.tsx` | **신규** |
| 7 | `frontend/src/pages/AdminDashboard/components/CheerEditor.tsx` | **신규** |
| 8 | `frontend/src/pages/AdminDashboard/components/PlayerManager.tsx` | **신규** |
| 9 | `frontend/src/pages/AdminDashboard/components/NotificationManager.tsx` | **신규** |
| 10 | `frontend/src/pages/AdminDashboard/components/FeedbackViewer.tsx` | **신규** |
| 11 | `frontend/src/pages/AdminDashboard/components/ConfigManager.tsx` | **신규** |
| 12 | `frontend/src/pages/AdminDashboard/hooks/useAdmin.ts` | **신규** |
| 13 | `frontend/src/pages/AdminDashboard/api/adminApi.ts` | **신규** |
| 14 | `frontend/src/App.tsx` | 수정 (AdminProtectedRoute + 라우트) |
| 15 | `frontend/src/shared/stores/useAuthStore.ts` | 수정 (isAdmin 추가) |
| 16 | `frontend/src/pages/UserDashboard/components/BottomNav.tsx` | 수정 (onLongPress) |

**Step 2 완료 조건:**
- `npm run build` 0 errors
- `npx tsc --noEmit` 0 errors
- `/admin` 접근 시 Admin 페이지 렌더링
- is_admin=false 계정 → `/admin` 접근 시 `/`로 리다이렉트
- onLongPress (3초) → `/admin` 이동 확인

---

## 3. Task ID 매핑

### Step 1: BE

| Task ID | 작업 | 파일 |
|---|---|---|
| P4-001 | init.sql 변경 (is_admin, is_locked 컬럼 + Seed) | database/init.sql |
| P4-002 | auth 모델/스키마/서비스 확장 (is_admin) | auth/models, schema, service |
| P4-003 | auth dependencies 신규 (get_current_user, get_admin_user) | auth/dependencies.py |
| P4-004 | player 모델/스키마/서비스 보강 (is_locked, photo, admin 수정) | player/models, schema, service |
| P4-005 | mission 스키마/서비스 보강 (clone_missions) | mission/schema, service |
| P4-006 | admin 도메인 신규 (router.py) | admin/__init__, router |
| P4-007 | main.py admin router 등록 | main.py |
| P4-008 | Step 1 빌드 검증 (py_compile + 회귀 확인) | — |

### Step 2: FE

| Task ID | 작업 | 파일 |
|---|---|---|
| P4-009 | useAuthStore 확장 (isAdmin) | shared/stores/useAuthStore.ts |
| P4-010 | adminApi.ts (14개 API 함수) | AdminDashboard/api/adminApi.ts |
| P4-011 | useAdmin.ts 훅 | AdminDashboard/hooks/useAdmin.ts |
| P4-012 | AdminDashboard.module.css | AdminDashboard/AdminDashboard.module.css |
| P4-013 | AdminNav.tsx | AdminDashboard/components/AdminNav.tsx |
| P4-014 | MissionManager.tsx + MissionCloneModal.tsx | AdminDashboard/components/ |
| P4-015 | PointManager.tsx | AdminDashboard/components/ |
| P4-016 | CheerEditor.tsx | AdminDashboard/components/ |
| P4-017 | PlayerManager.tsx | AdminDashboard/components/ |
| P4-018 | NotificationManager.tsx + FeedbackViewer.tsx + ConfigManager.tsx | AdminDashboard/components/ |
| P4-019 | index.tsx (Admin 엔트리 조립) | AdminDashboard/index.tsx |
| P4-020 | App.tsx 변경 (AdminProtectedRoute + 라우트) | App.tsx |
| P4-021 | BottomNav.tsx 수정 (onLongPress) | UserDashboard/components/BottomNav.tsx |
| P4-022 | Step 2 빌드 검증 (npm build + tsc) | — |

---

## 4. 아키텍처 준수 체크리스트

| # | 원칙 | Phase 4 적용 |
|---|---|---|
| 1 | Thin Controller | admin/router.py → 각 도메인 service.py 위임 |
| 2 | SQL Annotation | clone_missions 등 신규 함수에 RAW SQL 주석 |
| 3 | Soft Delete | mission 삭제 시 deleted_at 사용 |
| 4 | 문자열 FK | 신규 컬럼에 FK 없음 (is_admin, is_locked은 Boolean) |
| 5 | Vertical Domain | admin/ 도메인 신규 생성 (router만, 자체 model 없음) |
| 6 | 1 Page = 1 Dir | AdminDashboard/ 수직 응집 |
| 7 | CSS Modules | AdminDashboard.module.css, 인라인 5개 미만 |
| 8 | AbortController | useAdmin.ts + adminApi.ts signal 전달 |
| 9 | Shared 승격 규칙 | AdminProtectedRoute는 App.tsx 로컬 유지 (1곳 사용) |

---

## 5. Gemini 감사 요청 포인트

1. **RBAC 구조**: dependencies.py의 get_admin_user가 충분한가? 미들웨어 vs Depends 방식 적절성.
2. **Admin 도메인 분리**: admin/router.py가 다른 도메인 service를 직접 호출하는 구조의 결합도.
3. **미션 복제 로직**: clone_missions의 트랜잭션 안전성, 동시성 문제.
4. **JWT is_admin**: 토큰 탈취 시 admin 권한 에스컬레이션 위험. Refresh Token 필요 여부.
5. **FE 컴포넌트 수**: 9개 컴포넌트가 단일 페이지에 적절한 규모인지.

---

## 6. 실행 순서 요약

```
1. PM → 본 설계서 승인
2. Gemini → 설계 감사 (Pass/Fail)
3. Claude Code → Step 1 실행 (P4-001 ~ P4-008)
4. Codex → Step 1 QA
5. Claude Code → Step 2 실행 (P4-009 ~ P4-022)
6. Codex → Step 2 QA
7. Gemini → 최종 재감사
8. PM → Phase 4 승인
```
