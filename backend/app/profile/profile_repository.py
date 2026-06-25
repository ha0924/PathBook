"""画像与行为域 - 用户画像数据访问层.

纯数据访问，不含业务判断。
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.profile.profile_models import UserProfile


async def get_by_user_id(db: AsyncSession, user_id: int) -> Optional[UserProfile]:
    """根据 user_id 查询画像."""
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def exists_initialized(db: AsyncSession, user_id: int) -> bool:
    """判断用户画像是否已初始化（用于 has_profile）."""
    stmt = select(UserProfile.id).where(
        UserProfile.user_id == user_id,
        UserProfile.is_initialized.is_(True),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def create_profile(db: AsyncSession, user_id: int, **kwargs) -> UserProfile:
    """创建用户画像."""
    profile = UserProfile(user_id=user_id, **kwargs)
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


async def update_profile(
    db: AsyncSession, profile: UserProfile, update_data: dict
) -> UserProfile:
    """更新画像字段（传入已过滤的 dict）."""
    for key, value in update_data.items():
        setattr(profile, key, value)
    await db.flush()
    await db.refresh(profile)
    return profile
