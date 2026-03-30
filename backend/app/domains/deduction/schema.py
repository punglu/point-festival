from datetime import date
from pydantic import BaseModel, Field


class DeductionCreate(BaseModel):
    player_id: int
    date: date
    reason: str = Field(max_length=300)
    amount: int = Field(gt=0)


class DeductionResponse(BaseModel):
    id: int
    player_id: int
    date: date
    reason: str
    amount: int

    model_config = {"from_attributes": True}
