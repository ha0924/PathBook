"""接入层 - 路由定义."""

from fastapi import APIRouter

from app.profile.router import router as auth_router

router = APIRouter(prefix="/api/v1", tags=["gateway"])

# 挂载用户认证路由
router.include_router(auth_router)


@router.get("/ping")
async def ping() -> dict[str, str]:
    """简单的 ping 接口，验证网关可达."""
    return {"message": "pong"}
