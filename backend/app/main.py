"""小路书 - FastAPI 应用入口."""

from fastapi import FastAPI

from app.gateway.error_handler import register_error_handlers
from app.gateway.middleware import RequestContextMiddleware
from app.gateway.router import router as gateway_router
from app.shared.logger import setup_logging
from app.config import settings

# 初始化日志（应用启动时执行一次）
setup_logging(level=settings.log_level)

app = FastAPI(
    title="小路书 PathBook",
    description="AI 驱动的个性化路线规划助手",
    version="0.1.0",
)

# 注册中间件
app.add_middleware(RequestContextMiddleware)

# 注册全局异常处理器
register_error_handlers(app)

# 注册路由
app.include_router(gateway_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查端点."""
    return {"status": "ok"}
