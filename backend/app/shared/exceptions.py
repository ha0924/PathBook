"""跨域共享 - 统一异常定义.

业务层只需 raise BizError(ErrorCode.XXX)，
全局异常处理器负责翻译 message、推导 HTTP status、记录日志。
"""

from __future__ import annotations

from enum import IntEnum
from typing import Optional


class ErrorCode(IntEnum):
    """业务错误码枚举 - 按域分段分配.

    分段规则：
    - 10xxx: 通用错误
    - 400xx: 用户/业务错误 → HTTP 400
    - 401xx: 认证错误 → HTTP 401
    - 403xx: 权限错误 → HTTP 403
    - 500xx: 路线域（预留）→ HTTP 400
    """

    # ===== 通用 10xxx =====
    UNKNOWN = 10000
    VALIDATION_ERROR = 10001
    INTERNAL_ERROR = 10002

    # ===== 用户/业务 400xx =====
    USER_ALREADY_EXISTS = 40001
    USER_NOT_FOUND = 40002
    USER_DISABLED = 40003
    USER_PASSWORD_TOO_SHORT = 40004

    # ===== 画像 400xx =====
    PROFILE_ALREADY_INITIALIZED = 40005
    PROFILE_NOT_FOUND = 40006

    # ===== 认证鉴权 401xx =====
    AUTH_INVALID_CREDENTIALS = 40101
    AUTH_TOKEN_EXPIRED = 40102
    AUTH_TOKEN_INVALID = 40103

    # ===== 权限 403xx =====
    AUTH_PERMISSION_DENIED = 40301


class BizError(Exception):
    """业务异常基类.

    用法：
        raise BizError(ErrorCode.USER_ALREADY_EXISTS)
        raise BizError(ErrorCode.AUTH_TOKEN_EXPIRED, detail="token 签名不匹配")
    """

    def __init__(self, code: ErrorCode, detail: Optional[str] = None) -> None:
        self.code = code
        self.detail = detail  # 仅开发环境返回，生产隐藏
        super().__init__(f"[{code.value}] {code.name}")
