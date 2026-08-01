from datetime import date, datetime
from pydantic import BaseModel, Field

class MissionCreate(BaseModel):
    assignee_membership_id: int
    title: str = Field(min_length=1, max_length=200)
    scheduled_for: date
    reward_amount: int = Field(ge=0)

class MissionDecision(BaseModel):
    reason: str | None = Field(default=None, max_length=300)

class PointAdjustment(BaseModel):
    beneficiary_membership_id: int
    amount: int
    reason: str = Field(min_length=1, max_length=300)
    idempotency_key: str = Field(min_length=1, max_length=160)

class TemplateCreate(BaseModel):
    assignee_membership_id: int; title: str = Field(min_length=1,max_length=200); reward_amount: int = Field(ge=0)
    cycle_type: str = "weekly"; start_date: date; end_date: date | None = None; day_of_week: int | None = Field(default=None,ge=0,le=6)
class TemplateUpdate(BaseModel):
    title: str | None = Field(default=None,min_length=1,max_length=200); reward_amount: int | None = Field(default=None,ge=0)
    end_date: date | None = None; day_of_week: int | None = Field(default=None,ge=0,le=6)
class TemplateOut(BaseModel):
    id:int; family_group_id:int; assignee_membership_id:int; title:str; reward_amount:int; cycle_type:str; start_date:date; end_date:date|None; day_of_week:int|None; status:str
    model_config={"from_attributes":True}

class MissionOut(BaseModel):
    id: int; family_group_id: int; assignee_membership_id: int; title: str; scheduled_for: date; reward_amount: int; status: str
    model_config = {"from_attributes": True}

class LedgerOut(BaseModel):
    id: int; family_group_id: int; family_membership_id: int; amount: int; entry_type: str; source_type: str; source_identifier: str; reason: str | None; occurred_at: datetime
    model_config = {"from_attributes": True}

class BalanceOut(BaseModel):
    family_group_id: int; family_membership_id: int; current_balance: int; lifetime_earned: int; lifetime_spent: int; version: int
    model_config = {"from_attributes": True}

class LevelOut(BaseModel):
    family_group_id: int; family_membership_id: int; lifetime_earned: int; level: int; title: str; current_threshold: int; next_threshold: int; progress_percent: int


class CycleConfigUpdate(BaseModel):
    cycle_type: str | None = None
    display_name: str | None = None


class CycleConfigOut(BaseModel):
    family_group_id: int
    cycle_type: str
    effective_from: date
    effective_to: date
    display_name: str | None = None
    configured: bool


class DeductionCorrection(BaseModel):
    # None cancels the deduction outright (reversal only). A negative value
    # replaces it. Zero is rejected by the service — a zero-amount debit is a
    # cancellation wearing a replacement's clothes.
    new_amount: int | None = None
    reason: str


class BulkApproval(BaseModel):
    mission_ids: list[int]
