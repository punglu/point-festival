from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class MissionCreate(BaseModel):
    player_id: int
    date: date
    text: str = Field(max_length=500)
    point: int = Field(ge=0)
    sender: Optional[str] = None
    msg: Optional[str] = None
    status: str = "active"
    sort_order: int = 0


class MissionUpdate(BaseModel):
    text: Optional[str] = Field(default=None, max_length=500)
    point: Optional[int] = Field(default=None, ge=0)
    status: Optional[str] = None
    msg: Optional[str] = None
    rejection_reason: Optional[str] = None
    sort_order: Optional[int] = None


class MissionStatusUpdate(BaseModel):
    status: str  # 'completed' | 'failed' | 'active'


class MissionPropose(BaseModel):
    player_id: int
    date: date
    text: str = Field(max_length=500)
    point: int = Field(ge=0)
    proposed_by: str
    proposal_reason: Optional[str] = None


class MissionResponse(BaseModel):
    id: int
    player_id: int
    date: date
    text: str
    point: int
    status: str
    sender: Optional[str]
    msg: Optional[str]
    proposed_by: Optional[str]
    proposal_reason: Optional[str]
    rejection_reason: Optional[str]
    sort_order: int

    model_config = {"from_attributes": True}


class MissionCloneRequest(BaseModel):
    source_player_id: int
    source_date: date
    target_date: date
    point_overrides: Optional[dict[int, int]] = None
    # key: 원본 mission_id, value: 변경할 포인트. None이면 원본 포인트 그대로 복제


class MissionCloneResponse(BaseModel):
    cloned_count: int
    missions: list[MissionResponse]
