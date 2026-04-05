# [Claude Code 실행 프롬프트] P-HOTFIX-DASHBOARD-DETAIL-001: DashboardView 카드 상세 테이블 + 밸런싱 섹션

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P-HOTFIX-DASHBOARD-DETAIL-001
> **상태:** TODO → 진행중
> **선행 조건:** P-HOTFIX-CYCLE-INTEGRITY-001 완료 (✅ 확인됨)
> **목표:** 스탯 카드 4종을 탭화하여 클릭 시 상세 테이블 표시 + 플레이어 밸런싱 섹션 추가

---

## 🚨 실행 전 필독

### CLAUDE.md를 먼저 읽으세요.

### 아키텍처 철칙 (위반 시 QA Fail)
1. **Thin Controller**: router.py에 비즈니스 로직 0줄 — 이 핫픽스는 BE 변경 없음
2. **1 Page = 1 Directory**: 신규 컴포넌트는 `DashboardView/components/` 하위에만 생성
3. **CSS Modules 강제**: 인라인 style={{}} 파일당 5개 미만
4. **AbortController**: useEffect 내 API 호출 시 cleanup abort 필수 — 이 핫픽스는 추가 API 호출 없음
5. **mobile table→card**: `thead{display:none}` + `td::before{content:attr(data-label)}` 확립된 패턴 준수

### 핵심 제약
- **BE 변경 없음**: 신규 API, 신규 컬럼, DB 마이그레이션 모두 없음
- **기존 컴포넌트 수정 없음**: PlayerStatusCard, MissionRanking 등 기존 하위 컴포넌트 건드리지 마라
- **useAdminData 수정 없음**: CYCLE-INTEGRITY-001에서 이미 주기 범위 필터 적용됨. 훅이 반환하는 `missions[]`, `dailyPoints[]`, `players[]`, `stats`, `cycle` 데이터를 그대로 사용
- **데이터는 FE 순수 계산만**: missions[]를 filter/reduce/groupBy로 가공. 추가 fetch 0건

### 실행 순서
**Step 0(영향도 분석) → Step 1(CardDetailTable) → Step 2(BalanceSection) → Step 3(DashboardView 통합) → Step 4(모바일 대응) → Step 5(빌드 검증) → Step 6(CLAUDE.md)**

---

## Step 0: 영향도 분석 (실행 전 필수)

### 0-1. 현재 DashboardView 구조 확인

```bash
# DashboardView 디렉토리 구조
find frontend/src/pages/AdminDashboard/views/DashboardView -type f | sort

# 현재 DashboardView.tsx에서 import하는 컴포넌트 목록
grep -n "^import" frontend/src/pages/AdminDashboard/views/DashboardView/DashboardView.tsx

# useAdminData 훅이 반환하는 stats 객체 구조 확인
grep -A 20 "totalActiveMissions\|totalPointsIssued\|totalCompletedMissions\|totalPendingMissions" \
  frontend/src/pages/AdminDashboard/hooks/useAdminData.ts

# 현재 스탯 카드 JSX 구조 확인 (어떤 CSS 클래스를 사용하는지)
grep -n "statCard\|statsGrid\|statValue\|statLabel" \
  frontend/src/pages/AdminDashboard/views/DashboardView/DashboardView.tsx

# missions 타입 확인
grep -B2 -A10 "interface.*Mission\|type.*Mission" \
  frontend/src/pages/AdminDashboard/types/admin.types.ts

# cycle 객체 구조 확인
grep -B2 -A10 "cycle\|startDate\|endDate\|label" \
  frontend/src/pages/AdminDashboard/hooks/useAdminData.ts | head -40
```

### 0-2. 영향도 판단

| # | 확인 항목 | 기준 | 블로커 여부 |
|---|---|---|---|
| 1 | useAdminData가 `missions[]`를 반환하는지 | 배열이어야 함 (filter/reduce 가능) | 반환 안 하면 블로커 |
| 2 | missions 객체에 `date`, `player_id`, `status`, `point`, `text` 필드가 있는지 | 5개 필드 모두 필요 | 누락 시 블로커 |
| 3 | `cycle.startDate`, `cycle.endDate` 문자열 형식 | YYYY-MM-DD 형식 | 형식 다르면 조정 필요 |
| 4 | DashboardView.tsx의 기존 스탯 카드 4종 CSS 클래스명 | Step 3에서 교체 시 정확한 클래스명 필요 | — |
| 5 | DashboardView/components/ 디렉토리 존재 여부 | 없으면 생성 | — |
| 6 | players 배열에서 role='player'인 항목 필터링 방법 | 아빠(3)/엄마(4)는 밸런싱에서 제외해야 함 | — |

### 0-3. 보고 형식

```
=== P-HOTFIX-DASHBOARD-DETAIL-001 영향도 분석 ===

1. useAdminData 반환 구조:
   - missions: [타입/개수]
   - players: [타입/개수]  
   - dailyPoints: [타입/개수]
   - stats: { 필드 목록 }
   - cycle: { 필드 목록 }

2. Mission 타입 필드: [나열]
3. 기존 스탯 카드 CSS 클래스: [나열]
4. DashboardView/components/ 존재: [예/아니오]
5. 플레이어 역할 구분: [role 필드 또는 id 기반 필터]
6. 블로커: [없음 / 있음]

→ 결론: [진행 가능 / 조정 필요]
```

**블로커 없으면 Step 1 진행.**

---

## Step 1: CardDetailTable 컴포넌트 신규 생성

### 1-1. 파일 생성

**파일:** `frontend/src/pages/AdminDashboard/views/DashboardView/components/CardDetailTable.tsx`

```tsx
import { useState, useMemo } from 'react';
import styles from './CardDetailTable.module.css';

// ========================================
// 타입 (Step 0에서 확인한 실제 타입에 맞춰 조정)
// ========================================

interface Mission {
  id: number;
  player_id: number;
  date: string;       // YYYY-MM-DD
  text: string;
  point: number;
  status: string;     // active | completed | pending_approval | failed | proposed | rejected
  sender?: string;
  msg?: string;
}

interface Player {
  id: number;
  name: string;
  role?: string;
}

// ========================================
// 그룹 행 타입 (총 발행포인트 아코디언용)
// ========================================

interface GroupRow {
  key: string;           // "2026-04-05_1" (date_playerId)
  date: string;
  playerId: number;
  playerName: string;
  totalCount: number;    // 배정 건수
  totalPoints: number;   // 배정 포인트 합
  doneCount: number;     // 완료 건수
  donePoints: number;    // 완료 포인트 합
  rate: number;          // 달성률 % (소수점 없이 반올림)
  missions: Mission[];   // 드릴다운용 원본
}

// ========================================
// Props
// ========================================

type CardMode = 'points' | 'active' | 'pending' | 'completed';

interface CardDetailTableProps {
  mode: CardMode;
  missions: Mission[];
  players: Player[];
  cycleLabel: string;    // "2026.03.31 ~ 2026.04.06"
}

// ========================================
// 상태 pill 매핑
// ========================================

const STATUS_LABEL: Record<string, string> = {
  active: '진행중',
  completed: '완료',
  pending_approval: '승인대기',
  failed: '실패',
  proposed: '제안',
  rejected: '거절',
};

const STATUS_CLASS: Record<string, string> = {
  active: 'statusActive',
  completed: 'statusCompleted',
  pending_approval: 'statusPending',
  failed: 'statusFailed',
};

// ========================================
// 컴포넌트
// ========================================

export default function CardDetailTable({
  mode, missions, players, cycleLabel,
}: CardDetailTableProps) {
  const [filterPlayerId, setFilterPlayerId] = useState<number | null>(null);
  const [expandedGroup, setExpandedGroup] = useState<string | null>(null);

  // 플레이어 이름 맵
  const playerMap = useMemo(() => {
    const map = new Map<number, string>();
    players.forEach(p => map.set(p.id, p.name));
    return map;
  }, [players]);

  // 모드별 필터된 미션
  const filtered = useMemo(() => {
    let list = [...missions];

    // 플레이어 필터
    if (filterPlayerId !== null) {
      list = list.filter(m => m.player_id === filterPlayerId);
    }

    // 상태 필터 (points 모드는 전체)
    if (mode === 'active') list = list.filter(m => m.status === 'active');
    else if (mode === 'pending') list = list.filter(m => m.status === 'pending_approval');
    else if (mode === 'completed') list = list.filter(m => m.status === 'completed');

    // 정렬: 일자 내림차순, 플레이어ID 오름차순
    list.sort((a, b) => {
      if (a.date !== b.date) return b.date.localeCompare(a.date);
      return a.player_id - b.player_id;
    });

    return list;
  }, [missions, mode, filterPlayerId]);

  // points 모드: 일자×플레이어 그룹 집계
  const groupRows = useMemo<GroupRow[]>(() => {
    if (mode !== 'points') return [];

    const groups = new Map<string, GroupRow>();

    filtered.forEach(m => {
      const key = `${m.date}_${m.player_id}`;
      if (!groups.has(key)) {
        groups.set(key, {
          key,
          date: m.date,
          playerId: m.player_id,
          playerName: playerMap.get(m.player_id) || '?',
          totalCount: 0,
          totalPoints: 0,
          doneCount: 0,
          donePoints: 0,
          rate: 0,
          missions: [],
        });
      }
      const g = groups.get(key)!;
      g.totalCount += 1;
      g.totalPoints += m.point;
      if (m.status === 'completed') {
        g.doneCount += 1;
        g.donePoints += m.point;
      }
      g.missions.push(m);
    });

    // 달성률 계산
    groups.forEach(g => {
      g.rate = g.totalPoints > 0 ? Math.round((g.donePoints / g.totalPoints) * 100) : 0;
    });

    // 정렬: 일자 내림차순, 플레이어 오름차순
    return Array.from(groups.values()).sort((a, b) => {
      if (a.date !== b.date) return b.date.localeCompare(a.date);
      return a.playerId - b.playerId;
    });
  }, [filtered, mode, playerMap]);

  // 날짜 포맷: YYYY-MM-DD → MM-DD
  const fmtDate = (d: string) => d.slice(5); // "04-05"

  // 아코디언 토글
  const toggleGroup = (key: string) => {
    setExpandedGroup(prev => prev === key ? null : key);
  };

  // ========================================
  // 렌더링
  // ========================================

  return (
    <div className={styles.container}>
      {/* 헤더: 주기 라벨 + 플레이어 필터 */}
      <div className={styles.tableHeader}>
        {(mode === 'points' || mode === 'completed') && (
          <span className={styles.cycleLabel}>{cycleLabel}</span>
        )}
        {mode !== 'points' && mode !== 'completed' && <span />}
        <select
          className={styles.playerFilter}
          value={filterPlayerId ?? ''}
          onChange={(e) => setFilterPlayerId(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">전체</option>
          {players.map(p => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      {/* points 모드: 아코디언 그룹 */}
      {mode === 'points' && (
        <div className={styles.groupList}>
          {groupRows.length === 0 && (
            <div className={styles.empty}>이번 주기 데이터가 없습니다.</div>
          )}
          {groupRows.map(g => (
            <div key={g.key} className={styles.groupItem}>
              {/* 그룹 요약 행 */}
              <div
                className={`${styles.groupRow} ${expandedGroup === g.key ? styles.groupRowActive : ''}`}
                onClick={() => toggleGroup(g.key)}
              >
                <span className={styles.grDate}>{fmtDate(g.date)}</span>
                <span className={styles.grName}>{g.playerName}</span>
                <span className={styles.grAssigned}>
                  배정 {g.totalCount}건 · {g.totalPoints}P
                </span>
                <span className={styles.grDone}>
                  완료 {g.doneCount}건 · {g.donePoints}P
                  <span className={styles.grRate}>({g.rate}%)</span>
                </span>
                <span className={styles.grToggle}>
                  {expandedGroup === g.key ? '▼' : '▶'}
                </span>
              </div>

              {/* 미션 상세 (펼쳐짐) */}
              {expandedGroup === g.key && (
                <div className={styles.drilldown}>
                  <table className={styles.detailTable}>
                    <thead>
                      <tr>
                        <th>일자</th>
                        <th>이름</th>
                        <th>미션명</th>
                        <th>포인트</th>
                        <th>상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      {g.missions.map(m => (
                        <tr key={m.id}>
                          <td data-label="일자">{fmtDate(m.date)}</td>
                          <td data-label="이름">{playerMap.get(m.player_id)}</td>
                          <td data-label="미션명">{m.text}</td>
                          <td data-label="포인트">{m.point}P</td>
                          <td data-label="상태">
                            <span className={`${styles.statusPill} ${styles[STATUS_CLASS[m.status] || '']}`}>
                              {STATUS_LABEL[m.status] || m.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* active / pending / completed 모드: flat 테이블 */}
      {mode !== 'points' && (
        <div className={styles.flatTableWrap}>
          {filtered.length === 0 && (
            <div className={styles.empty}>
              {mode === 'active' && '진행중인 미션이 없습니다.'}
              {mode === 'pending' && '승인 대기 미션이 없습니다.'}
              {mode === 'completed' && '완료된 미션이 없습니다.'}
            </div>
          )}
          {filtered.length > 0 && (
            <table className={styles.detailTable}>
              <thead>
                <tr>
                  <th>일자</th>
                  <th>이름</th>
                  <th>미션명</th>
                  <th>포인트</th>
                  <th>상태</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(m => (
                  <tr key={m.id}>
                    <td data-label="일자">{fmtDate(m.date)}</td>
                    <td data-label="이름">{playerMap.get(m.player_id)}</td>
                    <td data-label="미션명">{m.text}</td>
                    <td data-label="포인트">{m.point}P</td>
                    <td data-label="상태">
                      <span className={`${styles.statusPill} ${styles[STATUS_CLASS[m.status] || '']}`}>
                        {STATUS_LABEL[m.status] || m.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
```

> **중요:** 위의 `Mission`, `Player` 인터페이스는 Step 0에서 확인한 실제 타입과 일치시키세요. `admin.types.ts`에 이미 정의되어 있으면 그것을 import하고 위 로컬 인터페이스는 삭제하세요.

### 1-2. CSS

**파일:** `frontend/src/pages/AdminDashboard/views/DashboardView/components/CardDetailTable.module.css`

```css
.container {
  padding: 14px;
}

/* 헤더: 주기 라벨 + 플레이어 필터 */
.tableHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.cycleLabel {
  font-size: 11px;
  color: var(--color-text-secondary, #64748b);
}

.playerFilter {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  background: var(--color-background-primary, #fff);
}

/* 빈 상태 */
.empty {
  text-align: center;
  padding: 24px;
  font-size: 12px;
  color: var(--color-text-tertiary, #94a3b8);
}

/* ========================================
   아코디언 그룹 (총 발행포인트 모드)
   ======================================== */

.groupList {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.groupItem {
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  border-radius: 8px;
  overflow: hidden;
}

.groupRow {
  display: grid;
  grid-template-columns: 56px 40px 1fr 1fr 40px;
  align-items: center;
  padding: 9px 10px;
  gap: 6px;
  background: var(--color-background-secondary, #f8fafc);
  cursor: pointer;
  transition: background 0.15s;
}

.groupRow:hover {
  background: #F5F3FF;
}

.groupRowActive {
  background: #EEEDFE;
}

.grDate {
  font-size: 11px;
  font-weight: 500;
}

.grName {
  font-size: 11px;
  font-weight: 500;
}

.grAssigned {
  font-size: 10px;
  color: var(--color-text-secondary, #64748b);
}

.grDone {
  font-size: 10px;
  color: #27500A;
}

.grRate {
  opacity: 0.6;
  margin-left: 2px;
}

.grToggle {
  font-size: 10px;
  text-align: right;
  color: var(--color-text-secondary, #64748b);
}

.groupRowActive .grDate,
.groupRowActive .grName {
  color: #3C3489;
}

.groupRowActive .grAssigned {
  color: #534AB7;
}

.groupRowActive .grToggle {
  color: #534AB7;
}

/* 드릴다운 영역 */
.drilldown {
  border-top: 0.5px solid var(--color-border-tertiary, #e2e8f0);
}

/* ========================================
   공통 상세 테이블 (flat + drilldown)
   ======================================== */

.flatTableWrap {
  overflow-x: auto;
}

.detailTable {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.detailTable thead th {
  padding: 6px 10px;
  font-size: 10px;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  background: var(--color-background-secondary, #f8fafc);
  text-align: left;
  border-bottom: 0.5px solid var(--color-border-tertiary, #e2e8f0);
}

.detailTable tbody td {
  padding: 8px 10px;
  border-bottom: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  vertical-align: middle;
}

.detailTable tbody tr:last-child td {
  border-bottom: none;
}

/* 상태 pill */
.statusPill {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  text-align: center;
}

.statusActive {
  background: #E6F1FB;
  color: #185FA5;
}

.statusCompleted {
  background: #EAF3DE;
  color: #27500A;
}

.statusPending {
  background: #EEEDFE;
  color: #534AB7;
}

.statusFailed {
  background: #FCEBEB;
  color: #A32D2D;
}

/* ========================================
   모바일 대응 (확립된 패턴)
   ======================================== */

@media (max-width: 768px) {
  /* 그룹 행: 2행 레이아웃 */
  .groupRow {
    grid-template-columns: 56px 40px 1fr 32px;
    grid-template-rows: auto auto;
  }

  .grAssigned {
    grid-column: 1 / 4;
    grid-row: 2;
  }

  .grDone {
    grid-column: 1 / 4;
    grid-row: 3;
  }

  .grToggle {
    grid-row: 1 / 3;
    grid-column: 4;
    align-self: center;
  }

  /* flat 테이블 → 카드 전환 */
  .detailTable thead {
    display: none;
  }

  .detailTable tbody tr {
    display: block;
    padding: 10px;
    margin-bottom: 6px;
    border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
    border-radius: 8px;
    background: var(--color-background-primary, #fff);
  }

  .detailTable tbody td {
    display: flex;
    justify-content: space-between;
    padding: 3px 0;
    border-bottom: none;
    font-size: 12px;
  }

  .detailTable tbody td::before {
    content: attr(data-label);
    font-size: 10px;
    color: var(--color-text-secondary, #64748b);
    font-weight: 500;
    min-width: 48px;
  }
}
```

---

## Step 2: BalanceSection 컴포넌트 신규 생성

### 2-1. 파일 생성

**파일:** `frontend/src/pages/AdminDashboard/views/DashboardView/components/BalanceSection.tsx`

```tsx
import { useMemo } from 'react';
import styles from './BalanceSection.module.css';

interface Mission {
  id: number;
  player_id: number;
  point: number;
  status: string;
}

interface Player {
  id: number;
  name: string;
  role?: string;
}

interface BalanceSectionProps {
  missions: Mission[];
  players: Player[];
}

interface PlayerBalance {
  id: number;
  name: string;
  assignedCount: number;
  assignedPoints: number;
  doneCount: number;
  donePoints: number;
  pendingPoints: number;   // 미완료 미션 포인트 합 (active + pending_approval)
  rate: number;            // 완료율 %
}

export default function BalanceSection({ missions, players }: BalanceSectionProps) {
  // 아이 플레이어만 (아빠/엄마 제외)
  // Step 0에서 확인한 실제 필터 조건으로 조정하세요.
  // role='player'이면 role 기반, 아니면 id <= 2 등으로 필터.
  const childPlayers = useMemo(() => {
    return players.filter(p => p.role === 'player' || (!p.role && p.id <= 2));
  }, [players]);

  // 플레이어별 밸런스 집계
  const balances = useMemo<PlayerBalance[]>(() => {
    return childPlayers.map(p => {
      const myMissions = missions.filter(m => m.player_id === p.id);
      const assignedCount = myMissions.length;
      const assignedPoints = myMissions.reduce((s, m) => s + m.point, 0);
      const done = myMissions.filter(m => m.status === 'completed');
      const doneCount = done.length;
      const donePoints = done.reduce((s, m) => s + m.point, 0);
      const pending = myMissions.filter(m => m.status === 'active' || m.status === 'pending_approval');
      const pendingPoints = pending.reduce((s, m) => s + m.point, 0);
      const rate = assignedPoints > 0 ? Math.round((donePoints / assignedPoints) * 100) : 0;

      return { id: p.id, name: p.name, assignedCount, assignedPoints, doneCount, donePoints, pendingPoints, rate };
    });
  }, [childPlayers, missions]);

  // 비교 바 최대값 (배정 포인트 기준)
  const maxAssigned = useMemo(() => {
    return Math.max(...balances.map(b => b.assignedPoints), 1);
  }, [balances]);

  const maxEarned = useMemo(() => {
    return Math.max(...balances.map(b => b.donePoints), 1);
  }, [balances]);

  if (childPlayers.length === 0) return null;

  return (
    <div className={styles.section}>
      <h3 className={styles.sectionTitle}>미션 밸런싱</h3>

      {/* 플레이어별 밸런싱 카드 */}
      <div className={styles.cardGrid}>
        {balances.map(b => (
          <div key={b.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.avatar}>{b.name}</div>
              <div className={styles.cardInfo}>
                <div className={styles.cardName}>{b.name}</div>
              </div>
            </div>

            <div className={styles.statRow}>
              <div className={styles.stat}>
                <div className={styles.statNum}>{b.assignedCount}</div>
                <div className={styles.statLabel}>배정</div>
              </div>
              <div className={styles.stat}>
                <div className={`${styles.statNum} ${styles.statDone}`}>{b.doneCount}</div>
                <div className={styles.statLabel}>완료</div>
              </div>
              <div className={styles.stat}>
                <div className={`${styles.statNum} ${styles.statPending}`}>{b.pendingPoints}P</div>
                <div className={styles.statLabel}>예정</div>
              </div>
            </div>

            <div className={styles.progressTrack}>
              <div className={styles.progressFill} style={{ width: `${b.rate}%` }} />
            </div>
            <div className={styles.rateLabel}>완료율 {b.rate}%</div>
          </div>
        ))}
      </div>

      {/* 포인트 밸런스 비교 바 */}
      <div className={styles.compareCard}>
        <div className={styles.compareTitle}>포인트 밸런스 비교</div>

        <div className={styles.compareGroup}>
          <div className={styles.compareLabel}>배정 포인트 (이번 주기)</div>
          {balances.map(b => (
            <div key={b.id} className={styles.barRow}>
              <span className={styles.barName}>{b.name}</span>
              <div className={styles.barTrack}>
                <div
                  className={`${styles.barFill} ${styles.barAssigned}`}
                  style={{ width: `${(b.assignedPoints / maxAssigned) * 100}%` }}
                >
                  {b.assignedPoints > 0 && <span className={styles.barValue}>{b.assignedPoints}P</span>}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className={styles.compareGroup}>
          <div className={styles.compareLabel}>획득 포인트 (이번 주기)</div>
          {balances.map(b => (
            <div key={b.id} className={styles.barRow}>
              <span className={styles.barName}>{b.name}</span>
              <div className={styles.barTrack}>
                <div
                  className={`${styles.barFill} ${styles.barEarned}`}
                  style={{ width: `${(b.donePoints / maxEarned) * 100}%` }}
                >
                  {b.donePoints > 0 && <span className={styles.barValue}>{b.donePoints}P</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

> **중요:** `childPlayers` 필터 로직을 Step 0에서 확인한 실제 데이터에 맞춰 조정하세요. `players` 테이블에 아빠(id=3), 엄마(id=4)가 있으므로 이들은 밸런싱 비교에서 제외해야 합니다. `role === 'player'`이고 `is_visible`이 true인 항목이면 됩니다. 또는 CLAUDE.md에 기록된 대로 id=1(유빈), id=2(유현)만 대상입니다.

### 2-2. CSS

**파일:** `frontend/src/pages/AdminDashboard/views/DashboardView/components/BalanceSection.module.css`

```css
.section {
  margin-top: 24px;
}

.sectionTitle {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 10px;
}

/* 밸런싱 카드 그리드 */
.cardGrid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.card {
  background: var(--color-background-primary, #fff);
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  border-radius: var(--border-radius-lg, 12px);
  padding: 14px;
}

.cardHeader {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #EEEDFE;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 500;
  color: #534AB7;
}

.cardInfo {
  flex: 1;
}

.cardName {
  font-size: 13px;
  font-weight: 500;
}

/* 통계 3열 */
.statRow {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px;
  margin-bottom: 10px;
}

.stat {
  text-align: center;
}

.statNum {
  font-size: 16px;
  font-weight: 500;
  color: #3C3489;
}

.statDone { color: #27500A; }
.statPending { color: #854F0B; }

.statLabel {
  font-size: 9px;
  color: var(--color-text-secondary, #64748b);
}

/* 진행률 바 */
.progressTrack {
  background: #F1EFE8;
  border-radius: 4px;
  height: 5px;
  overflow: hidden;
}

.progressFill {
  height: 100%;
  background: #639922;
  border-radius: 4px;
  transition: width 0.3s;
}

.rateLabel {
  font-size: 9px;
  color: var(--color-text-secondary, #64748b);
  margin-top: 3px;
}

/* 비교 카드 */
.compareCard {
  background: var(--color-background-primary, #fff);
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  border-radius: var(--border-radius-lg, 12px);
  padding: 14px;
}

.compareTitle {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 12px;
}

.compareGroup {
  margin-bottom: 12px;
}

.compareGroup:last-child {
  margin-bottom: 0;
}

.compareLabel {
  font-size: 10px;
  color: var(--color-text-secondary, #64748b);
  margin-bottom: 5px;
}

.barRow {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 3px;
}

.barName {
  font-size: 11px;
  color: var(--color-text-secondary, #64748b);
  width: 28px;
  flex-shrink: 0;
}

.barTrack {
  flex: 1;
  background: #F1EFE8;
  border-radius: 3px;
  height: 12px;
  overflow: hidden;
}

.barFill {
  height: 100%;
  border-radius: 3px;
  display: flex;
  align-items: center;
  padding-left: 5px;
  min-width: 0;
  transition: width 0.3s;
}

.barAssigned { background: #AFA9EC; }
.barEarned { background: #97C459; }

.barValue {
  font-size: 9px;
  font-weight: 500;
  white-space: nowrap;
}

.barAssigned .barValue { color: #3C3489; }
.barEarned .barValue { color: #173404; }

/* 모바일 */
@media (max-width: 768px) {
  .cardGrid {
    grid-template-columns: 1fr;
  }
}
```

---

## Step 3: DashboardView.tsx 통합

### 3-1. 기존 DashboardView.tsx 수정

> **핵심 원칙:** 기존 스탯 카드 JSX를 **교체**합니다. 기존 카드의 CSS 클래스와 구조를 확인한 뒤, 탭 동작을 추가합니다. 플레이어 요약 테이블은 그대로 유지합니다.

**변경 사항:**

1. `CardDetailTable`, `BalanceSection` import 추가
2. `selectedCard` 상태 추가 (기본값: `null` — 아무 카드도 선택 안 됨. 카드 클릭 시 해당 모드로 전환. 같은 카드 다시 클릭 시 닫힘)
3. 스탯 카드 4종의 **순서 변경**: 총 발행 포인트 → 활성 미션 → 승인 대기 → 이번주 완료
4. 각 카드에 `onClick` 핸들러 + 선택 상태 시각 표시 (border-bottom 악센트 + opacity 변경)
5. 카드 바로 아래에 `CardDetailTable` 조건부 렌더링 (selectedCard !== null일 때만)
6. 기존 플레이어 요약 테이블 **아래에** `BalanceSection` 배치

**의사 코드:**

```tsx
import CardDetailTable from './components/CardDetailTable';
import BalanceSection from './components/BalanceSection';

// 상태 추가
const [selectedCard, setSelectedCard] = useState<'points' | 'active' | 'pending' | 'completed' | null>(null);

// 카드 클릭 핸들러
const handleCardClick = (mode: typeof selectedCard) => {
  setSelectedCard(prev => prev === mode ? null : mode);
};

// 주기 라벨 (cycle.startDate ~ cycle.endDate 포맷)
const cycleLabel = useMemo(() => {
  if (!cycle?.startDate || !cycle?.endDate) return '';
  const fmt = (d: string) => d.replace(/-/g, '.');
  return `${fmt(cycle.startDate)} ~ ${fmt(cycle.endDate)}`;
}, [cycle]);

// 밸런싱에 전달할 아이 플레이어만 필터
const childPlayers = useMemo(() => {
  return players.filter(p => /* Step 0에서 확인한 조건 */);
}, [players]);
```

**JSX 구조:**

```tsx
{/* 스탯 카드 4종 — 순서 변경, 탭화 */}
<div className={styles.statCards}>
  <div
    className={`${styles.statCard} ${styles.statCardPoints} ${selectedCard === 'points' ? styles.statCardSelected : ''}`}
    onClick={() => handleCardClick('points')}
  >
    <div className={styles.statLabel}>총 발행 포인트</div>
    <div className={styles.statValue}>{stats.totalPointsIssued}P</div>
    <div className={styles.statSub}>이번 주기</div>
  </div>
  {/* ... 활성 미션, 승인 대기, 이번주 완료 동일 패턴 */}
</div>

{/* 상세 테이블 (선택된 카드가 있을 때만) */}
{selectedCard && (
  <div className={styles.detailPanel}>
    <CardDetailTable
      mode={selectedCard}
      missions={missions}
      players={players}
      cycleLabel={cycleLabel}
    />
  </div>
)}

{/* 기존 플레이어 요약 테이블 — 그대로 유지 */}
{/* ... 기존 코드 유지 ... */}

{/* 밸런싱 섹션 — 신규 추가 */}
<BalanceSection
  missions={missions}
  players={childPlayers}
/>
```

### 3-2. DashboardView.module.css 추가 클래스

기존 스탯 카드 CSS를 **유지**하되, 아래 클래스를 **추가**합니다:

```css
/* 스탯 카드 탭 효과 */
.statCards {
  /* 기존 grid 유지, border-radius 조정 */
}

.statCard {
  /* 기존 스타일 유지 + 커서 포인터 + 전환 효과 */
  cursor: pointer;
  transition: opacity 0.15s, border-radius 0.15s;
}

/* 선택되지 않은 카드 */
.statCards:has(.statCardSelected) .statCard:not(.statCardSelected) {
  opacity: 0.65;
  border-radius: 12px 12px 0 0;
}

/* 선택된 카드 */
.statCardSelected {
  border-bottom: 3px solid currentColor;
  border-radius: 12px 12px 0 0;
}

/* :has() 미지원 브라우저 폴백 — JS 클래스로 처리 */
.statCardsHasSelection .statCard:not(.statCardSelected) {
  opacity: 0.65;
}

/* 상세 패널 */
.detailPanel {
  background: var(--color-background-primary, #fff);
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  border-top: none;
  border-radius: 0 0 12px 12px;
  margin-bottom: 24px;
}

/* 모바일: 카드 2×2 */
@media (max-width: 768px) {
  .statCards {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

> **주의:** 기존 `.statCard` 클래스에 이미 `border-radius`, `padding`, `background` 등이 정의되어 있을 것입니다. **기존 스타일을 덮어쓰지 마세요.** `cursor: pointer`와 선택 상태 스타일만 추가합니다. Step 0에서 확인한 기존 클래스명을 정확히 사용하세요.
>
> **`:has()` 주의:** CSS `:has()`는 Safari 15.4+, Chrome 105+에서 지원됩니다. NAS에서 접속하는 브라우저가 구버전일 수 있으므로, **JS로 `statCardsHasSelection` 클래스를 토글하는 방식도 병행**하세요:
>
> ```tsx
> <div className={`${styles.statCards} ${selectedCard ? styles.statCardsHasSelection : ''}`}>
> ```

---

## Step 4: 모바일 레이아웃 확인

빌드 후 아래 항목을 Chrome DevTools 모바일 뷰포트(375px)에서 확인하세요:

| # | 항목 | 기대 동작 |
|---|---|---|
| 1 | 스탯 카드 4종 | 2×2 그리드로 배치 |
| 2 | 상세 테이블 (flat) | thead 숨김 + data-label 카드 전환 |
| 3 | 아코디언 그룹 행 | 2행 레이아웃 (배정/완료 정보 줄바꿈) |
| 4 | 밸런싱 카드 | 1열로 쌓임 |
| 5 | 비교 바 | 바 텍스트가 잘리지 않는지 |

---

## Step 5: 빌드 검증

### 5-1. Frontend

```bash
cd frontend && npm run build
# 0 errors, 0 warnings (CSS Module 미사용 클래스 경고 제외)
docker-compose up -d --build frontend
```

### 5-2. 기능 검증 체크리스트

| # | 항목 | 방법 | 기대 |
|---|---|---|---|
| 1 | 카드 순서 | 대시보드 접속 | 총 발행 → 활성 → 승인대기 → 완료 순서 |
| 2 | 카드 클릭 → 상세 표시 | 총 발행 카드 클릭 | 아코디언 테이블 표시, 다른 카드 opacity 낮아짐 |
| 3 | 같은 카드 재클릭 | 총 발행 카드 다시 클릭 | 상세 테이블 닫힘, 모든 카드 opacity 원복 |
| 4 | 다른 카드 클릭 | 활성 미션 카드 클릭 | 상세 테이블이 flat 테이블로 교체됨 |
| 5 | 아코디언 펼치기/접기 | 총 발행 모드에서 그룹 행 클릭 | 미션 상세 드릴다운 표시/숨김 |
| 6 | 배정 대비 완료 비교 | 총 발행 모드 그룹 행 확인 | "배정 3건 25P → 완료 1건 5P (20%)" 형식 |
| 7 | 플레이어 필터 | 셀렉트에서 유빈 선택 | 유빈 미션만 표시 |
| 8 | 빈 상태 | 승인 대기 0건일 때 승인대기 탭 클릭 | "승인 대기 미션이 없습니다" 표시 |
| 9 | 플레이어 요약 테이블 | 상세 테이블 아래 확인 | 기존과 동일하게 유지 |
| 10 | 밸런싱 섹션 | 요약 테이블 아래 확인 | 플레이어 카드 + 비교 바 표시 |
| 11 | 밸런싱 대상 | 아빠/엄마 제외 확인 | 유빈/유현만 표시 |
| 12 | 모바일 375px | DevTools 확인 | 카드 2×2, 테이블 카드 전환, 밸런싱 1열 |
| 13 | 기존 기능 유지 | 다른 View (Mission, Point 등) 접속 | 깨지는 곳 없음 |
| 14 | npm build | 0 errors | 확인 |

---

## Step 6: CLAUDE.md 갱신

### 섹션 15 "Phase 5 이후 핫픽스" 하단에 추가:

```markdown
### P-HOTFIX-DASHBOARD-DETAIL-001 — DashboardView 카드 상세 + 밸런싱
| 작업 | 상태 |
|---|---|
| 스탯 카드 순서 변경: 총 발행 → 활성 → 승인대기 → 완료 | ✅ 완료 |
| 스탯 카드 탭화: 클릭 시 하단 상세 테이블 토글 | ✅ 완료 |
| CardDetailTable.tsx 신규: 4모드 (points/active/pending/completed) | ✅ 완료 |
| points 모드: 일자×플레이어 아코디언, 배정 대비 완료 비교 (달성률%) | ✅ 완료 |
| active/pending/completed 모드: flat 테이블 (일자/이름/미션명/포인트/상태) | ✅ 완료 |
| 플레이어 필터 셀렉트 (각 모드 공통) | ✅ 완료 |
| 모바일 카드 전환: thead 숨김 + data-label 패턴 | ✅ 완료 |
| BalanceSection.tsx 신규: 플레이어별 밸런싱 카드 + 포인트 비교 바 | ✅ 완료 |

#### 확립된 패턴
- **스탯 카드 탭 패턴**: selectedCard 상태로 1개 테이블 영역을 4모드로 전환. 4개 독립 테이블이 아닌 1개 컴포넌트 + 모드 분기
- **아코디언 그룹 집계**: missions[]를 date+player_id로 groupBy → 배정건수/포인트 vs 완료건수/포인트 비교
- **밸런싱 대상**: players에서 아이(role=player, is_visible=true)만 필터. 아빠/엄마 제외
- **:has() 폴백**: JS 클래스 토글로 구브라우저 대응 (`statCardsHasSelection`)
```

### 섹션 5 프로젝트 구조의 DashboardView 하위에 추가:

```
│                   ├── DashboardView/
│                   │   ├── DashboardView.tsx + DashboardView.module.css
│                   │   └── components/
│                   │       ├── PlayerStatusCard, MissionRanking, etc. (기존)
│                   │       ├── CardDetailTable.tsx + CardDetailTable.module.css (신규)
│                   │       └── BalanceSection.tsx + BalanceSection.module.css (신규)
```

---

## 생성/수정 파일 요약

| # | 작업 | 파일 경로 | Step |
|---|---|---|---|
| 1 | **신규** | `DashboardView/components/CardDetailTable.tsx` | 1 |
| 2 | **신규** | `DashboardView/components/CardDetailTable.module.css` | 1 |
| 3 | **신규** | `DashboardView/components/BalanceSection.tsx` | 2 |
| 4 | **신규** | `DashboardView/components/BalanceSection.module.css` | 2 |
| 5 | 수정 | `DashboardView/DashboardView.tsx` | 3 |
| 6 | 수정 | `DashboardView/DashboardView.module.css` | 3 |
| 7 | 수정 | `CLAUDE.md` | 6 |

**신규 4파일, 수정 3파일. BE 변경 0.**

---

## 완료 보고 형식

```
Task ID: P-HOTFIX-DASHBOARD-DETAIL-001
상태: 진행중 → 완료
총소요시간: _분
영향도 분석:
  - BE 변경: 없음
  - 기존 컴포넌트 수정: 없음 (DashboardView.tsx만 수정)
  - 신규 컬럼/API: 없음
생성 파일:
  - CardDetailTable.tsx + .module.css
  - BalanceSection.tsx + .module.css
수정 파일:
  - DashboardView.tsx (카드 탭화 + 신규 컴포넌트 배치)
  - DashboardView.module.css (탭 스타일 + detailPanel + 모바일)
  - CLAUDE.md
빌드 결과:
  - npm run build — 0 errors
Docker:
  - frontend 재빌드 완료
검증:
  - 카드 순서 변경 확인
  - 4모드 탭 전환 정상
  - 아코디언 배정/완료 비교 정상
  - 밸런싱 섹션 표시 정상
  - 모바일 카드 전환 정상
  - 기존 View 영향 없음
```
