from typing import Optional

from pydantic import BaseModel, Field


class PlayerUpdate(BaseModel):
    status_msg: Optional[str] = Field(default=None, max_length=200)


class PlayerUpdateAdmin(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    status_msg: Optional[str] = Field(default=None, max_length=200)
    photo: Optional[str] = None


class PlayerLockRequest(BaseModel):
    is_locked: bool


class PlayerListItem(BaseModel):
    id: int
    name: str
    role: str
    last_login: int | None = None
    is_locked: bool = False

    model_config = {"from_attributes": True}
