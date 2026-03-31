# [Claude Code 실행 프롬프트] P-HOTFIX-AUTH-FLOW-002: Auth 분기 구조 정리

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P-HOTFIX-AUTH-FLOW-002
> **근거:** Codex QA 발견 — Auth 분기 구조 이슈 3건
> **우선순위:** Phase 6 전에 즉시 실행
> **목표:** 로그인 흐름 정상화 + 레거시 코드 정리 + 빌드 0 errors

---

## 🚨 실행 전 필독

### Codex QA 발견 사항 3건

| # | 심각도 | 이슈 | 파일 |
|---|---|---|---|
| **1** | **중간** | 전역 401 리다이렉트가 로그인 실패 에러도 삼킴 | `httpClient.ts` |
| **2** | **낮음** | PlayerSelectView → PinInputView로 넘길 때 `photo` 유실 | `PlayerSelectView.tsx` |
| **3** | **낮음** | 구 Auth 컴포넌트(LoginOverlay, PlayerSelector, useAuth) 잔존 | `Auth/components/` |

### 수정 원칙
- **분기 책임 분리**: 로그인 실패 = 분기 내부 에러 / 토큰 만료 = 전역 세션 에러
- **데이터 무손실**: 앞 단계에서 다음 단계에 필요한 데이터를 잘라내지 않음
- **단일 분기 구조**: 현재 사용 중인 Login Hub 구조만 남기고 구 코드 제거
- **기존 UI/동작 보존**: 화면 레이아웃, 스타일, 기능 동작은 변경 없음

---

## FIX-001: 전역 401 리다이렉트에서 로그인 API 제외

### 문제
`frontend/src/shared/api/httpClient.ts`의 응답 인터셉터가 **모든** 401 응답에 대해 세션을 정리하고 `window.location.href = '/'`로 리다이렉트합니다. 이 때문에 PIN 오류나 관리자 비밀번호 오류 시 에러 메시지를 표시하지 못하고 페이지가 리셋됩니다.

### 수정 방법

`httpClient.ts`의 응답 인터셉터에서 **로그인 API 엔드포인트의 401은 전역 처리하지 않고 호출자에게 에러를 그대로 전달**하도록 수정합니다.

현재 코드 (수정 대상 부분):
```typescript
httpClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      sessionStorage.removeItem('accessToken');
      localStorage.removeItem('loggedInPlayer');
      window.location.href = '/';
    }
    return Promise.reject(err);
  },
);
```

수정 후:
```typescript
/** 로그인 API 경로 — 이 경로의 401은 전역 리다이렉트하지 않음 */
const AUTH_ENDPOINTS = ['/api/auth/login', '/api/auth/admin-login'];

httpClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const requestUrl = err.config?.url || '';

      // 로그인 API의 401은 "PIN/비밀번호 오류" → 호출자에게 에러 전달
      const isLoginRequest = AUTH_ENDPOINTS.some(ep => requestUrl.includes(ep));

      if (!isLoginRequest) {
        // 보호 API의 401은 "토큰 만료/무효" → 전역 세션 정리
        sessionStorage.removeItem('accessToken');
        localStorage.removeItem('loggedInPlayer');
        localStorage.removeItem('rememberMe');
        window.location.href = '/';
      }
    }
    return Promise.reject(err);
  },
);
```

### 검증
```bash
# 수정 후 확인
grep -n "AUTH_ENDPOINTS" frontend/src/shared/api/httpClient.ts
# → AUTH_ENDPOINTS 선언 + isLoginRequest 분기 존재 확인

grep -n "window.location.href" frontend/src/shared/api/httpClient.ts
# → 1곳만 존재 (전역 세션 정리 분기 내부)
```

---

## FIX-002: PlayerSelectView → PinInputView 데이터 전달 시 photo 포함

### 문제
`PlayerSelectView.tsx`에서 플레이어 목록을 매핑할 때 `photo` 필드를 빠뜨려서, `PinInputView.tsx`가 `player.photo`를 참조하면 `undefined`가 됩니다.

### 수정 방법

`frontend/src/pages/Auth/components/PlayerSelectView.tsx`를 열고, 플레이어 매핑 부분에서 `photo` 필드를 포함하세요.

**찾기:** players를 map/매핑하는 부분 (약 29행 부근)

현재 (예상):
```typescript
const mapped = data.map((p: any) => ({
  id: p.id,
  name: p.name,
  isLocked: p.is_locked ?? false,
  totalPoints: p.total_points ?? 0,
  color: getAvatarColor(p.name),
}));
```

수정 후:
```typescript
const mapped = data.map((p: any) => ({
  id: p.id,
  name: p.name,
  photo: p.photo ?? null,              // ← 추가
  isLocked: p.is_locked ?? false,
  totalPoints: p.total_points ?? 0,
  color: getAvatarColor(p.name),
}));
```

> **주의:** 정확한 매핑 위치는 실제 코드에서 확인하세요. `players` 상태를 설정하는 곳이 여러 곳일 수 있습니다 (useAuth 훅 내부, authApi 호출 결과 매핑 등). `photo`가 최종 player 객체에 포함되어 PinInputView까지 전달되도록 **모든 매핑 경로**를 점검하세요.

### 또한 확인할 것

PinInputView에서 `player.photo`를 사용하는 부분이 `photo`가 `null`일 때도 안전하게 동작하는지 확인:

```typescript
// photo가 있으면 이미지, 없으면 이니셜 아바타 fallback
{player.photo ? (
  <img src={player.photo} alt={player.name} className={styles.loginAvatarImg} />
) : (
  <div className={styles.loginAvatar} style={{ backgroundColor: player.color }}>
    {player.name.charAt(0)}
  </div>
)}
```

### 타입 정의 확인

Player 인터페이스(또는 타입)에 `photo` 필드가 정의되어 있는지 확인하고, 없으면 추가:

```typescript
interface Player {
  id: number;
  name: string;
  photo: string | null;    // ← 있는지 확인, 없으면 추가
  isLocked: boolean;
  totalPoints: number;
  color: string;
  lastLogin?: string | null;
}
```

---

## FIX-003: 사용되지 않는 구 Auth 컴포넌트 제거

### 문제
이전 Phase 1의 Auth 흐름(LoginOverlay, PlayerSelector, useAuth)이 삭제되지 않고 남아있어, 현재 Login Hub 구조(`PlayerSelectView`, `PinInputView`, `AdminLoginView` 기반)와 혼재합니다.

### 수정 방법

**Step 1:** 먼저 실제로 사용되지 않는 파일인지 import 참조를 확인합니다.

```bash
# 구 컴포넌트가 현재 코드에서 import되고 있는지 확인
echo "=== LoginOverlay 참조 확인 ==="
grep -rn "LoginOverlay" frontend/src/ --include="*.tsx" --include="*.ts" | grep -v "node_modules"

echo ""
echo "=== PlayerSelector 참조 확인 (구 버전) ==="
grep -rn "PlayerSelector" frontend/src/ --include="*.tsx" --include="*.ts" | grep -v "node_modules"

echo ""
echo "=== useAuth 참조 확인 (구 훅) ==="
grep -rn "useAuth" frontend/src/ --include="*.tsx" --include="*.ts" | grep -v "node_modules"
```

**Step 2:** 참조가 0건인 파일만 삭제합니다.

```bash
# 예상 삭제 대상 (참조 0건 확인 후에만 삭제!)
# frontend/src/pages/Auth/components/LoginOverlay.tsx
# frontend/src/pages/Auth/components/PlayerSelector.tsx
# frontend/src/pages/Auth/hooks/useAuth.ts
```

> **⚠️ 중요:** `grep` 결과에서 import하는 곳이 1곳이라도 있으면 **절대 삭제하지 마세요.** 그 경우 어떤 파일이 참조하는지를 보고에 기록만 하세요.

**Step 3:** 삭제 후 빌드 검증

```bash
cd frontend
npm run build
# 0 errors 확인
```

만약 삭제 후 빌드 에러가 발생하면:
- 에러 메시지에서 참조하는 파일/줄번호 확인
- 삭제한 파일을 git에서 복원 (`git checkout -- 파일경로`)
- 해당 import를 현재 구조의 올바른 컴포넌트로 교체

---

## 추가 확인: Auth CSS 클래스 정합성

Codex가 지적한 `styles.title` 참조 문제도 확인합니다.

```bash
# Auth/index.tsx에서 사용하는 CSS 클래스가 Auth.module.css에 모두 존재하는지
grep -oP 'styles\.\w+' frontend/src/pages/Auth/index.tsx | sort -u | while read cls; do
  name=$(echo "$cls" | sed 's/styles\.//')
  if ! grep -q "\.$name" frontend/src/pages/Auth/Auth.module.css 2>/dev/null; then
    echo "⚠️ CSS 클래스 미정의: $cls"
  fi
done
```

미정의 클래스가 있으면 `Auth.module.css`에 추가하거나, 올바른 클래스명으로 수정하세요.

---

## 빌드 검증

```bash
cd frontend

# TypeScript 타입 체크
npx tsc --noEmit
echo "tsc 결과: $?"

# 빌드
npm run build
echo "build 결과: $?"

# 구 파일 잔존 확인
echo ""
echo "=== 구 Auth 파일 잔존 확인 ==="
for f in LoginOverlay.tsx PlayerSelector.tsx; do
  [ -f "src/pages/Auth/components/$f" ] && echo "⚠️ 잔존: $f" || echo "✅ 정리됨: $f"
done
[ -f "src/pages/Auth/hooks/useAuth.ts" ] && echo "⚠️ 잔존: useAuth.ts" || echo "✅ 정리됨: useAuth.ts"

# 전역 401 분기 확인
echo ""
echo "=== httpClient 401 분기 확인 ==="
grep -c "AUTH_ENDPOINTS" src/shared/api/httpClient.ts && echo "✅ 로그인 API 예외 분기 존재" || echo "⚠️ 예외 분기 없음"
```

---

## 완료 보고

```
제목: P-HOTFIX-AUTH-FLOW-002 — Auth 분기 구조 정리
수행자: Claude Code
일시: [실행 시점]
Task ID: P-HOTFIX-AUTH-FLOW-002
상태: TODO → 완료

총소요시간: XX분
수정 파일:
  - frontend/src/shared/api/httpClient.ts (전역 401 → 로그인 API 예외 분기 추가)
  - frontend/src/pages/Auth/components/PlayerSelectView.tsx (photo 필드 추가)
  - (삭제) frontend/src/pages/Auth/components/LoginOverlay.tsx (참조 0건 확인 후)
  - (삭제) frontend/src/pages/Auth/components/PlayerSelector.tsx (참조 0건 확인 후)
  - (삭제) frontend/src/pages/Auth/hooks/useAuth.ts (참조 0건 확인 후)
  - (필요시) frontend/src/pages/Auth/Auth.module.css (미정의 CSS 클래스 보정)

검증 결과:
  - [ ] npm run build 0 errors
  - [ ] httpClient: AUTH_ENDPOINTS 예외 분기 존재
  - [ ] PlayerSelectView: photo 필드 매핑 포함
  - [ ] PinInputView: photo null 시 fallback 정상
  - [ ] 구 Auth 파일 삭제 또는 잔존 사유 기록
  - [ ] CSS 클래스 정합성 확인

다음 단계: PM 검수 → Phase 6 실행
```
