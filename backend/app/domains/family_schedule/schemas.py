from datetime import datetime
from pydantic import BaseModel, Field


class ScheduleEventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    starts_at: datetime
    location: str | None = Field(default=None, max_length=200)
    memo: str | None = Field(default=None, max_length=2000)
    attendee_membership_ids: list[int] | None = Field(default=None, max_length=8)
    visibility: str = Field(default="family", pattern="^(family|private)$")


class ScheduleEventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    starts_at: datetime | None = None
    location: str | None = Field(default=None, max_length=200)
    memo: str | None = Field(default=None, max_length=2000)
    attendee_membership_ids: list[int] | None = Field(default=None, max_length=8)
    visibility: str | None = Field(default=None, pattern="^(family|private)$")


class ScheduleEventOut(BaseModel):
    id: int
    family_group_id: int
    created_by_membership_id: int
    title: str
    starts_at: datetime
    location: str | None
    memo: str | None
    attendee_membership_ids: list[int] | None
    visibility: str
    model_config = {"from_attributes": True}
