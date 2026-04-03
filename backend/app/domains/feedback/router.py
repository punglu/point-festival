from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.feedback.schema import (
    FeedbackCreate, FeedbackReplyCreate,
    FeedbackResponse, FeedbackReplyResponse,
)
from app.domains.feedback.service import get_feedbacks_by_player, get_all_feedbacks, create_feedback, add_reply

router = APIRouter(prefix="/api/feedbacks", tags=["Feedback"])


@router.get("/", response_model=list[FeedbackResponse])
async def list_feedbacks(
    target_date: date = Query(..., alias="date"),
    player_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 피드백 + 답글 조회 (player_id 생략 시 전체 조회)"""
    if player_id is None:
        return await get_all_feedbacks(db, target_date)
    return await get_feedbacks_by_player(db, player_id, target_date)


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(data: FeedbackCreate, db: AsyncSession = Depends(get_db)):
    """피드백 작성"""
    return await create_feedback(db, data)


@router.post("/replies", response_model=FeedbackReplyResponse, status_code=201)
async def submit_reply(data: FeedbackReplyCreate, db: AsyncSession = Depends(get_db)):
    """피드백 답글 추가"""
    return await add_reply(db, data)
