from datetime import datetime, timedelta
from typing import List, Dict
from loguru import logger

from src.modules.seedwork.base_usecase import BaseUseCase, async_transactional
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork
from src.modules.mr_analytics.usecase.get_revision_stats.command import (
    GetRevisionStatsRequest,
    GetRevisionStatsResponse
)


class GetRevisionStatsUseCase(BaseUseCase[QueryUnitOfWork]):
    
    def __init__(self, uow: QueryUnitOfWork) -> None:
        self._uow = uow
    
    @async_transactional(read_only=True)
    async def invoke(self, request: GetRevisionStatsRequest) -> GetRevisionStatsResponse:
        logger.info(f"Получение статистики ревизий за последние {request.days} дней")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        
        async with self.uow:
            if request.author:
                metrics = await self.uow.repository.get_by_author(request.author)
            else:
                metrics = await self.uow.repository.get_by_date_range(start_date, end_date)
        
        if not metrics:
            return GetRevisionStatsResponse(
                total_mrs=0,
                mrs_with_changes_requested=0,
                mrs_without_changes_requested=0,
                changes_requested_rate=0.0,
                total_changes_requested=0,
                avg_changes_per_mr=0.0,
                author_stats={}
            )
        
        total_mrs = len(metrics)
        mrs_with_changes = sum(1 for m in metrics if m.changes_requested > 0)
        mrs_without_changes = total_mrs - mrs_with_changes
        total_changes = sum(m.changes_requested for m in metrics)
        
        author_stats = {}
        for metric in metrics:
            if metric.author not in author_stats:
                author_stats[metric.author] = {
                    'total_mrs': 0,
                    'changes_requested': 0,
                    'mrs_with_changes': 0
                }
            
            author_stats[metric.author]['total_mrs'] += 1
            author_stats[metric.author]['changes_requested'] += metric.changes_requested
            if metric.changes_requested > 0:
                author_stats[metric.author]['mrs_with_changes'] += 1
        
        for author_data in author_stats.values():
            if author_data['total_mrs'] > 0:
                author_data['changes_requested_rate'] = (
                    author_data['mrs_with_changes'] / author_data['total_mrs']
                )
                author_data['avg_changes_per_mr'] = (
                    author_data['changes_requested'] / author_data['total_mrs']
                )
            else:
                author_data['changes_requested_rate'] = 0.0
                author_data['avg_changes_per_mr'] = 0.0
        
        return GetRevisionStatsResponse(
            total_mrs=total_mrs,
            mrs_with_changes_requested=mrs_with_changes,
            mrs_without_changes_requested=mrs_without_changes,
            changes_requested_rate=(mrs_with_changes / total_mrs) if total_mrs > 0 else 0.0,
            total_changes_requested=total_changes,
            avg_changes_per_mr=(total_changes / total_mrs) if total_mrs > 0 else 0.0,
            author_stats=author_stats
        )
