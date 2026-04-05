from pydantic import BaseModel
from datetime import datetime


class ChatMessageCreate(BaseModel):
    receiver_id: int
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    is_read: bool
    created_at: datetime
    sender_name: str | None = None
    sender_photo: str | None = None

    model_config = {"from_attributes": True}


class ChatPartner(BaseModel):
    player_id: int
    name: str
    photo: str | None
    last_message: str | None
    last_message_at: datetime | None
    unread_count: int
