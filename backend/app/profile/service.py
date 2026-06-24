"""画像与行为域 - 用户认证业务逻辑.

职责：注册查重 → 哈希密码 → 存库；登录验证 → 签发 JWT。
抛 BizError，不关心 HTTP 细节。
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.toolkit.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.profile import repository
from app.profile.models import User
from app.shared.exceptions import BizError, ErrorCode


async def register(db: AsyncSession, username: str, password: str) -> User:
    """用户注册.

    Raises:
        BizError: USER_ALREADY_EXISTS / USER_PASSWORD_TOO_SHORT
    """
    if len(password) < 6:
        raise BizError(ErrorCode.USER_PASSWORD_TOO_SHORT)

    existing = await repository.get_user_by_username(db, username)
    if existing:
        raise BizError(ErrorCode.USER_ALREADY_EXISTS)

    hashed = hash_password(password)
    user = await repository.create_user(db, username=username, password_hash=hashed)
    return user


async def login(db: AsyncSession, username: str, password: str) -> str:
    """用户登录，返回 access_token.

    Raises:
        BizError: AUTH_INVALID_CREDENTIALS / USER_DISABLED
    """
    user = await repository.get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise BizError(ErrorCode.AUTH_INVALID_CREDENTIALS)

    if not user.is_active:
        raise BizError(ErrorCode.USER_DISABLED)

    token = create_access_token(data={"user_id": user.id, "username": user.username})
    return token


async def get_me(db: AsyncSession, user_id: int) -> User:
    """获取当前用户信息.

    Raises:
        BizError: AUTH_TOKEN_INVALID (用户不存在时)
    """
    user = await repository.get_user_by_id(db, user_id)
    if not user:
        raise BizError(ErrorCode.AUTH_TOKEN_INVALID)
    if not user.is_active:
        raise BizError(ErrorCode.USER_DISABLED)
    return user
