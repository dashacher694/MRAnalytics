from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.persistance.async_repository import AsyncRepository

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics


class MRMetricsRepository(AsyncRepository[MRMetrics, int]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id: int) -> Optional[MRMetrics]:
        stmt = select(MRMetrics).where(MRMetrics.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[MRMetrics]:
        stmt = select(MRMetrics)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def add(self, entity: MRMetrics) -> MRMetrics:
        self._session.add(entity)
        await self._session.flush()
        return entity
    
    async def update(self, entity: MRMetrics) -> MRMetrics:
        await self._session.merge(entity)
        await self._session.flush()
        return entity
    
    async def delete(self, id: int) -> bool:
        entity = await self.get(id)
        if entity:
            await self._session.delete(entity)
            await self._session.flush()
            return True
        return False


class SQLAlchemyMRMetricsRepository(MRMetricsRepository):
    """SQLAlchemy implementation of MRMetricsRepository"""
    pass
