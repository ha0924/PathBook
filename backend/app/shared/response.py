"""跨域共享 - 统一响应格式.

所有接口返回结构：{ "code": 0, "data": ..., "message": "success" }
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def success(data: Any = None, message: str = "success") -> Dict[str, Any]:
    """成功响应."""
    return {"code": 0, "data": data, "message": message}


def fail(code: int, message: str, detail: Optional[str] = None) -> Dict[str, Any]:
    """失败响应（由全局异常处理器调用，业务层不直接使用）."""
    resp: Dict[str, Any] = {"code": code, "data": None, "message": message}
    if detail:
        resp["detail"] = detail
    return resp
