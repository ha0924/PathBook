"""跨域共享 - 统一响应格式.

所有接口返回结构：{ "code": 0, "data": ..., "message": "success" }
"""

from typing import Any


def success(data: Any = None, message: str = "success") -> dict[str, Any]:
    """成功响应."""
    return {"code": 0, "data": data, "message": message}


def fail(code: int, message: str, detail: str | None = None) -> dict[str, Any]:
    """失败响应（由全局异常处理器调用，业务层不直接使用）."""
    resp: dict[str, Any] = {"code": code, "data": None, "message": message}
    if detail:
        resp["detail"] = detail
    return resp
