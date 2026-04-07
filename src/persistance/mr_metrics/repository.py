from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics
from .entity import MRMetricsEntity


class MRMetricsRepository(ABC):
    """Abstract repository for MRMetrics"""
    
    @abstractmethod
    async def get_by_iid(self, mr_iid: int) -> Optional[MRMetrics]:
        """Get metrics by MR IID"""
        pass
    
    @abstractmethod
    async def get_by_author(self, author: str) -> List[MRMetrics]:
        """Get metrics by author"""
        pass
    
    @abstractmethod
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MRMetrics]:
        """Get metrics by date range"""
        pass


class SQLAlchemyMRMetricsRepository(MRMetricsRepository):
    """SQLAlchemy implementation of MRMetricsRepository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_iid(self, mr_iid: int) -> Optional[MRMetrics]:
        """Get metrics by MR IID"""
        stmt = select(MRMetricsEntity).where(MRMetricsEntity.mr_iid == mr_iid)
        result = await self._session.execute(stmt)
        entity = result.scalar_one_or_none()
        return entity
    
    async def get_by_author(self, author: str) -> List[MRMetrics]:
        """Get metrics by author"""
        stmt = select(MRMetricsEntity).where(MRMetricsEntity.author == author)
        result = await self._session.execute(stmt)
        entities = result.scalars().all()
        return list(entities)
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MRMetrics]:
        """Get metrics by date range"""
        stmt = select(MRMetricsEntity).where(
            MRMetricsEntity.created_at >= start_date,
            MRMetricsEntity.created_at <= end_date
        )
        result = await self._session.execute(stmt)
        entities = result.scalars().all()
        return list(entities)
