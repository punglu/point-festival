# P-HOTFIX-CLEANUP-001 — 클린코드 스프린트

> **작성자:** Claude Web (Main Architect)
> **작성일:** 2026-04-01
> **목적:** Phase 7 (프로덕션 배포) 전 하드코딩 부채 해소 + CSS 캡슐화 완성
> **범위:** BE 3파일 수정 + FE 8파일 수정 + CSS 이관
> **선행 조건:** UI-OVERHAUL-001 완료 상태

---

## 🚨 실행 전 필독사항

### 아키텍처 원칙
1. **SSOT (Zero Hardcoding):** 서비스 데이터는 DB/env에서, 디자인 상수만 코드에
2. **Thin Controller:** router.py에 비즈니스 로직 금지
3. **CSS Modules 강제:** 인라인 스타일 → `.module.css` 이관
4. **SQL Annotation:** service.py 함수 상단 RAW SQL 주석 필수

### 변경하지 않을 것
- DB 스키마 변경 없음 (init.sql 수정 없음)
- 라우트 구조 변경 없음
- 기존 API 계약 변경 없음

---

## Task 1 — 인증 정책값 외부화 (B-4)

**파일:** `backend/app/domains/auth/service.py`

**현재 상태 (L18-19):**
```python
MAX_ATTEMPTS = 5
LOCK_DURATION_MS = 5 * 60 * 1000  # 5분
```

**수정:**

1. `backend/app/config.py`(또는 settings 객체)에 환경변수 기반 설정 추가:
```python
# config.py의 Settings 클래스에 추가
MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOCK_DURATION_SECONDS: int = int(os.getenv("LOCK_DURATION_SECONDS", "300"))
```

2. `auth/service.py`에서 settings 참조로 교체:
```python
# 기존 상수 2줄 삭제하고:
# from app.config import settings 는 이미 import 되어 있음

# 사용처 교체:
# MAX_ATTEMPTS → settings.MAX_LOGIN_ATTEMPTS
# LOCK_DURATION_MS → settings.LOCK_DURATION_SECONDS * 1000
```

3. `.env.example`에 추가:
```
MAX_LOGIN_ATTEMPTS=5
LOCK_DURATION_SECONDS=300
```

4. 기존 에러 메시지의 하드코딩된 "5회", "5분" 문구도 동적으로 변경:
```python
# L84 부근
detail=f"{settings.MAX_LOGIN_ATTEMPTS}회 실패하여 {settings.LOCK_DURATION_SECONDS // 60}분간 잠금되었습니다."

# L88 부근
detail=f"잘못된 PIN입니다. ({new_attempts}/{settings.MAX_LOGIN_ATTEMPTS})"
```

---

## Task 2 — CORS origins 외부화 (B-6)

**파일:** `backend/app/main.py` (L22-25)

**현재 상태:**
```python
allow_origins=["http://localhost:3000", "http://localhost:5173"],
```

**수정:**

1. `backend/app/config.py`의 Settings 클래스에 추가:
```python
CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
```

2. `main.py` 수정:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. `.env.example`에 추가:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Task 3 — 관리자 표시명 동적화 (B-1)

**파일:** `frontend/src/pages/AdminDashboard/components/FeedbackViewer.tsx` (L29)

**현재 상태:**
```tsx
await adminApi.createReply(feedbackId, { feedback_id: feedbackId, sender: '관리자', text });
```

**수정:**

1. `useAuthStore`에서 로그인한 관리자 이름을 가져오기:
```tsx
import { useAuthStore } from '../../../shared/stores/useAuthStore';

// 컴포넌트 내부 최상단:
const { player } = useAuthStore();
// player.name 또는 adminName이 JWT에서 디코딩된 display_name

// L29 수정:
const senderName = player?.name ?? '관리자';
await adminApi.createReply(feedbackId, { feedback_id: feedbackId, sender: senderName, text });
```

> **주의:** `useAuthStore`의 구조를 확인하여 관리자 로그인 시 `player.name`에 `display_name`이 들어가는지 확인할 것. 만약 별도 필드라면 그에 맞게 조정.

---

## Task 4 — 레벨 임계치 폴백 제거 (B-3)

**파일:** `frontend/src/pages/UserDashboard/hooks/useDashboard.ts`

**현재 상태 (L35 부근):**
```tsx
const [levelThresholds, setLevelThresholds] = useState<Record<string, number>>({
  '1': 0, '2': 50, '3': 150, '4': 300, '5': 500,
});
// ...
.catch(() => {}); // 실패 시 기본값 유지
```

**수정:**

1. 초기값을 빈 객체로 변경하고, 로딩/에러 상태 추가:
```tsx
const [levelThresholds, setLevelThresholds] = useState<Record<string, number> | null>(null);
const [configError, setConfigError] = useState(false);

// fetch 부분:
dashboardApi.getConfig('level.thresholds')
  .then(res => {
    if (res.data.value) setLevelThresholds(JSON.parse(res.data.value));
    else setConfigError(true);
  })
  .catch(() => setConfigError(true));
```

2. `levelThresholds`를 사용하는 곳(ProfileCard의 ExpBar 등)에서 null 체크:
   - `levelThresholds`가 null이면 레벨 표시 영역에 "-" 또는 로딩 스피너
   - `configError`가 true이면 "설정 로드 실패" 표시

3. **반환값에 configError 추가:**
```tsx
return {
  // ... 기존
  levelThresholds, configError,
  // ...
};
```

> **중요:** `PlayerSelectView.tsx`에도 동일한 `DEFAULT_THRESHOLDS` 폴백이 있습니다(L6). 이것도 같은 패턴으로 수정하되, Auth 화면에서는 레벨 로드 실패 시 배지를 숨기는 방식으로 처리하세요.

---

## Task 5 — 응원 발신자 모델 동적화 (B-2 + B-5)

> **이 Task는 가장 복잡합니다. 단계적으로 진행하세요.**

### 5-1. DB 기반 발신자 목록 설정 추가

**파일:** `database/init.sql` — Seed 추가 (기존 데이터 아래에):
```sql
-- 응원 발신자 설정 (관리자 화면에서 수정 가능)
INSERT INTO app_configs (key, value) VALUES
    ('cheer.senders', '[{"key":"dad","label":"아빠","color":"var(--blue)","emoji":"👨"},{"key":"mom","label":"엄마","color":"#db2777","emoji":"👩"}]')
ON CONFLICT (key) DO NOTHING;
```

### 5-2. FE: 발신자 목록을 API에서 로드

**파일:** `frontend/src/pages/AdminDashboard/components/CheerEditor.tsx`

```tsx
// 기존 하드코딩 제거:
// const SENDERS = [
//   { key: 'dad', label: '아빠 메시지' },
//   { key: 'mom', label: '엄마 메시지' },
// ] as const;

// API에서 로드:
interface SenderConfig {
  key: string;
  label: string;
  color: string;
  emoji: string;
}

const [senders, setSenders] = useState<SenderConfig[]>([]);

useEffect(() => {
  fetch('/api/configs/cheer.senders')
    .then(res => res.json())
    .then(data => {
      if (data?.value) setSenders(JSON.parse(data.value));
    })
    .catch(() => {
      // 폴백: 기존 하드코딩과 동일
      setSenders([
        { key: 'dad', label: '아빠', color: 'var(--blue)', emoji: '👨' },
        { key: 'mom', label: '엄마', color: '#db2777', emoji: '👩' },
      ]);
    });
}, []);

// messages 초기화도 동적으로:
useEffect(() => {
  const initial: Record<string, string> = {};
  senders.forEach(s => { initial[s.key] = ''; });
  setMessages(initial);
}, [senders]);

// SENDERS.map → senders.map 으로 렌더링 교체
```

### 5-3. FE: StoryCards 동적화

**파일:** `frontend/src/pages/UserDashboard/components/StoryCards.tsx`

```tsx
// 기존 하드코딩 인터페이스 제거:
// interface CheerData { dad?: string; mom?: string; }
// interface ParentPhotos { dad?: string; mom?: string; }

// 동적 인터페이스:
interface SenderConfig {
  key: string;
  label: string;
  color: string;
  emoji: string;
}

interface Props {
  cheers: Record<string, string>;      // { dad: "...", mom: "..." }
  parentPhotos: Record<string, string>; // { dad: "url", mom: "url" }
  senders: SenderConfig[];              // API에서 로드된 발신자 목록
}

const DEFAULT_CHEER = '오늘도 화이팅!';

export default function StoryCards({ cheers, parentPhotos, senders }: Props) {
  return (
    <div className={styles.cheerSection}>
      <div className={styles.cheerGrid}>
        {senders.map((sender) => (
          <div key={sender.key} className={styles.cheerItem}>
            <div className={styles.cheerPhotoRing} style={{ borderColor: sender.color }}>
              {parentPhotos[sender.key] ? (
                <img src={parentPhotos[sender.key]} alt={sender.label} className={styles.cheerPhoto} />
              ) : (
                <span className={styles.cheerInitial}>{sender.label}</span>
              )}
            </div>
            <div className={styles.cheerBubbleWrapper}>
              <span className={styles.cheerLabel} style={{ color: sender.color }}>{sender.label}</span>
              <div className={styles.cheerBubble}>
                {cheers[sender.key] || DEFAULT_CHEER}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 5-4. FE: CheerModal 동적화

**파일:** `frontend/src/pages/UserDashboard/components/CheerModal.tsx` (L13)

```tsx
// 기존:
// const emoji = sender === '아빠' || sender === 'dad' ? '👨' : '👩';

// sender 객체를 prop으로 받거나, emoji를 prop으로 전달:
// 가장 간단한 방식: emoji를 prop으로 추가
interface Props {
  sender: string;
  emoji: string;    // 추가
  message: string;
  isOpen: boolean;
  onClose: () => void;
}
// 사용: const emoji = props.emoji;
```

### 5-5. useDashboard에 senders 로드 추가

**파일:** `frontend/src/pages/UserDashboard/hooks/useDashboard.ts`

```tsx
// 기존 parentPhotos 로드 로직 옆에 추가:
const [senders, setSenders] = useState<SenderConfig[]>([]);

useEffect(() => {
  // 기존 레벨 + 사진 로드에 senders 추가
  dashboardApi.getConfig('cheer.senders')
    .then(res => {
      if (res.data.value) setSenders(JSON.parse(res.data.value));
    })
    .catch(() => {
      setSenders([
        { key: 'dad', label: '아빠', color: 'var(--blue)', emoji: '👨' },
        { key: 'mom', label: '엄마', color: '#db2777', emoji: '👩' },
      ]);
    });

  // parentPhotos도 senders 기반으로 동적 로드:
  // 기존 Promise.all([photos.dad, photos.mom]) 대신:
  // senders가 로드된 후 각 sender.key로 photos.{key} 조회
}, []);

// 반환값에 senders 추가
return {
  // ... 기존
  senders,
  // ...
};
```

### 5-6. UserDashboard/index.tsx에서 senders를 StoryCards에 전달

```tsx
// StoryCards에 senders prop 추가:
<StoryCards cheers={cheerData} parentPhotos={parentPhotos} senders={senders} />
```

---

## Task 6 — AdminDashboard 인라인 스타일 → CSS Module 이관 (C)

**대상 파일 3개 (각 5건):**
- `frontend/src/pages/AdminDashboard/components/MissionCloneModal.tsx`
- `frontend/src/pages/AdminDashboard/components/MissionManager.tsx`
- `frontend/src/pages/AdminDashboard/components/PointManager.tsx`

**추가 대상 (인라인 4건):**
- `frontend/src/pages/AdminDashboard/components/FeedbackViewer.tsx`
- `frontend/src/pages/AdminDashboard/components/CheerEditor.tsx` (2건)

**작업:**

1. 각 파일의 `style={{ ... }}` 패턴을 모두 찾기
2. `AdminDashboard.module.css`에 해당 스타일을 클래스로 추가
3. JSX에서 `style={...}` → `className={styles.newClassName}`으로 교체

**네이밍 규칙:** 파일명 + 용도 (예: `feedbackReplyRow`, `cheerDateLabel`, `missionCloneField`)

**예시 (FeedbackViewer.tsx):**
```tsx
// Before:
<div style={{ paddingLeft: 16, fontSize: 13, color: '#4a5568', marginBottom: 4 }}>

// After (CSS):
.feedbackReply { padding-left: 16px; font-size: 13px; color: #4a5568; margin-bottom: 4px; }

// After (JSX):
<div className={styles.feedbackReply}>
```

> **주의:** `style={{ flex: 1 }}`처럼 동적 레이아웃 값도 CSS 클래스로 이관 가능합니다. `.flexOne { flex: 1; }` 또는 더 의미있는 이름 사용.

---

## Task 7 — global.css data-domain 주석 정리 (D)

**파일:** `frontend/src/styles/global.css`

**현재 상태:** L1에 `/* global.css — Gemini E-3: data-domain 테마 격리 */` 주석이 있지만, 실제 `[data-domain]` 선택자가 없음.

**수정:**

1. 현재 실제 data-domain 사용 현황 확인:
```bash
grep -rn "data-domain" frontend/src/ --include="*.tsx" --include="*.css"
```

2. **만약 어디에서도 사용하지 않는다면:** 주석을 실제 상태에 맞게 수정
```css
/* global.css — 전역 CSS 변수 및 리셋 */
/* 참고: data-domain 기반 테마 격리는 Phase 5에서 home 전용 다크 테마로 대체됨 */
```

3. **만약 일부에서 사용한다면:** 주석과 구현을 일치시키기

---

## Task 8 — 빌드 검증 및 보고

```bash
# BE 검증
cd backend && python -m py_compile app/main.py && python -m py_compile app/domains/auth/service.py && python -m py_compile app/config.py && echo "✅ BE OK"

# FE 검증
cd frontend && npx tsc --noEmit && npm run build && echo "✅ FE OK"
```

**0 errors 필수.**

---

## 완료 보고 형식

```
제목: P-HOTFIX-CLEANUP-001 — 클린코드 스프린트
수행자: Claude Code
Task ID: P-HOTFIX-CLEANUP-001
상태: 진행중 → 완료

Task별 결과:
- Task 1 (인증 정책 외부화): [결과]
- Task 2 (CORS 외부화): [결과]
- Task 3 (관리자 표시명): [결과]
- Task 4 (레벨 폴백 제거): [결과]
- Task 5 (응원 발신자 동적화): [결과]
- Task 6 (인라인 스타일 이관): [결과]
- Task 7 (global.css 주석 정리): [결과]
- Task 8 (빌드 검증): [결과]

수정/생성 파일:
- [목록]

빌드: tsc ✓ | npm run build ✓ | py_compile ✓
```
