# Phase 2 설계서 — Core Domains BE (8개 도메인 CRUD)

> **작성자:** Claude Web (Main Architect)
> **작성일:** 2026-03-30
> **대상:** Gemini (Auditor) → 감사 후 Claude Code (Developer) → 실행
> **선행 완료:** Phase 1 (Scaffolding + Auth) — 10/10 Task 완료, QA 34/34 PASS
> **목표:** 나머지 8개 도메인의 BE 완전 구현 (models/schema/service/router)

---

## 🚨 Phase 2 범위 및 제약

### 범위: BE Only
- **생성:** 8개 도메인의 `models.py`, `schema.py`, `service.py`, `router.py`
- **수정:** `all_models.py` (Junction Hub에 8개 모델 등록), `main.py` (8개 라우터 등록)
- **미포함:** FE 코드 일체 (Phase 3~5에서 구현)

### Phase 1에서 이미 완료된 것
- DB: `init.sql`에 11개 테이블 + Seed 이미 존재 (테이블 재생성 불필요)
- BE: auth, player 도메인 완전 구현
- 인프라: Docker 3-Tier, nginx.conf, deploy.sh 완료

### 아키텍처 철칙 (Phase 1과 동일)
1. **Thin Controller**: `router.py`에 비즈니스 로직 0줄
2. **SQL Annotation**: `service.py` 핵심 함수 상단 RAW SQL 주석 필수
3. **Soft Delete**: 물리 삭제 금지, `deleted_at IS NULL` 필터
4. **문자열 기반 FK**: `ForeignKey("players.id")` 형식
5. **Junction Hub**: `all_models.py` import 전용

---

## Part 1. 도메인별 상세 설계

---

### 1. Mission 도메인 (P2-001)

**테이블:** `missions`
**Firebase 원본:** `mc_mission_data/{playerId}/{date}/{missionId}`

#### models.py

```python
from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Mission(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    text = Column(String(500), nullable=False)
    point = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="active")
    sender = Column(String(20), nullable=True)
    msg = Column(Text, nullable=True)
    proposed_by = Column(String(20), nullable=True)
    proposal_reason = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
```

#### schema.py

```python
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class MissionCreate(BaseModel):
    player_id: int
    date: date
    text: str = Field(max_length=500)
    point: int = Field(ge=0)
    sender: Optional[str] = None
    msg: Optional[str] = None
    status: str = "active"
    sort_order: int = 0


class MissionUpdate(BaseModel):
    text: Optional[str] = Field(default=None, max_length=500)
    point: Optional[int] = Field(default=None, ge=0)
    status: Optional[str] = None
    msg: Optional[str] = None
    rejection_reason: Optional[str] = None
    sort_order: Optional[int] = None


class MissionPropose(BaseModel):
    player_id: int
    date: date
    text: str = Field(max_length=500)
    point: int = Field(ge=0)
    proposed_by: str
    proposal_reason: Optional[str] = None


class MissionResponse(BaseModel):
    id: int
    player_id: int
    date: date
    text: str
    point: int
    status: str
    sender: Optional[str]
    msg: Optional[str]
    proposed_by: Optional[str]
    proposal_reason: Optional[str]
    rejection_reason: Optional[str]
    sort_order: int

    model_config = {"from_attributes": True}
```

#### service.py

```python
from datetime import date
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.mission.models import Mission
from app.domains.mission.schema import MissionCreate, MissionUpdate, MissionPropose, MissionResponse


async def get_missions_by_player_date(
    db: AsyncSession, player_id: int, target_date: date
) -> list[MissionResponse]:
    """
    -- [SQL] 특정 플레이어의 날짜별 미션 목록 조회
    -- SELECT * FROM missions
    -- WHERE player_id = :player_id AND date = :date AND deleted_at IS NULL
    -- ORDER BY sort_order ASC, id ASC;
    """
    stmt = (
        select(Mission)
        .where(Mission.player_id == player_id, Mission.date == target_date, Mission.deleted_at.is_(None))
        .order_by(Mission.sort_order.asc(), Mission.id.asc())
    )
    result = await db.execute(stmt)
    return [MissionResponse.model_validate(r) for r in result.scalars().all()]


async def create_mission(db: AsyncSession, data: MissionCreate) -> MissionResponse:
    """
    -- [SQL] 미션 생성
    -- INSERT INTO missions (player_id, date, text, point, sender, msg, status, sort_order, created_at)
    -- VALUES (:player_id, :date, :text, :point, :sender, :msg, :status, :sort_order, NOW());
    """
    mission = Mission(**data.model_dump())
    db.add(mission)
    await db.commit()
    await db.refresh(mission)
    return MissionResponse.model_validate(mission)


async def update_mission(db: AsyncSession, mission_id: int, data: MissionUpdate) -> Optional[MissionResponse]:
    """
    -- [SQL] 미션 수정
    -- UPDATE missions SET text = :text, point = :point, status = :status, ...
    -- WHERE id = :id AND deleted_at IS NULL;
    """
    stmt = select(Mission).where(Mission.id == mission_id, Mission.deleted_at.is_(None))
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(mission, key, value)
    await db.commit()
    await db.refresh(mission)
    return MissionResponse.model_validate(mission)


async def soft_delete_mission(db: AsyncSession, mission_id: int) -> bool:
    """
    -- [SQL] 미션 소프트 삭제
    -- UPDATE missions SET deleted_at = NOW() WHERE id = :id AND deleted_at IS NULL;
    """
    from datetime import datetime, timezone
    stmt = select(Mission).where(Mission.id == mission_id, Mission.deleted_at.is_(None))
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        return False
    mission.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def propose_mission(db: AsyncSession, data: MissionPropose) -> MissionResponse:
    """
    -- [SQL] 아이가 미션 제안
    -- INSERT INTO missions (player_id, date, text, point, status, proposed_by, proposal_reason, ...)
    -- VALUES (:player_id, :date, :text, :point, 'proposed', :proposed_by, :reason, ...);
    """
    mission = Mission(
        **data.model_dump(),
        status="proposed",
    )
    db.add(mission)
    await db.commit()
    await db.refresh(mission)
    return MissionResponse.model_validate(mission)


async def batch_copy_missions(
    db: AsyncSession, player_id: int, from_date: date, to_date: date
) -> list[MissionResponse]:
    """
    -- [SQL] 특정 날짜의 미션을 다른 날짜로 일괄 복제
    -- INSERT INTO missions (player_id, date, text, point, sender, status, sort_order, ...)
    -- SELECT player_id, :to_date, text, point, sender, 'active', sort_order, ...
    -- FROM missions WHERE player_id = :player_id AND date = :from_date AND deleted_at IS NULL;
    """
    source = await get_missions_by_player_date(db, player_id, from_date)
    created = []
    for m in source:
        new_mission = Mission(
            player_id=player_id, date=to_date, text=m.text, point=m.point,
            sender=m.sender, status="active", sort_order=m.sort_order,
        )
        db.add(new_mission)
        created.append(new_mission)
    await db.commit()
    for m in created:
        await db.refresh(m)
    return [MissionResponse.model_validate(m) for m in created]
```

#### router.py

```python
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.mission.schema import MissionCreate, MissionUpdate, MissionPropose, MissionResponse
from app.domains.mission.service import (
    get_missions_by_player_date, create_mission, update_mission,
    soft_delete_mission, propose_mission, batch_copy_missions,
)

router = APIRouter(prefix="/api/missions", tags=["Mission"])


@router.get("/", response_model=list[MissionResponse])
async def list_missions(
    player_id: int = Query(...),
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 미션 목록 조회"""
    return await get_missions_by_player_date(db, player_id, target_date)


@router.post("/", response_model=MissionResponse, status_code=201)
async def add_mission(data: MissionCreate, db: AsyncSession = Depends(get_db)):
    """미션 추가"""
    return await create_mission(db, data)


@router.patch("/{mission_id}", response_model=MissionResponse)
async def edit_mission(mission_id: int, data: MissionUpdate, db: AsyncSession = Depends(get_db)):
    """미션 수정 (상태 변경 포함)"""
    result = await update_mission(db, mission_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    return result


@router.delete("/{mission_id}", status_code=204)
async def remove_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    """미션 소프트 삭제"""
    deleted = await soft_delete_mission(db, mission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")


@router.post("/propose", response_model=MissionResponse, status_code=201)
async def submit_proposal(data: MissionPropose, db: AsyncSession = Depends(get_db)):
    """아이 미션 제안"""
    return await propose_mission(db, data)


@router.post("/copy", response_model=list[MissionResponse], status_code=201)
async def copy_missions(
    player_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """미션 일괄 복제"""
    return await batch_copy_missions(db, player_id, from_date, to_date)
```

---

### 2. Cheer 도메인 (P2-002)

**테이블:** `cheer_messages`
**Firebase 원본:** `mc_cheer_msgs/{date}/{sender}`

#### models.py

```python
from sqlalchemy import Column, String, Integer, Date, Text
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class CheerMessage(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "cheer_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    sender = Column(String(20), nullable=False)  # 'dad' | 'mom'
    message = Column(Text, nullable=False)
```

#### schema.py

```python
from datetime import date
from typing import Optional
from pydantic import BaseModel


class CheerCreate(BaseModel):
    date: date
    sender: str  # 'dad' | 'mom'
    message: str


class CheerUpdate(BaseModel):
    message: Optional[str] = None


class CheerResponse(BaseModel):
    id: int
    date: date
    sender: str
    message: str

    model_config = {"from_attributes": True}
```

#### service.py

```python
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.cheer.models import CheerMessage
from app.domains.cheer.schema import CheerCreate, CheerUpdate, CheerResponse


async def get_cheers_by_date(db: AsyncSession, target_date: date) -> list[CheerResponse]:
    """
    -- [SQL] 날짜별 응원 메시지 조회
    -- SELECT * FROM cheer_messages WHERE date = :date AND deleted_at IS NULL;
    """
    stmt = select(CheerMessage).where(
        CheerMessage.date == target_date, CheerMessage.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    return [CheerResponse.model_validate(r) for r in result.scalars().all()]


async def upsert_cheer(db: AsyncSession, data: CheerCreate) -> CheerResponse:
    """
    -- [SQL] 응원 메시지 Upsert (같은 날짜+sender 조합이면 갱신)
    -- SELECT * FROM cheer_messages WHERE date = :date AND sender = :sender AND deleted_at IS NULL;
    -- 존재: UPDATE cheer_messages SET message = :message WHERE id = :id;
    -- 미존재: INSERT INTO cheer_messages (date, sender, message) VALUES (...);
    """
    stmt = select(CheerMessage).where(
        CheerMessage.date == data.date,
        CheerMessage.sender == data.sender,
        CheerMessage.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.message = data.message
        await db.commit()
        await db.refresh(existing)
        return CheerResponse.model_validate(existing)
    else:
        cheer = CheerMessage(**data.model_dump())
        db.add(cheer)
        await db.commit()
        await db.refresh(cheer)
        return CheerResponse.model_validate(cheer)
```

#### router.py

```python
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.cheer.schema import CheerCreate, CheerResponse
from app.domains.cheer.service import get_cheers_by_date, upsert_cheer

router = APIRouter(prefix="/api/cheers", tags=["Cheer"])


@router.get("/", response_model=list[CheerResponse])
async def list_cheers(target_date: date = Query(..., alias="date"), db: AsyncSession = Depends(get_db)):
    """날짜별 응원 메시지 조회"""
    return await get_cheers_by_date(db, target_date)


@router.post("/", response_model=CheerResponse, status_code=201)
async def save_cheer(data: CheerCreate, db: AsyncSession = Depends(get_db)):
    """응원 메시지 저장 (Upsert)"""
    return await upsert_cheer(db, data)
```

---

### 3. Feedback 도메인 (P2-003)

**테이블:** `feedbacks` + `feedback_replies`
**Firebase 원본:** `mc_feedbacks/{playerId}/{date}`

#### models.py

```python
from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Feedback(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    msg = Column(Text, nullable=False)


class FeedbackReply(Base, SoftDeleteMixin):
    __tablename__ = "feedback_replies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(20), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(TimestampMixin.created_at.copy())
```

> **주의:** `FeedbackReply`는 `updated_at`이 없는 특수 모델 (init.sql 기준). `TimestampMixin` 대신 `created_at`만 직접 정의합니다. 구현 시 init.sql 스키마를 정확히 따르세요.

#### schema.py

```python
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    player_id: int
    date: date
    msg: str


class FeedbackReplyCreate(BaseModel):
    feedback_id: int
    sender: str
    text: str


class FeedbackReplyResponse(BaseModel):
    id: int
    feedback_id: int
    sender: str
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackResponse(BaseModel):
    id: int
    player_id: int
    date: date
    msg: str
    replies: list[FeedbackReplyResponse] = []

    model_config = {"from_attributes": True}
```

#### service.py

```python
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.feedback.models import Feedback, FeedbackReply
from app.domains.feedback.schema import (
    FeedbackCreate, FeedbackReplyCreate,
    FeedbackResponse, FeedbackReplyResponse,
)


async def get_feedbacks_by_player(
    db: AsyncSession, player_id: int, target_date: date
) -> list[FeedbackResponse]:
    """
    -- [SQL] 플레이어의 날짜별 피드백 + 답글 조회
    -- SELECT f.*, fr.* FROM feedbacks f
    -- LEFT JOIN feedback_replies fr ON fr.feedback_id = f.id AND fr.deleted_at IS NULL
    -- WHERE f.player_id = :player_id AND f.date = :date AND f.deleted_at IS NULL;
    """
    stmt = select(Feedback).where(
        Feedback.player_id == player_id,
        Feedback.date == target_date,
        Feedback.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    feedbacks = result.scalars().all()

    response = []
    for fb in feedbacks:
        reply_stmt = select(FeedbackReply).where(
            FeedbackReply.feedback_id == fb.id,
            FeedbackReply.deleted_at.is_(None),
        ).order_by(FeedbackReply.created_at.asc())
        reply_result = await db.execute(reply_stmt)
        replies = [FeedbackReplyResponse.model_validate(r) for r in reply_result.scalars().all()]
        fb_data = FeedbackResponse.model_validate(fb)
        fb_data.replies = replies
        response.append(fb_data)
    return response


async def create_feedback(db: AsyncSession, data: FeedbackCreate) -> FeedbackResponse:
    """
    -- [SQL] 피드백(답장) 생성
    -- INSERT INTO feedbacks (player_id, date, msg, created_at) VALUES (..., NOW());
    """
    feedback = Feedback(**data.model_dump())
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return FeedbackResponse.model_validate(feedback)


async def add_reply(db: AsyncSession, data: FeedbackReplyCreate) -> FeedbackReplyResponse:
    """
    -- [SQL] 피드백 답글 추가
    -- INSERT INTO feedback_replies (feedback_id, sender, text, created_at) VALUES (..., NOW());
    """
    reply = FeedbackReply(**data.model_dump())
    db.add(reply)
    await db.commit()
    await db.refresh(reply)
    return FeedbackReplyResponse.model_validate(reply)
```

#### router.py

```python
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.feedback.schema import (
    FeedbackCreate, FeedbackReplyCreate,
    FeedbackResponse, FeedbackReplyResponse,
)
from app.domains.feedback.service import get_feedbacks_by_player, create_feedback, add_reply

router = APIRouter(prefix="/api/feedbacks", tags=["Feedback"])


@router.get("/", response_model=list[FeedbackResponse])
async def list_feedbacks(
    player_id: int = Query(...),
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 피드백 + 답글 조회"""
    return await get_feedbacks_by_player(db, player_id, target_date)


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(data: FeedbackCreate, db: AsyncSession = Depends(get_db)):
    """피드백 작성"""
    return await create_feedback(db, data)


@router.post("/replies", response_model=FeedbackReplyResponse, status_code=201)
async def submit_reply(data: FeedbackReplyCreate, db: AsyncSession = Depends(get_db)):
    """피드백 답글 추가"""
    return await add_reply(db, data)
```

---

### 4. Deduction 도메인 (P2-004)

**테이블:** `deductions`
**Firebase 원본:** `mc_deductions/{playerId}/{date}/{id}`

#### models.py

```python
from sqlalchemy import Column, String, Integer, Date, ForeignKey
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Deduction(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "deductions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    reason = Column(String(300), nullable=False)
    amount = Column(Integer, nullable=False)
```

#### schema.py

```python
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class DeductionCreate(BaseModel):
    player_id: int
    date: date
    reason: str = Field(max_length=300)
    amount: int = Field(gt=0)


class DeductionResponse(BaseModel):
    id: int
    player_id: int
    date: date
    reason: str
    amount: int

    model_config = {"from_attributes": True}
```

#### service.py

```python
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.deduction.models import Deduction
from app.domains.deduction.schema import DeductionCreate, DeductionResponse


async def get_deductions_by_player_date(
    db: AsyncSession, player_id: int, target_date: date
) -> list[DeductionResponse]:
    """
    -- [SQL] 플레이어의 날짜별 차감 내역 조회
    -- SELECT * FROM deductions
    -- WHERE player_id = :player_id AND date = :date AND deleted_at IS NULL
    -- ORDER BY id ASC;
    """
    stmt = (
        select(Deduction)
        .where(Deduction.player_id == player_id, Deduction.date == target_date, Deduction.deleted_at.is_(None))
        .order_by(Deduction.id.asc())
    )
    result = await db.execute(stmt)
    return [DeductionResponse.model_validate(r) for r in result.scalars().all()]


async def create_deduction(db: AsyncSession, data: DeductionCreate) -> DeductionResponse:
    """
    -- [SQL] 차감 내역 생성
    -- INSERT INTO deductions (player_id, date, reason, amount, created_at) VALUES (..., NOW());
    """
    deduction = Deduction(**data.model_dump())
    db.add(deduction)
    await db.commit()
    await db.refresh(deduction)
    return DeductionResponse.model_validate(deduction)


async def soft_delete_deduction(db: AsyncSession, deduction_id: int) -> bool:
    """
    -- [SQL] 차감 소프트 삭제
    -- UPDATE deductions SET deleted_at = NOW() WHERE id = :id AND deleted_at IS NULL;
    """
    from datetime import datetime, timezone
    stmt = select(Deduction).where(Deduction.id == deduction_id, Deduction.deleted_at.is_(None))
    result = await db.execute(stmt)
    deduction = result.scalar_one_or_none()
    if not deduction:
        return False
    deduction.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return True
```

#### router.py

```python
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.deduction.schema import DeductionCreate, DeductionResponse
from app.domains.deduction.service import get_deductions_by_player_date, create_deduction, soft_delete_deduction

router = APIRouter(prefix="/api/deductions", tags=["Deduction"])


@router.get("/", response_model=list[DeductionResponse])
async def list_deductions(
    player_id: int = Query(...),
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 차감 내역 조회"""
    return await get_deductions_by_player_date(db, player_id, target_date)


@router.post("/", response_model=DeductionResponse, status_code=201)
async def add_deduction(data: DeductionCreate, db: AsyncSession = Depends(get_db)):
    """차감 내역 추가"""
    return await create_deduction(db, data)


@router.delete("/{deduction_id}", status_code=204)
async def remove_deduction(deduction_id: int, db: AsyncSession = Depends(get_db)):
    """차감 소프트 삭제"""
    deleted = await soft_delete_deduction(db, deduction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="차감 내역을 찾을 수 없습니다")
```

---

### 5. DailyPoint 도메인 (P2-005)

**테이블:** `daily_points`
**Firebase 원본:** `mc_daily_points/{playerId}/{date}`

#### models.py

```python
from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class DailyPoint(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "daily_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    earned = Column(Integer, nullable=False, default=0)
    spent = Column(Integer, nullable=False, default=0)
    balance = Column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("player_id", "date"),)
```

#### schema.py

```python
from datetime import date
from pydantic import BaseModel


class DailyPointUpsert(BaseModel):
    player_id: int
    date: date
    earned: int = 0
    spent: int = 0
    balance: int = 0


class DailyPointResponse(BaseModel):
    id: int
    player_id: int
    date: date
    earned: int
    spent: int
    balance: int

    model_config = {"from_attributes": True}
```

#### service.py

```python
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.daily_point.models import DailyPoint
from app.domains.daily_point.schema import DailyPointUpsert, DailyPointResponse


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


async def upsert_daily_point(db: AsyncSession, data: DailyPointUpsert) -> DailyPointResponse:
    """
    -- [SQL] 일일 포인트 Upsert
    -- SELECT * FROM daily_points WHERE player_id = :pid AND date = :date AND deleted_at IS NULL;
    -- 존재: UPDATE daily_points SET earned=:e, spent=:s, balance=:b WHERE id = :id;
    -- 미존재: INSERT INTO daily_points (player_id, date, earned, spent, balance) VALUES (...);
    """
    stmt = select(DailyPoint).where(
        DailyPoint.player_id == data.player_id,
        DailyPoint.date == data.date,
        DailyPoint.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.earned = data.earned
        existing.spent = data.spent
        existing.balance = data.balance
        await db.commit()
        await db.refresh(existing)
        return DailyPointResponse.model_validate(existing)
    else:
        dp = DailyPoint(**data.model_dump())
        db.add(dp)
        await db.commit()
        await db.refresh(dp)
        return DailyPointResponse.model_validate(dp)
```

#### router.py

```python
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.daily_point.schema import DailyPointUpsert, DailyPointResponse
from app.domains.daily_point.service import get_daily_point, get_daily_points_range, upsert_daily_point

router = APIRouter(prefix="/api/daily-points", tags=["DailyPoint"])


@router.get("/", response_model=DailyPointResponse | None)
async def get_point(
    player_id: int = Query(...),
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """특정 날짜 일일 포인트 조회"""
    return await get_daily_point(db, player_id, target_date)


@router.get("/range", response_model=list[DailyPointResponse])
async def get_points_range(
    player_id: int = Query(...),
    start_date: date = Query(..., alias="start"),
    end_date: date = Query(..., alias="end"),
    db: AsyncSession = Depends(get_db),
):
    """날짜 범위 포인트 조회"""
    return await get_daily_points_range(db, player_id, start_date, end_date)


@router.post("/", response_model=DailyPointResponse, status_code=201)
async def save_point(data: DailyPointUpsert, db: AsyncSession = Depends(get_db)):
    """일일 포인트 저장 (Upsert)"""
    return await upsert_daily_point(db, data)
```

---

### 6. Notification 도메인 (P2-006)

**테이블:** `notifications`
**Firebase 원본:** `mc_notifications/{id}`

#### models.py

```python
from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey
from app.models.base import Base, SoftDeleteMixin

# notifications 테이블에는 updated_at이 없음 (init.sql 기준)
from sqlalchemy import func
from sqlalchemy.types import TIMESTAMP


class Notification(Base, SoftDeleteMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(30), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
```

#### schema.py

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationCreate(BaseModel):
    type: str
    player_id: Optional[int] = None
    title: str
    body: Optional[str] = None


class NotificationResponse(BaseModel):
    id: int
    type: str
    player_id: Optional[int]
    title: str
    body: Optional[str]
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

#### service.py

```python
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.notification.models import Notification
from app.domains.notification.schema import NotificationCreate, NotificationResponse


async def get_unread_notifications(db: AsyncSession) -> list[NotificationResponse]:
    """
    -- [SQL] 읽지 않은 알림 목록 조회
    -- SELECT * FROM notifications
    -- WHERE is_read = FALSE AND deleted_at IS NULL
    -- ORDER BY created_at DESC;
    """
    stmt = (
        select(Notification)
        .where(Notification.is_read.is_(False), Notification.deleted_at.is_(None))
        .order_by(Notification.created_at.desc())
    )
    result = await db.execute(stmt)
    return [NotificationResponse.model_validate(r) for r in result.scalars().all()]


async def create_notification(db: AsyncSession, data: NotificationCreate) -> NotificationResponse:
    """
    -- [SQL] 알림 생성
    -- INSERT INTO notifications (type, player_id, title, body, created_at) VALUES (..., NOW());
    """
    notif = Notification(**data.model_dump())
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return NotificationResponse.model_validate(notif)


async def mark_as_read(db: AsyncSession, notification_id: int) -> bool:
    """
    -- [SQL] 알림 읽음 처리
    -- UPDATE notifications SET is_read = TRUE WHERE id = :id AND deleted_at IS NULL;
    """
    stmt = select(Notification).where(
        Notification.id == notification_id, Notification.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    notif = result.scalar_one_or_none()
    if not notif:
        return False
    notif.is_read = True
    await db.commit()
    return True


async def mark_all_as_read(db: AsyncSession) -> int:
    """
    -- [SQL] 전체 알림 읽음 처리
    -- UPDATE notifications SET is_read = TRUE WHERE is_read = FALSE AND deleted_at IS NULL;
    """
    stmt = (
        update(Notification)
        .where(Notification.is_read.is_(False), Notification.deleted_at.is_(None))
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
```

#### router.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.notification.schema import NotificationCreate, NotificationResponse
from app.domains.notification.service import (
    get_unread_notifications, create_notification, mark_as_read, mark_all_as_read,
)

router = APIRouter(prefix="/api/notifications", tags=["Notification"])


@router.get("/", response_model=list[NotificationResponse])
async def list_unread(db: AsyncSession = Depends(get_db)):
    """읽지 않은 알림 목록"""
    return await get_unread_notifications(db)


@router.post("/", response_model=NotificationResponse, status_code=201)
async def add_notification(data: NotificationCreate, db: AsyncSession = Depends(get_db)):
    """알림 생성"""
    return await create_notification(db, data)


@router.patch("/{notification_id}/read", status_code=204)
async def read_one(notification_id: int, db: AsyncSession = Depends(get_db)):
    """알림 개별 읽음 처리"""
    success = await mark_as_read(db, notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")


@router.patch("/read-all", status_code=204)
async def read_all(db: AsyncSession = Depends(get_db)):
    """전체 알림 읽음 처리"""
    await mark_all_as_read(db)
```

---

### 7. Config 도메인 (P2-007)

**테이블:** `app_configs`
**Firebase 원본:** `mc_config/{key}`

#### models.py

```python
from sqlalchemy import Column, String, Integer, Text
from app.models.base import Base, TimestampMixin

# app_configs에는 deleted_at 없음 (init.sql 기준) — SoftDeleteMixin 미적용


class AppConfig(Base, TimestampMixin):
    __tablename__ = "app_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=True)
```

#### schema.py

```python
from typing import Optional
from pydantic import BaseModel


class ConfigUpdate(BaseModel):
    value: Optional[str] = None


class ConfigResponse(BaseModel):
    id: int
    key: str
    value: Optional[str]

    model_config = {"from_attributes": True}
```

#### service.py

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.config.models import AppConfig
from app.domains.config.schema import ConfigUpdate, ConfigResponse


async def get_all_configs(db: AsyncSession) -> list[ConfigResponse]:
    """
    -- [SQL] 전체 앱 설정 조회
    -- SELECT * FROM app_configs ORDER BY key ASC;
    """
    stmt = select(AppConfig).order_by(AppConfig.key.asc())
    result = await db.execute(stmt)
    return [ConfigResponse.model_validate(r) for r in result.scalars().all()]


async def get_config_by_key(db: AsyncSession, key: str) -> ConfigResponse | None:
    """
    -- [SQL] 키로 설정값 조회
    -- SELECT * FROM app_configs WHERE key = :key;
    """
    stmt = select(AppConfig).where(AppConfig.key == key)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    return ConfigResponse.model_validate(config) if config else None


async def upsert_config(db: AsyncSession, key: str, data: ConfigUpdate) -> ConfigResponse:
    """
    -- [SQL] 설정값 Upsert
    -- SELECT * FROM app_configs WHERE key = :key;
    -- 존재: UPDATE app_configs SET value = :value, updated_at = NOW() WHERE key = :key;
    -- 미존재: INSERT INTO app_configs (key, value) VALUES (:key, :value);
    """
    stmt = select(AppConfig).where(AppConfig.key == key)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.value = data.value
        await db.commit()
        await db.refresh(existing)
        return ConfigResponse.model_validate(existing)
    else:
        config = AppConfig(key=key, value=data.value)
        db.add(config)
        await db.commit()
        await db.refresh(config)
        return ConfigResponse.model_validate(config)
```

#### router.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.config.schema import ConfigUpdate, ConfigResponse
from app.domains.config.service import get_all_configs, get_config_by_key, upsert_config

router = APIRouter(prefix="/api/configs", tags=["Config"])


@router.get("/", response_model=list[ConfigResponse])
async def list_configs(db: AsyncSession = Depends(get_db)):
    """전체 앱 설정 조회"""
    return await get_all_configs(db)


@router.get("/{key}", response_model=ConfigResponse)
async def get_config(key: str, db: AsyncSession = Depends(get_db)):
    """키로 설정값 조회"""
    result = await get_config_by_key(db, key)
    if not result:
        raise HTTPException(status_code=404, detail=f"설정 키 '{key}'를 찾을 수 없습니다")
    return result


@router.put("/{key}", response_model=ConfigResponse)
async def save_config(key: str, data: ConfigUpdate, db: AsyncSession = Depends(get_db)):
    """설정값 저장 (Upsert)"""
    return await upsert_config(db, key, data)
```

---

### 8. LoginLog 도메인 (P2-008)

**테이블:** `login_logs`
**Firebase 원본:** `mc_login_logs/{playerId}/{logId}`

#### models.py

```python
from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey, func
from sqlalchemy.types import TIMESTAMP
from app.models.base import Base

# login_logs에는 updated_at, deleted_at 없음 (init.sql 기준) — Mixin 미적용


class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
```

#### schema.py

```python
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class LoginLogCreate(BaseModel):
    player_id: int
    success: bool
    ip_address: Optional[str] = None
    date: date


class LoginLogResponse(BaseModel):
    id: int
    player_id: int
    success: bool
    ip_address: Optional[str]
    date: date
    created_at: datetime

    model_config = {"from_attributes": True}
```

#### service.py

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.login_log.models import LoginLog
from app.domains.login_log.schema import LoginLogCreate, LoginLogResponse


async def get_login_logs_by_player(
    db: AsyncSession, player_id: int, limit: int = 50
) -> list[LoginLogResponse]:
    """
    -- [SQL] 플레이어의 로그인 이력 조회 (최근 N건)
    -- SELECT * FROM login_logs
    -- WHERE player_id = :player_id
    -- ORDER BY created_at DESC LIMIT :limit;
    """
    stmt = (
        select(LoginLog)
        .where(LoginLog.player_id == player_id)
        .order_by(LoginLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return [LoginLogResponse.model_validate(r) for r in result.scalars().all()]


async def create_login_log(db: AsyncSession, data: LoginLogCreate) -> LoginLogResponse:
    """
    -- [SQL] 로그인 로그 기록
    -- INSERT INTO login_logs (player_id, success, ip_address, date, created_at)
    -- VALUES (:player_id, :success, :ip, :date, NOW());
    """
    log = LoginLog(**data.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return LoginLogResponse.model_validate(log)
```

#### router.py

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.login_log.schema import LoginLogResponse
from app.domains.login_log.service import get_login_logs_by_player

router = APIRouter(prefix="/api/login-logs", tags=["LoginLog"])


@router.get("/", response_model=list[LoginLogResponse])
async def list_logs(
    player_id: int = Query(...),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """플레이어의 로그인 이력 조회"""
    return await get_login_logs_by_player(db, player_id, limit)
```

> **참고:** `LoginLog` 생성은 `auth/service.py`의 `_save_login_log`에서 이미 수행 중이므로, login_log 라우터에는 POST 없음. 조회 전용 엔드포인트만 제공합니다.

---

## Part 2. 공통 수정 파일

### P2-009: all_models.py Junction Hub 갱신

```python
"""Junction Hub: import만 수행"""
from app.domains.auth.models import PlayerAuth           # noqa: F401
from app.domains.player.models import Player             # noqa: F401
from app.domains.mission.models import Mission           # noqa: F401
from app.domains.cheer.models import CheerMessage        # noqa: F401
from app.domains.feedback.models import Feedback, FeedbackReply  # noqa: F401
from app.domains.deduction.models import Deduction       # noqa: F401
from app.domains.daily_point.models import DailyPoint    # noqa: F401
from app.domains.notification.models import Notification  # noqa: F401
from app.domains.config.models import AppConfig          # noqa: F401
from app.domains.login_log.models import LoginLog        # noqa: F401
```

### P2-010: main.py 라우터 등록

```python
# 기존 import 유지 + 8개 추가
from app.domains.auth.router import router as auth_router
from app.domains.player.router import router as player_router
from app.domains.mission.router import router as mission_router
from app.domains.cheer.router import router as cheer_router
from app.domains.feedback.router import router as feedback_router
from app.domains.deduction.router import router as deduction_router
from app.domains.daily_point.router import router as daily_point_router
from app.domains.notification.router import router as notification_router
from app.domains.config.router import router as config_router
from app.domains.login_log.router import router as login_log_router

# 기존 등록 유지 + 8개 추가
app.include_router(auth_router)
app.include_router(player_router)
app.include_router(mission_router)
app.include_router(cheer_router)
app.include_router(feedback_router)
app.include_router(deduction_router)
app.include_router(daily_point_router)
app.include_router(notification_router)
app.include_router(config_router)
app.include_router(login_log_router)
```

---

## Part 3. Gemini Audit 체크리스트 (Phase 2)

### A. Thin Controller (8항목)

| # | 도메인 | 검증 항목 |
|---|---|---|
| A-1 | mission/router.py | 비즈니스 로직 0줄, service 호출만? |
| A-2 | cheer/router.py | 비즈니스 로직 0줄? |
| A-3 | feedback/router.py | 비즈니스 로직 0줄? |
| A-4 | deduction/router.py | 비즈니스 로직 0줄? |
| A-5 | daily_point/router.py | 비즈니스 로직 0줄? |
| A-6 | notification/router.py | 비즈니스 로직 0줄? |
| A-7 | config/router.py | 비즈니스 로직 0줄? |
| A-8 | login_log/router.py | 비즈니스 로직 0줄? |

### B. SQL Annotation (8항목)

| # | 도메인 | 검증 항목 |
|---|---|---|
| B-1 | mission/service.py | 모든 핵심 함수에 RAW SQL 주석? |
| B-2 | cheer/service.py | SQL 주석? |
| B-3 | feedback/service.py | SQL 주석? |
| B-4 | deduction/service.py | SQL 주석? |
| B-5 | daily_point/service.py | SQL 주석? |
| B-6 | notification/service.py | SQL 주석? |
| B-7 | config/service.py | SQL 주석? |
| B-8 | login_log/service.py | SQL 주석? |

### C. Soft Delete / Mixin 적합성 (8항목)

| # | 도메인 | 검증 항목 |
|---|---|---|
| C-1 | Mission | SoftDeleteMixin 적용 + 쿼리에 deleted_at IS NULL? |
| C-2 | CheerMessage | SoftDeleteMixin 적용? |
| C-3 | Feedback / FeedbackReply | 양 모델 SoftDeleteMixin 적용? |
| C-4 | Deduction | SoftDeleteMixin 적용? |
| C-5 | DailyPoint | SoftDeleteMixin 적용? |
| C-6 | Notification | SoftDeleteMixin만 적용 (updated_at 없음)? |
| C-7 | AppConfig | SoftDeleteMixin 미적용 (init.sql에 deleted_at 없음)이 올바른가? |
| C-8 | LoginLog | Mixin 미적용 (init.sql에 updated_at/deleted_at 없음)이 올바른가? |

### D. 모델-스키마 정합성 (4항목)

| # | 검증 항목 |
|---|---|
| D-1 | 모든 Response 스키마에 `model_config = {"from_attributes": True}` 존재? |
| D-2 | FeedbackReply의 created_at 직접 정의가 init.sql과 일치? |
| D-3 | Notification의 created_at 직접 정의가 init.sql과 일치? |
| D-4 | LoginLog의 created_at 직접 정의가 init.sql과 일치? |

### E. Junction Hub + 라우터 등록 (3항목)

| # | 검증 항목 |
|---|---|
| E-1 | all_models.py에 10개 모델(기존 2 + 신규 8+1) import 완비? |
| E-2 | main.py에 10개 라우터 등록 완비? |
| E-3 | API prefix 네이밍 일관성 (복수형/kebab-case)? |

### F. init.sql 정합성 (3항목)

| # | 검증 항목 |
|---|---|
| F-1 | 모든 models.py 컬럼 정의가 init.sql 테이블과 1:1 일치? |
| F-2 | FK 참조가 init.sql의 REFERENCES와 일치? |
| F-3 | CHECK 제약조건 (mission.status, cheer.sender 등)이 반영? |

---

## Gemini 응답 형식

```
## Phase 2 Audit Report — Core Domains BE

### 종합 판정: [PASS / CONDITIONAL PASS / FAIL]

### A. Thin Controller (8)
- A-1 ~ A-8: [판정] (코멘트)

### B. SQL Annotation (8)
- B-1 ~ B-8: [판정] (코멘트)

### C. Soft Delete / Mixin (8)
- C-1 ~ C-8: [판정] (코멘트)

### D. 모델-스키마 정합성 (4)
- D-1 ~ D-4: [판정] (코멘트)

### E. Junction + 라우터 (3)
- E-1 ~ E-3: [판정] (코멘트)

### F. init.sql 정합성 (3)
- F-1 ~ F-3: [판정] (코멘트)

### Warning/Fail 상세
1. ...

### Claude Code 실행 가부
- [ ] Phase 2 실행 승인
- [ ] 설계 수정 후 재감사 필요
```
