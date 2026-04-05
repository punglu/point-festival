# [Claude Code 실행 프롬프트] P-HOTFIX-CYCLE-INTEGRITY-001: 주기 기반 미션 생명주기 정합성

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P-HOTFIX-CYCLE-INTEGRITY-001
> **상태:** TODO → 진행중
> **목표:** 스탯 카드 데이터 범위 통일 + 주기 만료 미션 자동 실패 + 주기 변경 안전망

---

## 🚨 실행 전 필독

### CLAUDE.md를 먼저 읽으세요.

### 아키텍처 철칙 (위반 시 QA Fail)
1. **Thin Controller**: router.py에 비즈니스 로직 0줄. service.py로 위임만.
2. **SQL Annotation**: service.py 핵심 함수 상단 RAW SQL 주석 필수
3. **Soft Delete**: deleted_at IS NULL 필터링 유지
4. **CSS Modules 강제**: 인라인 style={{}} 파일당 5개 미만
5. **AbortController**: useEffect 내 API 호출 시 cleanup abort 필수
6. **Fixed-string 반환은 Thin Controller 위반이 아님** (프로젝트 컨벤션)

### 실행 순서
**Step 0(영향도 분석) → Step 1(BE 주기 유틸) → Step 2(BE Lazy Expiry) → Step 3(BE 미션 필터) → Step 4(BE 주기 변경 가드) → Step 5(FE) → Step 6(빌드 검증)**

---

## Step 0: 운영 영향도 분석 (실행 전 필수)

> **이 Step은 코드를 변경하기 전에 반드시 수행하세요.**
> 분석 결과를 마크다운으로 출력하고, 블로커가 있으면 PM에게 보고 후 대기하세요.

### 0-1. 현재 운영 데이터 현황 파악

아래 명령으로 현재 프로덕션 DB 상태를 로컬 개발 환경에서 확인하세요:

```bash
# 현재 주기 설정 확인
docker exec mc-db psql -U mc_admin -d mc_festival -c \
  "SELECT key, value FROM app_configs WHERE key = 'point_cycle';"

# 현재 active 상태인 전체 미션 수 + 날짜 범위
docker exec mc-db psql -U mc_admin -d mc_festival -c \
  "SELECT COUNT(*), MIN(date), MAX(date) FROM missions WHERE status = 'active' AND deleted_at IS NULL;"

# 현재 pending_approval 상태인 전체 미션 수 + 날짜 범위
docker exec mc-db psql -U mc_admin -d mc_festival -c \
  "SELECT COUNT(*), MIN(date), MAX(date) FROM missions WHERE status = 'pending_approval' AND deleted_at IS NULL;"

# 이번 주기 이전 active 미션 (Lazy Expiry 대상 후보)
# 주기 설정에 따라 WHERE 조건을 조정하세요
docker exec mc-db psql -U mc_admin -d mc_festival -c \
  "SELECT id, player_id, date, text, point, status FROM missions WHERE status IN ('active', 'pending_approval') AND deleted_at IS NULL ORDER BY date ASC LIMIT 20;"

# 활성 반복 미션 템플릿 수
docker exec mc-db psql -U mc_admin -d mc_festival -c \
  "SELECT COUNT(*) FROM mission_templates WHERE is_active = TRUE AND deleted_at IS NULL;"

# daily_points 데이터 범위 확인
docker exec mc-db psql -U mc_admin -d mc_festival -c \
  "SELECT COUNT(*), MIN(date), MAX(date) FROM daily_points WHERE deleted_at IS NULL;"
```

### 0-2. 영향도 판단 기준

위 결과를 바탕으로 아래 항목을 판단하여 보고하세요:

| # | 판단 항목 | 기준 | 블로커 여부 |
|---|---|---|---|
| 1 | Lazy Expiry 대상 미션 수 | 이번 주기 이전 active/pending 미션이 0건이면 영향 없음. 1건 이상이면 자동 failed 처리됨을 PM에게 고지 | 10건 초과 시 PM 확인 필요 |
| 2 | point_cycle 현재 값 | `get_cycle_range` 함수가 해당 값을 지원하는지 확인 | 미지원 값이면 블로커 |
| 3 | mission_templates 테이블 존재 여부 | 테이블 없으면 가드 B 쿼리 실패 | 테이블 없으면 Step 0-3 선행 |
| 4 | getMissions API 시그니처 | 현재 파라미터 확인. 기존 호출처가 date_from/date_to 추가로 깨지지 않는지 | 파라미터가 optional이 아니면 블로커 |
| 5 | FE useAdminData의 getMissions 호출 위치 | 다른 View에서도 getMissions를 호출하는지 확인. MissionView 등에서 전체 조회가 필요할 수 있음 | 2곳 이상 호출 시 주의 |

### 0-3. mission_templates 테이블 미존재 시

만약 테이블이 없으면 아래 마이그레이션을 먼저 실행하세요:

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival << 'SQL'
CREATE TABLE IF NOT EXISTS mission_templates (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    text            VARCHAR(500) NOT NULL,
    point           INTEGER NOT NULL DEFAULT 0,
    day_of_week     INTEGER NOT NULL DEFAULT 127,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_generated_date DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_mission_templates_player ON mission_templates(player_id);
SQL
```

### 0-4. 보고 형식

```
=== P-HOTFIX-CYCLE-INTEGRITY-001 영향도 분석 ===

1. 현재 주기 설정: [weekly/monthly/etc]
2. Lazy Expiry 대상 미션: [N]건
   - 가장 오래된 미션: [날짜] "[미션명]" ([player_name])
   - PM 고지 필요: [예/아니오]
3. 활성 반복 미션 템플릿: [N]건
4. mission_templates 테이블: [존재/미존재]
5. getMissions 호출처: [파일 목록]
6. 블로커: [없음 / 있음 — 상세]

→ 결론: [진행 가능 / PM 확인 후 진행]
```

**블로커가 없으면 Step 1로 진행. 블로커가 있으면 이 보고를 출력하고 대기.**

---

## Step 1: BE — 주기 범위 계산 유틸

### 1-1. mission/service.py에 주기 유틸 함수 추가

기존 `get_week_range`, `is_same_week` 함수가 이미 있을 수 있습니다. 있으면 확장, 없으면 신규 추가하세요.

```python
from datetime import date, timedelta
import calendar


def get_cycle_range(cycle_type: str, ref_date: date) -> tuple[date, date]:
    """
    주기 타입에 따른 시작/종료 날짜 계산.
    지원: daily, weekly, biweekly, monthly, quarterly, yearly
    """
    if cycle_type == "daily":
        return ref_date, ref_date

    elif cycle_type == "weekly":
        start = ref_date - timedelta(days=ref_date.weekday())  # 월요일
        end = start + timedelta(days=6)  # 일요일
        return start, end

    elif cycle_type == "biweekly":
        # ISO week number 기반: 홀수주 시작 → 2주 단위
        start = ref_date - timedelta(days=ref_date.weekday())  # 이번 주 월요일
        iso_week = start.isocalendar()[1]
        if iso_week % 2 == 0:
            start = start - timedelta(weeks=1)  # 홀수주 월요일로 이동
        end = start + timedelta(days=13)  # 2주 뒤 일요일
        return start, end

    elif cycle_type == "monthly":
        start = ref_date.replace(day=1)
        last_day = calendar.monthrange(ref_date.year, ref_date.month)[1]
        end = ref_date.replace(day=last_day)
        return start, end

    elif cycle_type == "quarterly":
        quarter_month = ((ref_date.month - 1) // 3) * 3 + 1  # 1, 4, 7, 10
        start = ref_date.replace(month=quarter_month, day=1)
        end_month = quarter_month + 2
        last_day = calendar.monthrange(ref_date.year, end_month)[1]
        end = ref_date.replace(month=end_month, day=last_day)
        return start, end

    elif cycle_type == "yearly":
        start = ref_date.replace(month=1, day=1)
        end = ref_date.replace(month=12, day=31)
        return start, end

    else:
        # 알 수 없는 주기 → weekly 폴백
        start = ref_date - timedelta(days=ref_date.weekday())
        end = start + timedelta(days=6)
        return start, end
```

> **주의:** 기존 `get_week_range` 함수가 있으면 삭제하지 말고, `get_cycle_range`에서 weekly 분기가 동일 로직을 사용하도록 맞추세요. 기존 `get_week_range` 호출처가 있으면 그대로 유지합니다.

### 1-2. 주기 설정 조회 헬퍼

```python
from app.domains.config.models import AppConfig


async def get_current_cycle(db: AsyncSession) -> str:
    """
    -- [SQL] 현재 주기 설정 조회
    -- SELECT value FROM app_configs WHERE key = 'point_cycle';
    """
    from sqlalchemy import select
    stmt = select(AppConfig.value).where(AppConfig.key == "point_cycle")
    result = await db.execute(stmt)
    value = result.scalar_one_or_none()
    return value or "weekly"  # 미설정 시 weekly 기본값
```

> **참고:** 이 함수가 config 도메인 모델을 직접 import합니다. 엄밀히는 Vertical Domain 원칙 위반이나, 읽기 전용 1컬럼 조회이므로 PM 승인으로 예외 처리합니다. CLAUDE.md에 "설계 예외" 항목으로 기록하세요.

---

## Step 2: BE — Lazy Expiry 구현

### 2-1. mission/service.py에 만료 처리 함수 추가

```python
from datetime import datetime, timezone


async def expire_stale_missions(db: AsyncSession, cycle_end_date: date) -> int:
    """
    -- [SQL] 주기 만료 미션 일괄 실패 처리
    -- UPDATE missions 
    -- SET status = 'failed',
    --     msg = '[시스템] 주기 마감 자동 실패',
    --     updated_at = NOW()
    -- WHERE date <= :cycle_end_date
    --   AND status IN ('active', 'pending_approval')
    --   AND deleted_at IS NULL;
    --
    -- 트리거: Admin 대시보드 조회 시 1회 호출 (Lazy Expiry)
    -- pending_approval 포함 이유: 주기 내 미승인 = 미완료로 간주
    """
    from sqlalchemy import update as sql_update

    now_utc = datetime.now(timezone.utc)

    stmt = (
        sql_update(Mission)
        .where(
            Mission.date < cycle_end_date,
            Mission.status.in_(["active", "pending_approval"]),
            Mission.deleted_at.is_(None),
        )
        .values(
            status="failed",
            msg="[시스템] 주기 마감 자동 실패",
            updated_at=now_utc,
        )
    )
    result = await db.execute(stmt)
    return result.rowcount
```

> **핵심:** `date < cycle_end_date`입니다. `<=`가 아닙니다. 현재 주기의 시작일(cycle_start) 이전 미션만 만료시킵니다. 현재 주기 내 미션은 건드리지 않습니다.
>
> **정정:** 위 쿼리를 다시 확인하세요. 의도는 "현재 주기 시작일 이전의 미완료 미션을 실패 처리"입니다. 따라서 파라미터명은 `cycle_start_date`가 더 정확합니다:

```python
async def expire_stale_missions(db: AsyncSession, cycle_start_date: date) -> int:
    """
    -- [SQL] 주기 만료 미션 일괄 실패 처리
    -- UPDATE missions 
    -- SET status = 'failed',
    --     msg = '[시스템] 주기 마감 자동 실패',
    --     updated_at = NOW()
    -- WHERE date < :cycle_start_date
    --   AND status IN ('active', 'pending_approval')
    --   AND deleted_at IS NULL;
    """
    from sqlalchemy import update as sql_update

    now_utc = datetime.now(timezone.utc)

    stmt = (
        sql_update(Mission)
        .where(
            Mission.date < cycle_start_date,
            Mission.status.in_(["active", "pending_approval"]),
            Mission.deleted_at.is_(None),
        )
        .values(
            status="failed",
            msg="[시스템] 주기 마감 자동 실패",
            updated_at=now_utc,
        )
    )
    result = await db.execute(stmt)
    return result.rowcount
```

### 2-2. admin/router.py에 Lazy Expiry 트리거 삽입

admin/router.py에서 대시보드 데이터를 조회하는 엔드포인트를 찾으세요. 미션 목록을 반환하는 부분 **직전에** 아래를 삽입합니다:

```python
# Lazy Expiry: 현재 주기 이전 미완료 미션 자동 실패 처리
from app.domains.mission.service import expire_stale_missions, get_current_cycle, get_cycle_range
from datetime import date

current_cycle = await get_current_cycle(db)
cycle_start, cycle_end = get_cycle_range(current_cycle, date.today())
expired_count = await expire_stale_missions(db, cycle_start)
if expired_count > 0:
    await db.commit()
```

> **Thin Controller 예외:** 위 코드는 4줄이며 서비스 함수 호출만 수행합니다. 분기 로직이 없으므로 Thin Controller를 위반하지 않습니다. 만약 더 복잡해지면 `admin_dashboard_service.py` 같은 orchestrator로 분리하세요. 현재 수준에서는 불필요합니다.

---

## Step 3: BE — getMissions 주기 범위 필터

### 3-1. 현재 getMissions API 확인

먼저 현재 `admin/router.py`와 `mission/service.py`에서 미션 목록을 조회하는 함수의 시그니처를 확인하세요.

**기대하는 변경:**

mission/service.py의 미션 조회 함수에 optional 파라미터 추가:

```python
async def get_missions(
    db: AsyncSession,
    player_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    signal=None,  # 기존 파라미터 유지
) -> list[MissionResponse]:
    """
    -- [SQL] 미션 목록 조회 (주기 범위 필터 지원)
    -- SELECT * FROM missions
    -- WHERE deleted_at IS NULL
    --   [AND player_id = :player_id]
    --   [AND date >= :date_from]
    --   [AND date <= :date_to]
    -- ORDER BY date DESC, sort_order ASC;
    """
    stmt = select(Mission).where(Mission.deleted_at.is_(None))

    if player_id is not None:
        stmt = stmt.where(Mission.player_id == player_id)
    if date_from is not None:
        stmt = stmt.where(Mission.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Mission.date <= date_to)

    stmt = stmt.order_by(Mission.date.desc(), Mission.sort_order.asc())
    result = await db.execute(stmt)
    return [MissionResponse.model_validate(m) for m in result.scalars().all()]
```

> **핵심:** `date_from`, `date_to`는 모두 optional입니다. 기존 호출처에서 파라미터 없이 호출해도 전체 조회가 유지됩니다. 깨지는 곳 없습니다.

### 3-2. admin/router.py에서 주기 범위 전달

대시보드 미션 조회 시:

```python
missions = await mission_service.get_missions(
    db, 
    date_from=cycle_start, 
    date_to=cycle_end,
)
```

### 3-3. FE 호출처 확인 및 수정

**반드시 확인:** `getMissions`를 호출하는 모든 FE 파일을 검색하세요:

```bash
grep -rn "getMissions\|get_missions\|/api/admin/missions" frontend/src/ --include="*.ts" --include="*.tsx"
```

- `useAdminData.ts` → 주기 범위 전달로 변경
- `MissionView` 등 다른 곳에서 전체 조회가 필요한 경우 → 기존 파라미터 없는 호출 유지 (optional이므로 문제 없음)

---

## Step 4: BE — 주기 변경 가드

### 4-1. config/service.py에 가드 로직 추가

기존 `update_config` 함수를 찾아 `point_cycle` 키 변경 시 가드를 삽입하세요.

```python
from datetime import date
from app.domains.mission.service import get_cycle_range, get_current_cycle


async def validate_cycle_change(db: AsyncSession, new_cycle: str) -> None:
    """
    주기 변경 전 2중 가드 검증.
    실패 시 HTTPException(400) raise.
    
    가드 A: 현재 주기가 종료됐는지 확인
    가드 B: 활성 반복 미션 템플릿이 없는지 확인
    """
    from fastapi import HTTPException

    today = date.today()
    current_cycle = await get_current_cycle(db)

    # 같은 주기로 변경하면 가드 불필요
    if current_cycle == new_cycle:
        return

    # --- 가드 A: 주기 진행 중 잠금 ---
    cycle_start, cycle_end = get_cycle_range(current_cycle, today)
    if today <= cycle_end:
        remaining = (cycle_end - today).days
        raise HTTPException(
            status_code=400,
            detail=f"현재 주기({current_cycle}) 종료까지 {remaining}일 남았습니다. "
                   f"{cycle_end.isoformat()} 이후 변경 가능합니다.",
        )

    # --- 가드 B: 반복 미션 의존성 잠금 ---
    from app.domains.mission_template.models import MissionTemplate
    from sqlalchemy import select, func

    stmt = select(func.count()).select_from(MissionTemplate).where(
        MissionTemplate.is_active.is_(True),
        MissionTemplate.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    template_count = result.scalar() or 0

    if template_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"활성 반복 미션이 {template_count}건 있습니다. "
                   f"반복 미션을 모두 비활성화하거나 삭제한 후 주기를 변경하세요.",
        )
```

### 4-2. update_config에 가드 호출 삽입

기존 `update_config` 함수 (또는 config 관련 PATCH 엔드포인트)를 찾아서, `point_cycle` 키 업데이트 직전에 가드를 호출하세요:

```python
# config 업데이트 로직 내부
if key == "point_cycle":
    await validate_cycle_change(db, new_value)
# ... 기존 업데이트 로직 계속
```

> **주의:** 가드 함수가 `mission_template` 모델을 import합니다. Step 1-2의 `get_current_cycle`과 마찬가지로 읽기 전용 count 쿼리이므로 PM 승인 예외입니다.

---

## Step 5: FE — useAdminData 주기 범위 적용 + ConfigView 가드 UI

### 5-1. useAdminData.ts 수정

`getMissions` 호출을 찾아서 주기 범위 파라미터를 전달하세요:

```typescript
// 변경 전
adminApi.getMissions({}, signal)

// 변경 후
adminApi.getMissions({ 
  date_from: cycle.startDate, 
  date_to: cycle.endDate 
}, signal)
```

> **확인:** `adminApi.getMissions`의 타입 정의도 `date_from?: string`, `date_to?: string` 파라미터를 지원하도록 수정하세요. query string으로 전달됩니다.

### 5-2. adminApi.ts 수정

```typescript
// 변경 전 (추정)
getMissions: (params: Record<string, unknown>, signal?: AbortSignal) =>
  httpClient.get('/api/admin/missions', { params, signal }),

// 변경 후 — 타입 명확화
interface GetMissionsParams {
  player_id?: number;
  date_from?: string;  // YYYY-MM-DD
  date_to?: string;    // YYYY-MM-DD
}

getMissions: (params: GetMissionsParams, signal?: AbortSignal) =>
  httpClient.get('/api/admin/missions', { params, signal }),
```

### 5-3. ConfigView.tsx — 주기 변경 가드 UI

ConfigView에서 `point_cycle` 설정 변경 UI를 찾으세요. select/dropdown 변경 시 BE에 PATCH 요청을 보내는 부분입니다.

**변경 사항:**

1. BE가 400을 반환하면 에러 메시지를 토스트로 표시
2. 주기 select 옆에 현재 주기 잔여일 표시
3. 에러 메시지에 "반복 미션"이 포함되면 MissionView로 이동하는 링크 표시

```tsx
// 주기 변경 핸들러 수정
const handleCycleChange = async (newValue: string) => {
  try {
    await adminApi.updateConfig('point_cycle', newValue);
    // 성공 시 기존 로직
    showToast('주기 설정이 변경되었습니다.', 'success');
    // 데이터 리로드
  } catch (err: any) {
    const detail = err.response?.data?.detail || '주기 변경에 실패했습니다.';
    showToast(detail, 'error');
  }
};
```

**주기 잔여일 표시 (select 옆):**

```tsx
// cycle 정보를 useAdminData 또는 useCycle에서 가져옴
const cycleDaysRemaining = useMemo(() => {
  if (!cycle?.endDate) return null;
  const end = new Date(cycle.endDate + 'T23:59:59');
  const today = new Date();
  const diff = Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  return diff > 0 ? diff : 0;
}, [cycle]);
```

```tsx
{cycleDaysRemaining !== null && cycleDaysRemaining > 0 && (
  <span className={styles.cycleRemaining}>
    현재 주기 종료까지 {cycleDaysRemaining}일
  </span>
)}
```

**CSS (ConfigView.module.css에 추가):**

```css
.cycleRemaining {
  font-size: 11px;
  color: var(--color-text-warning, #854F0B);
  background: var(--color-background-warning, #FAEEDA);
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
}
```

---

## Step 6: 빌드 검증

### 6-1. Backend

```bash
find backend -name "*.py" -exec python -m py_compile {} +
docker-compose up -d --build backend
sleep 5
curl -s http://localhost:8000/api/health
```

### 6-2. Frontend

```bash
cd frontend && npm run build
# 0 errors 확인
docker-compose up -d --build frontend
```

### 6-3. 기능 검증 체크리스트

| # | 항목 | 방법 | 기대 |
|---|---|---|---|
| 1 | Lazy Expiry | 과거 날짜에 active 미션 생성 → Admin 대시보드 접속 | 해당 미션이 failed로 변경, msg에 "[시스템] 주기 마감 자동 실패" |
| 2 | Lazy Expiry — pending | 과거 날짜에 pending_approval 미션 생성 → 대시보드 접속 | failed로 변경 |
| 3 | 현재 주기 미션 보존 | 오늘 날짜의 active 미션 확인 → 대시보드 접속 | active 유지 (변경 없음) |
| 4 | 스탯 카드 범위 통일 | 대시보드 스탯 카드 4종 확인 | 모두 현재 주기 데이터만 표시 |
| 5 | 주기 변경 가드 A | 주기 진행 중 주기 변경 시도 | 400 + "N일 남았습니다" 메시지 |
| 6 | 주기 변경 가드 B | 활성 반복 미션이 있을 때 주기 변경 시도 | 400 + "반복 미션 N건 비활성화" 메시지 |
| 7 | 주기 변경 성공 | 주기 종료 + 반복 미션 없음 → 주기 변경 | 200 성공 |
| 8 | MissionView 전체 조회 | MissionView에서 미션 목록 조회 | 기존처럼 전체 조회 정상 동작 (깨지지 않음) |
| 9 | ConfigView 잔여일 | ConfigView 주기 설정 옆 확인 | 잔여일 뱃지 표시 |
| 10 | ConfigView 에러 토스트 | 가드에 걸렸을 때 UI 확인 | 에러 메시지 토스트 표시 |
| 11 | npm build | 0 errors | 확인 |

---

## Step 7: CLAUDE.md 갱신

아래 내용을 CLAUDE.md에 추가하세요.

### 섹션 15 "Phase 5 이후 핫픽스" 하단에 추가:

```markdown
### P-HOTFIX-CYCLE-INTEGRITY-001 — 주기 기반 미션 생명주기 정합성
| 작업 | 상태 |
|---|---|
| `get_cycle_range()` 주기 유틸 함수 (daily~yearly 지원) | ✅ 완료 |
| `expire_stale_missions()` Lazy Expiry — 이전 주기 active/pending 미션 자동 failed | ✅ 완료 |
| Admin 대시보드 조회 시 Lazy Expiry 트리거 | ✅ 완료 |
| `getMissions` date_from/date_to optional 파라미터 추가 | ✅ 완료 |
| `useAdminData` → 주기 범위로 미션 조회 (스탯 카드 범위 통일) | ✅ 완료 |
| 주기 변경 가드 A: 주기 진행 중 잠금 | ✅ 완료 |
| 주기 변경 가드 B: 활성 반복 미션 의존성 잠금 | ✅ 완료 |
| ConfigView 잔여일 뱃지 + 에러 토스트 | ✅ 완료 |

#### 확립된 패턴
- **Lazy Expiry**: cron 없이 조회 시점에 만료 처리. `expire_stale_missions(db, cycle_start_date)` — 현재 주기 시작일 이전 active/pending 미션 → failed
- **주기 변경 2중 가드**: (A) 주기 진행 중 변경 불가 + (B) 활성 반복 미션 존재 시 변경 불가
- **get_cycle_range**: daily/weekly/biweekly/monthly/quarterly/yearly 지원. 미지원 값은 weekly 폴백
- **설계 예외**: `mission/service.py`에서 `app_configs` 읽기 전용 조회 허용 (PM 승인, Vertical Domain 예외)
```

---

## 생성/수정 파일 요약

| # | 작업 | 파일 경로 | Step |
|---|---|---|---|
| 1 | 수정 | `backend/app/domains/mission/service.py` | Step 1, 2, 3 |
| 2 | 수정 | `backend/app/domains/config/service.py` | Step 4 |
| 3 | 수정 | `backend/app/domains/admin/router.py` | Step 2, 3 |
| 4 | 수정 | `frontend/src/pages/AdminDashboard/hooks/useAdminData.ts` | Step 5 |
| 5 | 수정 | `frontend/src/pages/AdminDashboard/api/adminApi.ts` | Step 5 |
| 6 | 수정 | `frontend/src/pages/AdminDashboard/views/ConfigView/ConfigView.tsx` | Step 5 |
| 7 | 수정 | `frontend/src/pages/AdminDashboard/views/ConfigView/ConfigView.module.css` | Step 5 |
| 8 | 수정 | `CLAUDE.md` | Step 7 |

**신규 파일 0개. 기존 파일 8개 수정.**

---

## 완료 보고 형식

```
Task ID: P-HOTFIX-CYCLE-INTEGRITY-001
상태: 진행중 → 완료
총소요시간: _분
영향도 분석:
  - Lazy Expiry 대상: [N]건 처리됨
  - 블로커: 없음
수정 파일:
  - backend/app/domains/mission/service.py (get_cycle_range, expire_stale_missions, getMissions date 필터)
  - backend/app/domains/config/service.py (validate_cycle_change 가드)
  - backend/app/domains/admin/router.py (Lazy Expiry 트리거 + 주기 범위 전달)
  - frontend useAdminData.ts (주기 범위 파라미터)
  - frontend adminApi.ts (GetMissionsParams 타입)
  - frontend ConfigView.tsx + .module.css (잔여일 뱃지 + 에러 토스트)
  - CLAUDE.md (핫픽스 이력 + 확립된 패턴)
빌드 결과:
  - py_compile — 0 errors
  - npm run build — 0 errors
Docker:
  - backend + frontend 재빌드 완료
검증:
  - Lazy Expiry 동작 확인
  - 스탯 카드 범위 통일 확인
  - 주기 변경 가드 A/B 동작 확인
  - MissionView 전체 조회 기존 동작 유지
  - ConfigView UI 정상
```
