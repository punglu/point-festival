from datetime import datetime
from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    category: str
    title: str
    body: str | None
    read_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}
