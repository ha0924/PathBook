"""画像与行为域 - 用户画像 ORM 模型."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database import Base


class UserProfile(Base):
    """用户画像表 ORM 映射."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # 偏好字段 — JSON 列
    home_cities: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    home_locations: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    transport_preferences: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    food_preferences: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    leisure_preferences: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    frequent_areas: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)

    # 原子字段
    budget_level: Mapped[str] = mapped_column(String(20), default="100-200")
    queue_tolerance_minutes: Mapped[int] = mapped_column(Integer, default=15)
    walking_tolerance_meters: Mapped[int] = mapped_column(Integer, default=1000)

    # 状态标志
    is_initialized: Mapped[bool] = mapped_column(Boolean, default=False)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
