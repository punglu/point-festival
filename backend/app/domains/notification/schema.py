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
