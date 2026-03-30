from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.cheer.models import CheerMessage
from app.domains.cheer.schema import CheerCreate, CheerResponse


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
