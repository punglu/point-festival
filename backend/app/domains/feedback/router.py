from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_player, get_current_user, require_self_player_id
from app.domains.feedback.models import Feedback
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
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 피드백 + 답글 조회 (player_id 생략 시 전체 조회)"""
    if user.get("role") == "admin":
        if player_id is None:
            return await get_all_feedbacks(db, target_date)
        return await get_feedbacks_by_player(db, player_id, target_date)
    if user.get("role") != "player":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="허용되지 않은 역할입니다")
    current_player_id = int(user["sub"])
    if player_id is None:
        return await get_feedbacks_by_player(db, current_player_id, target_date)
    if player_id != current_player_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="다른 사용자의 피드백에 접근할 수 없습니다")
    return await get_feedbacks_by_player(db, player_id, target_date)


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    data: FeedbackCreate,
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """피드백 작성"""
    current_player_id = require_self_player_id(user, data.player_id)
    return await create_feedback(db, data.model_copy(update={"player_id": current_player_id}))


@router.post("/replies", response_model=FeedbackReplyResponse, status_code=201)
async def submit_reply(
    data: FeedbackReplyCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """피드백 답글 추가"""
    feedback = await db.get(Feedback, data.feedback_id)
    if not feedback or feedback.deleted_at is not None:
        raise HTTPException(status_code=404, detail="피드백을 찾을 수 없습니다")
    if user.get("role") == "player" and feedback.player_id != int(user["sub"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="다른 사용자의 피드백에 답글을 작성할 수 없습니다")
    if user.get("role") not in {"player", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="허용되지 않은 역할입니다")
    return await add_reply(db, data.model_copy(update={"sender": user.get("name", data.sender)}))
