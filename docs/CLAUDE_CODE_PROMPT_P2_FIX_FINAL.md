# [Claude Code 실행 프롬프트] Phase 2 Core BE 최종 정상화 (P2-FIX-FINAL)

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P2-FIX-001 ~ P2-FIX-004
> **근거:** Codex QA FAIL → Gemini 감사 → Architect 검토 → PM 승인
> **목표:** 4개 영역 수정 + py_compile 45/45 통과

---

## 🚨 수정 범위 (확정)

| # | 영역 | 수정 대상 | 비고 |
|---|---|---|---|
| FIX-001 | Thin Controller 복구 | mission, deduction, notification, config 라우터 | BLOCKER |
| FIX-002 | 미션 상태 머신 | mission/service.py | CRITICAL |
| FIX-003 | 포인트 엔진 고도화 | daily_point/service.py + schema.py | CRITICAL |
| FIX-004 | SQL Annotation 정합성 | feedback, mission service.py 주석 보정 | WARNING |

### 수정하지 않는 것 (확정 제외)
- **AppConfig**: SoftDeleteMixin 미적용 유지 (init.sql에 deleted_at 없음)
- **LoginLog**: SoftDeleteMixin 미적용 유지 (init.sql에 deleted_at 없음)
- **Unified Timeline API**: Phase 3 FE 요구사항 확정 시 재검토

---

## FIX-001: Thin Controller 완벽 이행

### 원칙
router.py에는 **service 호출 1줄 + return**만 존재해야 합니다.
`if not result`, `raise HTTPException` 등 모든 조건문/예외처리는 service.py로 이관합니다.

### 수정 대상 4개 파일

#### 1) mission/router.py → mission/service.py

**router.py 수정 전:**
```python
@router.patch("/{mission_id}", response_model=MissionResponse)
async def edit_mission(mission_id: int, data: MissionUpdate, db: AsyncSession = Depends(get_db)):
    result = await update_mission(db, mission_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    return result

@router.delete("/{mission_id}", status_code=204)
async def remove_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await soft_delete_mission(db, mission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
```

**router.py 수정 후:**
```python
@router.patch("/{mission_id}", response_model=MissionResponse)
async def edit_mission(mission_id: int, data: MissionUpdate, db: AsyncSession = Depends(get_db)):
    """미션 수정 (상태 변경 포함)"""
    return await update_mission(db, mission_id, data)

@router.delete("/{mission_id}", status_code=204)
async def remove_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    """미션 소프트 삭제"""
    return await soft_delete_mission(db, mission_id)
```

**service.py에 추가할 예외 처리:**
```python
from fastapi import HTTPException

# update_mission 내부 — mission이 None일 때:
    if not mission:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")

# soft_delete_mission 내부 — mission이 None일 때:
    if not mission:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
```

> 반환 타입 변경: `update_mission`은 `Optional[MissionResponse]` → `MissionResponse` (None 반환 제거)
> 반환 타입 변경: `soft_delete_mission`은 `bool` → `None` (204 응답이므로 반환값 불필요)

#### 2) deduction/router.py → deduction/service.py

**router.py에서 제거:**
```python
# 아래 조건문 제거
if not deleted:
    raise HTTPException(status_code=404, detail="차감 내역을 찾을 수 없습니다")
```

**service.py `soft_delete_deduction`에 추가:**
```python
from fastapi import HTTPException

    if not deduction:
        raise HTTPException(status_code=404, detail="차감 내역을 찾을 수 없습니다")
```

#### 3) notification/router.py → notification/service.py

**router.py에서 제거:**
```python
# read_one의 조건문 제거
if not success:
    raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
```

**service.py `mark_as_read`에 추가:**
```python
from fastapi import HTTPException

    if not notif:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
```

#### 4) config/router.py → config/service.py

**router.py에서 제거:**
```python
# get_config의 조건문 제거
if not result:
    raise HTTPException(status_code=404, detail=f"설정 키 '{key}'를 찾을 수 없습니다")
```

**service.py `get_config_by_key`에 추가:**
```python
from fastapi import HTTPException

    if not config:
        raise HTTPException(status_code=404, detail=f"설정 키 '{key}'를 찾을 수 없습니다")
```

> `get_config_by_key` 반환 타입: `ConfigResponse | None` → `ConfigResponse`

---

## FIX-002: 미션 상태 머신 도입

### mission/service.py에 상태 전이 규칙 추가

파일 상단에 전이 맵을 정의하고, `update_mission` 함수에서 검증합니다.

```python
# mission/service.py 상단에 추가

# 상태 전이 규칙: {현재 상태: [허용되는 다음 상태]}
VALID_TRANSITIONS: dict[str, list[str]] = {
    "active": ["pending_approval", "failed"],
    "pending_approval": ["completed", "rejected", "active"],  # active 복귀 = 반려 후 재시도
    "proposed": ["active", "rejected"],  # 관리자 승인/거절
    "completed": [],  # 최종 상태
    "failed": ["active"],  # 재도전 허용
    "rejected": [],  # 최종 상태
}


def _validate_status_transition(current: str, new: str) -> None:
    """
    상태 전이 유효성 검사.
    허용되지 않는 전이 시 400 Bad Request를 발생시킵니다.
    """
    if current == new:
        return  # 동일 상태는 허용 (다른 필드만 수정하는 경우)
    allowed = VALID_TRANSITIONS.get(current, [])
    if new not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"상태 전이 불가: '{current}' → '{new}'. 허용: {allowed}"
        )
```

### update_mission 함수 수정

```python
async def update_mission(db: AsyncSession, mission_id: int, data: MissionUpdate) -> MissionResponse:
    """
    -- [SQL] 미션 수정 (상태 전이 검증 포함)
    -- SELECT * FROM missions WHERE id = :id AND deleted_at IS NULL;
    -- UPDATE missions SET text = :text, point = :point, status = :status, ...
    -- WHERE id = :id;
    """
    stmt = select(Mission).where(Mission.id == mission_id, Mission.deleted_at.is_(None))
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)

    # 상태 전이 검증
    if "status" in update_data:
        _validate_status_transition(mission.status, update_data["status"])

    for key, value in update_data.items():
        setattr(mission, key, value)
    await db.commit()
    await db.refresh(mission)
    return MissionResponse.model_validate(mission)
```

---

## FIX-003: 포인트 엔진 고도화

### daily_point/schema.py 변경

기존 `DailyPointUpsert`를 **증감(delta) 기반**으로 변경합니다.

```python
# 기존 DailyPointUpsert 유지 (내부 서비스용) + 새 스키마 추가

class DailyPointAdjust(BaseModel):
    """클라이언트가 보내는 포인트 증감 요청"""
    player_id: int
    date: date
    earned_delta: int = 0   # 획득 증감량 (양수: 추가, 음수: 차감)
    spent_delta: int = 0    # 사용 증감량 (양수: 추가, 음수: 차감)
```

### daily_point/service.py 변경

```python
from fastapi import HTTPException


async def get_daily_point(
    db: AsyncSession, player_id: int, target_date: date
) -> DailyPointResponse | None:
    """
    -- [SQL] 특정 날짜의 일일 포인트 조회
    -- SELECT * FROM daily_points
    -- WHERE player_id = :player_id AND date = :date AND deleted_at IS NULL;
    """
    stmt = select(DailyPoint).where(
        DailyPoint.player_id == player_id,
        DailyPoint.date == target_date,
        DailyPoint.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    dp = result.scalar_one_or_none()
    return DailyPointResponse.model_validate(dp) if dp else None


async def get_daily_points_range(
    db: AsyncSession, player_id: int, start_date: date, end_date: date
) -> list[DailyPointResponse]:
    """
    -- [SQL] 날짜 범위 일일 포인트 조회 (랭킹/합산용)
    -- SELECT * FROM daily_points
    -- WHERE player_id = :player_id AND date BETWEEN :start AND :end AND deleted_at IS NULL
    -- ORDER BY date ASC;
    """
    stmt = (
        select(DailyPoint)
        .where(
            DailyPoint.player_id == player_id,
            DailyPoint.date >= start_date,
            DailyPoint.date <= end_date,
            DailyPoint.deleted_at.is_(None),
        )
        .order_by(DailyPoint.date.asc())
    )
    result = await db.execute(stmt)
    return [DailyPointResponse.model_validate(r) for r in result.scalars().all()]


async def adjust_daily_point(db: AsyncSession, data: DailyPointAdjust) -> DailyPointResponse:
    """
    -- [SQL] 포인트 증감 (서버 측 계산 + Row Lock)
    -- SELECT * FROM daily_points
    -- WHERE player_id = :pid AND date = :date AND deleted_at IS NULL
    -- FOR UPDATE;
    -- 존재: UPDATE daily_points SET earned = earned + :delta_e, spent = spent + :delta_s,
    --        balance = (earned + :delta_e) - (spent + :delta_s) WHERE id = :id;
    -- 미존재: INSERT INTO daily_points (player_id, date, earned, spent, balance)
    --         VALUES (:pid, :date, :delta_e, :delta_s, :delta_e - :delta_s);
    """
    stmt = (
        select(DailyPoint)
        .where(
            DailyPoint.player_id == data.player_id,
            DailyPoint.date == data.date,
            DailyPoint.deleted_at.is_(None),
        )
        .with_for_update()
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.earned = existing.earned + data.earned_delta
        existing.spent = existing.spent + data.spent_delta
        existing.balance = existing.earned - existing.spent
        await db.commit()
        await db.refresh(existing)
        return DailyPointResponse.model_validate(existing)
    else:
        dp = DailyPoint(
            player_id=data.player_id,
            date=data.date,
            earned=max(0, data.earned_delta),
            spent=max(0, data.spent_delta),
            balance=data.earned_delta - data.spent_delta,
        )
        db.add(dp)
        await db.commit()
        await db.refresh(dp)
        return DailyPointResponse.model_validate(dp)
```

### daily_point/router.py 변경

기존 `upsert_daily_point` 엔드포인트를 `adjust_daily_point`로 교체합니다.

```python
from app.domains.daily_point.schema import DailyPointAdjust, DailyPointResponse
from app.domains.daily_point.service import get_daily_point, get_daily_points_range, adjust_daily_point


@router.post("/", response_model=DailyPointResponse, status_code=201)
async def save_point(data: DailyPointAdjust, db: AsyncSession = Depends(get_db)):
    """포인트 증감 (서버 측 계산)"""
    return await adjust_daily_point(db, data)
```

> **중요:** 기존 `DailyPointUpsert` 스키마와 `upsert_daily_point` 함수는 삭제하지 말고 남겨두세요. 
> 내부 서비스 호출(예: 미션 완료 시 자동 포인트 적립)에서 사용될 수 있습니다.
> router에서만 `DailyPointAdjust` + `adjust_daily_point`를 사용합니다.

---

## FIX-004: SQL Annotation 정합성

### feedback/service.py — N+1 쿼리 주석 보정

현재 `get_feedbacks_by_player`는 피드백 목록을 먼저 조회한 후, **각 피드백마다 답글을 개별 조회**하는 N+1 패턴입니다. 
주석을 실제 동작과 일치시킵니다.

```python
async def get_feedbacks_by_player(
    db: AsyncSession, player_id: int, target_date: date
) -> list[FeedbackResponse]:
    """
    -- [SQL] 플레이어의 날짜별 피드백 조회 (N+1 패턴)
    -- Step 1: SELECT * FROM feedbacks
    --         WHERE player_id = :player_id AND date = :date AND deleted_at IS NULL;
    -- Step 2 (per feedback): SELECT * FROM feedback_replies
    --         WHERE feedback_id = :fb_id AND deleted_at IS NULL
    --         ORDER BY created_at ASC;
    -- Note: 데이터량이 소규모(가족 단위)이므로 N+1 허용. 대규모 시 JOIN으로 전환 필요.
    """
```

### mission/service.py — batch_copy_missions 주석 보정

현재 구현은 SELECT 후 Python 루프 INSERT입니다. 주석의 "INSERT ... SELECT" 문구와 불일치합니다.

```python
async def batch_copy_missions(
    db: AsyncSession, player_id: int, from_date: date, to_date: date
) -> list[MissionResponse]:
    """
    -- [SQL] 특정 날짜의 미션을 다른 날짜로 일괄 복제 (Python 루프)
    -- Step 1: SELECT * FROM missions
    --         WHERE player_id = :player_id AND date = :from_date AND deleted_at IS NULL;
    -- Step 2 (per mission): INSERT INTO missions (player_id, date, text, point, sender, status, sort_order)
    --         VALUES (:pid, :to_date, :text, :point, :sender, 'active', :sort_order);
    -- Note: ORM 개별 INSERT 방식. 대량 복제 시 bulk_insert_mappings 전환 고려.
    """
```

---

## 검증 체크리스트

패치 완료 후 아래 항목을 확인합니다:

| # | 검증 항목 | 기대 결과 |
|---|---|---|
| 1 | mission/router.py에 `raise HTTPException` 0건 | `grep -c "HTTPException" backend/app/domains/mission/router.py` → 0 |
| 2 | deduction/router.py에 `raise HTTPException` 0건 | `grep -c "HTTPException" backend/app/domains/deduction/router.py` → 0 |
| 3 | notification/router.py에 `raise HTTPException` 0건 | `grep -c "HTTPException" backend/app/domains/notification/router.py` → 0 |
| 4 | config/router.py에 `raise HTTPException` 0건 | `grep -c "HTTPException" backend/app/domains/config/router.py` → 0 |
| 5 | mission/service.py에 `VALID_TRANSITIONS` 존재 | `grep "VALID_TRANSITIONS" backend/app/domains/mission/service.py` → 1건+ |
| 6 | mission/service.py에 `_validate_status_transition` 존재 | `grep "_validate_status_transition" backend/app/domains/mission/service.py` → 1건+ |
| 7 | daily_point/service.py에 `with_for_update` 존재 | `grep "with_for_update" backend/app/domains/daily_point/service.py` → 1건+ |
| 8 | daily_point/schema.py에 `DailyPointAdjust` 존재 | `grep "DailyPointAdjust" backend/app/domains/daily_point/schema.py` → 1건+ |
| 9 | py_compile 45/45 통과 | `find backend -name "*.py" -exec python -m py_compile {} +` → 0 errors |
| 10 | AppConfig/LoginLog 변경 없음 | `git diff backend/app/domains/config/models.py backend/app/domains/login_log/models.py` → 변경 없음 |

---

## 보고 형식

### 작업 시작
```
제목: Phase 2 Core BE 최종 정상화
수행자: Claude Code
일시: [YYYY-MM-DD HH:MM]
Task ID: P2-FIX-001 ~ P2-FIX-004
상태: TODO → 진행중
목표: Codex QA FAIL 4개 영역 수정 + py_compile 45/45 통과
```

### 작업 완료
```
총소요시간: XX분
Task ID: P2-FIX-001 ~ P2-FIX-004
상태: 진행중 → 완료
수정 파일:
  - backend/app/domains/mission/router.py (HTTPException 제거)
  - backend/app/domains/mission/service.py (HTTPException 이관 + 상태 머신 추가)
  - backend/app/domains/deduction/router.py (HTTPException 제거)
  - backend/app/domains/deduction/service.py (HTTPException 이관)
  - backend/app/domains/notification/router.py (HTTPException 제거)
  - backend/app/domains/notification/service.py (HTTPException 이관)
  - backend/app/domains/config/router.py (HTTPException 제거)
  - backend/app/domains/config/service.py (HTTPException 이관)
  - backend/app/domains/daily_point/schema.py (DailyPointAdjust 추가)
  - backend/app/domains/daily_point/service.py (adjust_daily_point + with_for_update)
  - backend/app/domains/daily_point/router.py (엔드포인트 변경)
  - backend/app/domains/feedback/service.py (SQL 주석 보정)
```
