# [Claude Code 실행 프롬프트] P-HOTFIX-DASHBOARD-DETAIL-002: 밸런싱 카드 개선 + 세로 바 차트 + 글로벌 주기 배너

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P-HOTFIX-DASHBOARD-DETAIL-002
> **상태:** TODO → 진행중
> **선행 조건:** P-HOTFIX-DASHBOARD-DETAIL-001 완료 (✅ 확인됨)
> **목표:** BalanceSection 카드 필드 2행 분리 + 가로 바→세로 바 차트 전환 + 스탯 카드 주기 라벨을 글로벌 배너로 이동

---

## 🚨 실행 전 필독

### CLAUDE.md를 먼저 읽으세요.

### 핵심 제약
- **BE 변경 없음**: 신규 API, 신규 컬럼, DB 마이그레이션 모두 없음
- **CardDetailTable.tsx 수정 없음**: 이 핫픽스는 BalanceSection + DashboardView만 수정
- **useAdminData 수정 없음**: 기존 데이터 그대로 사용
- **기존 기능 파괴 금지**: 카드 탭 클릭 동작, 아코디언 드릴다운 등 DETAIL-001의 기능 유지

### 변경 요약 3건
1. **BalanceSection 밸런싱 카드**: 3셀 1행 → 2행 분리 (미션 현황 / 포인트 현황) + 구분선 + 서브 라벨 + 셀 배경
2. **BalanceSection 포인트 밸런스 비교**: 가로 바 차트 → 세로 바 차트 (배정/획득 2그룹, 4인 막대)
3. **DashboardView 글로벌 주기 배너**: 개별 카드의 "이번 주기" 제거 → 대시보드 타이틀 우측에 주기 뱃지 + 밸런싱/비교 섹션에 집계 기간 표기

---

## Step 1: BalanceSection.tsx 밸런싱 카드 필드 변경

### 1-1. 카드 내부 구조를 2행으로 분리

현재 카드 내부의 stat 3열 그리드를 찾아서 아래 구조로 교체:

```tsx
{/* ---- 미션 현황 ---- */}
<div className={styles.rowLabel}>미션 현황</div>
<div className={`${styles.statRow} ${styles.statRow2}`}>
  <div className={styles.statCell}>
    <div className={`${styles.statNum} ${styles.statPurple}`}>{b.assignedCount}</div>
    <div className={styles.statCellLabel}>배정</div>
  </div>
  <div className={styles.statCell}>
    <div className={`${styles.statNum} ${styles.statGreen}`}>{b.doneCount}</div>
    <div className={styles.statCellLabel}>완료</div>
  </div>
</div>

{/* 구분선 */}
<div className={styles.separator} />

{/* ---- 포인트 현황 ---- */}
<div className={styles.rowLabel}>포인트 현황</div>
<div className={`${styles.statRow} ${styles.statRow3}`}>
  <div className={styles.statCell}>
    <div className={`${styles.statNum} ${styles.statPurple}`} style={{ fontSize: '13px' }}>
      {b.assignedPoints}P
    </div>
    <div className={styles.statCellLabel}>배정</div>
  </div>
  <div className={styles.statCell}>
    <div className={`${styles.statNum} ${styles.statGreen}`} style={{ fontSize: '13px' }}>
      {b.donePoints}P
    </div>
    <div className={styles.statCellLabel}>획득</div>
  </div>
  <div className={styles.statCell}>
    <div className={`${styles.statNum} ${styles.statAmber}`} style={{ fontSize: '13px' }}>
      {b.pendingPoints}P
    </div>
    <div className={styles.statCellLabel}>남은</div>
  </div>
</div>
```

> **주의:** 기존 `statRow`, `stat`, `statNum`, `statLabel` 등의 클래스명은 Step 0에서 확인한 실제 클래스명에 맞추세요. 위 코드는 구조 가이드이며, 실제 변수명/클래스명은 기존 코드를 따르세요.

### 1-2. pendingPoints 계산 추가

BalanceSection의 PlayerBalance 타입에 `pendingPoints`가 이미 있는지 확인하세요. 없으면 추가:

```typescript
// 밸런싱 집계에서 남은 포인트 계산
const pendingPoints = assignedPoints - donePoints;
```

> `pendingPoints`는 `assignedPoints - donePoints`입니다. active + pending_approval 미션의 포인트 합이 아닌, **배정 총합 - 완료 총합**으로 계산해야 failed 미션의 포인트도 "남은"에 반영되지 않습니다. 단, CYCLE-INTEGRITY에서 이전 주기 미완료는 이미 failed 처리되었으므로, 현재 주기 내에서는 `assignedPoints - donePoints`가 정확합니다.

---

## Step 2: BalanceSection.module.css 카드 스타일 변경

기존 `.statRow`, `.stat` 관련 CSS를 찾아서 아래로 교체/추가:

```css
/* 서브 라벨 (미션 현황 / 포인트 현황) */
.rowLabel {
  font-size: 9px;
  color: var(--color-text-secondary, #64748b);
  margin-bottom: 4px;
  padding-left: 2px;
}

/* 구분선 */
.separator {
  height: 0.5px;
  background: var(--color-border-tertiary, #e2e8f0);
  margin: 8px 0;
}

/* stat 행 공통 */
.statRow {
  display: grid;
  gap: 4px;
}

/* 2열 (배정/완료) */
.statRow2 {
  grid-template-columns: 1fr 1fr;
}

/* 3열 (배정P/획득P/남은P) */
.statRow3 {
  grid-template-columns: 1fr 1fr 1fr;
}

/* 개별 셀 — 배경색으로 구분 */
.statCell {
  text-align: center;
  background: var(--color-background-secondary, #f8fafc);
  border-radius: 6px;
  padding: 5px 4px;
}

.statNum {
  font-size: 14px;
  font-weight: 500;
}

.statCellLabel {
  font-size: 9px;
  color: var(--color-text-secondary, #64748b);
  margin-top: 1px;
}

/* 색상 */
.statPurple { color: #3C3489; }
.statGreen { color: #27500A; }
.statAmber { color: #854F0B; }
```

> **주의:** 기존 CSS에 `.statRow`, `.stat` 등이 있으면 **덮어쓰지 말고** 새 클래스명으로 추가하세요. 기존 클래스가 다른 곳에서 참조될 수 있습니다. 안전한 방법: 기존 클래스를 유지하고, 새 클래스(예: `statRow2`, `statRow3`, `statCell`, `rowLabel`, `separator`)만 추가.

---

## Step 3: BalanceSection 포인트 밸런스 비교 — 가로 바 → 세로 바

### 3-1. 기존 가로 바 JSX 제거

`compareCard` 또는 비교 섹션에서 `.barRow`, `.barTrack`, `.barFill` 등 가로 바 관련 JSX를 **전체 교체**합니다.

### 3-2. 세로 바 차트 JSX로 교체

```tsx
<div className={styles.compareCard}>
  <div className={styles.compareHeader}>
    <div className={styles.compareTitle}>포인트 밸런스 비교</div>
    <div className={styles.compareSub}>집계: {cycleLabel}</div>
  </div>

  <div className={styles.chartRow}>
    {/* 배정 포인트 그룹 */}
    <div className={styles.chartGroup}>
      <div className={styles.chartLabel}>배정 포인트</div>
      <div className={styles.verticalBars}>
        {balances.map(b => (
          <div key={`a-${b.id}`} className={styles.vBar}>
            <div className={styles.vBarValue} style={{ color: '#3C3489' }}>
              {b.assignedPoints > 0 ? `${b.assignedPoints}P` : '0'}
            </div>
            <div
              className={`${styles.vBarBlock} ${styles.vBarPurple}`}
              style={{ height: `${maxAssigned > 0 ? (b.assignedPoints / maxAssigned) * 100 : 0}%`, minHeight: '2px' }}
            />
            <div className={styles.vBarName}>{b.name}</div>
          </div>
        ))}
      </div>
    </div>

    {/* 구분선 */}
    <div className={styles.chartDivider} />

    {/* 획득 포인트 그룹 */}
    <div className={styles.chartGroup}>
      <div className={styles.chartLabel}>획득 포인트</div>
      <div className={styles.verticalBars}>
        {balances.map(b => (
          <div key={`e-${b.id}`} className={styles.vBar}>
            <div className={styles.vBarValue} style={{ color: '#27500A' }}>
              {b.donePoints > 0 ? `${b.donePoints}P` : '0'}
            </div>
            <div
              className={`${styles.vBarBlock} ${styles.vBarGreen}`}
              style={{ height: `${maxEarned > 0 ? (b.donePoints / maxEarned) * 100 : 0}%`, minHeight: '2px' }}
            />
            <div className={styles.vBarName}>{b.name}</div>
          </div>
        ))}
      </div>
    </div>
  </div>
</div>
```

### 3-3. Props에 cycleLabel 추가

BalanceSection의 Props에 `cycleLabel: string`을 추가하세요. DashboardView에서 전달합니다 (Step 5에서 처리).

### 3-4. 세로 바 CSS

기존 가로 바 관련 CSS (`.barRow`, `.barTrack`, `.barFill`, `.barAssigned`, `.barEarned`, `.barName`, `.barValue`)를 **삭제**하고 아래로 교체:

```css
/* 비교 카드 헤더 */
.compareHeader {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 10px;
}

.compareTitle {
  font-size: 12px;
  font-weight: 500;
}

.compareSub {
  font-size: 10px;
  color: var(--color-text-secondary, #64748b);
}

/* 차트 2그룹 가로 배치 */
.chartRow {
  display: flex;
  gap: 16px;
}

.chartGroup {
  flex: 1;
}

.chartLabel {
  font-size: 10px;
  color: var(--color-text-secondary, #64748b);
  margin-bottom: 6px;
  text-align: center;
}

.chartDivider {
  width: 0.5px;
  background: var(--color-border-tertiary, #e2e8f0);
}

/* 세로 바 컨테이너 */
.verticalBars {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 6px;
  height: 100px;
}

/* 개별 바 */
.vBar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  flex: 1;
  max-width: 40px;
}

.vBarValue {
  font-size: 9px;
  font-weight: 500;
}

.vBarBlock {
  width: 100%;
  border-radius: 3px 3px 0 0;
  min-height: 2px;
  transition: height 0.3s;
}

.vBarPurple { background: #AFA9EC; }
.vBarGreen { background: #97C459; }

.vBarName {
  font-size: 9px;
  color: var(--color-text-secondary, #64748b);
}

/* 모바일: 바 높이 축소 */
@media (max-width: 768px) {
  .verticalBars {
    height: 80px;
    gap: 4px;
  }

  .vBarValue { font-size: 8px; }
  .vBarName { font-size: 8px; }
  .chartRow { gap: 12px; }
}
```

---

## Step 4: DashboardView.tsx — 글로벌 주기 배너

### 4-1. 대시보드 타이틀 영역에 주기 뱃지 추가

DashboardView.tsx 상단의 타이틀 JSX를 찾아서 수정:

```tsx
{/* 변경 전 (추정) */}
<h2 className={styles.dashboardTitle}>
  대시보드
  <span className={styles.weekRange}>{getWeekRange()}</span>
</h2>

{/* 변경 후 */}
<div className={styles.dashboardHeader}>
  <h2 className={styles.dashboardTitle}>대시보드</h2>
  <span className={styles.cycleBadge}>이번 주기: {cycleLabel}</span>
</div>
```

> **주의:** `cycleLabel`은 기존에 `useMemo`로 계산하고 있을 것입니다 (DETAIL-001에서 추가됨). 없으면:
> ```tsx
> const cycleLabel = useMemo(() => {
>   if (!cycle?.startDate || !cycle?.endDate) return '';
>   const fmt = (d: string) => d.replace(/-/g, '.');
>   return `${fmt(cycle.startDate)} ~ ${fmt(cycle.endDate)}`;
> }, [cycle]);
> ```

### 4-2. 스탯 카드에서 "이번 주기" 텍스트 제거

4개 스탯 카드 JSX에서 "이번 주기", `statSub` 같은 서브 라벨을 **모두 삭제**하세요:

```tsx
{/* 변경 전 */}
<div className={styles.statCard}>
  <div className={styles.statLabel}>총 발행 포인트</div>
  <div className={styles.statValue}>{stats.totalPointsIssued}P</div>
  <div className={styles.statSub}>이번 주기</div>  {/* ← 삭제 */}
</div>

{/* 변경 후 */}
<div className={styles.statCard}>
  <div className={styles.statLabel}>총 발행 포인트</div>
  <div className={styles.statValue}>{stats.totalPointsIssued}P</div>
</div>
```

4개 카드 모두 동일하게 `statSub` 또는 해당 서브 라벨 행을 제거합니다.

### 4-3. BalanceSection에 cycleLabel 전달

```tsx
<BalanceSection
  missions={missions}
  players={childPlayers}
  cycleLabel={cycleLabel}  {/* 신규 추가 */}
/>
```

### 4-4. 밸런싱 섹션 타이틀에 집계 기간 표기

BalanceSection.tsx 내부의 섹션 타이틀을 수정:

```tsx
{/* 변경 전 */}
<h3 className={styles.sectionTitle}>미션 밸런싱</h3>

{/* 변경 후 */}
<div className={styles.sectionHeader}>
  <h3 className={styles.sectionTitle}>미션 밸런싱</h3>
  <span className={styles.sectionSub}>집계: {cycleLabel}</span>
</div>
```

---

## Step 5: DashboardView.module.css 추가

```css
/* 글로벌 주기 배너 */
.dashboardHeader {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 14px;
}

.cycleBadge {
  font-size: 11px;
  color: #534AB7;
  background: #EEEDFE;
  padding: 3px 10px;
  border-radius: 6px;
}

/* 모바일: 배너 줄바꿈 */
@media (max-width: 768px) {
  .dashboardHeader {
    flex-wrap: wrap;
    gap: 6px;
  }

  .cycleBadge {
    font-size: 10px;
  }
}
```

---

## Step 6: BalanceSection.module.css 추가

섹션 헤더 스타일:

```css
.sectionHeader {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 8px;
}

.sectionSub {
  font-size: 10px;
  color: var(--color-text-secondary, #64748b);
}
```

---

## Step 7: 빌드 검증

```bash
cd frontend && npm run build
# 0 errors 확인
docker-compose up -d --build frontend
```

### 기능 검증 체크리스트

| # | 항목 | 방법 | 기대 |
|---|---|---|---|
| 1 | 글로벌 주기 배너 | 대시보드 접속 | 타이틀 우측에 "이번 주기: YYYY.MM.DD ~ YYYY.MM.DD" 뱃지 |
| 2 | 카드 서브 라벨 제거 | 4개 카드 확인 | "이번 주기" 텍스트 없음 |
| 3 | 카드 탭 동작 유지 | 카드 클릭 | 기존 DETAIL-001 동작 그대로 유지 |
| 4 | 밸런싱 카드 2행 | 유빈 카드 확인 | 1행: 배정 12 / 완료 6, 구분선, 2행: 배정 70P / 획득 35P / 남은 35P |
| 5 | 행 구분 라벨 | 카드 확인 | "미션 현황", "포인트 현황" 서브 라벨 표시 |
| 6 | 셀 배경 | 각 셀 확인 | 배경색으로 카드 배경과 구분 |
| 7 | 세로 바 차트 | 밸런스 비교 확인 | 배정(보라) / 획득(초록) 2그룹, 4인 세로 막대 |
| 8 | 밸런싱 집계 기간 | "미션 밸런싱" 우측 확인 | "집계: YYYY.MM.DD ~ YYYY.MM.DD" 표기 |
| 9 | 비교 차트 집계 기간 | 차트 카드 내부 확인 | 동일 집계 기간 표기 |
| 10 | 밸런싱 카드 2열 | iPad 해상도 확인 | 2열 × 2행 |
| 11 | 밸런싱 카드 1열 | 모바일 375px 확인 | 1열 × 4행 |
| 12 | 세로 바 모바일 | 375px에서 차트 확인 | 높이 80px, 텍스트 8px, 잘리지 않음 |
| 13 | 기존 기능 유지 | 아코디언, 플레이어 필터 확인 | 깨지는 곳 없음 |
| 14 | npm build | 0 errors | 확인 |

---

## Step 8: CLAUDE.md 갱신

### P-HOTFIX-DASHBOARD-DETAIL-001 이력 하단에 추가:

```markdown
### P-HOTFIX-DASHBOARD-DETAIL-002 — 밸런싱 카드 개선 + 세로 바 + 주기 배너
| 작업 | 상태 |
|---|---|
| BalanceSection 카드: 3셀 1행 → 2행 분리 (미션 현황 / 포인트 현황) + 구분선 + 서브 라벨 | ✅ 완료 |
| BalanceSection 카드: 셀 배경색 적용 (statCell → background-secondary) | ✅ 완료 |
| BalanceSection 포인트 밸런스 비교: 가로 바 → 세로 바 차트 (4인 막대) | ✅ 완료 |
| DashboardView: 글로벌 주기 배너 (타이틀 우측 cycleBadge) | ✅ 완료 |
| DashboardView: 스탯 카드 4종에서 "이번 주기" 서브 라벨 제거 | ✅ 완료 |
| BalanceSection: 섹션 타이틀 + 비교 차트에 "집계: 기간" 표기 | ✅ 완료 |

#### 확립된 패턴
- **글로벌 주기 배너**: 개별 컴포넌트가 주기를 각자 표기하지 않고, 대시보드 최상단에 1회 표기. 하위 섹션은 "집계: 기간"으로 참조
- **밸런싱 카드 2행 분리**: 건수(미션 현황)와 포인트(포인트 현황)를 구분선으로 분리. 서브 라벨 + 셀 배경으로 시각 구분
- **세로 바 차트**: 4인 이하 비교에서 가로 바보다 직관적. 2그룹(배정/획득) 나란히 배치
```

---

## 생성/수정 파일 요약

| # | 작업 | 파일 경로 | Step |
|---|---|---|---|
| 1 | 수정 | `DashboardView/components/BalanceSection.tsx` | 1, 3 |
| 2 | 수정 | `DashboardView/components/BalanceSection.module.css` | 2, 3, 6 |
| 3 | 수정 | `DashboardView/DashboardView.tsx` | 4 |
| 4 | 수정 | `DashboardView/DashboardView.module.css` | 5 |
| 5 | 수정 | `CLAUDE.md` | 8 |

**신규 파일 0개. 수정 5파일. BE 변경 0.**

---

## 완료 보고 형식

```
Task ID: P-HOTFIX-DASHBOARD-DETAIL-002
상태: 진행중 → 완료
총소요시간: _분
수정 파일:
  - BalanceSection.tsx (카드 2행 분리 + 세로 바 차트 + cycleLabel prop)
  - BalanceSection.module.css (rowLabel/separator/statCell + 세로 바 CSS + sectionHeader)
  - DashboardView.tsx (글로벌 cycleBadge + 카드 서브 라벨 제거 + cycleLabel 전달)
  - DashboardView.module.css (dashboardHeader + cycleBadge)
  - CLAUDE.md
빌드 결과:
  - npm run build — 0 errors
Docker:
  - frontend 재빌드 완료
검증:
  - 글로벌 주기 배너 표시
  - 카드 서브 라벨 제거 확인
  - 밸런싱 카드 2행 + 구분선 + 서브 라벨
  - 세로 바 차트 정상
  - 집계 기간 표기 (밸런싱 + 비교 차트)
  - 모바일 반응형 정상
  - 기존 기능 유지
```
