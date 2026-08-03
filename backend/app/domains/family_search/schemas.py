from datetime import datetime
from pydantic import BaseModel


class SearchResultItem(BaseModel):
    source: str  # "mission" | "message"
    title: str
    meta: str
    occurred_at: datetime
