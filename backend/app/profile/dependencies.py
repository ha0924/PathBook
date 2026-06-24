"""画像与行为域 - FastAPI 依赖注入.

提供 get_current_user，从 Authorization header 解析 JWT 并返回当前用户。
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_db
from app.infra.toolkit.security import decode_access_token
from app.profile import repository
from app.profile.models import User
from app.shared.exceptions import BizError, ErrorCode

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """解析 Bearer token 并返回当前用户.

    Raises:
        BizError: AUTH_TOKEN_INVALID / USER_DISABLED
    """
    if credentials is None:
        raise BizError(ErrorCode.AUTH_TOKEN_INVALID, detail="Missing Authorization header")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise BizError(ErrorCode.AUTH_TOKEN_INVALID, detail="Token decode failed")

    user_id: int | None = payload.get("user_id")
    if user_id is None:
        raise BizError(ErrorCode.AUTH_TOKEN_INVALID, detail="Token payload missing user_id")

    user = await repository.get_user_by_id(db, user_id)
    if user is None:
        raise BizError(ErrorCode.AUTH_TOKEN_INVALID, detail="User not found")
    if not user.is_active:
        raise BizError(ErrorCode.USER_DISABLED)

    return user
