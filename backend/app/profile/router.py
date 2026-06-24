"""画像与行为域 - 用户认证路由.

POST /auth/register — 注册
POST /auth/login    — 登录
GET  /auth/me       — 获取当前用户
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_db
from app.profile import service
from app.profile.dependencies import get_current_user
from app.profile.models import User
from app.profile.schemas import LoginRequest, RegisterRequest, TokenOut, UserOut
from app.shared.response import success

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册."""
    user = await service.register(db, username=body.username, password=body.password)
    return success(data=UserOut.model_validate(user).model_dump())


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录."""
    token = await service.login(db, username=body.username, password=body.password)
    return success(data=TokenOut(access_token=token).model_dump())


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息."""
    return success(data=UserOut.model_validate(current_user).model_dump())
