from datetime import datetime
from pydantic import BaseModel


class ActivityLogEntryOut(BaseModel):
    actor_membership_id: int | None
    actor_display_name: str | None
    action: str
    aggregate_type: str
    payload: dict
    occurred_at: datetime
