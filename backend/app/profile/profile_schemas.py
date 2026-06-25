"""画像与行为域 - 用户画像 Schema."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ProfileInitRequest(BaseModel):
    """画像初始化请求（onboarding）.

    所有字段 Optional：跳过 onboarding 即全部使用默认值。
    """

    home_cities: Optional[List[str]] = None
    home_locations: Optional[List[str]] = None
    budget_level: Optional[str] = Field(None, max_length=20)
    transport_preferences: Optional[List[str]] = None
    queue_tolerance_minutes: Optional[int] = Field(None, ge=0, le=120)
    walking_tolerance_meters: Optional[int] = Field(None, ge=0, le=5000)
    food_preferences: Optional[List[str]] = None
    leisure_preferences: Optional[List[str]] = None
    frequent_areas: Optional[List[str]] = None


class ProfileUpdateRequest(BaseModel):
    """画像部分更新请求.

    仅传需要修改的字段，未传字段保持原值。
    """

    home_cities: Optional[List[str]] = None
    home_locations: Optional[List[str]] = None
    budget_level: Optional[str] = Field(None, max_length=20)
    transport_preferences: Optional[List[str]] = None
    queue_tolerance_minutes: Optional[int] = Field(None, ge=0, le=120)
    walking_tolerance_meters: Optional[int] = Field(None, ge=0, le=5000)
    food_preferences: Optional[List[str]] = None
    leisure_preferences: Optional[List[str]] = None
    frequent_areas: Optional[List[str]] = None


class ProfileOut(BaseModel):
    """画像完整输出."""

    home_cities: Optional[List[str]]
    home_locations: Optional[List[str]]
    budget_level: str
    transport_preferences: Optional[List[str]]
    queue_tolerance_minutes: int
    walking_tolerance_meters: int
    food_preferences: Optional[List[str]]
    leisure_preferences: Optional[List[str]]
    frequent_areas: Optional[List[str]]
    is_initialized: bool

    model_config = {"from_attributes": True}
