# [Claude Code 실행 프롬프트] BUNDLE-B: 모바일 최적화 + 반복미션 관리

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P-HOTFIX-BUNDLE-B-001
> **상태:** TODO → 진행중
> **목표:** iPhone 13 Pro(390px) 해상도 최적화 + Admin 모바일 상단바 변경 + 반복미션 관리 통합 모달

---

## 🚨 실행 전 필독사항

### CLAUDE.md를 먼저 읽으세요

### 아키텍처 철칙 (위반 시 QA Fail)
1. **Thin Controller**: router.py에 비즈니스 로직 0줄
2. **SQL Annotation**: service.py 핵심 함수 상단 RAW SQL 주석 필수
3. **CSS Modules 강제**: 인라인 style={{}} 파일당 5개 미만
4. **Soft Delete**: deleted_at IS NULL 필터링 유지

### 실행 순서
**반드시 Task 순서대로.** B-1(해상도) → B-2(상단바) → B-3(반복미션 모달) → 빌드 검증

---

## Task B-1: 모바일 해상도 최적화 (iPhone 13 Pro 390px)

### 대상: Admin 대시보드 + User 대시보드 전체

### 1-1. 현황 조사

```bash
# viewport 메타태그 확인
grep -rn "viewport" frontend/index.html frontend/src/ --include="*.html" --include="*.tsx"

# 현재 반응형 breakpoint 확인
grep -rn "max-width\|min-width" frontend/src/ --include="*.css" --include="*.module.css" | grep "@media" | sort -u

# overflow-x 설정 확인
grep -rn "overflow-x\|overflow:" frontend/src/styles/ --include="*.css"

# 루트 레이아웃 width 확인
grep -rn "max-width\|min-width\|width:" frontend/src/styles/global.css
```

### 1-2. 글로벌 overflow 방지

**파일: `frontend/src/styles/global.css`**

아래 규칙이 없으면 추가:

```css
html, body, #root {
  max-width: 100vw;
  overflow-x: hidden;
}
```

**파일: `frontend/index.html`**

viewport 메타태그 확인/수정:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

### 1-3. Admin 대시보드 390px 최적화

```bash
# Admin 레이아웃 관련 CSS 모듈 전체 확인
find frontend/src/pages/AdminDashboard -name "*.module.css" -exec echo "=== {} ===" \; -exec grep -n "max-width\|grid-template\|flex-wrap\|width:" {} \;
```

**점검 및 수정 항목:**

1. **사이드바**: 모바일(≤768px)에서 오버레이/숨김 처리 확인. 사이드바가 메인 콘텐츠를 밀어내면 안 됨.

2. **대시보드 카드 그리드**: 390px에서 카드가 가로로 넘치지 않도록 확인.
```css
@media (max-width: 480px) {
  .statGrid {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
}
```

3. **바차트 섹션**: 좌우 차트가 390px에서 세로 스택 확인.
```css
@media (max-width: 480px) {
  .balanceRow {
    flex-direction: column;
  }
}
```

4. **미션관리 액션바**: 버튼 5개가 390px에서 wrap.
```css
@media (max-width: 480px) {
  .actionBar {
    gap: 4px;
  }
  .actionBtn {
    font-size: 10px;
    padding: 4px 8px;
  }
}
```

5. **테이블/리스트**: 가로 넘침이 있는 요소에 `overflow-x: auto` 래퍼 추가.

6. **모달**: 모달 width가 390px에서 화면을 넘지 않도록 `max-width: calc(100vw - 32px)` 확인.

### 1-4. User 대시보드 390px 최적화

```bash
find frontend/src/pages/UserDashboard -name "*.module.css" -exec echo "=== {} ===" \; -exec grep -n "max-width\|grid-template\|flex-wrap\|width:" {} \;
```

**점검 항목:**

1. **프로필 카드**: 사진 + 이름 + 통계 3칸이 390px에서 깨지지 않는지.
2. **미션 카드**: 좌측(미션명) + 우측(포인트) 레이아웃 유지 확인.
3. **주간 날짜 바**: 7일 칩이 390px에서 가로 스크롤 없이 보이는지. 안 되면 칩 크기 축소.

### 1-5. 검증

브라우저 DevTools에서 iPhone 13 Pro (390×844) 시뮬레이션으로 아래 확인:
- Admin 대시보드: 좌우 스크롤 발생하지 않음
- Admin 미션관리: 액션바 + 미션카드 정상 표시
- Admin 채팅: 채팅 영역 정상 표시
- User 대시보드: 좌우 스크롤 발생하지 않음
- 모든 모달: 화면 내에 수용됨

---

## Task B-2: Admin 모바일 상단바 변경

### 변경 대상
모바일 해상도(≤768px)에서 Admin 상단바 우측 아이콘 영역.

### 현재 구조
```
☰ [로고] 포인트 잔치          🏠  💬  🔔  [아]
```

### 변경 후 구조
```
☰ [로고] 포인트 잔치          🏠  💬  🔔  [아]  로그아웃↗
```

### 2-1. 현황 조사

```bash
# 상단바 컴포넌트 위치 확인
grep -rn "header\|topbar\|TopBar\|Header\|navbar\|NavBar" \
  frontend/src/pages/AdminDashboard/ --include="*.tsx" -l

# 로그아웃 버튼 현재 위치 확인
grep -rn "logout\|로그아웃\|Logout" \
  frontend/src/pages/AdminDashboard/ --include="*.tsx" --include="*.css"

# 사이드바에서 로그아웃 확인
grep -rn "logout\|로그아웃" \
  frontend/src/pages/AdminDashboard/components/Sidebar/ --include="*.tsx"
```

### 2-2. 상단바 수정 (모바일)

상단바 컴포넌트를 찾아서, 우측 아이콘 영역에 로그아웃 버튼을 추가하라.

**조건: `@media (max-width: 768px)` 에서만 표시**

**JSX 변경:**

```tsx
{/* 기존 아이콘들 뒤에 추가 */}
<button 
  className={styles.mobileLogout}
  onClick={handleLogout}
  title="로그아웃"
>
  <span className={styles.logoutText}>로그아웃</span>
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4.5 10.5H2.5C2.23478 10.5 1.98043 10.3946 1.79289 10.2071C1.60536 10.0196 1.5 9.76522 1.5 9.5V2.5C1.5 2.23478 1.60536 1.98043 1.79289 1.79289C1.98043 1.60536 2.23478 1.5 2.5 1.5H4.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M8 8.5L10.5 6L8 3.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M10.5 6H4.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
</button>
```

**CSS 추가:**

```css
/* 모바일에서만 로그아웃 버튼 표시 */
.mobileLogout {
  display: none;
}

@media (max-width: 768px) {
  .mobileLogout {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 10px;
    border: none;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.15);
    color: white;
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s;
  }

  .mobileLogout:hover {
    background: rgba(255, 255, 255, 0.25);
  }

  .logoutText {
    font-size: 11px;
  }
}
```

### 2-3. 사이드바 로그아웃 모바일 숨김

사이드바 컴포넌트에서 로그아웃 버튼에 CSS 클래스 추가:

```css
@media (max-width: 768px) {
  .sidebarLogout {
    display: none;
  }
}
```

> **주의:** 사이드바 로그아웃의 기존 클래스명을 확인한 뒤 위 미디어 쿼리를 적용하라. 새 클래스를 추가하는 것이 아니라 기존 클래스에 미디어 쿼리만 추가.

### 2-4. 검증

| # | 항목 | 기대 |
|---|---|---|
| 1 | 모바일(390px) 상단바 | 🏠 💬 🔔 [아] 로그아웃↗ 순서로 보임 |
| 2 | 모바일 사이드바 | 로그아웃 버튼 안 보임 |
| 3 | 태블릿/데스크탑(>768px) | 상단바에 로그아웃 안 보임, 사이드바에 로그아웃 보임 |
| 4 | 로그아웃 클릭 | 기존과 동일하게 로그아웃 동작 |

---

## Task B-3: 반복미션 관리 통합 모달

### 설계 요약

기존 MissionView 액션바의 "🔄 반복 미션 추가" 버튼을 **"🔄 반복미션 관리"** 버튼으로 변경.
클릭 시 통합 관리 모달이 열리고, 그 안에서 조회/추가/편집/일괄삭제를 모두 처리.

### 3-1. BE — 일괄삭제 API 추가

기존 API 확인:
```bash
# 그룹 삭제 API 존재 확인
grep -rn "by-group\|by_group\|batch.*delete\|bulk.*delete" \
  backend/app/domains/ --include="*.py"

# mission_template 라우터 전체 확인
cat backend/app/domains/mission_template/router.py
```

**신규 API: 반복미션 일괄삭제 (템플릿 + 생성된 미션)**

**파일: `backend/app/domains/mission_template/service.py`에 추가**

```python
async def batch_delete_template_and_missions(
    db: AsyncSession,
    template_ids: list[int],
    delete_missions: bool = False,
    mission_date_start: date | None = None,
    mission_date_end: date | None = None,
) -> dict:
    """
    -- [SQL] 반복미션 일괄삭제
    --
    -- 1. 대상 템플릿 조회
    -- SELECT * FROM mission_templates WHERE id IN (:ids) AND deleted_at IS NULL;
    --
    -- 2. 템플릿 소프트 삭제
    -- UPDATE mission_templates SET deleted_at = NOW() WHERE id IN (:ids);
    --
    -- 3. (delete_missions=true) 생성된 미션 소프트 삭제
    --    completed 미션은 제외, pending_approval 포함
    -- UPDATE missions SET deleted_at = NOW()
    -- WHERE player_id IN (템플릿의 player_id들)
    --   AND text IN (템플릿의 text들)
    --   AND date BETWEEN :start AND :end
    --   AND status != 'completed'
    --   AND deleted_at IS NULL;
    """
    from datetime import datetime, timezone

    now_utc = datetime.now(timezone.utc)

    # 1. 대상 템플릿 조회
    stmt = select(MissionTemplate).where(
        MissionTemplate.id.in_(template_ids),
        MissionTemplate.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    templates = result.scalars().all()

    if not templates:
        raise HTTPException(status_code=404, detail="삭제할 템플릿을 찾을 수 없습니다")

    # 2. 템플릿 소프트 삭제
    template_count = 0
    for tmpl in templates:
        tmpl.deleted_at = now_utc
        template_count += 1

    # 3. 생성된 미션 삭제 (옵션)
    mission_count = 0
    pending_count = 0
    if delete_missions and mission_date_start and mission_date_end:
        from app.domains.mission.models import Mission
        from sqlalchemy import and_

        # 각 템플릿의 (player_id, text) 조합으로 매칭
        for tmpl in templates:
            # pending_approval 건수 먼저 조회 (경고용)
            pending_stmt = select(func.count()).where(
                Mission.player_id == tmpl.player_id,
                Mission.text == tmpl.text,
                Mission.date >= mission_date_start,
                Mission.date <= mission_date_end,
                Mission.status == "pending_approval",
                Mission.deleted_at.is_(None),
            )
            pending_result = await db.execute(pending_stmt)
            pending_count += pending_result.scalar() or 0

            # completed 제외, 나머지 삭제
            mission_stmt = (
                update(Mission)
                .where(
                    Mission.player_id == tmpl.player_id,
                    Mission.text == tmpl.text,
                    Mission.date >= mission_date_start,
                    Mission.date <= mission_date_end,
                    Mission.status != "completed",
                    Mission.deleted_at.is_(None),
                )
                .values(deleted_at=now_utc)
            )
            result = await db.execute(mission_stmt)
            mission_count += result.rowcount

    await db.flush()

    return {
        "deleted_templates": template_count,
        "deleted_missions": mission_count,
        "preserved_completed": "completed 미션은 보존됨",
        "pending_deleted": pending_count,
    }
```

**파일: `backend/app/domains/mission_template/schema.py`에 추가**

```python
class BatchDeleteRequest(BaseModel):
    template_ids: list[int]
    delete_missions: bool = False
    mission_date_start: Optional[date] = None
    mission_date_end: Optional[date] = None
```

**파일: `backend/app/domains/mission_template/router.py`에 추가**

```python
@router.post("/api/mission-templates/batch-delete")
async def batch_delete(
    data: BatchDeleteRequest,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """반복미션 일괄삭제 (템플릿 + 선택적으로 생성된 미션)"""
    result = await batch_delete_template_and_missions(
        db,
        template_ids=data.template_ids,
        delete_missions=data.delete_missions,
        mission_date_start=data.mission_date_start,
        mission_date_end=data.mission_date_end,
    )
    await db.commit()
    return result
```

**미리보기 API (삭제 전 영향 범위 확인용):**

```python
@router.post("/api/mission-templates/batch-delete/preview")
async def batch_delete_preview(
    data: BatchDeleteRequest,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """삭제 미리보기: 실제 삭제 없이 영향 범위만 반환"""
    from app.domains.mission.models import Mission

    # 템플릿 건수
    tmpl_stmt = select(func.count()).where(
        MissionTemplate.id.in_(data.template_ids),
        MissionTemplate.deleted_at.is_(None),
    )
    tmpl_result = await db.execute(tmpl_stmt)
    template_count = tmpl_result.scalar() or 0

    mission_count = 0
    completed_count = 0
    pending_count = 0

    if data.delete_missions and data.mission_date_start and data.mission_date_end:
        # 대상 템플릿 조회
        templates = (await db.execute(
            select(MissionTemplate).where(
                MissionTemplate.id.in_(data.template_ids),
                MissionTemplate.deleted_at.is_(None),
            )
        )).scalars().all()

        for tmpl in templates:
            base_where = [
                Mission.player_id == tmpl.player_id,
                Mission.text == tmpl.text,
                Mission.date >= data.mission_date_start,
                Mission.date <= data.mission_date_end,
                Mission.deleted_at.is_(None),
            ]

            # 삭제 대상 (completed 제외)
            active_stmt = select(func.count()).where(
                *base_where, Mission.status != "completed"
            )
            mission_count += (await db.execute(active_stmt)).scalar() or 0

            # 보존 대상 (completed)
            comp_stmt = select(func.count()).where(
                *base_where, Mission.status == "completed"
            )
            completed_count += (await db.execute(comp_stmt)).scalar() or 0

            # 경고 대상 (pending_approval)
            pend_stmt = select(func.count()).where(
                *base_where, Mission.status == "pending_approval"
            )
            pending_count += (await db.execute(pend_stmt)).scalar() or 0

    return {
        "template_count": template_count,
        "mission_count": mission_count,
        "completed_count": completed_count,
        "pending_count": pending_count,
    }
```

### 3-2. FE — "반복미션 관리" 통합 모달

### 액션바 버튼 변경

**파일: MissionView.tsx**

```tsx
// 변경 전
<button className={styles.actionBtn} onClick={() => setTemplateModalOpen(true)}>
  🔄 반복 미션 추가
</button>

// 변경 후
<button className={styles.actionBtn} onClick={() => setTemplateManagerOpen(true)}>
  🔄 반복미션 관리
</button>
```

### TemplateManager 모달 신규 생성

**파일: `frontend/src/pages/AdminDashboard/views/MissionView/components/TemplateManager.tsx`**

이 모달은 2개 서브뷰를 가진다:
- **목록 뷰**: 등록된 반복미션 카드 목록 + 상단 "새 반복미션 추가" 버튼
- **삭제 확인 뷰**: 일괄삭제 모달 (합의된 UI 그대로)

```tsx
import { useState, useEffect, useCallback } from 'react';
import { httpClient } from '../../../../../shared/api/httpClient';
import styles from './TemplateManager.module.css';

interface Template {
  id: number;
  player_id: number;
  text: string;
  point: number;
  day_of_week: number;
  is_active: boolean;
  group_id?: string | null;
}

interface Player {
  id: number;
  name: string;
}

interface TemplateManagerProps {
  isOpen: boolean;
  onClose: () => void;
  players: Player[];
  onOpenCreateModal: () => void;  // 기존 TemplateModal 열기
  onOpenEditModal: (template: Template) => void;  // 기존 TemplateModal 편집모드
}

const DAY_LABELS = ['월', '화', '수', '목', '금', '토', '일'];
const DAY_BITS = [1, 2, 4, 8, 16, 32, 64];

export default function TemplateManager({
  isOpen, onClose, players, onOpenCreateModal, onOpenEditModal
}: TemplateManagerProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);

  // 삭제 모달 상태
  const [deleteMode, setDeleteMode] = useState(false);
  const [deleteTargetIds, setDeleteTargetIds] = useState<number[]>([]);
  const [deleteOption, setDeleteOption] = useState<'template' | 'template_and_missions'>('template');
  const [dateStart, setDateStart] = useState('');
  const [dateEnd, setDateEnd] = useState('');
  const [preview, setPreview] = useState<{
    template_count: number;
    mission_count: number;
    completed_count: number;
    pending_count: number;
  } | null>(null);
  const [deleting, setDeleting] = useState(false);

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await httpClient.get('/api/mission-templates');
      setTemplates(data);
    } catch { /* */ } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) loadTemplates();
  }, [isOpen, loadTemplates]);

  // group_id로 템플릿 그룹핑
  const groupedTemplates = templates.reduce<Record<string, Template[]>>((acc, t) => {
    const key = t.group_id || `single_${t.id}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(t);
    return acc;
  }, {});

  const formatDays = (bitmask: number) => {
    if (bitmask === 127) return '매일';
    const weekdays = 1 | 2 | 4 | 8 | 16; // 31
    if (bitmask === weekdays) return '주중(월~금)';
    return DAY_LABELS.filter((_, i) => bitmask & DAY_BITS[i]).join(', ');
  };

  const getPlayerName = (id: number) => players.find(p => p.id === id)?.name ?? '?';

  // 삭제 미리보기 요청
  const fetchPreview = async () => {
    try {
      const { data } = await httpClient.post('/api/mission-templates/batch-delete/preview', {
        template_ids: deleteTargetIds,
        delete_missions: deleteOption === 'template_and_missions',
        mission_date_start: dateStart || null,
        mission_date_end: dateEnd || null,
      });
      setPreview(data);
    } catch { /* */ }
  };

  // 삭제 실행
  const executeDelete = async () => {
    setDeleting(true);
    try {
      await httpClient.post('/api/mission-templates/batch-delete', {
        template_ids: deleteTargetIds,
        delete_missions: deleteOption === 'template_and_missions',
        mission_date_start: dateStart || null,
        mission_date_end: dateEnd || null,
      });
      setDeleteMode(false);
      setDeleteTargetIds([]);
      setPreview(null);
      await loadTemplates();
    } catch { /* 에러 토스트 */ } finally {
      setDeleting(false);
    }
  };

  // 그룹 삭제 진입
  const openDeleteForGroup = (groupTemplates: Template[]) => {
    setDeleteTargetIds(groupTemplates.map(t => t.id));
    setDeleteMode(true);
    setDeleteOption('template');
    setPreview(null);

    // 날짜 기본값: 이번 주 월~일
    const today = new Date();
    const weekday = today.getDay();
    const mondayOffset = weekday === 0 ? -6 : 1 - weekday;
    const monday = new Date(today);
    monday.setDate(today.getDate() + mondayOffset);
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);
    setDateStart(monday.toISOString().slice(0, 10));
    setDateEnd(sunday.toISOString().slice(0, 10));
  };

  if (!isOpen) return null;

  // --- 삭제 확인 서브뷰 ---
  if (deleteMode) {
    return (
      <div className={styles.overlay} onClick={() => setDeleteMode(false)}>
        <div className={styles.modal} onClick={e => e.stopPropagation()}>
          <div className={styles.header}>
            <h3 className={styles.title}>반복미션 일괄 삭제</h3>
            <button className={styles.closeBtn} onClick={() => setDeleteMode(false)}>✕</button>
          </div>

          <div className={styles.dangerBanner}>
            이 작업은 되돌릴 수 없습니다. 삭제 전 내용을 확인해 주세요.
          </div>

          {/* 삭제 대상 선택 */}
          <div className={styles.section}>
            <label className={styles.sectionLabel}>삭제 대상</label>
            <div className={styles.optionRow}>
              <button
                className={`${styles.optionCard} ${deleteOption === 'template' ? styles.optionActive : ''}`}
                onClick={() => { setDeleteOption('template'); setPreview(null); }}
              >
                <strong>템플릿만</strong>
                <span>향후 자동생성 중단</span>
              </button>
              <button
                className={`${styles.optionCard} ${deleteOption === 'template_and_missions' ? styles.optionActive : ''}`}
                onClick={() => { setDeleteOption('template_and_missions'); setPreview(null); }}
              >
                <strong>템플릿 + 미션</strong>
                <span>생성된 미션도 함께 삭제</span>
              </button>
            </div>
          </div>

          {/* 날짜 범위 (template_and_missions일 때만) */}
          {deleteOption === 'template_and_missions' && (
            <div className={styles.section}>
              <label className={styles.sectionLabel}>미션 삭제 날짜 범위</label>
              <div className={styles.dateRow}>
                <input type="date" value={dateStart} onChange={e => { setDateStart(e.target.value); setPreview(null); }} />
                <span>~</span>
                <input type="date" value={dateEnd} onChange={e => { setDateEnd(e.target.value); setPreview(null); }} />
              </div>
            </div>
          )}

          {/* 미리보기 버튼 */}
          <button className={styles.previewBtn} onClick={fetchPreview}>
            삭제 미리보기
          </button>

          {/* 미리보기 결과 */}
          {preview && (
            <div className={styles.previewBox}>
              <div className={styles.previewRow}>
                <span>삭제될 템플릿</span>
                <span className={styles.dangerText}>{preview.template_count}건</span>
              </div>
              {deleteOption === 'template_and_missions' && (
                <>
                  <div className={styles.previewRow}>
                    <span>삭제될 미션 (active+pending 등)</span>
                    <span className={styles.dangerText}>{preview.mission_count}건</span>
                  </div>
                  {preview.pending_count > 0 && (
                    <div className={styles.warningBanner}>
                      ⚠️ 승인 대기 중 {preview.pending_count}건도 삭제됩니다
                    </div>
                  )}
                  <div className={styles.previewRow}>
                    <span>완료 미션 (보존)</span>
                    <span className={styles.successText}>{preview.completed_count}건</span>
                  </div>
                </>
              )}
            </div>
          )}

          {/* 액션 버튼 */}
          <div className={styles.actionRow}>
            <button className={styles.cancelBtn} onClick={() => setDeleteMode(false)}>취소</button>
            <button
              className={styles.deleteBtn}
              onClick={executeDelete}
              disabled={!preview || deleting}
            >
              {deleting ? '삭제 중...' : '삭제 실행'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- 목록 뷰 ---
  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <h3 className={styles.title}>반복미션 관리</h3>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        <button className={styles.addBtn} onClick={onOpenCreateModal}>
          + 새 반복미션 추가
        </button>

        {loading ? (
          <div className={styles.loadingText}>로딩 중...</div>
        ) : Object.keys(groupedTemplates).length === 0 ? (
          <div className={styles.emptyText}>등록된 반복미션이 없습니다</div>
        ) : (
          <div className={styles.templateList}>
            {Object.entries(groupedTemplates).map(([groupKey, groupTemplates]) => {
              const first = groupTemplates[0];
              const playerNames = groupTemplates.map(t => getPlayerName(t.player_id)).join(', ');
              const isGroup = groupTemplates.length > 1;

              return (
                <div key={groupKey} className={styles.templateCard}>
                  <div className={styles.cardTop}>
                    <div className={styles.cardInfo}>
                      <span className={styles.cardTitle}>{first.text}</span>
                      <span className={styles.cardPoint}>{first.point}P</span>
                    </div>
                    <div className={styles.cardMeta}>
                      <span>{playerNames}{isGroup ? ` (${groupTemplates.length}명)` : ''}</span>
                      <span className={styles.dot} />
                      <span>{formatDays(first.day_of_week)}</span>
                    </div>
                  </div>
                  <div className={styles.cardActions}>
                    {!isGroup && (
                      <button className={styles.editBtn} onClick={() => onOpenEditModal(first)}>편집</button>
                    )}
                    <button className={styles.deleteTrigger} onClick={() => openDeleteForGroup(groupTemplates)}>
                      삭제
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
```

### TemplateManager CSS

**파일: `frontend/src/pages/AdminDashboard/views/MissionView/components/TemplateManager.module.css`**

```css
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--color-background-primary, #fff);
  border-radius: 16px;
  width: 90%;
  max-width: 480px;
  max-height: 80vh;
  overflow-y: auto;
  padding: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.title {
  font-size: 17px;
  font-weight: 600;
  margin: 0;
}

.closeBtn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: var(--color-background-secondary, #f1f5f9);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.addBtn {
  width: 100%;
  padding: 10px;
  border: 2px dashed var(--color-border-tertiary, #e2e8f0);
  border-radius: 10px;
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  margin-bottom: 1rem;
  transition: all 0.15s;
}

.addBtn:hover {
  border-color: #7F77DD;
  color: #534AB7;
  background: #EEEDFE;
}

.templateList {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.templateCard {
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  border-radius: 10px;
  padding: 12px;
}

.cardTop {
  margin-bottom: 8px;
}

.cardInfo {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.cardTitle {
  font-size: 14px;
  font-weight: 500;
}

.cardPoint {
  font-size: 14px;
  font-weight: 600;
  color: #534AB7;
}

.cardMeta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-secondary, #94a3b8);
}

.dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--color-text-secondary, #94a3b8);
}

.cardActions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

.editBtn, .deleteTrigger {
  padding: 4px 12px;
  border-radius: 6px;
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  background: transparent;
  font-size: 12px;
  cursor: pointer;
}

.editBtn:hover {
  background: #EEEDFE;
  color: #534AB7;
}

.deleteTrigger {
  color: #dc2626;
}

.deleteTrigger:hover {
  background: #fef2f2;
}

/* 삭제 모달 */
.dangerBanner {
  background: #fef2f2;
  color: #dc2626;
  font-size: 12px;
  font-weight: 500;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.warningBanner {
  background: #fffbeb;
  color: #d97706;
  font-size: 12px;
  font-weight: 500;
  padding: 8px 10px;
  border-radius: 6px;
  margin-top: 6px;
}

.section {
  margin-bottom: 1rem;
}

.sectionLabel {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  margin-bottom: 6px;
}

.optionRow {
  display: flex;
  gap: 8px;
}

.optionCard {
  flex: 1;
  padding: 10px;
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  text-align: center;
}

.optionCard strong {
  display: block;
  font-size: 13px;
  margin-bottom: 2px;
}

.optionCard span {
  font-size: 11px;
  color: var(--color-text-secondary, #94a3b8);
}

.optionActive {
  border: 2px solid #534AB7;
  background: #EEEDFE;
}

.optionActive strong {
  color: #3C3489;
}

.optionActive span {
  color: #534AB7;
}

.dateRow {
  display: flex;
  gap: 8px;
  align-items: center;
}

.dateRow input {
  flex: 1;
  font-size: 13px;
  padding: 8px;
  border-radius: 8px;
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
}

.dateRow span {
  font-size: 13px;
  color: var(--color-text-secondary, #94a3b8);
}

.previewBtn {
  width: 100%;
  padding: 10px;
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  border-radius: 8px;
  background: var(--color-background-secondary, #f8fafc);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: 1rem;
}

.previewBtn:hover {
  background: #EEEDFE;
}

.previewBox {
  background: var(--color-background-secondary, #f8fafc);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.previewRow {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.previewRow span:first-child {
  color: var(--color-text-secondary, #94a3b8);
}

.dangerText {
  font-weight: 500;
  color: #dc2626;
}

.successText {
  font-weight: 500;
  color: #10b981;
}

.actionRow {
  display: flex;
  gap: 8px;
}

.cancelBtn {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  border: 0.5px solid var(--color-border-tertiary, #e2e8f0);
  background: transparent;
  font-size: 14px;
  cursor: pointer;
}

.deleteBtn {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  border: none;
  background: #dc2626;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.deleteBtn:disabled {
  background: #fca5a5;
  cursor: not-allowed;
}

.loadingText, .emptyText {
  text-align: center;
  padding: 2rem;
  font-size: 13px;
  color: var(--color-text-secondary, #94a3b8);
}

/* 모바일 390px */
@media (max-width: 480px) {
  .modal {
    width: 95%;
    padding: 1rem;
  }

  .optionRow {
    flex-direction: column;
  }

  .dateRow input {
    font-size: 12px;
    padding: 6px;
  }
}
```

### 3-3. MissionView 통합

**파일: MissionView.tsx 수정**

```tsx
// 기존 import에 추가
import TemplateManager from './components/TemplateManager';

// 상태 추가
const [templateManagerOpen, setTemplateManagerOpen] = useState(false);

// 액션바에서 버튼 교체
// 변경 전: "🔄 반복 미션 추가"  onClick={() => setTemplateModalOpen(true)}
// 변경 후: "🔄 반복미션 관리"  onClick={() => setTemplateManagerOpen(true)}

// JSX에 모달 추가 (기존 TemplateModal과 병행)
<TemplateManager
  isOpen={templateManagerOpen}
  onClose={() => setTemplateManagerOpen(false)}
  players={players}
  onOpenCreateModal={() => {
    setTemplateManagerOpen(false);
    setTemplateModalOpen(true);
    setEditingTemplate(null);
  }}
  onOpenEditModal={(template) => {
    setTemplateManagerOpen(false);
    setEditingTemplate(template);
    setTemplateModalOpen(true);
  }}
/>
```

---

## Step 4: 빌드 검증

### 4-1. Backend

```bash
find backend -name "*.py" -exec python -m py_compile {} +
docker-compose up -d --build backend
sleep 5
curl -s http://localhost:8000/api/health
```

### 4-2. Frontend

```bash
cd frontend && npm run build
# 0 errors 확인
docker-compose up -d --build frontend
```

### 4-3. 검증 체크리스트

| # | Task | 항목 | 기대 |
|---|------|------|------|
| 1 | B-1 | iPhone 13 Pro(390px) Admin 좌우 스크롤 | 없음 |
| 2 | B-1 | iPhone 13 Pro(390px) User 좌우 스크롤 | 없음 |
| 3 | B-1 | Admin 모달 390px 수용 | 화면 내 표시 |
| 4 | B-2 | 모바일 상단바 아이콘 순서 | 🏠 💬 🔔 [아] 로그아웃↗ |
| 5 | B-2 | 모바일 사이드바 로그아웃 | 숨김 |
| 6 | B-2 | 태블릿 상단바 | 로그아웃 안 보임 |
| 7 | B-2 | 태블릿 사이드바 로그아웃 | 보임 |
| 8 | B-3 | "반복미션 관리" 버튼 | 클릭 시 관리 모달 열림 |
| 9 | B-3 | 관리 모달 목록 | group_id 그룹핑 + 플레이어명 표시 |
| 10 | B-3 | 새 반복미션 추가 | 기존 TemplateModal 열림 |
| 11 | B-3 | 그룹 삭제 → 삭제 모달 | 삭제 대상 선택 + 날짜 범위 |
| 12 | B-3 | 삭제 미리보기 | 건수 정확히 표시 |
| 13 | B-3 | 삭제 실행 | 템플릿 soft delete + 미션 soft delete (completed 보존) |
| 14 | B-3 | pending_approval 경고 | 있을 경우 경고 표시 |
| 15 | — | py_compile | 0 errors |
| 16 | — | npm build | 0 errors |
| 17 | — | Docker 재빌드 | 정상 기동 |

---

## 생성/수정 파일 요약

| # | Task | 파일 | 작업 |
|---|------|------|------|
| 1 | B-1 | `frontend/src/styles/global.css` | overflow-x hidden 추가 |
| 2 | B-1 | `frontend/index.html` | viewport 메타 확인/수정 |
| 3 | B-1 | Admin 각 CSS 모듈 | 390px 미디어쿼리 추가/수정 |
| 4 | B-1 | User 각 CSS 모듈 | 390px 미디어쿼리 추가/수정 |
| 5 | B-2 | Admin 상단바 컴포넌트 (.tsx) | 모바일 로그아웃 버튼 추가 |
| 6 | B-2 | Admin 상단바 CSS (.module.css) | mobileLogout 스타일 |
| 7 | B-2 | Admin 사이드바 CSS (.module.css) | 모바일 로그아웃 숨김 |
| 8 | B-3 | `backend/app/domains/mission_template/service.py` | batch_delete 함수 추가 |
| 9 | B-3 | `backend/app/domains/mission_template/schema.py` | BatchDeleteRequest 추가 |
| 10 | B-3 | `backend/app/domains/mission_template/router.py` | batch-delete + preview 엔드포인트 |
| 11 | B-3 | `TemplateManager.tsx` (신규) | 관리 통합 모달 |
| 12 | B-3 | `TemplateManager.module.css` (신규) | 모달 스타일 |
| 13 | B-3 | `MissionView.tsx` | 버튼 교체 + TemplateManager 연동 |

---

## 완료 보고 형식

```
제목: BUNDLE-B 모바일 최적화 + 반복미션 관리
수행자: Claude Code
일시: [YYYY-MM-DD HH:MM]
Task ID: P-HOTFIX-BUNDLE-B-001
상태: 진행중 → 완료

총소요시간: XX분
생성 파일: TemplateManager.tsx, TemplateManager.module.css
수정 파일: [위 목록 참조]

검증 결과:
  - B-1 해상도: Admin 390px 좌우스크롤 [없음/있음], User 390px [없음/있음]
  - B-2 상단바: 모바일 [순서 확인], 태블릿 [현행 유지 확인]
  - B-3 반복미션 관리: 목록 [확인], 삭제 미리보기 [확인], 삭제 실행 [확인]
  - py_compile: 0 errors
  - npm build: 0 errors
  - Docker: 정상
```
