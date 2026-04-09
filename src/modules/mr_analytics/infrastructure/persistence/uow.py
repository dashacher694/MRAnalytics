from abc import ABC, abstractmethod
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.persistance.mr_metrics.repository import MRMetricsRepository
from src.modules.mr_analytics.infrastructure.persistence.impl.repository import MRMetricsRepositoryImpl


class BaseAsyncUnitOfWork(ABC):
    """Base Unit of Work interface"""
    
    @abstractmethod
    async def __aenter__(self) -> "BaseAsyncUnitOfWork":
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        pass


class AsyncSQLAlchemyUnitOfWork(BaseAsyncUnitOfWork):
    """Async SQLAlchemy Unit of Work implementation"""
    
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._sessionmaker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.session: AsyncSession = None
    
    async def __aenter__(self) -> "AsyncSQLAlchemyUnitOfWork":
        self.session = self._sessionmaker()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()
    
    async def commit(self) -> None:
        await self.session.commit()
    
    async def rollback(self) -> None:
        await self.session.rollback()


class MRPersistenceUnitOfWork(AsyncSQLAlchemyUnitOfWork):
    """MR-specific Unit of Work"""
    
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)
    
    async def __aenter__(self) -> "MRPersistenceUnitOfWork":
        await super().__aenter__()
        self.metrics_repository = MRMetricsRepositoryImpl(self.session)
        return self
