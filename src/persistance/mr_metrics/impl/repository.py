from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics


class MRMetricsRepositoryImpl:
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_iid(self, mr_iid: int) -> Optional[MRMetrics]:
        stmt = select(MRMetrics).where(MRMetrics.mr_iid == mr_iid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_author(self, author: str) -> List[MRMetrics]:
        stmt = select(MRMetrics).where(MRMetrics.author == author)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MRMetrics]:
        stmt = select(MRMetrics).where(
            MRMetrics.created_at >= start_date,
            MRMetrics.created_at <= end_date
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    
