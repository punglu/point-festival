# Phase 5 실행 지시서 — Login Hub + Admin 인증 분리

> **수행자:** Claude Code
> **기준 문서:** `PHASE5_DESIGN_LOGIN_HUB.md`, `CLAUDE.md` v4
> **목표:** Auth 페이지를 Login Hub로 리팩토링 + Admin ID/PW 인증 분리
> **제약:** 설계서에 명시된 파일만 생성/수정. 다른 코드 변경 금지.

---

## Step 1: BE — Admin 인증 기반 구축 (P5-001 ~ P5-007)

### P5-001: init.sql 변경

`database/init.sql`에 `admin_auth` 테이블 추가.

```sql
CREATE TABLE admin_auth (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    display_name VARCHAR(50) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMP NULL DEFAULT NULL
);
```

**Seed 데이터:**
- Python으로 bcrypt 해시 생성 후 INSERT문에 삽입
- 계정 2개: `dad` / `mom`
- **초기 비밀번호는 `admin1234` 로 통일** (운영 배포 시 변경)

```python
# 해시 생성 예시 (Claude Code에서 실행)
import bcrypt
hashed = bcrypt.hashpw('admin1234'.encode(), bcrypt.gensalt()).decode()
print(hashed)
```

```sql
INSERT INTO admin_auth (username, password, display_name) VALUES
    ('dad', '<위에서_생성한_해시값>', '아빠'),
    ('mom', '<위에서_생성한_해시값>', '엄마');
```

**주의:**
- 평문 비밀번호를 init.sql에 넣지 말 것
- 기존 테이블 정의 변경 없이 admin_auth만 추가
- 테이블 위치: 기존 CREATE TABLE 문들 뒤, Seed INSERT 문들 앞

---

### P5-002: AdminAuth 모델 추가

`backend/app/domains/auth/models.py`에 AdminAuth 클래스 추가.

```python
from app.models.base import Base, SoftDeleteMixin

class AdminAuth(Base, SoftDeleteMixin):
    __tablename__ = "admin_auth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    # deleted_at은 SoftDeleteMixin에서 상속
```

**주의:**
- 기존 `PlayerAuth` 클래스는 변경하지 않을 것
- import 추가 필요: `SoftDeleteMixin`, `Integer`, `DateTime`, `func` 등 기존 import에 맞춰 추가

---

### P5-003: Admin 로그인 스키마 추가

`backend/app/domains/auth/schema.py`에 추가.

```python
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    display_name: str
    is_admin: bool = True
```

**주의:** 기존 스키마 (LoginRequest, LoginResponse 등) 변경 금지.

---

### P5-004: authenticate_admin 서비스 함수 추가

`backend/app/domains/auth/service.py`에 추가.

```python
async def authenticate_admin(
    db: AsyncSession,
    username: str,
    password: str
) -> AdminLoginResponse:
    """
    -- RAW SQL 참조 --
    SELECT * FROM admin_auth
    WHERE username = :username
      AND deleted_at IS NULL;
    """
    # 1. username으로 admin_auth 조회 (deleted_at IS NULL)
    # 2. 조회 결과 없으면 ValueError raise
    # 3. bcrypt.checkpw(password.encode(), admin.password.encode()) 검증
    # 4. 실패 시 ValueError raise
    # 5. JWT 생성: create_access_token(player_id=admin.username, is_admin=True)
    #    → 기존 create_access_token 함수 재사용
    # 6. AdminLoginResponse 반환 (access_token, display_name, is_admin=True)
```

**Thin Controller 원칙:**
- 모든 검증/예외는 service 레벨에서 처리
- ValueError를 raise하면 router의 에러 핸들러가 처리
- service.py에서 HTTPException을 직접 raise하지 않을 것 (기존 패턴 확인 후 동일하게 처리)

**기존 패턴 확인:**
- 기존 `authenticate_player` 함수의 에러 처리 방식을 확인하고 동일하게 적용
- `create_access_token` 함수의 시그니처를 확인하고 재사용

---

### P5-005: Admin 로그인 라우트 추가

`backend/app/domains/auth/router.py`에 추가.

```python
@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.authenticate_admin(
        db=db, username=request.username, password=request.password
    )
```

**주의:**
- 기존 라우트 변경 금지
- HTTPException 없음 (Thin Controller)
- 에러 처리는 service에서 raise → 기존 에러 핸들러가 처리

---

### P5-006: all_models.py 갱신

`backend/app/models/all_models.py`에 AdminAuth import 추가.

```python
from app.domains.auth.models import PlayerAuth, AdminAuth  # AdminAuth 추가
```

**주의:** import만 추가. 다른 코드 변경 금지.

---

### P5-007: Step 1 빌드 검증

```bash
# 1) py_compile 전체
find backend/app -name "*.py" -exec python -m py_compile {} \;

# 2) DB 초기화 + 재기동
docker compose down -v
docker compose up -d
sleep 30

# 3) DB 에러 확인
docker compose logs db 2>&1 | grep -i "error"
# → 0건

# 4) admin_auth 테이블 존재 확인
docker compose exec db psql -U postgres -d mc_point_festival -c "\d admin_auth"

# 5) Seed 확인
docker compose exec db psql -U postgres -d mc_point_festival -c "SELECT username, display_name, deleted_at FROM admin_auth;"
# → dad/아빠, mom/엄마, deleted_at NULL

# 6) 3 서비스 healthy
docker compose ps

# 7) 기존 Player 로그인 회귀 확인 (기존 API 동작)
# → POST /api/auth/login 이 정상 동작하는지 확인
```

---

## Step 2: FE — Login Hub (P5-008 ~ P5-016)

### P5-008: authApi.ts 확장

`frontend/src/pages/Auth/api/authApi.ts`에 추가.

```typescript
export async function adminLogin(
  username: string,
  password: string,
  signal?: AbortSignal
): Promise<AdminLoginResponse> {
  const { data } = await httpClient.post('/auth/admin/login', {
    username, password
  }, { signal });
  return data;
}

export interface AdminLoginResponse {
  access_token: string;
  token_type: string;
  display_name: string;
  is_admin: boolean;
}
```

**주의:** 기존 함수/타입 변경 금지. 추가만.

---

### P5-009: useAuthStore 확장

`frontend/src/shared/stores/useAuthStore.ts` 수정.

추가 항목:
- `adminDisplayName: string | null` 상태
- `adminLogin(response: AdminLoginResponse)` 액션

```typescript
// adminLogin 액션 구현
adminLogin: (response) => set({
  isLoggedIn: true,
  isAdmin: true,
  token: response.access_token,
  adminDisplayName: response.display_name,
  playerId: null,      // Admin은 player가 아님
  playerName: null,
}),
```

**주의:**
- 기존 `login`, `logout` 액션 변경 최소화
- `logout`에서 `adminDisplayName: null` 초기화 추가

---

### P5-010: PlayerCard.tsx 신규

`frontend/src/pages/Auth/components/PlayerCard.tsx` 생성.

```tsx
// 캐릭터 카드 컴포넌트
// Props: player (photo, name, totalPoints 등), onSelect 콜백
// photo가 있으면 <img src={`data:image/...;base64,${photo}`} /> 표시
// photo가 없으면 이니셜 + 배경색 폴백
// 이름, 포인트 표시
// 클릭 시 onSelect(player)
```

이니셜 폴백 색상 배열:
```typescript
const FALLBACK_COLORS = [
  { bg: '#E1F5EE', text: '#085041' },  // teal
  { bg: '#E6F1FB', text: '#0C447C' },  // blue
  { bg: '#FAEEDA', text: '#633806' },  // amber
  { bg: '#EEEDFE', text: '#3C3489' },  // purple
];
// index % FALLBACK_COLORS.length 로 순환
```

**사진 표시 규칙:**
- 원형 크롭 (`border-radius: 50%`)
- 크기: 64px × 64px
- `object-fit: cover`
- Base64 문자열이 `data:` prefix를 포함할 수 있으므로 처리 필요:
  ```tsx
  const src = photo.startsWith('data:') ? photo : `data:image/jpeg;base64,${photo}`;
  ```

---

### P5-011: PlayerSelectView.tsx 신규

`frontend/src/pages/Auth/components/PlayerSelectView.tsx` 생성.

```tsx
// 캐릭터 카드 선택 화면
// Props: onPlayerSelect(player), onAdminClick()
// useEffect로 GET /api/players 호출 (AbortController 적용)
// 플레이어 목록을 PlayerCard 그리드로 표시
// 하단에 "관리자 로그인 →" 링크
```

**그리드 레이아웃 규칙:**
- 기본: `grid-template-columns: repeat(2, 1fr)`
- 1명: 단일 열 중앙 (`max-width: 200px; margin: 0 auto`)
- 3명: 2열, 마지막 카드 중앙 정렬
  ```css
  .cardGridThree > :last-child:nth-child(odd) {
    grid-column: 1 / -1;
    max-width: 50%;
    justify-self: center;
  }
  ```
- 4명+: 기본 2열 다행

**AbortController 패턴:**
```tsx
useEffect(() => {
  const controller = new AbortController();
  loadPlayers(controller.signal);
  return () => controller.abort();
}, []);
```

---

### P5-012: PinInputView.tsx 신규

`frontend/src/pages/Auth/components/PinInputView.tsx` 생성.

```tsx
// 기존 Auth 페이지의 PIN 입력 로직을 분리한 컴포넌트
// Props: player (선택된 플레이어), onBack (뒤로가기 콜백)
// 상단: 플레이어 사진/이니셜 + 이름 표시
// 중단: 4자리 PIN 입력 (기존 로직 재사용)
// 하단: "← 다른 플레이어 선택" 링크 → onBack()
// PIN 성공 시: useAuthStore.login() → navigate('/dashboard')
```

**주의:**
- 기존 Auth 페이지의 PIN 입력 로직을 최대한 그대로 가져올 것
- 기존 useAuth.ts 훅이 있다면 재사용
- PIN 입력 UX 변경 최소화 (사용자 혼란 방지)

---

### P5-013: AdminLoginView.tsx 신규

`frontend/src/pages/Auth/components/AdminLoginView.tsx` 생성.

```tsx
// 관리자 ID/PW 로그인 폼
// Props: onBack (뒤로가기 콜백)
// 아이디 입력 (text), 비밀번호 입력 (password), 로그인 버튼
// 제출 시 authApi.adminLogin() 호출
// 성공 시: useAuthStore.adminLogin() → navigate('/admin')
// 실패 시: 에러 메시지 표시 ("아이디 또는 비밀번호가 올바르지 않습니다")
// 하단: "← 플레이어 선택으로" 링크 → onBack()
```

**AbortController 적용:**
- 폼 제출 시에도 signal 전달
- 컴포넌트 언마운트 시 cleanup

---

### P5-014: Auth/index.tsx 리팩토링

`frontend/src/pages/Auth/index.tsx`를 Login Hub 구조로 리팩토링.

```tsx
function AuthPage() {
  const [mode, setMode] = useState<'select' | 'pin' | 'admin'>('select');
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);

  const handlePlayerSelect = (player: Player) => {
    setSelectedPlayer(player);
    setMode('pin');
  };

  const handleBackToSelect = () => {
    setSelectedPlayer(null);
    setMode('select');
  };

  return (
    <div data-domain="auth" className={styles.authPage}>
      <header className={styles.header}>
        <h1 className={styles.title}>마인크래프트 포인트 잔치</h1>
        {mode !== 'select' && (
          <p className={styles.subtitle}>
            {mode === 'pin' ? '로그인' : '관리자 로그인'}
          </p>
        )}
      </header>

      {mode === 'select' && (
        <PlayerSelectView
          onPlayerSelect={handlePlayerSelect}
          onAdminClick={() => setMode('admin')}
        />
      )}
      {mode === 'pin' && selectedPlayer && (
        <PinInputView
          player={selectedPlayer}
          onBack={handleBackToSelect}
        />
      )}
      {mode === 'admin' && (
        <AdminLoginView onBack={handleBackToSelect} />
      )}
    </div>
  );
}
```

**주의:**
- 기존 Auth/index.tsx의 로직을 PinInputView로 분리한 뒤, 엔트리는 모드 전환 허브로 변경
- 기존 hooks/useAuth.ts가 있다면 PinInputView에서 재사용
- 이미 로그인된 상태라면 `/dashboard` 또는 `/admin`으로 리다이렉트 (기존 동작 유지)

---

### P5-015: Auth.module.css 확장

`frontend/src/pages/Auth/Auth.module.css`에 Login Hub 스타일 추가.

추가할 클래스:
```
.cardGrid          — 캐릭터 카드 그리드 (gap: 12px)
.cardGridSingle    — 1명 레이아웃 (단일 열 중앙)
.cardGridThree     — 3명 레이아웃 (마지막 카드 중앙)
.playerCard        — 개별 카드 (배경, 라운딩, 패딩, hover)
.playerPhoto       — 사진 (원형, 64px)
.playerInitial     — 이니셜 폴백 (원형, 배경색, 텍스트)
.playerName        — 이름 텍스트
.playerPoints      — 포인트 텍스트 (muted)
.adminLink         — "관리자 로그인 →" 링크 영역
.adminForm         — 관리자 로그인 폼 컨테이너
.adminFormInput    — ID/PW 입력 필드
.adminFormButton   — 로그인 버튼
.backLink          — "← 뒤로가기" 링크
.pinHeader         — PIN 입력 화면 헤더 (사진 + 이름)
.errorMessage      — 로그인 실패 에러 메시지
```

**주의:**
- 기존 Auth.module.css의 클래스 삭제/변경 최소화
- 기존 PIN 관련 스타일이 있다면 유지 (PinInputView에서 재사용)
- 인라인 style={{}} 5개/파일 미만 준수

---

### P5-016: Step 2 빌드 검증

```bash
# 1) 빌드
cd frontend && npm run build

# 2) 타입체크
npx tsc --noEmit

# 3) 인라인 style 확인 (각 파일 4개 이하)
grep -c "style={{" frontend/src/pages/Auth/components/PlayerSelectView.tsx
grep -c "style={{" frontend/src/pages/Auth/components/PlayerCard.tsx
grep -c "style={{" frontend/src/pages/Auth/components/PinInputView.tsx
grep -c "style={{" frontend/src/pages/Auth/components/AdminLoginView.tsx
grep -c "style={{" frontend/src/pages/Auth/index.tsx

# 4) AbortController 확인
grep -rn "AbortController" frontend/src/pages/Auth/

# 5) 수평 구조 위반 없음
ls frontend/src/components/ 2>/dev/null
# → 존재하면 안 됨

# 6) Docker 재기동 + 접속 테스트
docker compose down
docker compose up -d
sleep 30
docker compose ps
# → 3 서비스 healthy

# 7) http://localhost:3000 접속
# → 캐릭터 카드 그리드 표시 확인
# → 카드 클릭 → PIN 입력 전환 확인
# → "관리자 로그인" → ID/PW 폼 전환 확인
```

---

## 전체 완료 조건

| # | 항목 | 기준 |
|---|---|---|
| 1 | py_compile 전체 PASS | backend 0 errors |
| 2 | npm build PASS | frontend 0 errors |
| 3 | tsc --noEmit PASS | 0 errors |
| 4 | admin_auth 테이블 정상 | Seed 2건, deleted_at NULL |
| 5 | POST /api/auth/admin/login 정상 | JWT 반환 (is_admin=true) |
| 6 | 기존 Player 로그인 회귀 없음 | POST /api/auth/login 정상 동작 |
| 7 | 기존 /api/admin/* 회귀 없음 | JWT is_admin claim 호환 |
| 8 | 3 서비스 healthy | docker compose ps |
| 9 | / 접근 시 캐릭터 카드 표시 | 사진 Base64 or 이니셜 폴백 |
| 10 | 카드 클릭 → PIN 전환 | 모드 전환 정상 |
| 11 | 관리자 로그인 → /admin | ID/PW → JWT → 리다이렉트 |
| 12 | 뒤로가기 링크 동작 | 모든 모드에서 select로 복귀 |
| 13 | 인라인 style 5개/파일 미만 | 전체 컴포넌트 |
| 14 | AbortController 적용 | PlayerSelectView useEffect |

---

## 보고 형식

```
제목: Phase 5 Login Hub + Admin 인증 분리
수행자: Claude Code
일시: [YYYY-MM-DD HH:MM]
Task ID: P5-001 ~ P5-016
상태: TODO → 완료

Step 1 (BE):
- admin_auth 테이블 생성 + Seed 2건
- AdminAuth 모델 (SoftDeleteMixin 적용)
- POST /api/auth/admin/login 구현
- py_compile: ✅
- DB 에러: 0건

Step 2 (FE):
- Auth 페이지 → Login Hub 리팩토링 (3모드 전환)
- 신규 컴포넌트: PlayerSelectView, PlayerCard, PinInputView, AdminLoginView
- authApi.ts + useAuthStore 확장
- npm build: ✅
- tsc --noEmit: ✅

검증 결과:
- docker compose ps: 3 서비스 healthy
- 기존 Player 로그인: 회귀 없음
- 기존 /api/admin/*: 회귀 없음
- 인라인 style: 각 파일 [N]개

총소요시간: XX분
생성/수정 파일: [경로 목록]
```
