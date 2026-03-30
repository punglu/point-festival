from typing import Optional
from pydantic import BaseModel


class ConfigUpdate(BaseModel):
    value: Optional[str] = None


class ConfigResponse(BaseModel):
    id: int
    key: str
    value: Optional[str]

    model_config = {"from_attributes": True}
