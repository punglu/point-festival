from typing import Optional

from pydantic import BaseModel, Field


class PlayerCreate(BaseModel):
    name: str = Field(..., max_length=50)
    pin: str = Field(..., min_length=4, max_length=6)
    role: str = Field(default="player")


class PlayerUpdate(BaseModel):
    status_msg: Optional[str] = Field(default=None, max_length=200)


class PlayerUpdateAdmin(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    status_msg: Optional[str] = Field(default=None, max_length=200)
    photo: Optional[str] = None


class PlayerLockRequest(BaseModel):
    is_locked: bool


class PlayerVisibilityRequest(BaseModel):
    is_dashboard_visible:  bool | None = None


class PlayerListItem(BaseModel):
    id: int
    name: str
    role: str
    status_msg: Optional[str] = None
    last_login: int | None = None
    is_locked:            bool = False
    is_dashboard_visible: bool = True
    photo: Optional[str] = None
    total_points: int = 0

    model_config = {"from_attributes": True}
