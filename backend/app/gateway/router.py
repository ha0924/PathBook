"""接入层 - 路由定义."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["gateway"])


@router.get("/ping")
async def ping() -> dict[str, str]:
    """简单的 ping 接口，验证网关可达."""
    return {"message": "pong"}
