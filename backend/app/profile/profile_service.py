"""画像与行为域 - 用户画像业务逻辑.

职责：画像初始化（onboarding）、查询、部分更新。
抛 BizError，不关心 HTTP 细节。
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.profile import profile_repository as repo
from app.profile.profile_models import UserProfile
from app.profile.profile_schemas import ProfileInitRequest, ProfileUpdateRequest
from app.shared.exceptions import BizError, ErrorCode
from app.shared.logger import get_logger

logger = get_logger(__name__)


async def init_profile(
    db: AsyncSession, user_id: int, body: ProfileInitRequest
) -> UserProfile:
    """画像初始化（onboarding）.

    Raises:
        BizError: PROFILE_ALREADY_INITIALIZED — 重复初始化
    """
    existing = await repo.get_by_user_id(db, user_id)
    if existing and existing.is_initialized:
        raise BizError(ErrorCode.PROFILE_ALREADY_INITIALIZED)

    # 构建写入数据：仅取客户端实际传入的字段 + 标记 is_initialized
    data = body.model_dump(exclude_unset=True)
    data["is_initialized"] = True

    if existing:
        # 存在未初始化记录（边缘情况），直接更新
        profile = await repo.update_profile(db, existing, data)
    else:
        profile = await repo.create_profile(db, user_id=user_id, **data)

    logger.info(f"Profile initialized: user_id={user_id}")
    return profile


async def get_profile(db: AsyncSession, user_id: int) -> UserProfile:
    """获取当前用户画像.

    Raises:
        BizError: PROFILE_NOT_FOUND — 未初始化
    """
    profile = await repo.get_by_user_id(db, user_id)
    if not profile or not profile.is_initialized:
        raise BizError(ErrorCode.PROFILE_NOT_FOUND)
    return profile


async def update_profile(
    db: AsyncSession, user_id: int, body: ProfileUpdateRequest
) -> UserProfile:
    """部分更新画像字段.

    Raises:
        BizError: PROFILE_NOT_FOUND — 未初始化
    """
    profile = await repo.get_by_user_id(db, user_id)
    if not profile or not profile.is_initialized:
        raise BizError(ErrorCode.PROFILE_NOT_FOUND)

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        return profile  # 没有要更新的字段，直接返回

    profile = await repo.update_profile(db, profile, update_data)
    logger.info(f"Profile updated: user_id={user_id}")
    return profile
