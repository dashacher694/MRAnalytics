"""
SQLAlchemy Base and Session configuration
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from src.core.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass


# For SQLite, we need sync engine for Alembic migrations
sync_engine = create_engine(
    settings.database_url.replace("sqlite:///", "sqlite:///"),
    echo=False
)

# For async operations
if settings.is_sqlite:
    async_engine = create_async_engine(
        settings.database_url.replace("sqlite:///", "sqlite+aiosqlite:///"),
        echo=False
    )
else:
    async_engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


# Session factory
AsyncSessionFactory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Export engine for DI container
engine = async_engine


async def get_session() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionFactory() as session:
        yield session


async def init_db() -> None:
    """Initialize database (create tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
