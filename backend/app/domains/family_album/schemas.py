from datetime import datetime
from pydantic import BaseModel, Field


class AlbumCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class AlbumUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    shared_with_membership_ids: list[int] | None = None


class AlbumOut(BaseModel):
    id: int
    family_group_id: int
    created_by_membership_id: int
    title: str
    shared_with_membership_ids: list[int] | None
    photo_count: int
    model_config = {"from_attributes": True}


class PhotoCreate(BaseModel):
    caption: str | None = Field(default=None, max_length=200)
    taken_at: datetime | None = None


class PhotoOut(BaseModel):
    id: int
    album_id: int
    uploaded_by_membership_id: int
    caption: str | None
    taken_at: datetime | None
    model_config = {"from_attributes": True}
