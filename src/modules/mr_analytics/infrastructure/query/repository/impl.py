from uuid import UUID
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .protocol import MRMetricsQueryRepository
from src.modules.mr_analytics.domain.aggregate.model import MRMetrics


class SQLAlchemyMRMetricsQueryRepository(MRMetricsQueryRepository):
    """SQLAlchemy implementation of MRMetricsQueryRepository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_all(self) -> List[MRMetrics]:
        """Get all metrics"""
        stmt = select(MRMetrics)
        result = await self._session.execute(stmt)
        entities = result.scalars().all()
        return list(entities)
    
    async def get_by_id(self, metrics_id: UUID) -> Optional[MRMetrics]:
        """Get metrics by ID"""
        stmt = select(MRMetrics).where(MRMetrics.id == metrics_id)
        result = await self._session.execute(stmt)
        entity = result.scalar_one_or_none()
        return entity
    
    async def get_by_iid(self, mr_iid: int) -> Optional[MRMetrics]:
        """Get metrics by MR IID"""
        stmt = select(MRMetrics).where(MRMetrics.mr_iid == mr_iid)
        result = await self._session.execute(stmt)
        entity = result.scalar_one_or_none()
        return entity
    
    async def get_by_author(self, author: str) -> List[MRMetrics]:
        """Get metrics by author"""
        stmt = select(MRMetrics).where(MRMetrics.author == author)
        result = await self._session.execute(stmt)
        entities = result.scalars().all()
        return list(entities)
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MRMetrics]:
        """Get metrics by date range"""
        stmt = select(MRMetrics).where(
            MRMetrics.created_at >= start_date,
            MRMetrics.created_at <= end_date
        )
        result = await self._session.execute(stmt)
        entities = result.scalars().all()
        return list(entities)
