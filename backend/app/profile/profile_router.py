"""画像与行为域 - 用户画像路由.

POST /init — 画像初始化（onboarding）
GET  /      — 获取当前用户画像
PATCH /     — 部分更新画像
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_db
from app.profile import profile_service
from app.profile.dependencies import get_current_user
from app.profile.models import User
from app.profile.profile_schemas import ProfileInitRequest, ProfileOut, ProfileUpdateRequest
from app.shared.response import success

router = APIRouter(prefix="/user/profile", tags=["profile"])


@router.post("/init")
async def init_profile(
    body: ProfileInitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """画像初始化（onboarding）."""
    profile = await profile_service.init_profile(db, user_id=current_user.id, body=body)
    return success(data=ProfileOut.model_validate(profile).model_dump())


@router.get("")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户画像."""
    profile = await profile_service.get_profile(db, user_id=current_user.id)
    return success(data=ProfileOut.model_validate(profile).model_dump())


@router.patch("")
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """部分更新画像."""
    profile = await profile_service.update_profile(db, user_id=current_user.id, body=body)
    return success(data=ProfileOut.model_validate(profile).model_dump())
