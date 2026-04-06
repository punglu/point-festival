"""Level Tier 스키마"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LevelTierResponse(BaseModel):
    id: int
    job_code: str
    level: int
    title: str
    required_points: int
    icon_path: Optional[str] = None
    milestone_type: Optional[str] = None
    milestone_data: Optional[dict] = None

    model_config = {"from_attributes": True}


class LevelTierCreate(BaseModel):
    job_code: str = Field(default="COMMON", max_length=20)
    level: int = Field(ge=1)
    title: str = Field(max_length=100)
    required_points: int = Field(ge=0)
    icon_path: Optional[str] = None
    milestone_type: Optional[str] = None
    milestone_data: Optional[dict] = None


class LevelTierUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    required_points: Optional[int] = Field(default=None, ge=0)
    icon_path: Optional[str] = None
    milestone_type: Optional[str] = None
    milestone_data: Optional[dict] = None


class LevelTierBulkSave(BaseModel):
    """Admin UI에서 전체 레벨 구간을 한번에 저장할 때 사용"""
    job_code: str = Field(default="COMMON", max_length=20)
    tiers: list[LevelTierCreate]


class PlayerLevelInfo(BaseModel):
    """플레이어의 현재 레벨 정보 (FE ExpBar용)"""
    player_id: int
    total_earned: int
    level: int
    title: str
    current_threshold: int
    next_threshold: int
    progress_percent: int  # 0~100
