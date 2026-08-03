from datetime import datetime
from pydantic import BaseModel, Field


class RewardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    cost: int = Field(ge=0)


class RewardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    cost: int | None = Field(default=None, ge=0)
    is_available: bool | None = None


class RewardOut(BaseModel):
    id: int
    family_group_id: int
    name: str
    cost: int
    is_available: bool
    model_config = {"from_attributes": True}


class RedemptionRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=160)


class RedemptionOut(BaseModel):
    id: int
    reward_item_id: int
    redeemed_by_membership_id: int
    cost_at_redemption: int
    ledger_entry_id: int
    redeemed_at: datetime
    model_config = {"from_attributes": True}
