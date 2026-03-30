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
    -- [SQL] 플레이어의 날짜별 피드백 + 답글 조회 (N+1 패턴 — 가족 규모 데이터로 허용)
    -- 1) SELECT * FROM feedbacks WHERE player_id=:pid AND date=:date AND deleted_at IS NULL;
    -- 2) for each feedback:
    --    SELECT * FROM feedback_replies WHERE feedback_id=:id AND deleted_at IS NULL ORDER BY created_at ASC;
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
        reply_stmt = (
            select(FeedbackReply)
            .where(
                FeedbackReply.feedback_id == fb.id,
                FeedbackReply.deleted_at.is_(None),
            )
            .order_by(FeedbackReply.created_at.asc())
        )
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
