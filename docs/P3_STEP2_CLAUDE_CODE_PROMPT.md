# Phase 3 Step 2 — Claude Code 실행 지시서

> **Phase:** 3 | **Step:** 2 (v2 Overhaul)
> **수행자:** Claude Code (Developer)
> **선행 조건:** Step 1 완료 (P3-001 ~ P3-009 ✅, npm build 0 errors)
> **CLAUDE.md 필독 후 작업 시작**

---

## 🚨 실행 규칙

1. **이 문서에 명시된 파일만 생성/수정** — 임의 파일 생성 금지
2. **CSS Modules 강제** — 모든 스타일은 `UserDashboard.module.css`에 추가
3. **global.css 수정 금지** — CSS Variable은 global.css에서 상속만
4. **router.py에 로직 금지** — Thin Controller 원칙
5. **Step 1 기존 코드 동작 보존** — 기능 회귀 금지

---

## Task P3-010: ExpBar.tsx 생성 + ProfileCard 통합

### 10-A. ExpBar.tsx 생성

**경로:** `frontend/src/pages/UserDashboard/components/ExpBar.tsx`

```tsx
import React from 'react';
import styles from '../UserDashboard.module.css';

interface ExpBarProps {
  totalPoints: number;
  levelThresholds: Record<string, number>;
}

export default function ExpBar({ totalPoints, levelThresholds }: ExpBarProps) {
  // 레벨 계산: thresholds 내림차순 순회
  const levels = Object.entries(levelThresholds)
    .map(([lv, pts]) => ({ level: Number(lv), points: pts }))
    .sort((a, b) => b.points - a.points);

  let currentLevel = 1;
  for (const { level, points } of levels) {
    if (totalPoints >= points) {
      currentLevel = level;
      break;
    }
  }

  // 현재 레벨 → 다음 레벨 진행률
  const currentThreshold = levelThresholds[String(currentLevel)] ?? 0;
  const nextLevel = currentLevel + 1;
  const nextThreshold = levelThresholds[String(nextLevel)] ?? null;

  let progressPercent = 100;
  if (nextThreshold !== null) {
    const range = nextThreshold - currentThreshold;
    const progress = totalPoints - currentThreshold;
    progressPercent = range > 0 ? Math.min(Math.round((progress / range) * 100), 100) : 100;
  }

  return (
    <div className={styles.expBarContainer}>
      <span className={styles.levelBadge}>Lv.{currentLevel}</span>
      <div className={styles.expBarTrack}>
        <div
          className={styles.expBarFill}
          style={{ width: `${progressPercent}%` }}
        />
      </div>
      <span className={styles.expBarText}>
        {nextThreshold !== null
          ? `${totalPoints - currentThreshold} / ${nextThreshold - currentThreshold}`
          : 'MAX'}
      </span>
    </div>
  );
}
```

### 10-B. ProfileCard.tsx 수정

**경로:** `frontend/src/pages/UserDashboard/components/ProfileCard.tsx`

**수정 내용:** ExpBar import 추가 + 프로필 하단에 ExpBar 렌더링

```
// import 추가
import ExpBar from './ExpBar';

// ProfileCard JSX 내부, 상태메시지/stat-row 아래에 추가:
<ExpBar
  totalPoints={dailyPoint?.balance ?? 0}
  levelThresholds={levelThresholds}
/>
```

> ProfileCard의 기존 props에 `levelThresholds`가 이미 포함되어 있는지 확인.
> 없으면 Props 타입에 `levelThresholds: Record<string, number>` 추가하고
> index.tsx에서 전달.

---

## Task P3-011: MissionProgressBar.tsx 생성 + MissionList 통합

### 11-A. MissionProgressBar.tsx 생성

**경로:** `frontend/src/pages/UserDashboard/components/MissionProgressBar.tsx`

```tsx
import React from 'react';
import styles from '../UserDashboard.module.css';

interface MissionProgressBarProps {
  status: string;
}

const STEPS = [
  { key: 'active', label: '도전중' },
  { key: 'pending_approval', label: '확인중' },
  { key: 'completed', label: '완료!' },
];

export default function MissionProgressBar({ status }: MissionProgressBarProps) {
  const currentIndex = STEPS.findIndex(s => s.key === status);
  // rejected, failed, proposed 등은 바를 표시하지 않음
  if (currentIndex < 0) return null;

  return (
    <div className={styles.missionProgressBar}>
      {STEPS.map((step, i) => (
        <React.Fragment key={step.key}>
          <div
            className={`${styles.progressStep} ${i <= currentIndex ? styles.progressStepActive : ''}`}
          >
            <div className={styles.progressDot} />
            <span className={styles.progressLabel}>{step.label}</span>
          </div>
          {i < STEPS.length - 1 && (
            <div
              className={`${styles.progressLine} ${i < currentIndex ? styles.progressLineActive : ''}`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
```

### 11-B. MissionList.tsx 수정

**수정 내용:** 기존 텍스트 상태 표시를 MissionProgressBar로 교체

```
// import 추가
import MissionProgressBar from './MissionProgressBar';

// 각 미션 카드 내부에서 기존 상태 텍스트 대신:
<MissionProgressBar status={mission.status} />
// (기존 상태 텍스트/뱃지는 제거하거나, MissionProgressBar가 null 반환하는 상태에서만 폴백)
```

---

## Task P3-012: ConfettiEffect.tsx 생성 + 미션 완료 트리거

### 12-A. ConfettiEffect.tsx 생성

**경로:** `frontend/src/pages/UserDashboard/components/ConfettiEffect.tsx`

```tsx
import React, { useEffect, useState, useCallback } from 'react';
import styles from '../UserDashboard.module.css';

interface ConfettiEffectProps {
  trigger: boolean;
}

interface Particle {
  id: number;
  x: number;
  color: string;
  delay: number;
  duration: number;
}

const COLORS = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'];

export default function ConfettiEffect({ trigger }: ConfettiEffectProps) {
  const [particles, setParticles] = useState<Particle[]>([]);

  const createParticles = useCallback(() => {
    const newParticles: Particle[] = Array.from({ length: 30 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      delay: Math.random() * 0.5,
      duration: 1.5 + Math.random() * 1,
    }));
    setParticles(newParticles);
    // 애니메이션 종료 후 정리
    setTimeout(() => setParticles([]), 3000);
  }, []);

  useEffect(() => {
    if (trigger) createParticles();
  }, [trigger, createParticles]);

  if (particles.length === 0) return null;

  return (
    <div className={styles.confettiContainer}>
      {particles.map(p => (
        <div
          key={p.id}
          className={styles.confettiParticle}
          style={{
            left: `${p.x}%`,
            backgroundColor: p.color,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.duration}s`,
          }}
        />
      ))}
    </div>
  );
}
```

### 12-B. index.tsx (또는 MissionList) 수정

**수정 내용:** 승인 요청 성공 시 confetti 트리거

```
// useDashboard 또는 index.tsx에 상태 추가:
const [showConfetti, setShowConfetti] = useState(false);

// requestApproval 래핑:
const handleApproval = async (missionId: number) => {
  await requestApproval(missionId);
  setShowConfetti(true);
  setTimeout(() => setShowConfetti(false), 100);
};

// JSX에 ConfettiEffect 배치 (최상위):
<ConfettiEffect trigger={showConfetti} />
```

---

## Task P3-013: StoryCards "+" 추가 카드 제거

**경로:** `frontend/src/pages/UserDashboard/components/StoryCards.tsx`

**수정 내용:**
- "+" 아이콘이 표시되는 추가 카드 요소를 **삭제**
- 아빠/엄마 2개 스토리 카드만 남김
- 관련 CSS 클래스(`.storyCardAdd` 등)가 있다면 `UserDashboard.module.css`에서도 삭제

---

## Task P3-014: CSS v2 오버라이드

**경로:** `frontend/src/pages/UserDashboard/UserDashboard.module.css`

아래 CSS를 **기존 CSS 하단에 추가** (Step 1 CSS는 수정하지 말 것):

```css
/* ========================================
   Step 2: v2 Overhaul — 마인크래프트 픽셀 스타일
   ======================================== */

/* --- 픽셀 스타일 기본 --- */
.missionCard,
.profileCard,
.feedbackCard,
.deductSection,
.proposalSection {
  border: 3px solid var(--border);
  border-radius: 4px;
  box-shadow: 4px 4px 0 var(--border);
  image-rendering: pixelated;
}

/* --- ExpBar --- */
.expBarContainer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 12px;
  background: var(--card-bg);
  border: 2px solid var(--border);
  border-radius: 4px;
}

.levelBadge {
  font-weight: 800;
  font-size: 0.85rem;
  color: var(--accent);
  background: var(--accent-bg, rgba(76, 175, 80, 0.1));
  padding: 2px 8px;
  border-radius: 4px;
  border: 2px solid var(--accent);
  white-space: nowrap;
}

.expBarTrack {
  flex: 1;
  height: 12px;
  background: var(--input-bg);
  border: 2px solid var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.expBarFill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #8BC34A);
  transition: width 0.6s ease;
  image-rendering: pixelated;
}

.expBarText {
  font-size: 0.75rem;
  color: var(--muted);
  white-space: nowrap;
  min-width: 60px;
  text-align: right;
}

/* --- Mission Progress Bar --- */
.missionProgressBar {
  display: flex;
  align-items: center;
  gap: 0;
  margin-top: 8px;
  padding: 6px 0;
}

.progressStep {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  z-index: 1;
}

.progressDot {
  width: 14px;
  height: 14px;
  border-radius: 2px;
  border: 2px solid var(--border);
  background: var(--input-bg);
  transition: all 0.3s ease;
}

.progressStepActive .progressDot {
  background: var(--accent);
  border-color: var(--accent);
  box-shadow: 0 0 6px var(--accent);
}

.progressLabel {
  font-size: 0.65rem;
  color: var(--muted);
  white-space: nowrap;
}

.progressStepActive .progressLabel {
  color: var(--accent);
  font-weight: 700;
}

.progressLine {
  flex: 1;
  height: 3px;
  background: var(--border);
  margin: 0 -2px;
  margin-bottom: 18px;
  transition: background 0.3s ease;
}

.progressLineActive {
  background: var(--accent);
}

/* --- Confetti --- */
.confettiContainer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
  overflow: hidden;
}

.confettiParticle {
  position: absolute;
  top: -10px;
  width: 8px;
  height: 8px;
  border-radius: 1px;
  animation: confettiFall linear forwards;
}

@keyframes confettiFall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
    opacity: 0;
  }
}

/* --- 포인트 코인 스타일 --- */
.coinIcon {
  display: inline-block;
  width: 18px;
  height: 18px;
  background: #FFD700;
  border: 2px solid #DAA520;
  border-radius: 2px;
  text-align: center;
  line-height: 14px;
  font-size: 0.6rem;
  font-weight: 900;
  color: #8B6914;
  margin-right: 4px;
  vertical-align: middle;
  box-shadow: 1px 1px 0 #B8860B;
}

.pointValue {
  font-weight: 800;
  color: var(--accent);
}
```

### 추가 수정: MissionList의 포인트 표시를 코인 스타일로 변경

MissionList.tsx에서 포인트 표시 부분:

```tsx
// 기존: <span>{mission.point}P</span>
// 변경:
<span className={styles.pointValue}>
  <span className={styles.coinIcon}>P</span>
  {mission.point}
</span>
```

---

## Task P3-015: 빌드 검증

```bash
# 1. Frontend 빌드
cd frontend && npm run build
# 결과: 0 errors, 0 warnings (Expected)

# 2. Backend py_compile (Step 1에서 추가한 player PATCH 포함)
python -m py_compile backend/app/domains/player/router.py
python -m py_compile backend/app/domains/player/service.py
python -m py_compile backend/app/domains/player/schema.py

# 3. TypeScript 타입 체크 (선택)
cd frontend && npx tsc --noEmit
```

---

## 완료 보고 형식

```
제목: Phase 3 Step 2 — v2 Overhaul 완료
수행자: Claude Code
일시: [YYYY-MM-DD HH:MM]
Task ID: P3-010 ~ P3-015
상태: 진행중 → 완료
생성/수정 파일:
  - frontend/src/pages/UserDashboard/components/ExpBar.tsx [신규]
  - frontend/src/pages/UserDashboard/components/MissionProgressBar.tsx [신규]
  - frontend/src/pages/UserDashboard/components/ConfettiEffect.tsx [신규]
  - frontend/src/pages/UserDashboard/components/ProfileCard.tsx [수정]
  - frontend/src/pages/UserDashboard/components/MissionList.tsx [수정]
  - frontend/src/pages/UserDashboard/components/StoryCards.tsx [수정]
  - frontend/src/pages/UserDashboard/index.tsx [수정]
  - frontend/src/pages/UserDashboard/UserDashboard.module.css [수정]
빌드 결과: npm build 0 errors / py_compile OK
```

---

*이 문서는 Claude Code 실행 전용입니다. 설계 의도는 PHASE3_DESIGN_USER_DASHBOARD_FE.md를 참조하세요.*
