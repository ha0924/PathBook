"""小路书 - FastAPI 应用入口."""

from fastapi import FastAPI

from app.gateway.router import router as gateway_router

app = FastAPI(
    title="小路书 PathBook",
    description="AI 驱动的个性化路线规划助手",
    version="0.1.0",
)

app.include_router(gateway_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查端点."""
    return {"status": "ok"}
