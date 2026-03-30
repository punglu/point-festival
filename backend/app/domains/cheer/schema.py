from datetime import date
from typing import Optional
from pydantic import BaseModel


class CheerCreate(BaseModel):
    date: date
    sender: str  # 'dad' | 'mom'
    message: str


class CheerUpdate(BaseModel):
    message: Optional[str] = None


class CheerResponse(BaseModel):
    id: int
    date: date
    sender: str
    message: str

    model_config = {"from_attributes": True}
