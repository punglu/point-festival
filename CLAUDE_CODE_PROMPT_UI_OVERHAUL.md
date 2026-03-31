# [Claude Code 실행 프롬프트] P-HOTFIX-UI-OVERHAUL-001: 목업 기반 UI 통합 개선

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P-HOTFIX-UI-OVERHAUL-001
> **근거:** PM 시각 검수 + 확정 목업 4종
> **목표:** 로그인/대시보드/관리자 전체 화이트 테마 통일 + Auth 카드형 개선 + PIN 오류 토스트 + 응원 섹션 개선

---

## 🚨 실행 전 필독

### 이 프롬프트는 4개 영역을 한 번에 수정합니다:
1. **Auth 플레이어 선택** — 단순 버튼 → 아바타+레벨 카드형 + 선물상자 아이콘
2. **Auth PIN 오류 처리** — 무응답 → 토스트 스낵바 + 플레이어 선택 복귀
3. **User Dashboard 응원 섹션** — 이모지 → 부모 사진(원형) + 말풍선 2열 가운데 배치
4. **화이트 테마 통일** — 다크 테마 잔재 제거, 전체 `--bg: #f8fafc` / `--card: #fff` 기준

### 아키텍처 철칙 (위반 시 QA Fail)
- **CSS Modules 강제**: Auth.module.css, UserDashboard.module.css만 수정
- **1 Page = 1 Directory**: 신규 컴포넌트는 해당 pages/ 하위에만 생성
- **Shared 승격 규칙**: Toast 컴포넌트는 2개+ 페이지에서 사용 가능성 있으므로 `src/shared/components/Toast/`에 생성

### 수정 전 반드시 확인
```bash
# 현재 Auth 컴포넌트 구조 확인
ls frontend/src/pages/Auth/components/
# 예상: PlayerSelectView.tsx, PinInputView.tsx, PlayerCard.tsx, AdminLoginView.tsx, PinInput.tsx

# 현재 UserDashboard 컴포넌트 구조 확인
ls frontend/src/pages/UserDashboard/components/

# global.css 테마 변수 확인
head -30 frontend/src/styles/global.css
```

---

## Task 1: 공통 Toast 컴포넌트 생성

### frontend/src/shared/components/Toast/Toast.tsx

```tsx
import { useEffect, useState } from 'react';
import styles from './Toast.module.css';

interface ToastProps {
  message: string;
  type?: 'error' | 'success' | 'info';
  duration?: number;
  onClose: () => void;
}

export default function Toast({ message, type = 'error', duration = 3000, onClose }: ToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, 300); // fade-out 후 제거
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className={`${styles.toast} ${styles[type]} ${visible ? styles.show : styles.hide}`}>
      <span className={styles.icon}>
        {type === 'error' ? '✕' : type === 'success' ? '✓' : 'ℹ'}
      </span>
      <span className={styles.message}>{message}</span>
    </div>
  );
}
```

### frontend/src/shared/components/Toast/Toast.module.css

```css
.toast {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  transition: opacity 0.3s, transform 0.3s;
  max-width: 90%;
}

.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.hide {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

.error {
  background: #501313;
  color: #f7c1c1;
}

.success {
  background: #04342c;
  color: #9fe1cb;
}

.info {
  background: #042c53;
  color: #b5d4f4;
}

.icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.message {
  flex: 1;
}
```

### frontend/src/shared/components/Toast/index.ts

```ts
export { default as Toast } from './Toast';
```

---

## Task 2: Auth 플레이어 선택 카드형 개선

### 선물상자 SVG 아이콘 — PlayerSelectView.tsx에 인라인 삽입

현재 `frontend/src/pages/Auth/components/PlayerSelectView.tsx`를 수정합니다.

**변경 사항:**
1. 상단에 선물상자 SVG 아이콘 + "포인트 잔치" 타이틀 + "플레이어를 선택하세요" 서브타이틀 추가
2. PlayerCard에 레벨 배지 표시 (포인트 대신 레벨)
3. 하단에 "관리자 로그인" 텍스트 링크 유지

```tsx
// PlayerSelectView.tsx 전체 교체
import { useEffect, useState } from 'react';
import styles from '../Auth.module.css';
import PlayerCard from './PlayerCard';
import { authApi } from '../api/authApi';

// 레벨 임계치 (app_configs에서 로드 실패 시 fallback)
const DEFAULT_THRESHOLDS: Record<number, number> = { 1: 0, 2: 50, 3: 150, 4: 300, 5: 500 };

function calcLevel(totalPoints: number, thresholds: Record<number, number>): number {
  let level = 1;
  for (const [lv, threshold] of Object.entries(thresholds).sort((a, b) => Number(b[0]) - Number(a[0]))) {
    if (totalPoints >= threshold) { level = Number(lv); break; }
  }
  return level;
}

interface Player {
  id: number;
  name: string;
  photo: string | null;
  total_points: number;
  is_locked: boolean;
  role: string;
}

interface Props {
  onSelectPlayer: (player: { id: number; name: string; photo: string | null }) => void;
  onAdminClick: () => void;
}

export default function PlayerSelectView({ onSelectPlayer, onAdminClick }: Props) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [thresholds, setThresholds] = useState<Record<number, number>>(DEFAULT_THRESHOLDS);

  useEffect(() => {
    authApi.getPlayers()
      .then((list) => setPlayers(list.filter((p: Player) => p.role === 'player')))
      .catch(() => setPlayers([]));

    // 레벨 임계치 로드 시도
    fetch('/api/configs/level.thresholds')
      .then(res => res.json())
      .then(data => {
        if (data?.value) setThresholds(JSON.parse(data.value));
      })
      .catch(() => {}); // fallback 사용
  }, []);

  return (
    <div className={styles.selectViewWrapper}>
      {/* 선물상자 아이콘 */}
      <div className={styles.giftIcon}>
        <svg width="48" height="48" viewBox="0 0 64 64" fill="none">
          <rect x="10" y="26" width="44" height="28" rx="4" fill="#10b981"/>
          <rect x="10" y="26" width="44" height="8" rx="3" fill="#6ee7b7"/>
          <rect x="29" y="26" width="6" height="28" fill="#ef4444"/>
          <rect x="29" y="26" width="6" height="8" fill="#fca5a5"/>
          <path d="M32 26c-4-8-14-8-14-2s10 2 14 2z" fill="#ef4444"/>
          <path d="M32 26c4-8 14-8 14-2s-10 2-14 2z" fill="#fca5a5"/>
          <rect x="29" y="34" width="6" height="20" rx="1" fill="#dc2626"/>
        </svg>
      </div>

      <h1 className={styles.authTitle}>포인트 잔치</h1>
      <p className={styles.authSubtitle}>플레이어를 선택하세요</p>

      <div className={styles.cardGrid} data-count={players.length}>
        {players.map((p) => (
          <PlayerCard
            key={p.id}
            name={p.name}
            photo={p.photo}
            level={calcLevel(p.total_points, thresholds)}
            isLocked={p.is_locked}
            onClick={() => onSelectPlayer({ id: p.id, name: p.name, photo: p.photo })}
          />
        ))}
      </div>

      <button className={styles.adminLinkBtn} onClick={onAdminClick}>
        관리자 로그인
      </button>
    </div>
  );
}
```

### PlayerCard.tsx 수정 — 레벨 배지 표시

```tsx
// PlayerCard.tsx 전체 교체
import styles from '../Auth.module.css';

interface Props {
  name: string;
  photo: string | null;
  level: number;
  isLocked: boolean;
  onClick: () => void;
}

export default function PlayerCard({ name, photo, level, isLocked, onClick }: Props) {
  return (
    <button className={styles.playerCard} onClick={onClick} disabled={isLocked}>
      <div className={styles.playerAvatar}>
        {photo ? (
          <img src={photo} alt={name} className={styles.playerPhoto} />
        ) : (
          <span className={styles.playerInitial}>{name.charAt(0)}</span>
        )}
      </div>
      <span className={styles.playerName}>{name}</span>
      <span className={styles.levelBadge}>Lv.{level}</span>
      {isLocked && <span className={styles.lockIcon}>🔒</span>}
    </button>
  );
}
```

---

## Task 3: PIN 오류 시 토스트 + 플레이어 선택 복귀

### Auth/index.tsx 수정

현재 `frontend/src/pages/Auth/index.tsx`의 PIN 제출 실패 핸들러를 수정합니다.

**변경 사항:**
- PIN 오류(401) 시 → Toast 표시("비밀번호가 틀렸습니다") + mode를 'select'로 전환
- 5회 실패 잠금 시 → Toast 표시("5분 후 다시 시도해주세요") + mode를 'select'로 전환

```tsx
// index.tsx에 추가할 상태 및 import
import { useState } from 'react';
import { Toast } from '../../shared/components/Toast';

// 기존 state에 추가:
const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' } | null>(null);

// PIN 제출 핸들러 수정 (기존 handlePinSubmit 또는 해당 함수):
const handlePinSubmit = async (pin: string, rememberMe: boolean) => {
  try {
    const result = await authApi.login({
      player_id: selectedPlayer!.id,
      pin,
      remember_me: rememberMe,
    });
    // 성공 처리 (기존 로직 유지)
    authStore.setLogin(result.access_token, {
      id: result.player_id,
      name: result.player_name,
      role: result.role,
    });
    navigate('/dashboard');
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '비밀번호가 틀렸습니다. 다시 시도해주세요.';
    setToast({ message: msg, type: 'error' });
    setMode('select'); // 플레이어 선택으로 복귀
  }
};

// JSX에 Toast 렌더링 추가 (return문 최상단):
{toast && (
  <Toast
    message={toast.message}
    type={toast.type}
    onClose={() => setToast(null)}
  />
)}
```

> **주의:** 위 코드는 가이드입니다. 실제 index.tsx의 현재 구조를 확인한 후, 기존 상태 관리 패턴에 맞게 통합하세요. mode 전환은 현재 `useState<'select' | 'pin' | 'admin'>` 패턴을 따릅니다.

---

## Task 4: 화이트 테마 통일

### global.css 수정

```bash
# 현재 global.css 확인
cat frontend/src/styles/global.css
```

**변경 사항:**
- `:root` CSS Variables가 화이트 테마 기준인지 확인
- `[data-domain="user"]`, `[data-domain="admin"]` 블록에 다크 테마 변수가 남아 있으면 제거
- `[data-domain="home"]`만 다크 테마 유지 (Phase 5 홈페이지)

**확정 CSS Variables (화이트 테마):**
```css
:root {
  --bg: #f8fafc;
  --card: #ffffff;
  --accent: #10b981;
  --blue: #3b82f6;
  --text: #1e293b;
  --muted: #64748b;
  --gold: #f59e0b;
  --danger: #ef4444;
  --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  --input-bg: #f1f5f9;
}

/* 홈페이지만 다크 테마 */
[data-domain="home"] {
  --bg: #0f0f0f;
  --card: #1a1a1a;
  --accent: #4CAF50;
  --blue: #00B0FF;
  --text: #efefef;
  --muted: #666;
  --gold: #FFD700;
  --shadow: none;
  --input-bg: #222;
}
```

- `[data-domain="user"]` 블록이 있으면 삭제 (루트 변수 상속으로 충분)
- `[data-domain="admin"]` 블록이 있으면 삭제

### Auth.module.css 수정

화이트 테마에 맞게 배경/텍스트 색상 확인 및 수정:
- `loginOverlay` 배경: `rgba(248, 250, 252, 0.95)` (화이트 반투명)
- `loginCard` 배경: `#ffffff`, 보더: `1px solid #e2e8f0`
- 텍스트: `#1e293b`, 서브텍스트: `#64748b`

### UserDashboard.module.css 수정

다크 테마 잔재가 있는지 확인 후 화이트 테마로 수정:
```bash
# 다크 테마 색상 검색
grep -n "#0f0f0f\|#1a1a1a\|#222\|#333\|#efefef\|rgba(15" frontend/src/pages/UserDashboard/UserDashboard.module.css
```
발견되는 다크 색상을 모두 화이트 테마 변수로 교체합니다.

---

## Task 5: User Dashboard 응원 섹션 개선

### StoryCards.tsx (또는 해당 응원 컴포넌트) 수정

**현재 구조 확인:**
```bash
cat frontend/src/pages/UserDashboard/components/StoryCards.tsx
```

**변경 사항:**
1. 이모지(👨/👩) → 실제 사진 (원형 클리핑, `app_configs`의 `photos.dad`/`photos.mom`)
2. 사진 옆에 말풍선으로 응원 메시지 표시
3. **2열 가운데 배치**: 아빠(사진+말풍선) | 엄마(사진+말풍선)
4. 메시지 미설정 시 기본값: "오늘도 화이팅!" 표시
5. 화면 너비 좁으면 1열 폴백 (모바일 대응)

**컴포넌트 구조:**
```tsx
// StoryCards.tsx 가이드
interface CheerData {
  dad?: string;
  mom?: string;
}

interface ParentPhotos {
  dad?: string;
  mom?: string;
}

interface Props {
  cheers: CheerData;
  parentPhotos: ParentPhotos;
}

const DEFAULT_CHEER = '오늘도 화이팅!';

export default function StoryCards({ cheers, parentPhotos }: Props) {
  return (
    <div className={styles.cheerSection}>
      <div className={styles.cheerGrid}>
        {/* 아빠 */}
        <div className={styles.cheerItem}>
          <div className={styles.cheerPhotoRing} style={{ borderColor: 'var(--blue)' }}>
            {parentPhotos.dad ? (
              <img src={parentPhotos.dad} alt="아빠" className={styles.cheerPhoto} />
            ) : (
              <span className={styles.cheerInitial}>아빠</span>
            )}
          </div>
          <div className={styles.cheerBubbleWrapper}>
            <span className={styles.cheerLabel} style={{ color: 'var(--blue)' }}>아빠</span>
            <div className={styles.cheerBubble}>
              {cheers.dad || DEFAULT_CHEER}
            </div>
          </div>
        </div>

        {/* 엄마 */}
        <div className={styles.cheerItem}>
          <div className={styles.cheerPhotoRing} style={{ borderColor: '#db2777' }}>
            {parentPhotos.mom ? (
              <img src={parentPhotos.mom} alt="엄마" className={styles.cheerPhoto} />
            ) : (
              <span className={styles.cheerInitial}>엄마</span>
            )}
          </div>
          <div className={styles.cheerBubbleWrapper}>
            <span className={styles.cheerLabel} style={{ color: '#db2777' }}>엄마</span>
            <div className={styles.cheerBubble}>
              {cheers.mom || DEFAULT_CHEER}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### UserDashboard.module.css 응원 섹션 스타일 추가

```css
/* 응원 섹션 — 2열 가운데 배치 */
.cheerSection {
  background: var(--card);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
}

.cheerGrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  justify-items: center;
}

.cheerItem {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  max-width: 300px;
}

.cheerPhotoRing {
  width: 48px;
  height: 48px;
  min-width: 48px;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
  overflow: hidden;
  background: var(--input-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cheerPhoto {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cheerInitial {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--muted);
}

.cheerBubbleWrapper {
  flex: 1;
  min-width: 0;
}

.cheerLabel {
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 4px;
  display: block;
}

.cheerBubble {
  position: relative;
  background: var(--input-bg);
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 10px 14px;
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--text);
  word-break: keep-all;
}

.cheerBubble::before {
  content: '';
  position: absolute;
  left: -7px;
  top: 14px;
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-right: 7px solid #e2e8f0;
}

.cheerBubble::after {
  content: '';
  position: absolute;
  left: -5.5px;
  top: 14.5px;
  width: 0;
  height: 0;
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-right: 6px solid var(--input-bg);
}

/* 모바일 1열 폴백 */
@media (max-width: 600px) {
  .cheerGrid {
    grid-template-columns: 1fr;
  }
  .cheerItem {
    max-width: 100%;
  }
}
```

### useDashboard.ts 수정 — parentPhotos 로드 추가

`useDashboard.ts`에서 `app_configs`의 부모 사진 데이터를 로드하도록 보강합니다:

```typescript
// useDashboard.ts에 추가
const [parentPhotos, setParentPhotos] = useState<{ dad?: string; mom?: string }>({});

useEffect(() => {
  dashboardApi.getConfig('photos')
    .then(res => {
      if (res?.data?.value) {
        const photos = JSON.parse(res.data.value);
        setParentPhotos({ dad: photos.dad, mom: photos.mom });
      }
    })
    .catch(() => {});
}, []);

// return에 parentPhotos 추가
```

---

## Task 6: Auth.module.css 카드형 스타일 추가/수정

기존 Auth.module.css에 아래 클래스를 추가하거나 수정합니다:

```css
/* 선물상자 아이콘 */
.giftIcon {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

/* 타이틀 */
.authTitle {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text);
  text-align: center;
  margin: 0 0 4px;
}

.authSubtitle {
  font-size: 0.85rem;
  color: var(--muted);
  text-align: center;
  margin: 0 0 20px;
}

/* 플레이어 카드 */
.playerCard {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 16px;
  background: var(--card);
  cursor: pointer;
  transition: 0.2s;
  text-align: center;
}

.playerCard:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
}

.playerCard:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.playerAvatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #ecfdf5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  overflow: hidden;
}

.playerPhoto {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.playerInitial {
  font-size: 1rem;
  font-weight: 700;
  color: #059669;
}

.playerName {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.levelBadge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #ecfdf5;
  color: #059669;
}

.lockIcon {
  margin-top: 4px;
  font-size: 0.8rem;
}

/* 관리자 로그인 링크 */
.adminLinkBtn {
  display: block;
  margin: 16px auto 0;
  background: none;
  border: none;
  color: var(--muted);
  font-size: 0.85rem;
  text-decoration: underline;
  cursor: pointer;
}

.adminLinkBtn:hover {
  color: var(--text);
}
```

---

## 최종 검증

```bash
# 1. TypeScript 검증
cd frontend
npx tsc --noEmit && echo "✅ tsc OK"

# 2. 빌드
npm run build && echo "✅ Build OK"

# 3. 백엔드 (수정 없지만 확인)
cd ../backend
python3 -m py_compile app/main.py && echo "✅ BE OK"
cd ..

# 4. 화이트 테마 확인 — 다크 테마 잔재 검색
echo "=== 다크 테마 잔재 검색 ==="
grep -rn "#0f0f0f\|#1a1a1a\|#222222\|rgba(15, 23, 42" \
  frontend/src/pages/UserDashboard/ \
  frontend/src/pages/Auth/ \
  --include="*.css" --include="*.module.css" | grep -v "data-domain.*home"

# 5. Toast 컴포넌트 존재 확인
ls frontend/src/shared/components/Toast/
```

---

## Definition of Done

| # | 항목 | 확인 |
|---|---|---|
| 1 | npm run build 0 errors | |
| 2 | tsc --noEmit 0 errors | |
| 3 | 로그인 화면: 선물상자 아이콘 + "포인트 잔치" + 카드형 플레이어 + Lv 배지 | |
| 4 | PIN 오류: 토스트 "비밀번호가 틀렸습니다" 3초 표시 + 플레이어 선택 복귀 | |
| 5 | User Dashboard: 부모 응원 섹션 2열 가운데, 사진(원형)+말풍선 | |
| 6 | 응원 메시지 기본값 "오늘도 화이팅!" 표시 | |
| 7 | 다크 테마 잔재 없음 (home 제외) | |
| 8 | Toast 컴포넌트 shared/components/Toast/ 에 존재 | |

---

## 완료 보고 형식

```
제목: P-HOTFIX-UI-OVERHAUL-001 — 목업 기반 UI 통합 개선
수행자: Claude Code
Task ID: P-HOTFIX-UI-OVERHAUL-001
상태: 진행중 → 완료

수정/생성 파일:
- frontend/src/shared/components/Toast/Toast.tsx (신규)
- frontend/src/shared/components/Toast/Toast.module.css (신규)
- frontend/src/shared/components/Toast/index.ts (신규)
- frontend/src/pages/Auth/index.tsx (수정)
- frontend/src/pages/Auth/components/PlayerSelectView.tsx (수정)
- frontend/src/pages/Auth/components/PlayerCard.tsx (수정)
- frontend/src/pages/Auth/Auth.module.css (수정)
- frontend/src/styles/global.css (수정)
- frontend/src/pages/UserDashboard/components/StoryCards.tsx (수정)
- frontend/src/pages/UserDashboard/UserDashboard.module.css (수정)
- frontend/src/pages/UserDashboard/hooks/useDashboard.ts (수정)

검증:
- [ ] npm run build 0 errors
- [ ] tsc --noEmit 0 errors
- [ ] 다크 테마 잔재 0건 (home 제외)
```
