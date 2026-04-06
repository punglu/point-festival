# [Claude Code 실행 프롬프트] P-HOTFIX-LEVEL-001: 레벨 시스템 정규화 + 누적 포인트 물리화

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P-HOTFIX-LEVEL-001
> **상태:** TODO → 진행중
> **감사 상태:** Gemini Audit — PASS (복합 유니크, 트랜잭션 정합성, 하이브리드 확장 승인)
> **목표:** 레벨 초기화 버그 수정 (누적 포인트 물리화) + level_tiers 전용 테이블 이관 + FE ExpBar 연동

---

## 🚨 실행 전 필독

### CLAUDE.md를 먼저 읽으세요.

### 핵심 원칙
1. **기존 기능 전체 유지** — 미션/포인트/차감 등 기존 도메인 로직을 깨뜨리지 마라
2. **Thin Controller** — router.py에 비즈니스 로직 0줄
3. **SQL Annotation** — service.py 핵심 함수 상단 RAW SQL 주석 필수
4. **CSS Modules** — 인라인 style={{}} 파일당 5개 미만
5. **ACID 트랜잭션** — total_earned 변경은 반드시 daily_points 변경과 동일 트랜잭션
6. **Admin UI는 이번 핫픽스에서 건드리지 않는다** — BE API만 준비

### 실행 순서
**반드시 Step 순서대로.** Step 0(DB) → Step 1(BE 모델) → Step 2(BE 서비스+라우터) → Step 3(기존 코드 수정) → Step 4(FE) → Step 5(빌드)

---

## Step 0: DB — 스키마 변경

### 0-1. 마이그레이션 SQL 실행

```bash
docker exec -i mc-db psql -U mc_admin -d mc_festival << 'SQL'
BEGIN;

-- 1) players 테이블에 누적 포인트 컬럼 추가
ALTER TABLE players ADD COLUMN IF NOT EXISTS total_earned INTEGER NOT NULL DEFAULT 0;

-- 2) level_tiers 전용 테이블 생성
CREATE TABLE IF NOT EXISTS level_tiers (
    id              SERIAL PRIMARY KEY,
    job_code        VARCHAR(20) NOT NULL DEFAULT 'COMMON',
    level           INTEGER NOT NULL,
    title           VARCHAR(100) NOT NULL,
    required_points INTEGER NOT NULL DEFAULT 0,
    icon_path       VARCHAR(300),
    milestone_type  VARCHAR(30),
    milestone_data  JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_job_level UNIQUE (job_code, level)
);

-- 3) 기본 Seed 데이터 (COMMON 10레벨)
INSERT INTO level_tiers (job_code, level, title, required_points) VALUES
    ('COMMON', 1,  '새싹 모험가',           0),
    ('COMMON', 2,  '돌 검 용사',           30),
    ('COMMON', 3,  '철 검 기사',           80),
    ('COMMON', 4,  '다이아 전사',         150),
    ('COMMON', 5,  '네더 탐험가',         250),
    ('COMMON', 6,  '엔더 사냥꾼',         380),
    ('COMMON', 7,  '위더 정복자',         550),
    ('COMMON', 8,  '엔드 드래곤 슬레이어', 750),
    ('COMMON', 9,  '전설의 마스터',      1000),
    ('COMMON', 10, '월드 챔피언',        1300)
ON CONFLICT (job_code, level) DO NOTHING;

-- 4) 기존 players의 total_earned 보정 (현재 daily_points 기반 역산)
UPDATE players p
SET total_earned = COALESCE(sub.sum_earned, 0)
FROM (
    SELECT player_id, SUM(earned) AS sum_earned
    FROM daily_points
    WHERE deleted_at IS NULL
    GROUP BY player_id
) sub
WHERE p.id = sub.player_id;

COMMIT;
SQL
```

### 0-2. init.sql 반영 (신규 배포용)

**파일:** `database/init.sql`

#### 0-2-A. players 테이블 CREATE문에 total_earned 추가

`players` 테이블의 CREATE문을 찾아서 `last_login` 컬럼 아래에 추가:

```sql
    total_earned    INTEGER NOT NULL DEFAULT 0,
```

#### 0-2-B. level_tiers 테이블 추가

`mission_templates` 테이블 이후 위치에 추가 (없다면 `app_configs` 테이블 이전):

```sql
-- 12. Level Tiers (레벨 구간 정의 — Phase B 직업 분기 대응)
CREATE TABLE level_tiers (
    id              SERIAL PRIMARY KEY,
    job_code        VARCHAR(20) NOT NULL DEFAULT 'COMMON',
    level           INTEGER NOT NULL,
    title           VARCHAR(100) NOT NULL,
    required_points INTEGER NOT NULL DEFAULT 0,
    icon_path       VARCHAR(300),
    milestone_type  VARCHAR(30),
    milestone_data  JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_job_level UNIQUE (job_code, level)
);
```

#### 0-2-C. Seed 데이터 추가

기존 Seed 섹션 하단에 추가:

```sql
INSERT INTO level_tiers (job_code, level, title, required_points) VALUES
    ('COMMON', 1,  '새싹 모험가',           0),
    ('COMMON', 2,  '돌 검 용사',           30),
    ('COMMON', 3,  '철 검 기사',           80),
    ('COMMON', 4,  '다이아 전사',         150),
    ('COMMON', 5,  '네더 탐험가',         250),
    ('COMMON', 6,  '엔더 사냥꾼',         380),
    ('COMMON', 7,  '위더 정복자',         550),
    ('COMMON', 8,  '엔드 드래곤 슬레이어', 750),
    ('COMMON', 9,  '전설의 마스터',      1000),
    ('COMMON', 10, '월드 챔피언',        1300);
```

#### 0-2-D. 기존 level.thresholds Seed 삭제

init.sql의 `app_configs` Seed에서 아래 행을 찾아 삭제:

```sql
-- 삭제 대상 (있다면):
-- ('level.thresholds', '{"1":0,"2":50,"3":150,"4":300,"5":500}')
```

> 해당 행이 없을 수도 있음. 있으면 삭제, 없으면 무시.

---

## Step 1: BE — level_tier 도메인 생성

### 1-1. 디렉토리 구조

```
backend/app/domains/level_tier/
├── __init__.py
├── models.py
├── schema.py
├── service.py
└── router.py
```

### 1-2. models.py

```python
"""Level Tier 모델 — 레벨 구간 정의"""
from sqlalchemy import String, Integer, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.base import Base


class LevelTier(Base):
    __tablename__ = "level_tiers"
    __table_args__ = (
        UniqueConstraint("job_code", "level", name="uq_job_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_code: Mapped[str] = mapped_column(String(20), nullable=False, default="COMMON")
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    required_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    icon_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    milestone_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    milestone_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
```

### 1-3. schema.py

```python
"""Level Tier 스키마"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LevelTierResponse(BaseModel):
    id: int
    job_code: str
    level: int
    title: str
    required_points: int
    icon_path: Optional[str] = None
    milestone_type: Optional[str] = None
    milestone_data: Optional[dict] = None

    model_config = {"from_attributes": True}


class LevelTierCreate(BaseModel):
    job_code: str = Field(default="COMMON", max_length=20)
    level: int = Field(ge=1)
    title: str = Field(max_length=100)
    required_points: int = Field(ge=0)
    icon_path: Optional[str] = None
    milestone_type: Optional[str] = None
    milestone_data: Optional[dict] = None


class LevelTierUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    required_points: Optional[int] = Field(default=None, ge=0)
    icon_path: Optional[str] = None
    milestone_type: Optional[str] = None
    milestone_data: Optional[dict] = None


class LevelTierBulkSave(BaseModel):
    """Admin UI에서 전체 레벨 구간을 한번에 저장할 때 사용"""
    job_code: str = Field(default="COMMON", max_length=20)
    tiers: list[LevelTierCreate]


class PlayerLevelInfo(BaseModel):
    """플레이어의 현재 레벨 정보 (FE ExpBar용)"""
    player_id: int
    total_earned: int
    level: int
    title: str
    current_threshold: int
    next_threshold: int
    progress_percent: int  # 0~100
```

### 1-4. service.py

```python
"""Level Tier 서비스"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete
from fastapi import HTTPException

from app.domains.level_tier.models import LevelTier
from app.domains.level_tier.schema import (
    LevelTierResponse,
    LevelTierCreate,
    LevelTierUpdate,
    LevelTierBulkSave,
    PlayerLevelInfo,
)


async def get_tiers_by_job(db: AsyncSession, job_code: str = "COMMON") -> list[LevelTierResponse]:
    """
    -- [SQL] 직업별 레벨 구간 전체 조회
    -- SELECT * FROM level_tiers
    -- WHERE job_code = :job_code
    -- ORDER BY level ASC;
    """
    stmt = (
        select(LevelTier)
        .where(LevelTier.job_code == job_code)
        .order_by(LevelTier.level.asc())
    )
    result = await db.execute(stmt)
    return [LevelTierResponse.model_validate(t) for t in result.scalars().all()]


async def create_tier(db: AsyncSession, data: LevelTierCreate) -> LevelTierResponse:
    """
    -- [SQL] 레벨 구간 추가
    -- INSERT INTO level_tiers (job_code, level, title, required_points, icon_path, milestone_type, milestone_data)
    -- VALUES (:job_code, :level, :title, :required_points, :icon_path, :milestone_type, :milestone_data);
    """
    tier = LevelTier(**data.model_dump())
    db.add(tier)
    await db.flush()
    await db.refresh(tier)
    return LevelTierResponse.model_validate(tier)


async def update_tier(db: AsyncSession, tier_id: int, data: LevelTierUpdate) -> LevelTierResponse:
    """
    -- [SQL] 레벨 구간 수정
    -- UPDATE level_tiers SET title = :title, required_points = :points, ...
    -- WHERE id = :id;
    """
    stmt = select(LevelTier).where(LevelTier.id == tier_id)
    result = await db.execute(stmt)
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="레벨 구간을 찾을 수 없습니다")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(tier, key, value)
    await db.flush()
    await db.refresh(tier)
    return LevelTierResponse.model_validate(tier)


async def delete_tier(db: AsyncSession, tier_id: int) -> None:
    """
    -- [SQL] 레벨 구간 삭제 (물리 삭제 — Soft Delete 미적용, 설정 데이터)
    -- DELETE FROM level_tiers WHERE id = :id;
    """
    stmt = select(LevelTier).where(LevelTier.id == tier_id)
    result = await db.execute(stmt)
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="레벨 구간을 찾을 수 없습니다")
    await db.delete(tier)
    await db.flush()


async def bulk_save_tiers(db: AsyncSession, data: LevelTierBulkSave) -> list[LevelTierResponse]:
    """
    -- [SQL] 레벨 구간 벌크 저장 (기존 전체 삭제 후 재생성)
    -- DELETE FROM level_tiers WHERE job_code = :job_code;
    -- INSERT INTO level_tiers (...) VALUES (...), (...), ...;
    """
    # 구간 검증: required_points 오름차순 정렬 확인
    sorted_tiers = sorted(data.tiers, key=lambda t: t.required_points)
    for i, tier in enumerate(sorted_tiers):
        if tier.level != i + 1:
            # 레벨 번호 자동 재할당
            sorted_tiers[i] = tier.model_copy(update={"level": i + 1})

    # 중복 포인트 검증
    points_set = set()
    for tier in sorted_tiers:
        if tier.required_points in points_set:
            raise HTTPException(
                status_code=400,
                detail=f"중복된 포인트 값: {tier.required_points}"
            )
        points_set.add(tier.required_points)

    # Lv.1은 반드시 0P
    if sorted_tiers and sorted_tiers[0].required_points != 0:
        raise HTTPException(
            status_code=400,
            detail="Lv.1의 필요 포인트는 반드시 0이어야 합니다"
        )

    # 기존 데이터 삭제
    del_stmt = sql_delete(LevelTier).where(LevelTier.job_code == data.job_code)
    await db.execute(del_stmt)

    # 새 데이터 삽입
    new_tiers = []
    for tier_data in sorted_tiers:
        tier = LevelTier(
            job_code=data.job_code,
            level=tier_data.level,
            title=tier_data.title,
            required_points=tier_data.required_points,
            icon_path=tier_data.icon_path,
            milestone_type=tier_data.milestone_type,
            milestone_data=tier_data.milestone_data,
        )
        db.add(tier)
        new_tiers.append(tier)

    await db.flush()
    for t in new_tiers:
        await db.refresh(t)
    return [LevelTierResponse.model_validate(t) for t in new_tiers]


def calculate_level(total_earned: int, tiers: list[LevelTierResponse]) -> PlayerLevelInfo:
    """
    플레이어의 누적 포인트로 레벨 계산.
    정의된 구간 초과 시 하이브리드 자동 확장 (마지막 두 구간의 간격 반복).

    이 함수는 DB 접근 없음 — 순수 계산 함수.
    """
    if not tiers:
        return PlayerLevelInfo(
            player_id=0, total_earned=total_earned,
            level=1, title="Lv.1", current_threshold=0,
            next_threshold=100, progress_percent=0,
        )

    sorted_tiers = sorted(tiers, key=lambda t: t.required_points)

    # 정의된 구간 내 레벨 찾기
    current_tier = sorted_tiers[0]
    for tier in sorted_tiers:
        if total_earned >= tier.required_points:
            current_tier = tier
        else:
            break

    # 다음 레벨 임계치 계산
    current_idx = sorted_tiers.index(current_tier)
    if current_idx + 1 < len(sorted_tiers):
        # 정의된 구간 내
        next_threshold = sorted_tiers[current_idx + 1].required_points
        level = current_tier.level
        title = current_tier.title
    else:
        # 정의된 구간 초과 → 하이브리드 자동 확장
        if len(sorted_tiers) >= 2:
            last_gap = sorted_tiers[-1].required_points - sorted_tiers[-2].required_points
        else:
            last_gap = 100  # fallback

        if last_gap <= 0:
            last_gap = 100

        excess = total_earned - sorted_tiers[-1].required_points
        extra_levels = excess // last_gap
        level = sorted_tiers[-1].level + extra_levels
        title = f"Lv.{level} (자동)"
        current_threshold_calc = sorted_tiers[-1].required_points + (extra_levels * last_gap)
        next_threshold = current_threshold_calc + last_gap

    # 프로그레스 계산
    current_threshold = current_tier.required_points
    if current_idx + 1 >= len(sorted_tiers) and len(sorted_tiers) >= 2:
        # 자동 확장 구간
        last_gap = sorted_tiers[-1].required_points - sorted_tiers[-2].required_points
        if last_gap <= 0:
            last_gap = 100
        excess = total_earned - sorted_tiers[-1].required_points
        extra_levels = excess // last_gap
        current_threshold = sorted_tiers[-1].required_points + (extra_levels * last_gap)

    range_size = next_threshold - current_threshold
    if range_size > 0:
        progress = int(((total_earned - current_threshold) / range_size) * 100)
        progress = max(0, min(100, progress))
    else:
        progress = 100

    return PlayerLevelInfo(
        player_id=0,  # 호출자가 설정
        total_earned=total_earned,
        level=level,
        title=title,
        current_threshold=current_threshold,
        next_threshold=next_threshold,
        progress_percent=progress,
    )


async def get_player_level(db: AsyncSession, player_id: int, job_code: str = "COMMON") -> PlayerLevelInfo:
    """
    -- [SQL] 플레이어 레벨 조회
    -- SELECT total_earned FROM players WHERE id = :pid AND deleted_at IS NULL;
    -- SELECT * FROM level_tiers WHERE job_code = :job_code ORDER BY level ASC;
    """
    from app.domains.player.models import Player
    
    stmt = select(Player).where(Player.id == player_id, Player.deleted_at.is_(None))
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다")

    tiers = await get_tiers_by_job(db, job_code)
    level_info = calculate_level(player.total_earned, tiers)
    level_info.player_id = player_id
    return level_info
```

### 1-5. router.py

```python
"""Level Tier 라우터"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.level_tier import service
from app.domains.level_tier.schema import (
    LevelTierResponse,
    LevelTierCreate,
    LevelTierUpdate,
    LevelTierBulkSave,
    PlayerLevelInfo,
)

router = APIRouter(prefix="/api/level-tiers", tags=["level-tiers"])


@router.get("", response_model=list[LevelTierResponse])
async def list_tiers(
    job_code: str = "COMMON",
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 목록 조회 (인증 불필요 — FE ExpBar에서 호출)"""
    return await service.get_tiers_by_job(db, job_code)


@router.get("/player/{player_id}", response_model=PlayerLevelInfo)
async def player_level(
    player_id: int,
    job_code: str = "COMMON",
    db: AsyncSession = Depends(get_db),
):
    """플레이어 현재 레벨 조회 (인증 불필요 — FE ExpBar/Ranking에서 호출)"""
    return await service.get_player_level(db, player_id, job_code)


@router.post("", response_model=LevelTierResponse, status_code=201)
async def create_tier(
    data: LevelTierCreate,
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 추가 (Admin용 — 추후 require_admin 추가)"""
    result = await service.create_tier(db, data)
    await db.commit()
    return result


@router.patch("/{tier_id}", response_model=LevelTierResponse)
async def update_tier(
    tier_id: int,
    data: LevelTierUpdate,
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 수정 (Admin용)"""
    result = await service.update_tier(db, tier_id, data)
    await db.commit()
    return result


@router.delete("/{tier_id}", status_code=204)
async def delete_tier(
    tier_id: int,
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 삭제 (Admin용)"""
    await service.delete_tier(db, tier_id)
    await db.commit()


@router.put("/bulk", response_model=list[LevelTierResponse])
async def bulk_save(
    data: LevelTierBulkSave,
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 벌크 저장 — 전체 교체 (Admin UI 저장 버튼용)"""
    result = await service.bulk_save_tiers(db, data)
    await db.commit()
    return result
```

### 1-6. all_models.py에 등록

**파일:** `backend/app/models/all_models.py`

기존 import 목록에 추가:

```python
from app.domains.level_tier.models import LevelTier  # noqa: F401
```

### 1-7. main.py에 라우터 등록

**파일:** `backend/app/main.py`

기존 라우터 import/include 섹션에 추가:

```python
from app.domains.level_tier.router import router as level_tier_router

# include 섹션에 추가:
app.include_router(level_tier_router)
```

---

## Step 2: BE — players 모델에 total_earned 추가

### 2-1. player/models.py

**파일:** `backend/app/domains/player/models.py`

Player 모델에 `total_earned` 컬럼 추가. `last_login` 컬럼 아래에:

```python
    total_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
```

> `from sqlalchemy import Integer`가 이미 import 되어 있는지 확인. 없으면 추가.

### 2-2. player/schema.py

Player 응답 스키마에 `total_earned` 필드 추가.

`PlayerListItem` (또는 `PlayerResponse` — 현재 사용 중인 응답 스키마 이름) 클래스에:

```python
    total_earned: int = 0
```

---

## Step 3: BE — 미션 완료/되돌리기 시 total_earned 동기화

### 핵심 원칙
**미션이 `completed` 상태가 될 때 `players.total_earned += mission.point`**
**미션이 `completed`에서 `active`로 되돌려질 때 `players.total_earned -= mission.point`**
**반드시 daily_points 업데이트와 동일 트랜잭션 내에서 처리**

### 3-1. 미션 상태 변경 시 total_earned 동기화 함수

**파일:** `backend/app/domains/mission/service.py`

기존 import 섹션에 추가:

```python
from sqlalchemy import update as sql_update
```

파일 내에 다음 헬퍼 함수를 추가:

```python
async def _sync_total_earned(db: AsyncSession, player_id: int, delta: int) -> None:
    """
    -- [SQL] players.total_earned 증감 (ACID 트랜잭션 내에서 호출)
    -- UPDATE players SET total_earned = total_earned + :delta, updated_at = NOW()
    -- WHERE id = :player_id AND deleted_at IS NULL;
    """
    from app.domains.player.models import Player
    from datetime import datetime, timezone

    stmt = (
        sql_update(Player)
        .where(Player.id == player_id, Player.deleted_at.is_(None))
        .values(
            total_earned=Player.total_earned + delta,
            updated_at=datetime.now(timezone.utc),
        )
    )
    await db.execute(stmt)
```

### 3-2. 기존 미션 상태 변경 로직에 _sync_total_earned 호출 삽입

mission/service.py에서 미션 상태가 `completed`로 변경되는 **모든 지점**을 찾아라. 현재 코드베이스에서 해당 지점은 다음과 같을 수 있다:

**A) `update_mission` 함수 내** — `pending_approval → completed` 전이 시:

```python
# 기존 상태 전이 검증 이후, commit 이전에 추가:
if "status" in update_data:
    old_status = mission.status  # setattr 전의 원래 상태를 미리 저장해야 함!
    # ... (기존 setattr 로직) ...
    new_status = update_data["status"]
    
    # completed 진입 시 포인트 적립
    if old_status != "completed" and new_status == "completed":
        await _sync_total_earned(db, mission.player_id, mission.point)
    
    # completed 이탈 시 포인트 차감 (admin revert 등)
    if old_status == "completed" and new_status != "completed":
        await _sync_total_earned(db, mission.player_id, -mission.point)
```

> **중요:** `old_status`는 `setattr` 루프 **이전에** 저장해야 한다. 기존 코드 구조를 확인하고, setattr 전에 `old_status = mission.status`를 캡처하라.

**B) `bulk_approve_missions` 함수** — 일괄 승인 시:

현재 `bulk_approve_missions`는 `UPDATE ... SET status = 'completed'`를 직접 실행한다.
이 함수 내에서 승인 대상 미션의 포인트 합계를 구해 `total_earned`에 반영해야 한다.

기존 `bulk_approve_missions` 함수를 수정:

```python
async def bulk_approve_missions(db: AsyncSession, player_id: int, date_str: str) -> int:
    """
    -- [SQL] 일괄 승인 + total_earned 동기화
    -- SELECT SUM(point) FROM missions
    --   WHERE player_id = :pid AND date = :date AND status = 'pending_approval' AND deleted_at IS NULL;
    -- UPDATE missions SET status = 'completed', updated_at = NOW()
    --   WHERE player_id = :pid AND date = :date AND status = 'pending_approval' AND deleted_at IS NULL;
    -- UPDATE players SET total_earned = total_earned + :sum_points WHERE id = :pid;
    """
    from datetime import datetime, timezone
    from sqlalchemy import func as sql_func

    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # 1) 승인 대상 포인트 합계 조회
    sum_stmt = select(sql_func.coalesce(sql_func.sum(Mission.point), 0)).where(
        Mission.player_id == player_id,
        Mission.date == target_date,
        Mission.status == "pending_approval",
        Mission.deleted_at.is_(None),
    )
    sum_result = await db.execute(sum_stmt)
    total_points = sum_result.scalar()

    # 2) 일괄 상태 변경
    stmt = (
        sql_update(Mission)
        .where(
            Mission.player_id == player_id,
            Mission.date == target_date,
            Mission.status == "pending_approval",
            Mission.deleted_at.is_(None),
        )
        .values(status="completed", updated_at=datetime.now(timezone.utc))
    )
    result = await db.execute(stmt)

    # 3) total_earned 동기화
    if total_points > 0:
        await _sync_total_earned(db, player_id, total_points)

    return result.rowcount
```

**C) `admin_revert_mission` 함수** — 관리자 완료 취소 시:

이 함수에서 이미 daily_points의 포인트를 차감하고 있다.
기존 포인트 환수 로직 **바로 아래에** total_earned 차감을 추가:

```python
    # 기존: 포인트 환수 (daily_points)
    # ... (기존 point_stmt 실행 코드) ...

    # 추가: total_earned 차감
    await _sync_total_earned(db, mission.player_id, -mission.point)
```

---

## Step 4: FE — ExpBar 연동 변경

### 4-1. 현재 ExpBar의 데이터 소스 변경

현재 ExpBar 컴포넌트는 `useDashboard` 훅에서 `levelThresholds` (app_configs JSON)와 일간/주간 포인트를 받아 레벨을 계산한다.

이것을 **새 API `GET /api/level-tiers/player/{playerId}`**로 교체한다.

**FE에서 변경해야 할 파일들을 아래 순서로 찾아 수정하라:**

### 4-2. dashboardApi.ts (또는 해당 API 모듈)

기존 `getConfig('level.thresholds')` 호출을 제거하고, 새 API 추가:

```typescript
/** 플레이어 레벨 정보 조회 */
getPlayerLevel: (playerId: number, jobCode: string = 'COMMON') =>
  httpClient.get<{
    player_id: number;
    total_earned: number;
    level: number;
    title: string;
    current_threshold: number;
    next_threshold: number;
    progress_percent: number;
  }>(`/api/level-tiers/player/${playerId}`, { params: { job_code: jobCode } }),

/** 레벨 구간 목록 조회 */
getLevelTiers: (jobCode: string = 'COMMON') =>
  httpClient.get<Array<{
    id: number;
    job_code: string;
    level: number;
    title: string;
    required_points: number;
  }>>('/api/level-tiers', { params: { job_code: jobCode } }),
```

### 4-3. useDashboard.ts 수정

**기존 levelThresholds 관련 코드를 찾아서 교체:**

기존:
```typescript
const [levelThresholds, setLevelThresholds] = useState<Record<string, number>>({ "1": 0, "2": 50, ... });

useEffect(() => {
    dashboardApi.getConfig('level.thresholds')
      .then(res => {
        if (res.data.value) setLevelThresholds(JSON.parse(res.data.value));
      })
      .catch(() => {});
  }, []);
```

변경:
```typescript
const [levelInfo, setLevelInfo] = useState<{
  level: number;
  title: string;
  total_earned: number;
  current_threshold: number;
  next_threshold: number;
  progress_percent: number;
} | null>(null);

// 레벨 정보 로드 (날짜 변경/미션 갱신 시마다)
const loadLevelInfo = useCallback(async () => {
  if (!player) return;
  try {
    const res = await dashboardApi.getPlayerLevel(player.id);
    setLevelInfo(res.data);
  } catch {
    // 실패 시 무시
  }
}, [player]);

// loadDayData 호출 후 레벨도 갱신
useEffect(() => { loadLevelInfo(); }, [loadLevelInfo, selectedDate]);
```

> `loadDayData` 콜백 내부 `finally` 블록에서도 `loadLevelInfo()`를 호출하면 미션 승인 후 레벨이 즉시 갱신됨.

반환값에 `levelInfo`와 `loadLevelInfo`를 추가:

```typescript
return {
  // ... 기존 반환값 ...
  levelInfo,
  loadLevelInfo,
};
```

### 4-4. ExpBar.tsx 수정

**기존 Props를 변경:**

기존:
```typescript
Props: { totalPoints, levelThresholds }
```

변경:
```typescript
interface ExpBarProps {
  levelInfo: {
    level: number;
    title: string;
    total_earned: number;
    current_threshold: number;
    next_threshold: number;
    progress_percent: number;
  } | null;
}
```

**기존 레벨 계산 로직(FE에서 thresholds 순회)을 완전히 제거하고, BE가 계산한 값을 그대로 표시:**

```tsx
export default function ExpBar({ levelInfo }: ExpBarProps) {
  if (!levelInfo) return null;

  return (
    <div className={styles.expBarContainer}>
      <span className={styles.levelBadge}>Lv.{levelInfo.level}</span>
      <div className={styles.expBarTrack}>
        <div
          className={styles.expBarFill}
          style={{ width: `${levelInfo.progress_percent}%` }}
        />
      </div>
      <span className={styles.expText}>
        {levelInfo.title} · {levelInfo.total_earned}P / {levelInfo.next_threshold}P
      </span>
    </div>
  );
}
```

### 4-5. ExpBar 호출부 수정

`ProfileCard.tsx` 또는 `index.tsx`에서 ExpBar를 호출하는 곳을 찾아 Props 변경:

기존:
```tsx
<ExpBar totalPoints={...} levelThresholds={levelThresholds} />
```

변경:
```tsx
<ExpBar levelInfo={levelInfo} />
```

### 4-6. RankingView에서도 레벨 표시 변경

RankingView.tsx에서 플레이어별 레벨을 표시하는 부분이 있다면, 각 플레이어에 대해 `GET /api/level-tiers/player/{id}`를 호출하거나, 플레이어 목록에 `total_earned`가 포함되어 있으면 FE에서 간이 계산.

> 현재 구조를 확인하고 최소한의 변경으로 대응하라. 기존 RankingView가 daily_points 범위 합산으로 레벨을 계산하고 있다면, 해당 로직을 `total_earned` 기반으로 교체.

---

## Step 5: 빌드 검증

### 5-1. Backend

```bash
find backend -name "*.py" -exec python -m py_compile {} +
docker-compose up -d --build backend
sleep 5
curl -s http://localhost:8000/api/health
```

### 5-2. Frontend

```bash
cd frontend && npm run build
# 0 errors 확인
docker-compose up -d --build frontend
```

### 5-3. 기능 검증 체크리스트

| # | 항목 | 방법 | 기대 |
|---|---|---|---|
| 1 | level_tiers 조회 | `curl http://localhost:8000/api/level-tiers` | 10개 COMMON 레벨 반환 |
| 2 | 플레이어 레벨 조회 | `curl http://localhost:8000/api/level-tiers/player/1` | total_earned 기반 레벨 정보 |
| 3 | total_earned 초기값 | DB에서 `SELECT id, name, total_earned FROM players;` | daily_points SUM과 일치 |
| 4 | 미션 승인 → total_earned | 미션 1개 완료 승인 → players.total_earned 확인 | 미션 point만큼 증가 |
| 5 | 미션 되돌리기 → total_earned | 관리자 revert → players.total_earned 확인 | 미션 point만큼 감소 |
| 6 | 일괄 승인 → total_earned | bulk-approve → total_earned 확인 | 승인된 미션 합계만큼 증가 |
| 7 | 주간 초기화 후 레벨 유지 | 다음 주로 이동 → 레벨 확인 | total_earned 변동 없음 → 레벨 유지 |
| 8 | ExpBar UI | User 대시보드 접속 | Lv.N + 칭호 + 프로그레스 바 표시 |
| 9 | 하이브리드 확장 | total_earned를 1300 이상으로 수동 설정 → 레벨 확인 | Lv.11+ 자동 계산 |
| 10 | py_compile | 0 errors | 확인 |
| 11 | npm build | 0 errors | 확인 |

---

## 생성/수정 파일 요약

| # | 작업 | 파일 경로 |
|---|---|---|
| 1 | **신규** | `backend/app/domains/level_tier/__init__.py` |
| 2 | **신규** | `backend/app/domains/level_tier/models.py` |
| 3 | **신규** | `backend/app/domains/level_tier/schema.py` |
| 4 | **신규** | `backend/app/domains/level_tier/service.py` |
| 5 | **신규** | `backend/app/domains/level_tier/router.py` |
| 6 | 수정 | `backend/app/models/all_models.py` (LevelTier import) |
| 7 | 수정 | `backend/app/main.py` (라우터 등록) |
| 8 | 수정 | `backend/app/domains/player/models.py` (total_earned 컬럼) |
| 9 | 수정 | `backend/app/domains/player/schema.py` (total_earned 필드) |
| 10 | 수정 | `backend/app/domains/mission/service.py` (_sync_total_earned + 호출 삽입) |
| 11 | 수정 | `database/init.sql` (players.total_earned + level_tiers 테이블 + Seed) |
| 12 | 수정 | FE `dashboardApi.ts` (새 API 추가, getConfig 제거) |
| 13 | 수정 | FE `useDashboard.ts` (levelInfo 상태 교체) |
| 14 | 수정 | FE `ExpBar.tsx` (Props + 렌더링 교체) |
| 15 | 수정 | FE `ProfileCard.tsx` 또는 `index.tsx` (ExpBar Props 전달 변경) |
| 16 | 수정 | FE `RankingView.tsx` (total_earned 기반 레벨 교체 — 해당 시) |

---

## 완료 보고 형식

```
Task ID: P-HOTFIX-LEVEL-001
상태: 진행중 → 완료
총소요시간: _분
생성 파일: level_tier 도메인 5개 (models/schema/service/router/__init__)
수정 파일: [위 목록 참조]
빌드 결과:
  - py_compile — 0 errors
  - npm run build — 0 errors
Docker:
  - backend + frontend 재빌드 완료
  - DB 마이그레이션 실행 완료
검증:
  - level_tiers API: 10개 COMMON 반환 확인
  - 플레이어 레벨 API: total_earned 기반 레벨 정보 확인
  - 미션 승인 → total_earned 증가 확인
  - 미션 되돌리기 → total_earned 감소 확인
  - 주간 초기화 후 레벨 유지 확인
  - ExpBar UI: Lv.N + 칭호 + 프로그레스 바 표시 확인
```
