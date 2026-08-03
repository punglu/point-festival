from datetime import datetime
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    assignee_membership_id: int | None = None
    due_at: datetime | None = None


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    assignee_membership_id: int | None = None
    due_at: datetime | None = None
    status: str | None = Field(default=None, pattern="^(open|done)$")


class TodoOut(BaseModel):
    id: int
    family_group_id: int
    assignee_membership_id: int | None
    created_by_membership_id: int
    title: str
    status: str
    due_at: datetime | None
    completed_at: datetime | None
    model_config = {"from_attributes": True}
