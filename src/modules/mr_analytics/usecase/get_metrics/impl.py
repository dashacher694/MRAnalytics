from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger

from src.modules.seedwork.base_usecase import BaseUseCase, async_transactional

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics
from src.modules.utils.errors import NotFoundError, BadRequestError
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork
from .command import GetMetricsRequest, GetMetricsResponse


class GetMetricsUseCase(BaseUseCase):
    
    def __init__(self, uow: QueryUnitOfWork):
        self.uow = uow
    
    @async_transactional(read_only=True)
    async def invoke(self, request: GetMetricsRequest) -> GetMetricsResponse:
        logger.info(f"Getting metrics with filters: mr_iid={request.mr_iid}, author={request.author}, days={request.days}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        
        if request.mr_iid:
            metric = await self.uow.metrics_repository.get_by_iid(request.mr_iid)
            if not metric:
                raise NotFoundError(f"Metrics not found for MR IID: {request.mr_iid}")
            metrics = [metric]
        
        elif request.author:
            metrics = await self.uow.metrics_repository.get_by_author(request.author)
            if not metrics:
                raise NotFoundError(f"Metrics not found for author: {request.author}")
        
        elif request.days < 1 or request.days > 365:
            raise BadRequestError(f"Days parameter must be between 1 and 365, got: {request.days}")
        
        else:
            metrics = await self.uow.metrics_repository.get_by_date_range(start_date, end_date)
            if not metrics:
                raise NotFoundError(f"No metrics found in the last {request.days} days")
        
        return GetMetricsResponse(
            metrics=[m.__dict__ for m in metrics],
            total=len(metrics)
        )
