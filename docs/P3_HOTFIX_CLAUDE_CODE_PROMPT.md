# Phase 3 핫픽스 — Claude Code 실행 지시서

> **Phase:** 3 | **유형:** 핫픽스 (Gemini CONDITIONAL PASS 조건 이행)
> **수행자:** Claude Code (Developer)
> **선행:** Phase 3 Codex QA PASS + Gemini 재감사 CONDITIONAL PASS
> **CLAUDE.md 필독 후 작업 시작**

---

## 🚨 실행 규칙

1. 이 문서에 명시된 2개 파일만 수정 — 임의 파일 생성/수정 금지
2. Step 1/Step 2 기존 기능 동작 보존 필수
3. 빌드 검증 후 완료 보고

---

## Task P3-FIX-1: StatDetailModal.tsx 인라인 스타일 → CSS Module 이관

**경로:** `frontend/src/pages/UserDashboard/components/StatDetailModal.tsx`

**문제:** 인라인 `style={{...}}` 15회 사용 → F-3 (CSS Modules 강제) 원칙 위반

**작업:**

1. StatDetailModal.tsx 내 모든 `style={{...}}` 인라인 스타일을 식별
2. 각 인라인 스타일을 의미 있는 CSS Module 클래스로 변환
3. `UserDashboard.module.css` 하단에 해당 클래스 추가
4. StatDetailModal.tsx에서 `styles.클래스명`으로 교체

**네이밍 규칙 (예시):**

| 인라인 용도 | CSS Module 클래스명 |
|---|---|
| 모달 오버레이 배경 | `.statModalOverlay` |
| 모달 박스 컨테이너 | `.statModalBox` |
| 모달 제목 | `.statModalTitle` |
| 통계 항목 행 | `.statModalRow` |
| 통계 라벨 | `.statModalLabel` |
| 통계 값 | `.statModalValue` |
| 닫기 버튼 | `.statModalClose` |
| 구분선 | `.statModalDivider` |
| 소계/합계 행 | `.statModalTotal` |

> 위 네이밍은 예시입니다. 실제 StatDetailModal.tsx 코드를 읽고 인라인 스타일의 용도에 맞게 클래스명을 결정하세요. 핵심 원칙: **인라인 style={{}} 0개 달성**.

**CSS 추가 위치:** `UserDashboard.module.css` 최하단에 섹션 주석과 함께 추가

```css
/* ========================================
   StatDetailModal — 인라인 스타일 CSS Module 이관
   ======================================== */
```

**검증:**
```bash
# 인라인 스타일 잔존 확인 — 0이어야 PASS
grep -c "style={{" frontend/src/pages/UserDashboard/components/StatDetailModal.tsx
# 결과: 0
```

---

## Task P3-FIX-2: useDashboard.ts AbortController 적용

**경로:** `frontend/src/pages/UserDashboard/hooks/useDashboard.ts`

**문제:** 날짜 연타 시 이전 요청 응답이 현재 데이터를 덮어쓰는 Race Condition 리스크

**작업:** `loadDayData`를 호출하는 `useEffect` 내부에 AbortController 패턴 적용

**수정 대상 코드 (현재):**
```typescript
useEffect(() => { loadDayData(); }, [loadDayData]);
```

**수정 후 패턴:**
```typescript
useEffect(() => {
  const abortController = new AbortController();

  const loadData = async () => {
    if (!player) return;
    setLoading(true);
    try {
      const data = await dashboardApi.fetchDayData(
        player.id,
        selectedDate,
        abortController.signal  // signal 전달
      );
      if (!abortController.signal.aborted) {
        setMissions(data.missions);
        setCheers(data.cheers);
        setFeedbacks(data.feedbacks);
        setDeductions(data.deductions);
        setDailyPoint(data.dailyPoint);
      }
    } catch (err) {
      if (!abortController.signal.aborted) {
        console.error('데이터 로드 실패:', err);
      }
    } finally {
      if (!abortController.signal.aborted) {
        setLoading(false);
      }
    }
  };

  loadData();

  return () => {
    abortController.abort();
  };
}, [player, selectedDate]);
```

**dashboardApi.ts 수정 — signal 전달:**

`fetchDayData` 함수에 `signal` 파라미터 추가:

```typescript
fetchDayData: async (playerId: number, date: string, signal?: AbortSignal) => {
  const [missions, cheers, feedbacks, deductions, dailyPoint] = await Promise.all([
    httpClient.get<MissionResponse[]>(`/api/missions`, { params: { player_id: playerId, date }, signal }),
    httpClient.get<CheerResponse[]>(`/api/cheers`, { params: { date }, signal }),
    httpClient.get<FeedbackResponse[]>(`/api/feedbacks`, { params: { player_id: playerId, date }, signal }),
    httpClient.get<DeductionResponse[]>(`/api/deductions`, { params: { player_id: playerId, date }, signal }),
    httpClient.get<DailyPointResponse | null>(`/api/daily-points`, { params: { player_id: playerId, date }, signal }),
  ]);
  // ... 기존 반환 로직 동일
},
```

**주의사항:**
- `loadDayData` useCallback을 제거하고 useEffect 내부 로컬 함수로 변경 (의존성 단순화)
- 기존 `requestApproval`, `proposeMission`, `sendFeedback` 등 액션 함수에서 호출하는 `loadDayData`는 별도 함수로 유지 (AbortController 불필요 — 사용자 명시 액션)
- 액션 후 갱신용 `refreshData` 함수를 별도로 분리할 것

```typescript
// 액션 후 갱신용 (abort 불필요)
const refreshData = useCallback(async () => {
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
    console.error('데이터 갱신 실패:', err);
  } finally {
    setLoading(false);
  }
}, [player, selectedDate]);
```

그리고 기존 `requestApproval`, `proposeMission`, `sendFeedback` 내부의 `loadDayData()` 호출을 `refreshData()`로 교체합니다.

**검증:**
```bash
# AbortController 적용 확인
grep -n "AbortController\|abort\|signal" frontend/src/pages/UserDashboard/hooks/useDashboard.ts
# 결과: AbortController 선언, abort() cleanup, signal.aborted 체크 존재

# dashboardApi signal 파라미터 확인
grep -n "signal" frontend/src/pages/UserDashboard/api/dashboardApi.ts
# 결과: fetchDayData 시그니처에 signal 파라미터 존재
```

---

## Task P3-FIX-3: 빌드 검증

```bash
# 1. Frontend 빌드
cd frontend && npm run build
# 결과: 0 errors

# 2. TypeScript 타입 체크
cd frontend && npx tsc --noEmit
# 결과: 0 errors

# 3. 인라인 스타일 잔존 최종 확인
grep -c "style={{" frontend/src/pages/UserDashboard/components/StatDetailModal.tsx
# 결과: 0

# 4. AbortController 적용 최종 확인
grep -c "AbortController" frontend/src/pages/UserDashboard/hooks/useDashboard.ts
# 결과: 1 이상
```

---

## 완료 보고 형식

```
제목: Phase 3 핫픽스 — Gemini 조건 이행 완료
수행자: Claude Code
일시: [YYYY-MM-DD HH:MM]
Task ID: P3-FIX-1, P3-FIX-2, P3-FIX-3
상태: 진행중 → 완료
수정 파일:
  - frontend/src/pages/UserDashboard/components/StatDetailModal.tsx [수정 — 인라인 스타일 제거]
  - frontend/src/pages/UserDashboard/UserDashboard.module.css [수정 — StatDetailModal 클래스 추가]
  - frontend/src/pages/UserDashboard/hooks/useDashboard.ts [수정 — AbortController 적용]
  - frontend/src/pages/UserDashboard/api/dashboardApi.ts [수정 — signal 파라미터 추가]
빌드 결과: npm build 0 errors / tsc 0 errors
인라인 스타일 잔존: 0개
AbortController 적용: 확인
```

---

*이 문서는 Claude Code 실행 전용입니다. 핫픽스 완료 후 Codex 재QA → Gemini 최종 확인 진행합니다.*
