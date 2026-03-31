# 🔧 Phase 5 핫픽스 — Claude Code 실행 지시서

> **수행자:** Claude Code
> **컨텍스트:** Phase 5 (Login Hub + Admin 인증 분리) Codex QA FAIL 4건 해결
> **Git 환경:** 활성화됨 (기준 브랜치: `origin/dev`)
> **날짜:** 2026-03-31

---

## 🎯 목표

Codex QA에서 발견된 **4개 블로커(FAIL)**를 해결하고, 설계 범위를 벗어난 코드를 롤백하며, 관리자/플레이어 인증 체계를 완전히 격리한다.

### FAIL 목록

| ID | 내용 | 원인 |
|----|------|------|
| **E-3** | admin router 변경 없음 기준 위반 | Phase 5 범위 초과 수정 |
| **E-5** | Admin JWT와 기존 `/api/admin/*` 검증 비호환 | sub에 username 할당 + int() 강제 변환 충돌 |
| **M-2** | AdminDashboard 변경 없음 기준 위반 | Phase 5 범위 초과 수정 |
| **M-7** | auth 외 BE 도메인 변경 없음 기준 위반 | mission 도메인 범위 초과 수정 |

### 추가 보완

| 항목 | 내용 |
|------|------|
| AbortController | PlayerSelectView.tsx에서 signal 미전달 |

---

## ⚠️ 사전 확인 (Task 시작 전 필수)

아래 명령으로 **실제 파일 경로를 확인**한 후 작업을 시작하세요.

```bash
# 1. dependencies.py 실제 위치 확인
find backend/ -name "dependencies.py" -path "*/auth/*"
# 예상: backend/app/domains/auth/dependencies.py
# 만약 backend/app/dependencies.py 에 있다면 해당 경로 사용

# 2. 롤백 대상 파일들의 현재 diff 확인
git diff origin/dev -- backend/app/domains/admin/router.py
git diff origin/dev -- backend/app/domains/mission/
git diff origin/dev -- frontend/src/pages/AdminDashboard/

# 3. admin/router.py에서 현재 사용중인 dependency import 확인
head -20 backend/app/domains/admin/router.py
```

**위 확인 결과를 기반으로 아래 Task를 순서대로 진행하세요.**

---

## 🛠️ Task 실행 순서

> **핵심: Task 2 → Task 1 → Task 3 → Task 4 순서를 반드시 준수하세요.**
>
> 이유: Task 1(롤백)을 먼저 하면 `admin/router.py`가 `origin/dev` 상태로 돌아가는데,
> Task 2에서 만든 `get_current_admin` dependency를 이 파일이 import하지 않는 상태가 됩니다.
> 따라서 **JWT 수정(Task 2)을 먼저 완료한 뒤, 롤백(Task 1) 후 의존성을 연결(Task 1-B)**합니다.

---

### Task 2: JWT 'Role' 기반 인증 격리 (E-5 해결) — 먼저 수행

관리자와 플레이어의 토큰이 충돌하지 않도록 Payload 구조와 검증 로직을 분리한다.

#### 2-A. JWT 생성 수정 (`backend/app/domains/auth/service.py`)

`authenticate_admin` 함수에서 토큰 생성 시 `role` 클레임을 추가하세요.

```python
# Admin 토큰 생성
payload = {
    "sub": str(admin.id),   # ← username이 아닌 admin.id (int → str)
    "role": "admin",         # ← 신규 클레임
    # 기존 클레임 유지 (exp, iat 등)
}
```

플레이어 로그인 함수에도 동일하게 `role` 클레임을 추가하세요.

```python
# Player 토큰 생성
payload = {
    "sub": str(player.id),
    "role": "player",        # ← 신규 클레임
    # 기존 클레임 유지
}
```

#### 2-B. 검증 로직 분리 (`backend/app/domains/auth/dependencies.py`)

> **경로 주의:** 사전 확인에서 찾은 실제 경로를 사용하세요.

**기존 `get_current_user` 수정:**

```python
async def get_current_user(...):
    payload = decode_token(token)
    role = payload.get("role")
    if role != "player":
        raise HTTPException(status_code=401, detail="Player token required")
    user_id = int(payload["sub"])
    # 기존 players 테이블 조회 로직 유지
    ...
```

**신규 `get_current_admin` 함수 추가:**

```python
async def get_current_admin(...):
    payload = decode_token(token)
    role = payload.get("role")
    if role != "admin":
        raise HTTPException(status_code=401, detail="Admin token required")
    admin_id = int(payload["sub"])
    # admin_auth 테이블에서 id로 조회
    admin = await db.get(AdminAuth, admin_id)
    if not admin or admin.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Admin not found")
    return admin
```

> **참고:** `AdminAuth` 모델을 import해야 합니다.
> `from backend.app.domains.auth.models import AdminAuth` (실제 import 경로는 프로젝트 구조에 맞게 조정)

---

### Task 1: 범위 초과 코드 롤백 (E-3, M-2, M-7 해결) — Task 2 완료 후 수행

#### 1-A. `origin/dev` 기준 롤백

```bash
# BE: admin router 롤백
git checkout origin/dev -- backend/app/domains/admin/router.py

# BE: mission 도메인 전체 롤백
git checkout origin/dev -- backend/app/domains/mission/

# FE: AdminDashboard 전체 롤백
git checkout origin/dev -- frontend/src/pages/AdminDashboard/
```

#### 1-B. 롤백 후 의존성 연결 (핵심!)

`admin/router.py`가 `origin/dev` 상태로 돌아갔으므로, 기존에 `get_current_user`를 사용하던 admin 보호 라우트를 **`get_current_admin`으로 교체**해야 합니다.

```bash
# 롤백된 admin/router.py에서 현재 dependency import 확인
grep -n "get_current_user\|Depends" backend/app/domains/admin/router.py
```

확인 결과를 기반으로:

1. import 문에 `get_current_admin`을 추가하세요.
2. admin 보호 라우트의 `Depends(get_current_user)` → `Depends(get_current_admin)`으로 교체하세요.

```python
# 변경 전 (예시)
from app.domains.auth.dependencies import get_current_user

@router.get("/api/admin/dashboard")
async def get_dashboard(user = Depends(get_current_user)):
    ...

# 변경 후
from app.domains.auth.dependencies import get_current_admin

@router.get("/api/admin/dashboard")
async def get_dashboard(admin = Depends(get_current_admin)):
    ...
```

> **주의:** `admin/router.py`에서 `get_current_user`를 사용하는 **모든 라우트**를 `get_current_admin`으로 교체하세요.
> 이 파일 외에 다른 변경은 하지 마세요. Phase 5 범위를 다시 벗어나지 않도록 주의!

---

### Task 3: FE AbortController 시그널 전달 (보완)

#### 3-A. API 함수 수정 (`frontend/src/pages/Auth/api/authApi.ts`)

`getPlayers` 함수에 `signal` 파라미터를 추가하세요.

```typescript
// 변경 전
export const getPlayers = async () => {
  const response = await apiClient.get('/api/players');
  return response.data;
};

// 변경 후
export const getPlayers = async (signal?: AbortSignal) => {
  const response = await apiClient.get('/api/players', { signal });
  return response.data;
};
```

#### 3-B. 컴포넌트 수정 (`frontend/src/pages/Auth/components/PlayerSelectView.tsx`)

`useEffect` 내에서 signal을 전달하세요.

```typescript
// 변경 전
useEffect(() => {
  const controller = new AbortController();
  authApi.getPlayers().then(/* ... */);
  return () => controller.abort();
}, []);

// 변경 후
useEffect(() => {
  const controller = new AbortController();
  authApi.getPlayers(controller.signal).then(/* ... */);
  return () => controller.abort();
}, []);
```

---

### Task 4: 빌드 및 자체 검증 (Definition of Done)

모든 작업 완료 후 아래 명령을 **순서대로** 실행하여 무결성을 증명하세요.

#### 4-A. 빌드 검증

```bash
# Backend 구문 검증
PYTHONPYCACHEPREFIX=/tmp/python-pyc python3 -m py_compile backend/app/domains/auth/service.py
PYTHONPYCACHEPREFIX=/tmp/python-pyc python3 -m py_compile backend/app/domains/auth/dependencies.py
PYTHONPYCACHEPREFIX=/tmp/python-pyc python3 -m py_compile backend/app/domains/admin/router.py

# Frontend 빌드 + 타입 체크
cd frontend && npm run build && npx tsc --noEmit
```

#### 4-B. 롤백 확인

```bash
# 범위 초과 파일이 origin/dev와 동일한지 확인 (admin/router.py의 dependency 변경만 diff 있어야 함)
git diff origin/dev -- backend/app/domains/mission/
# 예상 출력: (없음 — 완전 복원)

git diff origin/dev -- frontend/src/pages/AdminDashboard/
# 예상 출력: (없음 — 완전 복원)

git diff origin/dev -- backend/app/domains/admin/router.py
# 예상 출력: get_current_user → get_current_admin 변경 diff만 존재
```

#### 4-C. 동작 검증

```bash
# Docker 환경 재시작
docker compose down -v && docker compose up -d

# DB 초기화 확인 (admin_auth 테이블 존재)
docker compose exec db psql -U postgres -d outlook_hub -c "\dt admin_auth"

# Admin 로그인 테스트
curl -X POST http://localhost:8000/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin1234"}'
# 예상: JWT 토큰 반환, payload에 "role": "admin" 포함

# Admin 보호 API 테스트 (위에서 받은 토큰 사용)
curl -H "Authorization: Bearer <ADMIN_TOKEN>" \
  http://localhost:8000/api/admin/dashboard
# 예상: 200 OK (401 아님)

# Player 로그인 테스트 (기존 흐름 회귀)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1, "pin": "1234"}'
# 예상: JWT 토큰 반환, payload에 "role": "player" 포함
```

---

## 📋 수정 대상 파일 요약

| 파일 | 작업 | Task |
|------|------|------|
| `backend/app/domains/auth/service.py` | JWT payload에 role 클레임 추가 | Task 2-A |
| `backend/app/domains/auth/dependencies.py` | get_current_user 수정 + get_current_admin 신규 | Task 2-B |
| `backend/app/domains/admin/router.py` | origin/dev 롤백 → get_current_admin 연결 | Task 1-A, 1-B |
| `backend/app/domains/mission/` | origin/dev 롤백 (변경 없음) | Task 1-A |
| `frontend/src/pages/AdminDashboard/` | origin/dev 롤백 (변경 없음) | Task 1-A |
| `frontend/src/pages/Auth/api/authApi.ts` | getPlayers에 signal 파라미터 추가 | Task 3-A |
| `frontend/src/pages/Auth/components/PlayerSelectView.tsx` | signal 전달 | Task 3-B |

---

## 🚫 금지 사항

- 위 목록 외의 파일은 **절대 수정하지 마세요.**
- `frontend/src/pages/Auth/` 하위 Phase 5 신규 파일은 건드리지 마세요.
- `database/init.sql`은 수정하지 마세요 (QA에서 DB 항목 7/7 PASS).
- mission, AdminDashboard 롤백 파일에 추가 수정을 가하지 마세요.

---

## 📝 완료 보고 형식

```
## Phase 5 핫픽스 완료 보고

### 수정 파일
| 파일 | 변경 내용 |
|------|----------|
| (파일경로) | (변경 요약) |

### 검증 결과
- [ ] py_compile: PASS / FAIL
- [ ] npm run build: PASS / FAIL
- [ ] tsc --noEmit: PASS / FAIL
- [ ] git diff mission/: (없음)
- [ ] git diff AdminDashboard/: (없음)
- [ ] Admin 로그인 → 보호 API: PASS / FAIL
- [ ] Player 로그인 → Dashboard: PASS / FAIL

### 특이사항
(있으면 기재)
```

---

**지시 사항 끝. Task 2 → Task 1 → Task 3 → Task 4 순서를 준수하여 즉시 작업을 시작하세요.**
