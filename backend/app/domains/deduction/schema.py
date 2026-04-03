from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class DeductionCreate(BaseModel):
    player_id: int
    date: date
    reason: str = Field(max_length=300)
    amount: int = Field(gt=0)


class DeductionUpdate(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=300)
    amount: Optional[int] = Field(default=None, gt=0)


class DeductionResponse(BaseModel):
    id: int
    player_id: int
    date: date
    reason: str
    amount: int

    model_config = {"from_attributes": True}
