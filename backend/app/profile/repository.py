"""画像与行为域 - 数据访问层.

纯数据访问，不含业务判断。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.profile.models import User


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """根据用户名查询用户."""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """根据 ID 查询用户."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, password_hash: str) -> User:
    """创建新用户并返回."""
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    await db.flush()  # 拿到自增 id
    await db.refresh(user)
    return user
