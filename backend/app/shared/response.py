"""跨域共享 - 统一响应格式."""

from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一 API 响应结构."""

    code: int = 0
    data: Any = None
    message: str = "success"
