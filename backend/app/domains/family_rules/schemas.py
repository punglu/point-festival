from pydantic import BaseModel, Field


class FamilyRuleEntry(BaseModel):
    category: str = Field(pattern="^(life|point)$")
    label: str = Field(min_length=1, max_length=100)
    value_text: str = Field(min_length=1, max_length=200)


class FamilyRulesReplace(BaseModel):
    rules: list[FamilyRuleEntry] = Field(max_length=50)


class FamilyRuleOut(BaseModel):
    id: int
    family_group_id: int
    category: str
    label: str
    value_text: str
    sort_order: int
    model_config = {"from_attributes": True}
