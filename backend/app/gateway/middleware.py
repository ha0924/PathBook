"""接入层 - 请求中间件.

职责：
1. 为每个请求生成唯一 request_id
2. 记录请求耗时
3. 解析 Accept-Language 设置到 request.state
"""

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.shared.logger import get_logger

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 生成 request_id
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # 解析语言偏好
        accept_language = request.headers.get("Accept-Language", "zh_CN")
        request.state.locale = "en_US" if "en" in accept_language else "zh_CN"

        # 记录请求开始
        start_time = time.perf_counter()

        response = await call_next(request)

        # 记录请求耗时
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)",
            extra={"request_id": request_id},
        )

        # 响应头带上 request_id，方便排查
        response.headers["X-Request-ID"] = request_id
        return response
