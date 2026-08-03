"""Wagle wire schemas.  Sender and participant identity never come from clients."""
from __future__ import annotations
import json
from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, model_validator

# Conservative, code-enforced resource limits for the R2-B1 service ingress.
# The R2 canonical docs mark resource limits as "no approved values" - these
# are the proposed values enforced here pending PM sign-off (see closeout
# report). Kept deliberately small: this is a display-minimum event envelope,
# never a business-data payload.
SERVICE_ACTION_TYPE_MAX_LENGTH = 60
SERVICE_ACTION_SOURCE_MAX_LENGTH = 100
SERVICE_ACTION_SOURCE_EVENT_ID_MAX_LENGTH = 128
SERVICE_ACTION_SNAPSHOT_MAX_BYTES = 2000


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
    # W7.5 Phase C (2g). The column already existed on `wagle_messages`
    # (unused by any endpoint) -- this is a schema-only exposure, same shape
    # as MembershipSummary/ParticipantResponse's display-name gap.
    reply_to_message_id: UUID | None = None


class ReadStateUpdate(BaseModel):
    last_read_sequence: int = Field(ge=0)


class ParticipantResponse(BaseModel):
    id: UUID
    family_membership_id: int
    account_display_name: str
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


class RoomLastMessagePreview(BaseModel):
    """Just enough of the last message to render a room-list row.

    A deleted message is surfaced as a tombstone with no body, matching
    `message_out()`'s per-message rule — the list must not become a way to read
    content the message endpoint would withhold.
    """
    sequence: int
    message_type: str
    body: str | None
    created_at: datetime
    deleted: bool


class RoomSummaryResponse(BaseModel):
    """One room-list row: the room, the caller's cursor, and its unread count."""
    id: UUID
    family_group_id: int
    room_type: str
    title: str | None
    status: str
    next_message_sequence: int
    updated_at: datetime
    participant_id: UUID
    participant_status: str
    last_read_sequence: int
    unread_count: int
    last_message: RoomLastMessagePreview | None


class MessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    sequence: int
    sender_participant_id: UUID | None
    message_type: str
    body: str | None
    reply_to_message_id: UUID | None = None
    created_at: datetime
    deleted_at: datetime | None
    deleted: bool
    tombstone: str | None = None
    # Populated only for SERVICE_ACTION; service_code is the owning-service
    # reference, service_payload is the display-minimum snapshot. Never the
    # Service Principal's own id/credential.
    service_code: str | None = None
    service_payload_version: int | None = None
    service_payload: dict | None = None
    # W7.5 Phase D SLICE-WAGLE-BOARD-REACTIONS (3e). `reacted_by_me` lets a
    # client render a filled/outline heart without a second round trip.
    reaction_count: int = 0
    reacted_by_me: bool = False


class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    total: None = None
    cursor: dict


class ReadStateResponse(BaseModel):
    participant_id: UUID
    last_read_sequence: int
    unread_count: int
    updated_at: datetime


class ServiceRoomOnboardResponse(BaseModel):
    """Response for self-onboarding into a Family's canonical SERVICE Room.
    Deliberately excludes Binding/Principal internals (id, allowed_actions,
    credential) - a Family member only needs to know their own Room and
    Participant state."""
    room_id: UUID
    family_group_id: int
    service_code: str
    participant_id: UUID
    room_role: str
    status: str
    joined_sequence: int


class ServiceActionPublish(BaseModel):
    """The only shape a Service Principal may submit. There is no client-set
    family_id, sender, sequence, Principal id, or free-form executable payload
    - family_id comes from the URL like every other Wagle endpoint, and only
    an allow-listed action type/version plus a small display snapshot may be
    submitted here."""
    room_id: UUID
    action_type: str = Field(min_length=1, max_length=SERVICE_ACTION_TYPE_MAX_LENGTH)
    schema_version: int = Field(ge=1, le=1000)
    source: str = Field(min_length=1, max_length=SERVICE_ACTION_SOURCE_MAX_LENGTH)
    source_event_id: str = Field(min_length=1, max_length=SERVICE_ACTION_SOURCE_EVENT_ID_MAX_LENGTH)
    snapshot: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_snapshot_size(self):
        size = len(json.dumps(self.snapshot, ensure_ascii=False, separators=(",", ":")))
        if size > SERVICE_ACTION_SNAPSHOT_MAX_BYTES:
            raise ValueError(f"snapshot exceeds {SERVICE_ACTION_SNAPSHOT_MAX_BYTES} byte limit")
        return self


class ReactionToggleResponse(BaseModel):
    """W7.5 Phase D SLICE-WAGLE-BOARD-REACTIONS (3e)."""
    message_id: UUID
    reacted_by_me: bool
    reaction_count: int


class PopularPostOut(BaseModel):
    message_id: UUID
    body: str | None
    author_display_name: str
    created_at: datetime
    reaction_count: int
    comment_count: int
