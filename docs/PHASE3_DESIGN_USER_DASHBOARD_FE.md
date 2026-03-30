# Phase 3 설계서 — User Dashboard FE (Option C: Step 1 Baseline → Step 2 v2 Overhaul)

> **작성자:** Claude Web (Main Architect)
> **작성일:** 2026-03-30
> **감사 상태:** Gemini CONDITIONAL PASS → 조건 3건 반영 완료
> **목표:** user.html → React 마이그레이션 + DESIGN_V2_DECISIONS.md 디자인 고도화

---

## 🚨 실행 전 필독사항

### Phase 3 범위: FE Only + App.tsx 수정 + init.sql Seed 1건
- BE 코드 수정 없음 (Phase 2 완료 상태 유지)
- 신규 FE 페이지: `src/pages/UserDashboard/` 전체
- 수정 파일: `App.tsx` (라우트 변경 + Auth Guard), `init.sql` (레벨 임계치 Seed)

### Gemini 감사 조건 반영 사항
1. **Auth Guard**: App.tsx에 인증 가드 추가 — 미인증 시 `/dashboard` 접근 차단
2. **레벨 임계치**: FE 상수가 아닌 BE `app_configs` DB 연동
3. **Step 분리**: Step 1(Pixel-perfect Baseline) → Step 2(v2 Overhaul) 명확 구분

### 아키텍처 철칙 (FE)
1. **1 Page = 1 Directory**: `pages/UserDashboard/` 하위 수직 응집
2. **CSS Modules 강제**: `UserDashboard.module.css` (global.css 예외만)
3. **Shared 승격 규칙**: BottomNav는 Local 유지 (Admin과 기능/링크 상이)
4. **테마 격리**: `data-domain="user"` 래퍼 적용

---

## Part 0. 사전 작업 — init.sql Seed 추가

레벨 임계치를 `app_configs`에 Seed로 추가합니다.

```sql
-- init.sql 기존 Seed 하단에 추가
INSERT INTO app_configs (key, value) VALUES
    ('level.thresholds', '{"1":0,"2":50,"3":150,"4":300,"5":500}');
```

> JSON 문자열로 저장. FE에서 `GET /api/configs/level.thresholds`로 조회 후 파싱합니다.

---

## Part 1. 폴더 구조

```
src/pages/UserDashboard/
├── index.tsx                        # 엔트리: 레이아웃 조립 + 탭/네비 상태
├── UserDashboard.module.css         # Step 1: pixel-perfect CSS → Step 2: v2 오버라이드
├── components/
│   ├── DateSelector.tsx             # 어제/오늘/내일 칩 + 날짜 표시
│   ├── ProfileCard.tsx              # 프로필 (사진, 이름, 상태메시지, 통계 3칸)
│   ├── StoryCards.tsx               # 아빠/엄마 스토리 카드 (응원 메시지 모달)
│   ├── MissionList.tsx              # 미션 카드 목록 + 승인 요청 버튼
│   ├── MissionProposal.tsx          # 미션 제안 폼 + 내 제안 현황
│   ├── FeedbackSection.tsx          # 답장 목록 + 답글 표시 + 입력
│   ├── DeductionAccordion.tsx       # 포인트 사용 내역 (접기/펼치기)
│   ├── RankingView.tsx              # 순위 탭 (전체 플레이어 진행현황)
│   ├── BottomNav.tsx                # 하단 네비 (홈/순위)
│   ├── StatDetailModal.tsx          # 포인트 통계 상세 모달
│   ├── CheerModal.tsx               # 스토리 카드 클릭 시 응원 메시지 모달
│   ├── ExpBar.tsx                   # [Step 2] 레벨 + 경험치 바
│   ├── MissionProgressBar.tsx       # [Step 2] 미션 진행률 바 (3단계)
│   └── ConfettiEffect.tsx           # [Step 2] 축하 애니메이션
├── hooks/
│   └── useDashboard.ts              # 상태 관리 + API 호출 통합
└── api/
    └── dashboardApi.ts              # 미션/피드백/차감/포인트/응원/설정 API
```

---

## Part 2. App.tsx 수정 (Auth Guard + 라우트 변경)

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/Auth';
import UserDashboard from './pages/UserDashboard';
import { useAuthStore } from './shared/stores/useAuthStore';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAuthStore();
  if (!isLoggedIn) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* "/" → 플레이어 선택 (DESIGN_V2: 게이트 페이지 폐기) */}
        <Route
          path="/"
          element={
            <div data-domain="user">
              <AuthPage />
            </div>
          }
        />
        {/* "/dashboard" → 인증된 사용자만 접근 */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <div data-domain="user">
                <UserDashboard />
              </div>
            </ProtectedRoute>
          }
        />
        {/* Phase 4 placeholder */}
        <Route
          path="/admin"
          element={
            <div data-domain="admin">
              <div>Admin Dashboard (Phase 4)</div>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## Part 3. API 설계 — dashboardApi.ts

```typescript
import { httpClient } from '../../../shared/api/httpClient';

// === Types ===
export interface MissionResponse {
  id: number;
  player_id: number;
  date: string;
  text: string;
  point: number;
  status: string;
  sender: string | null;
  msg: string | null;
  proposed_by: string | null;
  proposal_reason: string | null;
  rejection_reason: string | null;
  sort_order: number;
}

export interface CheerResponse {
  id: number;
  date: string;
  sender: string;
  message: string;
}

export interface FeedbackReplyResponse {
  id: number;
  feedback_id: number;
  sender: string;
  text: string;
  created_at: string;
}

export interface FeedbackResponse {
  id: number;
  player_id: number;
  date: string;
  msg: string;
  replies: FeedbackReplyResponse[];
}

export interface DeductionResponse {
  id: number;
  player_id: number;
  date: string;
  reason: string;
  amount: number;
}

export interface DailyPointResponse {
  id: number;
  player_id: number;
  date: string;
  earned: number;
  spent: number;
  balance: number;
}

export interface ConfigResponse {
  id: number;
  key: string;
  value: string | null;
}

export interface PlayerResponse {
  id: number;
  name: string;
  role: string;
  last_login: number | null;
  is_locked: boolean;
}

// === API Functions ===
export const dashboardApi = {
  /** 날짜 변경 시 한번에 병렬 호출 */
  fetchDayData: async (playerId: number, date: string) => {
    const [missions, cheers, feedbacks, deductions, dailyPoint] = await Promise.all([
      httpClient.get<MissionResponse[]>(`/api/missions`, { params: { player_id: playerId, date } }),
      httpClient.get<CheerResponse[]>(`/api/cheers`, { params: { date } }),
      httpClient.get<FeedbackResponse[]>(`/api/feedbacks`, { params: { player_id: playerId, date } }),
      httpClient.get<DeductionResponse[]>(`/api/deductions`, { params: { player_id: playerId, date } }),
      httpClient.get<DailyPointResponse | null>(`/api/daily-points`, { params: { player_id: playerId, date } }),
    ]);
    return {
      missions: missions.data,
      cheers: cheers.data,
      feedbacks: feedbacks.data,
      deductions: deductions.data,
      dailyPoint: dailyPoint.data,
    };
  },

  /** 미션 승인 요청 (active → pending_approval) */
  requestApproval: (missionId: number) =>
    httpClient.patch<MissionResponse>(`/api/missions/${missionId}`, { status: 'pending_approval' }),

  /** 미션 제안 */
  proposeMission: (data: { player_id: number; date: string; text: string; point: number; proposed_by: string; proposal_reason?: string }) =>
    httpClient.post<MissionResponse>('/api/missions/propose', data),

  /** 피드백 전송 */
  sendFeedback: (data: { player_id: number; date: string; msg: string }) =>
    httpClient.post<FeedbackResponse>('/api/feedbacks', data),

  /** 전체 플레이어 목록 (랭킹용) */
  getPlayers: () =>
    httpClient.get<PlayerResponse[]>('/api/players'),

  /** 포인트 범위 조회 (랭킹용) */
  getPointsRange: (playerId: number, start: string, end: string) =>
    httpClient.get<DailyPointResponse[]>(`/api/daily-points/range`, { params: { player_id: playerId, start, end } }),

  /** 앱 설정 조회 (부모 사진, 레벨 임계치 등) */
  getConfig: (key: string) =>
    httpClient.get<ConfigResponse>(`/api/configs/${key}`),

  /** 프로필 상태 메시지 수정 */
  updateStatusMsg: (playerId: number, statusMsg: string) =>
    httpClient.patch(`/api/players/${playerId}`, { status_msg: statusMsg }),
};
```

> **참고:** `updateStatusMsg`는 현재 player/router.py에 PATCH 엔드포인트가 없습니다. Phase 3 실행 시 player 도메인에 `update_player` service + PATCH 라우트를 최소 추가해야 합니다. (상태 메시지 수정 전용)

---

## Part 4. 상태 관리 — useDashboard.ts

```typescript
import { useState, useCallback, useEffect } from 'react';
import { useAuthStore } from '../../../shared/stores/useAuthStore';
import { dashboardApi, MissionResponse, CheerResponse, FeedbackResponse, DeductionResponse, DailyPointResponse } from '../api/dashboardApi';

function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

export function useDashboard() {
  const { player } = useAuthStore();

  // 날짜
  const [selectedDate, setSelectedDate] = useState(getToday());

  // 데이터
  const [missions, setMissions] = useState<MissionResponse[]>([]);
  const [cheers, setCheers] = useState<CheerResponse[]>([]);
  const [feedbacks, setFeedbacks] = useState<FeedbackResponse[]>([]);
  const [deductions, setDeductions] = useState<DeductionResponse[]>([]);
  const [dailyPoint, setDailyPoint] = useState<DailyPointResponse | null>(null);

  // UI 상태
  const [activeTab, setActiveTab] = useState<'missions' | 'proposal' | 'feedback'>('missions');
  const [activeNav, setActiveNav] = useState<'home' | 'ranking'>('home');
  const [deductOpen, setDeductOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // 레벨 설정 (app_configs에서 로드)
  const [levelThresholds, setLevelThresholds] = useState<Record<string, number>>({ "1": 0, "2": 50, "3": 150, "4": 300, "5": 500 });

  // 날짜 변경 시 데이터 로드
  const loadDayData = useCallback(async () => {
    if (!player) return;
    setLoading(true);
    try {
      const data = await dashboardApi.fetchDayData(player.id, selectedDate);
      setMissions(data.missions);
      setCheers(data.cheers);
      setFeedbacks(data.feedbacks);
      setDeductions(data.deductions);
      setDailyPoint(data.dailyPoint);
    } catch (err) {
      console.error('데이터 로드 실패:', err);
    } finally {
      setLoading(false);
    }
  }, [player, selectedDate]);

  useEffect(() => { loadDayData(); }, [loadDayData]);

  // 레벨 임계치 로드 (최초 1회)
  useEffect(() => {
    dashboardApi.getConfig('level.thresholds')
      .then(res => {
        if (res.data.value) setLevelThresholds(JSON.parse(res.data.value));
      })
      .catch(() => {}); // 실패 시 기본값 유지
  }, []);

  // 미션 승인 요청
  const requestApproval = useCallback(async (missionId: number) => {
    await dashboardApi.requestApproval(missionId);
    await loadDayData(); // 목록 갱신
  }, [loadDayData]);

  // 미션 제안
  const proposeMission = useCallback(async (text: string, point: number, reason?: string) => {
    if (!player) return;
    await dashboardApi.proposeMission({
      player_id: player.id,
      date: selectedDate,
      text,
      point,
      proposed_by: player.name,
      proposal_reason: reason,
    });
    await loadDayData();
  }, [player, selectedDate, loadDayData]);

  // 피드백 전송
  const sendFeedback = useCallback(async (msg: string) => {
    if (!player) return;
    await dashboardApi.sendFeedback({
      player_id: player.id,
      date: selectedDate,
      msg,
    });
    await loadDayData();
  }, [player, selectedDate, loadDayData]);

  // 날짜 퀵 선택
  const quickDate = useCallback((offset: number) => {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    setSelectedDate(d.toISOString().slice(0, 10));
  }, []);

  // 파생 데이터
  const myProposals = missions.filter(m => m.status === 'proposed' && m.proposed_by === player?.name);
  const activeMissions = missions.filter(m => m.status !== 'proposed');
  const totalDeducted = deductions.reduce((sum, d) => sum + d.amount, 0);
  const totalAllocated = activeMissions.reduce((sum, m) => m.status !== 'rejected' ? sum + m.point : sum, 0);
  const pendingPoints = activeMissions.filter(m => m.status === 'active').reduce((sum, m) => sum + m.point, 0);

  return {
    // 상태
    player, selectedDate, missions, cheers, feedbacks, deductions, dailyPoint,
    activeTab, activeNav, deductOpen, loading, levelThresholds,
    // 파생
    myProposals, activeMissions, totalDeducted, totalAllocated, pendingPoints,
    // 액션
    setSelectedDate, setActiveTab, setActiveNav, setDeductOpen,
    quickDate, requestApproval, proposeMission, sendFeedback, loadDayData,
  };
}
```

---

## Part 5. CSS Modules 전략

### Step 1 (Baseline): design-v2-user.html CSS를 1:1 추출

`UserDashboard.module.css`에 design-v2-user.html의 `<style>` 블록(384줄)을 CSS Modules 형식으로 변환합니다.

**변환 규칙:**
- 전역 클래스명 → camelCase 모듈 클래스 (`.mission-card` → `.missionCard`)
- CSS Variable(`--accent` 등)은 global.css에서 상속 — 중복 선언 금지
- `@keyframes`는 모듈 내부에 정의 (자동 스코핑)
- 미디어 쿼리 보존

**예시 매핑:**

| design-v2-user.html 클래스 | CSS Module 클래스 |
|---|---|
| `.header` | `.header` |
| `.bottom-nav` | `.bottomNav` |
| `.story-card` | `.storyCard` |
| `.story-ring` | `.storyRing` |
| `.date-chip` | `.dateChip` |
| `.date-chip.active` | `.dateChipActive` |
| `.profile-card` | `.profileCard` |
| `.stat-pill` | `.statPill` |
| `.stat-earned` | `.statEarned` |
| `.mission-card` | `.missionCard` |
| `.mission-status` | `.missionStatus` |
| `.status-active` | `.statusActive` |
| `.status-completed` | `.statusCompleted` |
| `.deduct-section` | `.deductSection` |
| `.proposal-section` | `.proposalSection` |
| `.feedback-card` | `.feedbackCard` |
| `.progress-card` | `.progressCard` |
| `.login-overlay` | Phase 1 Auth에서 이미 구현 — 중복 금지 |
| `.selector-section` | Phase 1 Auth에서 이미 구현 — 중복 금지 |

### Step 2 (v2 Overhaul): CSS 변경/추가 사항

Step 2에서 `UserDashboard.module.css`에 추가/수정할 내용:

1. **마인크래프트 픽셀 스타일**: `image-rendering: pixelated`, 각진 `box-shadow`, 8bit 보더
2. **프로필 경험치 바**: `.expBarContainer`, `.expBarFill`, `.levelBadge`
3. **미션 진행률 바**: `.progressBar`, `.progressStep`, `.progressStepActive`
4. **축하 애니메이션**: `@keyframes confetti`, `.confettiParticle`
5. **스토리 카드 "+" 제거**: `.storyCardAdd` 삭제
6. **미션 포인트 게임 코인 스타일**: `.coinIcon`, `.pointValue`

---

## Part 6. 컴포넌트 상세 명세

### 6-1. DateSelector.tsx

```
Props: { selectedDate, quickDate, setSelectedDate }
기능: 어제/오늘/내일 칩 + 날짜 텍스트 표시
CSS: .dateBar, .dateChip, .dateChipActive, .dateDisplay
```

### 6-2. ProfileCard.tsx

```
Props: { player, dailyPoint, totalAllocated, pendingPoints, levelThresholds }
기능: 프로필 사진 + 이름 + 상태메시지 입력 + 포인트 통계 3칸
Step 2 추가: ExpBar (레벨 + 경험치 바)
CSS: .profileCard, .profileHeader, .profilePhoto, .profileName, .statusInput, .statRow, .statPill
```

### 6-3. StoryCards.tsx

```
Props: { cheers, configs }
기능: 아빠/엄마 스토리 링 (클릭 시 CheerModal 열기)
Step 1: "+" 추가 카드 포함 (원본 보존)
Step 2: "+" 추가 카드 제거 (DESIGN_V2 반영)
CSS: .storyRow, .storyCard, .storyRing, .storyAvatar, .storyName
```

### 6-4. MissionList.tsx

```
Props: { missions (activeMissions), requestApproval }
기능: 미션 카드 목록. 상태별 UI 분기 (6종)
  - active: "완료! 승인 요청" 버튼
  - pending_approval: "승인 대기 중..." 텍스트
  - completed: 완료 배지
  - failed: 취소선 + 0P
  - rejected: 거절 사유 표시
  - proposed: 이 목록에 미표시 (MissionProposal에서 처리)
sender 버블: msg-dad (파란) / msg-mom (핑크)
Step 2 추가: MissionProgressBar 교체 (텍스트 상태 → 시각 바)
CSS: .missionCard, .missionStatus, .statusActive/Completed/Pending/Failed/Rejected, .missionTitle, .missionPoints, .missionMsg, .msgDad, .msgMom, .missionAction, .actionApprove
```

### 6-5. MissionProposal.tsx

```
Props: { myProposals, proposeMission }
기능: 제안 폼 (제목 + 포인트 + 이유) + 내 제안 현황 아코디언
CSS: .proposalSection, .proposalTitle, .proposalInput, .proposalBtn
```

### 6-6. FeedbackSection.tsx

```
Props: { feedbacks, sendFeedback, playerName }
기능: 답장 목록 + 답글 (sender별 색상) + 답장 입력 + 전송
CSS: .feedbackCard, .feedbackInputRow, .feedbackInput, .feedbackSend
```

### 6-7. DeductionAccordion.tsx

```
Props: { deductions, totalDeducted, isOpen, onToggle }
기능: "포인트 사용 내역" 아코디언 (접기/펼치기)
CSS: .deductSection, .deductHeader, .deductItem, .deductAmount
```

### 6-8. RankingView.tsx

```
Props: { currentPlayerId }
기능: 전체 플레이어 진행현황 (완료/승인대기/보유P)
API: dashboardApi.getPlayers() + 각 플레이어별 dailyPoint 조회
CSS: .progressSection, .progressCard, .progressName, .progressBadge, .progressStats
```

### 6-9. BottomNav.tsx

```
Props: { activeNav, setActiveNav }
기능: 홈 / 순위 2버튼
CSS: .bottomNav, .navItem, .navItemActive, .navIcon, .navLabel
```

### 6-10. StatDetailModal.tsx

```
Props: { type, isOpen, onClose, missions, deductions, dailyPoint }
기능: 포인트 통계 칩 클릭 시 상세 모달 (배정/보유/남은미션)
CSS: .modalOverlay, .modalBox
```

### 6-11. CheerModal.tsx

```
Props: { sender, message, isOpen, onClose }
기능: 스토리 카드 클릭 시 응원 메시지 표시
CSS: .modalOverlay, .modalBox (공유)
```

### 6-12. ExpBar.tsx [Step 2]

```
Props: { totalPoints, levelThresholds }
기능: 레벨 배지 (Lv.3) + 경험치 프로그레스 바 (현재 레벨 진행률)
레벨 계산: thresholds에서 현재 포인트에 해당하는 레벨 결정
CSS: .expBarContainer, .expBarFill, .levelBadge
```

### 6-13. MissionProgressBar.tsx [Step 2]

```
Props: { status }
기능: 3단계 시각 바 (도전중 → 확인중 → 완료!)
CSS: .progressBar, .progressStep, .progressStepActive
```

### 6-14. ConfettiEffect.tsx [Step 2]

```
Props: { trigger: boolean }
기능: 미션 완료 승인 시 축하 폭죽 애니메이션 (CSS particle 또는 canvas-confetti)
CSS: @keyframes confetti
```

---

## Part 7. Player PATCH 엔드포인트 추가 (최소 BE 보강)

상태 메시지 수정을 위해 player 도메인에 PATCH를 추가합니다.

### player/schema.py 추가

```python
class PlayerUpdate(BaseModel):
    status_msg: Optional[str] = Field(default=None, max_length=200)
```

### player/service.py 추가

```python
async def update_player(db: AsyncSession, player_id: int, data: PlayerUpdate) -> PlayerListItem:
    """
    -- [SQL] 플레이어 정보 수정
    -- UPDATE players SET status_msg = :status_msg, updated_at = NOW()
    -- WHERE id = :player_id AND deleted_at IS NULL;
    """
    stmt = select(Player).where(Player.id == player_id, Player.deleted_at.is_(None))
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(player, key, value)
    await db.commit()
    await db.refresh(player)
    return PlayerListItem.model_validate(player)
```

### player/router.py 추가

```python
@router.patch("/{player_id}", response_model=PlayerListItem)
async def edit_player(player_id: int, data: PlayerUpdate, db: AsyncSession = Depends(get_db)):
    """플레이어 정보 수정"""
    return await update_player(db, player_id, data)
```

---

## Part 8. Step 분리 실행 계획

### Step 1: Pixel-perfect Baseline (Claude Code 세션 1)

| Task ID | 작업 |
|---|---|
| P3-001 | `init.sql` Seed 추가 (level.thresholds) |
| P3-002 | `App.tsx` 수정 (Auth Guard + 라우트 변경) |
| P3-003 | Player PATCH 엔드포인트 추가 (schema/service/router) |
| P3-004 | `dashboardApi.ts` 생성 |
| P3-005 | `useDashboard.ts` 생성 |
| P3-006 | `UserDashboard.module.css` 생성 (design-v2-user.html CSS 1:1 변환) |
| P3-007 | 컴포넌트 10개 생성 (DateSelector ~ CheerModal) |
| P3-008 | `index.tsx` 엔트리 조립 |
| P3-009 | 빌드 검증 (npm build 0 errors) |

**Step 1 완료 기준:**
- `npm run build` 0 errors
- `/` → 플레이어 선택 표시
- `/dashboard` → 미인증 시 `/`로 리다이렉트
- 인증 후 대시보드 — 모든 섹션 표시 (데이터 없어도 빈 상태 UI)
- design-v2-user.html과 pixel-perfect 일치

### Step 2: v2 Overhaul (Claude Code 세션 2)

| Task ID | 작업 |
|---|---|
| P3-010 | `ExpBar.tsx` 생성 + ProfileCard에 통합 |
| P3-011 | `MissionProgressBar.tsx` 생성 + MissionList에 통합 |
| P3-012 | `ConfettiEffect.tsx` 생성 + 미션 완료 시 트리거 |
| P3-013 | StoryCards "+" 추가 카드 제거 |
| P3-014 | CSS v2 오버라이드 (마인크래프트 픽셀 스타일, 코인 아이콘 등) |
| P3-015 | 빌드 검증 (npm build 0 errors) |

---

## Part 9. 기존 동작 보존 체크리스트

| # | 기능 | 컴포넌트 | 보존 |
|---|---|---|---|
| U-1 | 날짜 선택 시 모든 데이터 동시 갱신 | useDashboard | ✅ |
| U-2 | 미션 카드에 sender 버블 (아빠/엄마 색상) | MissionList | ✅ |
| U-3 | "완료! 승인 요청" → pending_approval | MissionList | ✅ |
| U-4 | 미션 제안 폼 (제목+포인트+이유) | MissionProposal | ✅ |
| U-5 | 내 제안 현황 (검토중/승인/거절) | MissionProposal | ✅ |
| U-6 | 거절 시 rejectionReason 표시 | MissionList | ✅ |
| U-7 | 포인트 사용 내역 아코디언 | DeductionAccordion | ✅ |
| U-8 | 답장 목록 + 답글 표시 | FeedbackSection | ✅ |
| U-9 | 답장 입력 + 전송 | FeedbackSection | ✅ |
| U-10 | 하단 네비 홈/순위 전환 | BottomNav | ✅ |
| U-11 | 순위 탭 포인트 표시 | RankingView | ✅ |
| U-12 | 프로필 상태 메시지 수정 | ProfileCard | ✅ |
| U-13 | 로그아웃 → 플레이어 선택 복귀 | Header (index.tsx) | ✅ |

---

## Part 10. Gemini 감사 조건 충족 확인

| # | 조건 | 반영 위치 | 상태 |
|---|---|---|---|
| 1 | Auth Guard | App.tsx `ProtectedRoute` 컴포넌트 | ✅ |
| 2 | 레벨 임계치 BE 연동 | init.sql Seed + dashboardApi.getConfig + useDashboard | ✅ |
| 3 | Step 1/2 분리 | Part 8 실행 계획 | ✅ |

---

*Phase 3 설계서 끝. Gemini 재감사 또는 Claude Code 실행 대기.*
