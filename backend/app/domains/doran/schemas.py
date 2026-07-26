"""Doran wire schemas.  Sender and participant identity never come from clients."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class RoomCreate(BaseModel):
    room_type: Literal["DIRECT", "GROUP", "SERVICE"]
    title: str | None = Field(default=None, max_length=200)
    target_membership_id: int | None = None
    participant_membership_ids: list[int] = Field(default_factory=list, max_length=49)

    @model_validator(mode="after")
    def validate_shape(self):
        if self.room_type == "DIRECT" and self.target_membership_id is None:
            raise ValueError("DIRECT room requires target_membership_id")
        if self.room_type == "GROUP" and not self.title:
            raise ValueError("GROUP room requires title")
        return self


class RoomUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    status: Literal["active", "read_only", "closed"] | None = None


class ParticipantCreate(BaseModel):
    family_membership_id: int
    room_role: Literal["room_admin", "member"] = "member"


class MessageCreate(BaseModel):
    client_message_id: str = Field(min_length=1, max_length=64)
    body: str = Field(min_length=1, max_length=4000)


class ReadStateUpdate(BaseModel):
    last_read_sequence: int = Field(ge=0)


class ParticipantResponse(BaseModel):
    id: UUID
    family_membership_id: int
    room_role: str
    status: str
    joined_sequence: int
    left_sequence: int | None
    joined_at: datetime
    left_at: datetime | None

    model_config = {"from_attributes": True}


class RoomResponse(BaseModel):
    id: UUID
    family_group_id: int
    room_type: str
    title: str | None
    status: str
    next_message_sequence: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    sequence: int
    sender_participant_id: UUID | None
    message_type: str
    body: str | None
    created_at: datetime
    deleted_at: datetime | None
    deleted: bool
    tombstone: str | None = None


class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    total: None = None
    cursor: dict


class ReadStateResponse(BaseModel):
    participant_id: UUID
    last_read_sequence: int
    unread_count: int
    updated_at: datetime
