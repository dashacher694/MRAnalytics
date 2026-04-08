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
    
    @abstractmethod
    async def save_all(self, metrics: List[MRMetrics]) -> None:
        """Save multiple metrics"""
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
    
    async def save_all(self, metrics: List[MRMetrics]) -> None:
        """Save multiple metrics"""
        for metric in metrics:
            # Convert aware datetime to naive for database
            created_at = metric.created_at
            if created_at and created_at.tzinfo:
                created_at = created_at.replace(tzinfo=None)
            
            merged_at = metric.merged_at
            if merged_at and merged_at.tzinfo:
                merged_at = merged_at.replace(tzinfo=None)
            
            entity = MRMetricsEntity(
                mr_iid=metric.mr_iid,
                title=metric.title,
                author=metric.author,
                created_at=created_at,
                merged_at=merged_at,
                web_url=metric.web_url,
                additions=metric.additions,
                deletions=metric.deletions,
                time_to_merge=metric.time_to_merge,
                review_rounds=metric.review_rounds,
                comment_density=metric.comment_density,
                formal_approval=metric.formal_approval,
                response_time_hours=metric.response_time_hours,
                num_comments=metric.num_comments,
                num_approvals=metric.num_approvals
            )
            self._session.add(entity)
        await self._session.flush()
