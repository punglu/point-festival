# P-HOTFIX-ADMIN-LAYOUT-001 — Admin 사이드바 레이아웃 개편

> **작성자:** Claude Web (Main Architect)
> **작성일:** 2026-04-01
> **감사 상태:** 대기 (Gemini Audit 전)
> **목표:** Admin Dashboard를 단일 스크롤 페이지에서 사이드바 + 멀티 서브페이지 구조로 전환

---

## 🚨 실행 전 필독사항

### 핵심 원칙
1. **BE 코드 수정 없음** — 순수 FE 레이아웃 리팩토링
2. **기존 기능 100% 보존** — 모든 Admin 기능은 서브페이지로 재배치되며 삭제 없음
3. **1 Page = 1 Directory** 철칙 유지 — `AdminDashboard/` 내부 수직 응집
4. **CSS Modules 강제** — `AdminLayout.module.css`, `Sidebar.module.css` 등
5. **Shared 승격: `AdminLayout` 컴포넌트는 Local 유지** (Admin 전용, User와 공유 안함)

### DESIGN_V2_DECISIONS.md 반영 사항
- 관리자 페이지 멀티 페이지 분리 (Dashboard / Mission / Point / Player / Config)
- 사이드바 네비게이션 적용 (모바일: Drawer 패턴)
- 하단 네비바 → 사이드바 전환 (Admin은 User와 네비 구조 상이)

---

## Part 0. 현재 Admin 기능 인벤토리

레거시 `admin.html` + 현재 React `AdminDashboard/`에서 추출한 전체 기능 목록:

| # | 기능 영역 | 현재 위치 | 신규 서브페이지 |
|---|---|---|---|
| F-1 | Quest Control (미션 생성: 대상 선택 + 발신자 + 제목 + 포인트 + 메시지) | 상단 패널 | **Mission** |
| F-2 | 미션 관리 (과거 미션 가져오기, 일괄 복제, 일괄 삭제) | 미션 관리 패널 | **Mission** |
| F-3 | 미션 제안 검토 (승인/거절 + 날짜 변경) | proposal-review-section | **Mission** |
| F-4 | 날짜 선택 (어제/오늘/내일 + Date Picker) | 날짜 패널 | **전역 필터 (Header)** |
| F-5 | 응원 메시지 편집 (아빠/엄마 + 사진 업로드) | 응원 패널 | **Mission** (또는 Config) |
| F-6 | 플레이어 카드 (프로필 + 통계 3칸 + 미션 목록 + 피드백) | player-cards 그리드 | **Dashboard** (요약) |
| F-7 | 미션 승인/실패/복구/삭제 | 각 미션 카드 내부 | **Mission** |
| F-8 | 포인트 차감 (모달) | deduct-modal | **Point** |
| F-9 | 포인트 사용 내역 아코디언 | 플레이어 카드 내부 | **Point** |
| F-10 | 통계 상세 모달 (획득/사용/잔액) | archive-modal | **Dashboard** |
| F-11 | 사용자 관리 (등록 + PIN 설정 + 잠금 해제 + 삭제) | user-management-panel | **Player** |
| F-12 | 로그인 기록 조회 | login-history-modal | **Player** |
| F-13 | 알림 센터 (읽음 처리, 미션 이동) | notification-modal | **Sidebar 배지 + Notifications 페이지** |
| F-14 | 관리자 로그인/로그아웃 | admin-auth / header | **Auth (기존) + Sidebar 하단** |
| F-15 | 사진 업로드 (부모 + 아이 프로필) | photo-upload hidden input | **Player** (아이) / **Config** (부모) |
| F-16 | 설정 관리 (레벨 임계치, 응원 발신자, 인증 정책) | CLEANUP-001에서 동적화 완료 | **Configuration** |

---

## Part 1. 서브페이지 라우트 설계

### 라우트 구조 (Nested Routes)

```
/admin                → AdminLayout (사이드바 + 헤더 + Outlet)
  /admin              → DashboardView (기본 진입 = 전체 현황 요약)
  /admin/mission      → MissionView (Quest Control + 미션 목록 + 제안 검토)
  /admin/point        → PointView (포인트 차감/지급 + 사용 내역)
  /admin/player       → PlayerView (사용자 관리 + 로그인 기록)
  /admin/config       → ConfigView (레벨 임계치 + 응원 발신자 + 인증 정책 + 부모 사진)
  /admin/notification → NotificationView (알림 센터 전체)
```

### App.tsx 수정 사항

```tsx
// 기존
<Route path="/admin" element={<AdminRoute><div data-domain="admin"><AdminDashboard /></div></AdminRoute>} />

// 변경
<Route path="/admin" element={<AdminRoute><div data-domain="admin"><AdminDashboard /></div></AdminRoute>}>
  <Route index element={<DashboardView />} />
  <Route path="mission" element={<MissionView />} />
  <Route path="point" element={<PointView />} />
  <Route path="player" element={<PlayerView />} />
  <Route path="config" element={<ConfigView />} />
  <Route path="notification" element={<NotificationView />} />
</Route>
```

---

## Part 2. 폴더 구조

```
src/pages/AdminDashboard/
├── index.tsx                          # AdminLayout 래퍼 (Sidebar + Header + Outlet)
├── AdminLayout.module.css             # 사이드바 레이아웃 전체 스타일
├── constants.ts                       # 메뉴 정의 (ADMIN_MENU_ITEMS)
│
├── layout/                            # 레이아웃 전용 컴포넌트
│   ├── Sidebar.tsx                    # 좌측 사이드바
│   ├── Sidebar.module.css
│   ├── AdminHeader.tsx                # 상단 헤더 (Breadcrumb + 전역 필터)
│   ├── AdminHeader.module.css
│   ├── MobileDrawer.tsx               # 모바일용 사이드바 Drawer
│   └── MobileDrawer.module.css
│
├── views/                             # 서브페이지 (각 메뉴 1:1 매핑)
│   ├── DashboardView.tsx              # 전체 현황 요약 (F-6, F-10)
│   ├── DashboardView.module.css
│   ├── MissionView.tsx                # 미션 관리 통합 (F-1~3, F-5, F-7)
│   ├── MissionView.module.css
│   ├── PointView.tsx                  # 포인트 관리 (F-8, F-9)
│   ├── PointView.module.css
│   ├── PlayerView.tsx                 # 사용자 관리 (F-11, F-12, F-15)
│   ├── PlayerView.module.css
│   ├── ConfigView.tsx                 # 설정 관리 (F-16, F-15부모)
│   ├── ConfigView.module.css
│   ├── NotificationView.tsx           # 알림 센터 (F-13)
│   └── NotificationView.module.css
│
├── components/                        # 기존 Admin 공용 컴포넌트 (리팩토링)
│   ├── PlayerFilterBar.tsx            # 플레이어 + 날짜 필터 (전역 공유)
│   ├── PlayerFilterBar.module.css
│   ├── StatCards.tsx                  # 통계 카드 3칸 (획득/사용/잔액)
│   ├── StatCards.module.css
│   ├── MissionCard.tsx                # 개별 미션 카드 (승인/실패/복구/삭제)
│   ├── MissionCard.module.css
│   ├── QuestControl.tsx               # 미션 생성 폼
│   ├── QuestControl.module.css
│   ├── ProposalReview.tsx             # 미션 제안 검토 패널
│   ├── ProposalReview.module.css
│   ├── CheerEditor.tsx                # 응원 메시지 편집 (기존 컴포넌트 이동)
│   ├── CheerEditor.module.css
│   ├── DeductModal.tsx                # 포인트 차감 모달
│   ├── DeductModal.module.css
│   ├── DeductionList.tsx              # 포인트 사용 내역 리스트
│   ├── DeductionList.module.css
│   ├── UserManagement.tsx             # 사용자 등록/PIN/잠금해제/삭제
│   ├── UserManagement.module.css
│   ├── LoginHistory.tsx               # 로그인 기록
│   └── LoginHistory.module.css
│
├── hooks/
│   ├── useAdminDashboard.ts           # 기존 통합 훅 (리팩토링)
│   └── useAdminMenu.ts               # 사이드바 메뉴 상태 관리
│
└── api/
    └── adminApi.ts                    # 기존 API (변경 없음)
```

---

## Part 3. 핵심 컴포넌트 상세

### 3-1. constants.ts — 메뉴 정의 (SSOT)

```typescript
export interface AdminMenuItem {
  key: string;
  label: string;
  path: string;
  icon: string;      // 이모지 (마인크래프트 테마)
  badge?: 'notification'; // 동적 배지 타입
}

export const ADMIN_MENU_ITEMS: AdminMenuItem[] = [
  { key: 'dashboard',    label: '대시보드',   path: '/admin',              icon: '🏠' },
  { key: 'mission',      label: '미션 관리',  path: '/admin/mission',      icon: '⚔️' },
  { key: 'point',        label: '포인트',     path: '/admin/point',        icon: '💎' },
  { key: 'player',       label: '플레이어',   path: '/admin/player',       icon: '👾' },
  { key: 'config',       label: '설정',       path: '/admin/config',       icon: '⚙️' },
  { key: 'notification', label: '알림',       path: '/admin/notification', icon: '🔔', badge: 'notification' },
];
```

### 3-2. index.tsx — AdminLayout

```tsx
import { Outlet } from 'react-router-dom';
import Sidebar from './layout/Sidebar';
import AdminHeader from './layout/AdminHeader';
import MobileDrawer from './layout/MobileDrawer';
import { useAdminMenu } from './hooks/useAdminMenu';
import styles from './AdminLayout.module.css';

export default function AdminDashboard() {
  const { isMobileOpen, toggleMobile, closeMobile } = useAdminMenu();

  return (
    <div className={styles.adminLayout}>
      {/* 데스크톱: 사이드바 고정 */}
      <Sidebar className={styles.desktopSidebar} />

      {/* 모바일: Drawer 오버레이 */}
      <MobileDrawer isOpen={isMobileOpen} onClose={closeMobile} />

      <div className={styles.mainArea}>
        <AdminHeader onMenuToggle={toggleMobile} />
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

### 3-3. Sidebar.tsx

```tsx
Props: { className? }
기능:
  - ADMIN_MENU_ITEMS 순회하여 NavLink 렌더링
  - 현재 경로 매칭 → active 클래스 적용
  - notification 배지: useNotificationStore에서 unread count 표시
  - 하단: 관리자 프로필 (useAuthStore.player.name) + 로그아웃 버튼
CSS: .sidebar, .brand, .nav, .navItem, .navItemActive, .navIcon,
     .navLabel, .badge, .profile, .logoutBtn
```

**디자인 방향:**
- 배경: `var(--admin-sidebar-bg)` — 진한 보라/남색 계열 (`#1e1b4b` ~ `#312e81`)
- 활성 메뉴: 반투명 흰색 배경 (`rgba(255,255,255,0.12)`) + 좌측 accent bar
- 텍스트: 흰색/반투명 흰색
- 아이콘: 이모지 (마인크래프트 픽셀 테마와 조화)
- 브랜드 영역: "Point Hub" + 마인크래프트 픽셀 아이콘 (SVG 또는 이모지 ⛏️)

### 3-4. AdminHeader.tsx

```tsx
Props: { onMenuToggle }
기능:
  - Breadcrumb 표시 (현재 라우트 기반 자동 생성)
  - 페이지 타이틀 표시
  - 전역 필터 바: PlayerFilterBar 임베드 (플레이어 선택 + 날짜 선택)
  - 모바일: 햄버거 메뉴 버튼
CSS: .header, .breadcrumb, .pageTitle, .filterArea, .menuToggle
```

### 3-5. MobileDrawer.tsx

```tsx
Props: { isOpen, onClose }
기능:
  - isOpen 시 좌측에서 슬라이드 인 (transform: translateX)
  - 배경 오버레이 클릭 시 닫기
  - 내부: Sidebar 컴포넌트 재사용
  - 메뉴 항목 클릭 시 자동 닫기
CSS: .overlay, .drawer, .drawerOpen
반응형 기준: 768px 이하에서 활성화
```

### 3-6. PlayerFilterBar.tsx (전역 필터)

```tsx
Props: { selectedPlayerId, selectedDate, onPlayerChange, onDateChange, onQuickDate }
기능:
  - 플레이어 드롭다운 (전체 플레이어 목록)
  - Date Picker + 어제/오늘/내일 퀵 버튼
  - 현재 날짜 텍스트 표시
  - 선택 변경 시 부모(View)에 콜백
CSS: .filterBar, .filterSelect, .filterDate, .quickDateChip, .quickDateActive
```

> **설계 의도:** 기존에 각 패널마다 중복되던 날짜/플레이어 선택을 전역 필터로 통합합니다.
> Header에 고정 배치하여 모든 View에서 동일한 필터 컨텍스트를 공유합니다.

---

## Part 4. 서브페이지(View) 상세

### 4-1. DashboardView.tsx — 전체 현황 요약

```
기능:
  - StatCards 3칸 (전체 플레이어 합산 또는 선택된 플레이어)
  - 오늘의 미션 요약 (미완료/승인대기/완료 카운트)
  - 미션 제안 알림 배지 (있으면 "N건 검토 대기" 카드)
  - 플레이어별 간략 진행현황 카드 (프로필 + 통계)
참조 기능: F-6, F-10
CSS: .dashboardGrid, .summaryCard, .playerOverview
```

### 4-2. MissionView.tsx — 미션 관리 통합

```
기능:
  - QuestControl (미션 생성 폼) — 상단 고정
  - ProposalReview (미션 제안 검토) — 대기 건 있을 때만 표시
  - 미션 목록 (MissionCard 반복 렌더링)
  - 미션 관리 도구: 과거 미션 가져오기 / 일괄 복제 / 일괄 삭제
  - CheerEditor (응원 메시지 편집)
참조 기능: F-1, F-2, F-3, F-5, F-7
CSS: .missionPage, .questControlPanel, .proposalPanel, .missionList, .missionTools
```

### 4-3. PointView.tsx — 포인트 관리

```
기능:
  - 플레이어별 포인트 요약 (현재 잔액, 총 획득, 총 사용)
  - 차감 버튼 → DeductModal 호출
  - 사용 내역 리스트 (DeductionList) — 수정/삭제 지원
  - 통계 상세 (획득/사용/잔액 상세 뷰)
참조 기능: F-8, F-9, F-10
CSS: .pointPage, .pointSummary, .deductionSection
```

### 4-4. PlayerView.tsx — 사용자 관리

```
기능:
  - 플레이어 등록 (이름 + PIN)
  - 플레이어 목록 (이름 변경, PIN 변경, 잠금 해제, 사진 업로드, 삭제)
  - 로그인 기록 조회 (LoginHistory)
참조 기능: F-11, F-12, F-15(아이)
CSS: .playerPage, .registerForm, .playerList, .playerItem
```

### 4-5. ConfigView.tsx — 설정 관리

```
기능:
  - 레벨 임계치 편집 (JSON 기반)
  - 응원 발신자 설정 (app_configs.cheer.senders)
  - 인증 정책 (MAX_LOGIN_ATTEMPTS, LOCK_DURATION_SECONDS) — 읽기 전용 표시 (env 기반)
  - 부모 사진 업로드 (아빠/엄마)
참조 기능: F-15(부모), F-16
CSS: .configPage, .configSection, .configField
```

### 4-6. NotificationView.tsx — 알림 센터

```
기능:
  - 알림 목록 (시간순 정렬)
  - 개별 읽음 처리
  - 모두 읽음 처리
  - 알림 클릭 시 해당 미션으로 이동 (MissionView + 스크롤)
참조 기능: F-13
CSS: .notificationPage, .notifItem, .notifUnread, .notifActions
```

---

## Part 5. CSS 설계

### 5-1. AdminLayout.module.css 핵심 구조

```css
.adminLayout {
  display: flex;
  min-height: 100vh;
}

.desktopSidebar {
  width: 240px;
  flex-shrink: 0;
}

.mainArea {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* flex 오버플로 방지 */
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 반응형: 768px 이하 */
@media (max-width: 768px) {
  .desktopSidebar {
    display: none;
  }
  .content {
    padding: 16px;
  }
}
```

### 5-2. Sidebar.module.css 디자인 토큰

```css
.sidebar {
  width: 240px;
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background: var(--admin-sidebar-bg, #1e1b4b);
  color: rgba(255, 255, 255, 0.85);
  padding: 16px 12px;
  overflow-y: auto;
}

.brand {
  padding: 12px 8px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 16px;
  text-align: center;
}

.brandTitle {
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.brandSub {
  font-size: 0.7rem;
  opacity: 0.6;
  margin-top: 4px;
}

.nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.navItem {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  text-decoration: none;
  color: inherit;
  font-size: 0.9rem;
  font-weight: 500;
}

.navItem:hover {
  background: rgba(255, 255, 255, 0.08);
}

.navItemActive {
  background: rgba(255, 255, 255, 0.12);
  border-left: 3px solid var(--accent, #10b981);
  padding-left: 9px; /* 3px border 보상 */
}

.navIcon {
  font-size: 1.1rem;
  width: 24px;
  text-align: center;
}

.badge {
  margin-left: auto;
  background: #ef4444;
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.profile {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 16px;
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.profileAvatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
}

.profileName {
  font-size: 0.85rem;
  font-weight: 600;
}

.logoutBtn {
  font-size: 0.75rem;
  opacity: 0.6;
  cursor: pointer;
  background: none;
  border: none;
  color: inherit;
  padding: 0;
}

.logoutBtn:hover {
  opacity: 1;
}
```

### 5-3. global.css 추가 필요 사항

```css
/* [data-domain="admin"] 테마 변수에 사이드바 변수 추가 */
[data-domain="admin"] {
  --admin-sidebar-bg: #1e1b4b;
  --admin-sidebar-text: rgba(255, 255, 255, 0.85);
  --admin-sidebar-active: rgba(255, 255, 255, 0.12);
  --admin-sidebar-hover: rgba(255, 255, 255, 0.08);
  --admin-sidebar-border: rgba(255, 255, 255, 0.1);
}
```

---

## Part 6. 상태 관리 설계

### 6-1. useAdminMenu.ts

```typescript
import { create } from 'zustand';

interface AdminMenuState {
  isMobileOpen: boolean;
  toggleMobile: () => void;
  closeMobile: () => void;
}

export const useAdminMenu = create<AdminMenuState>((set) => ({
  isMobileOpen: false,
  toggleMobile: () => set((s) => ({ isMobileOpen: !s.isMobileOpen })),
  closeMobile: () => set({ isMobileOpen: false }),
}));
```

### 6-2. useAdminDashboard.ts 리팩토링

기존 통합 훅을 View별로 필요한 데이터만 선택적으로 제공하도록 리팩토링합니다.
핵심 변경: **전역 필터(selectedPlayerId, selectedDate)를 Zustand store로 승격**

```typescript
// hooks/useAdminFilter.ts (신규)
import { create } from 'zustand';

interface AdminFilterState {
  selectedPlayerId: string | null; // null = 전체
  selectedDate: string;
  setPlayer: (id: string | null) => void;
  setDate: (date: string) => void;
  quickDate: (offset: number) => void;
}

export const useAdminFilter = create<AdminFilterState>((set) => ({
  selectedPlayerId: null,
  selectedDate: new Date().toISOString().slice(0, 10),
  setPlayer: (id) => set({ selectedPlayerId: id }),
  setDate: (date) => set({ selectedDate: date }),
  quickDate: (offset) => set(() => {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    return { selectedDate: d.toISOString().slice(0, 10) };
  }),
}));
```

---

## Part 7. App.tsx 수정 명세

### 변경 전:

```tsx
<Route path="/admin" element={<AdminRoute><div data-domain="admin"><AdminDashboard /></div></AdminRoute>} />
```

### 변경 후:

```tsx
import DashboardView from './pages/AdminDashboard/views/DashboardView';
import MissionView from './pages/AdminDashboard/views/MissionView';
import PointView from './pages/AdminDashboard/views/PointView';
import PlayerView from './pages/AdminDashboard/views/PlayerView';
import ConfigView from './pages/AdminDashboard/views/ConfigView';
import NotificationView from './pages/AdminDashboard/views/NotificationView';

// ...

<Route
  path="/admin"
  element={
    <AdminRoute>
      <div data-domain="admin">
        <AdminDashboard />
      </div>
    </AdminRoute>
  }
>
  <Route index element={<DashboardView />} />
  <Route path="mission" element={<MissionView />} />
  <Route path="point" element={<PointView />} />
  <Route path="player" element={<PlayerView />} />
  <Route path="config" element={<ConfigView />} />
  <Route path="notification" element={<NotificationView />} />
</Route>
```

---

## Part 8. 마이그레이션 매핑 — 기존 컴포넌트 → 신규 위치

| 기존 컴포넌트/로직 | 신규 위치 | 변경 사항 |
|---|---|---|
| `AdminDashboard/index.tsx` (전체 렌더링) | `index.tsx` (Layout만) + `views/DashboardView.tsx` | Layout/View 분리 |
| 플레이어 카드 그리드 전체 | `DashboardView` (요약) + `MissionView` (상세) | 분리 |
| Quest Control 패널 | `components/QuestControl.tsx` → `MissionView`에 임베드 | 위치 이동 |
| 미션 제안 검토 | `components/ProposalReview.tsx` → `MissionView`에 임베드 | 위치 이동 |
| 미션 관리 도구 (복제/삭제) | `MissionView` 내부 | 위치 이동 |
| 응원 메시지 편집 | `components/CheerEditor.tsx` → `MissionView`에 임베드 | 위치 이동 |
| 포인트 차감 모달 | `components/DeductModal.tsx` → `PointView`에서 호출 | 위치 이동 |
| 차감 내역 아코디언 | `components/DeductionList.tsx` → `PointView`에 임베드 | 아코디언 → 리스트 변환 |
| 사용자 관리 패널 | `components/UserManagement.tsx` → `PlayerView`에 임베드 | 위치 이동 |
| 로그인 기록 모달 | `components/LoginHistory.tsx` → `PlayerView`에 임베드 | 모달 → 섹션 변환 |
| 알림 모달 | `NotificationView` (전체 페이지) | 모달 → 페이지 변환 |
| 날짜 선택 패널 | `components/PlayerFilterBar.tsx` → `AdminHeader`에 임베드 | 전역화 |
| 통계 상세 모달 | `DashboardView` 내 StatCards 클릭 시 | 유지 |

---

## Part 9. Task 분해

| Task ID | 작업 | 생성/수정 파일 | 의존 |
|---|---|---|---|
| AL-001 | `constants.ts` + `useAdminMenu.ts` + `useAdminFilter.ts` 생성 | 3 파일 | 없음 |
| AL-002 | `AdminLayout.module.css` + `Sidebar.module.css` + `AdminHeader.module.css` + `MobileDrawer.module.css` 생성 | 4 파일 | AL-001 |
| AL-003 | `Sidebar.tsx` + `AdminHeader.tsx` + `MobileDrawer.tsx` 생성 | 3 파일 | AL-001, AL-002 |
| AL-004 | `index.tsx` 리팩토링 (Layout 래퍼 → Outlet 패턴) | 1 파일 수정 | AL-003 |
| AL-005 | `PlayerFilterBar.tsx` + CSS 생성 (전역 필터 컴포넌트) | 2 파일 | AL-001 |
| AL-006 | `DashboardView.tsx` + CSS 생성 (기존 요약 로직 추출) | 2 파일 | AL-004, AL-005 |
| AL-007 | `MissionView.tsx` + CSS 생성 (QuestControl + ProposalReview + 미션 목록 + CheerEditor 통합) | 2 파일 | AL-004, AL-005 |
| AL-008 | `PointView.tsx` + CSS 생성 (DeductModal + DeductionList 통합) | 2 파일 | AL-004, AL-005 |
| AL-009 | `PlayerView.tsx` + CSS 생성 (UserManagement + LoginHistory 통합) | 2 파일 | AL-004 |
| AL-010 | `ConfigView.tsx` + CSS 생성 (설정 관리) | 2 파일 | AL-004 |
| AL-011 | `NotificationView.tsx` + CSS 생성 (알림 센터) | 2 파일 | AL-004 |
| AL-012 | `App.tsx` 수정 (Nested Routes 적용) | 1 파일 수정 | AL-004~011 |
| AL-013 | `global.css` 사이드바 CSS Variable 추가 | 1 파일 수정 | AL-002 |
| AL-014 | 빌드 검증 (`npm run build` 0 errors) + Docker 이미지 재빌드 | — | 전체 |

**총 생성 파일: ~25개 | 수정 파일: ~3개**

---

## Part 10. 기존 동작 보존 체크리스트

| # | 기능 | 보존 방식 | View |
|---|---|---|---|
| A-1 | 미션 생성 (대상 + 발신자 + 제목 + 포인트 + 메시지) | QuestControl 컴포넌트 | Mission |
| A-2 | 미션 승인/실패/복구/삭제 | MissionCard 컴포넌트 | Mission |
| A-3 | 미션 제안 검토 (승인/거절 + 날짜 변경) | ProposalReview 컴포넌트 | Mission |
| A-4 | 과거 미션 가져오기 / 일괄 복제 / 일괄 삭제 | MissionView 내 도구 섹션 | Mission |
| A-5 | 날짜 선택 (어제/오늘/내일 + Date Picker) | PlayerFilterBar (전역) | Header |
| A-6 | 응원 메시지 편집 (저장/삭제 + 사진) | CheerEditor 컴포넌트 | Mission |
| A-7 | 포인트 차감 (모달) | DeductModal 컴포넌트 | Point |
| A-8 | 차감 내역 (수정/삭제) | DeductionList 컴포넌트 | Point |
| A-9 | 통계 상세 (획득/사용/잔액) | StatCards 클릭 → 모달 | Dashboard |
| A-10 | 사용자 등록/PIN변경/잠금해제/삭제 | UserManagement 컴포넌트 | Player |
| A-11 | 로그인 기록 조회 | LoginHistory 컴포넌트 | Player |
| A-12 | 알림 센터 (읽음/모두읽음/이동) | NotificationView | Notification |
| A-13 | 관리자 로그인/로그아웃 | Auth (기존) + Sidebar 하단 | Layout |
| A-14 | 플레이어 사진 업로드 | PlayerView 내 업로드 | Player |
| A-15 | 부모 사진 업로드 | ConfigView 내 업로드 | Config |
| A-16 | 설정 관리 (레벨/발신자/정책) | ConfigView | Config |

---

## Part 11. 반응형 설계

| 뷰포트 | 사이드바 | 헤더 | 콘텐츠 |
|---|---|---|---|
| ≥1024px (데스크톱) | 240px 고정 표시 | Breadcrumb + FilterBar 가로 배치 | 자유 레이아웃 |
| 769~1023px (태블릿) | 64px 아이콘 전용 (라벨 숨김) | FilterBar 축소 | 패딩 축소 |
| ≤768px (모바일) | 숨김 → Drawer | 햄버거 + 축약 필터 | 단일 컬럼 |

### 태블릿 모드 CSS (Sidebar)

```css
@media (min-width: 769px) and (max-width: 1023px) {
  .sidebar {
    width: 64px;
    padding: 12px 8px;
  }
  .navLabel, .brandTitle, .brandSub, .profileName, .logoutBtn {
    display: none;
  }
  .navItem {
    justify-content: center;
    padding: 10px;
  }
  .navIcon {
    font-size: 1.3rem;
  }
}
```

---

## Part 12. Gemini 감사 요청 포인트

이 설계서에서 Gemini가 특히 검증해야 할 항목:

1. **Nested Routes 구조**: `<Route>` 중첩이 React Router 6 규격에 맞는가?
2. **CSS Modules 캡슐화**: 사이드바 ↔ 메인 콘텐츠 스타일 충돌 가능성?
3. **전역 필터 상태**: `useAdminFilter` Zustand store가 View 간 공유 시 리렌더 범위 적절한가?
4. **기존 컴포넌트 호환성**: 기존 `useAdminDashboard` 훅과 API 호출이 View 분리 후에도 정상 동작하는가?
5. **모바일 Drawer**: 포커스 트랩, 스크롤 잠금 처리?
6. **기능 보존**: Part 10 체크리스트 A-1 ~ A-16 전건 커버 여부

---

*설계서 끝. Gemini Audit 후 Claude Code 실행 프롬프트로 전환합니다.*
