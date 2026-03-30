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
