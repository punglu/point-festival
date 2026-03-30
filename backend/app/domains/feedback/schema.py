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
