"""基础设施域 - 数据库连接.

提供异步 SQLAlchemy Engine、SessionLocal 工厂和 get_db 依赖注入。
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

# Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """ORM 基类，所有模型继承此类."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：获取数据库 session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """开发模式下 startup 建表（不用 Alembic）."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
