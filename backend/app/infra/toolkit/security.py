"""基础设施域 - 安全工具.

提供密码哈希和 JWT token 签发/验证能力。
业务层通过此模块完成安全相关操作，不直接依赖第三方 SDK。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import bcrypt
from jose import JWTError, jwt

from app.config import settings

# JWT 配置
_ALGORITHM = "HS256"


# ===== 密码相关 =====


def hash_password(plain_password: str) -> str:
    """将明文密码哈希."""
    pwd_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# ===== JWT 相关 =====


def create_access_token(data: Dict, expires_hours: Optional[int] = None) -> str:
    """签发 JWT access token.

    Args:
        data: payload 数据，通常包含 user_id, username
        expires_hours: 过期时间（小时），默认从配置读取
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        hours=expires_hours or settings.jwt_expire_hours
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict]:
    """验证并解码 JWT token.

    Returns:
        解码后的 payload dict，验证失败返回 None。
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[_ALGORITHM])
        return payload
    except JWTError:
        return None
