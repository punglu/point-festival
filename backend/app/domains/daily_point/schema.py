from datetime import date
from pydantic import BaseModel


class DailyPointUpsert(BaseModel):
    player_id: int
    date: date
    earned: int = 0
    spent: int = 0
    balance: int = 0


class DailyPointAdjust(BaseModel):
    """Delta-based point adjustment (FIX-003)"""
    player_id: int
    date: date
    earned_delta: int = 0
    spent_delta: int = 0


class DailyPointResponse(BaseModel):
    id: int
    player_id: int
    date: date
    earned: int
    spent: int
    balance: int

    model_config = {"from_attributes": True}
