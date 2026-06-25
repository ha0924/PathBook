"""接入层 - 路由定义."""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter

from app.profile.profile_router import router as profile_router
from app.profile.router import router as auth_router

router = APIRouter(prefix="/api/v1", tags=["gateway"])

# 挂载用户认证路由
router.include_router(auth_router)

# 挂载用户画像路由
router.include_router(profile_router)


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """简单的 ping 接口，验证网关可达."""
    return {"message": "pong"}
