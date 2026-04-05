from pydantic import BaseModel, Field
from datetime import date as DateType


class MissionTemplateCreate(BaseModel):
    player_id: int
    text: str = Field(max_length=500)
    point: int = Field(ge=0)
    day_of_week: int = Field(default=127, ge=1, le=127)
    group_id: str | None = None


class MissionTemplateUpdate(BaseModel):
    text: str | None = Field(default=None, max_length=500)
    point: int | None = Field(default=None, ge=0)
    day_of_week: int | None = Field(default=None, ge=1, le=127)
    is_active: bool | None = None


class MissionTemplateResponse(BaseModel):
    id: int
    player_id: int
    text: str
    point: int
    day_of_week: int
    is_active: bool
    last_generated_date: DateType | None
    group_id: str | None = None

    model_config = {"from_attributes": True}
