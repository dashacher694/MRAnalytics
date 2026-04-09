from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger

from src.modules.seedwork.base_usecase import BaseUseCase, async_transactional

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics
from src.modules.utils.errors import NotFoundError, BadRequestError
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork
from src.modules.mr_analytics.domain.constants import ValidationLimits
from .command import GetMetricsRequest, GetMetricsResponse


class GetMetricsUseCase(BaseUseCase[QueryUnitOfWork]):
    
    def __init__(self, uow: QueryUnitOfWork) -> None:
        self._uow = uow
    
    @async_transactional(read_only=True)
    async def invoke(self, request: GetMetricsRequest) -> GetMetricsResponse:
        logger.info(f"Получение метрик с фильтрами: mr_iid={request.mr_iid}, author={request.author}, days={request.days}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        
        if request.mr_iid:
            metric = await self.uow.metrics_repository.get_by_iid(request.mr_iid)
            if not metric:
                raise NotFoundError(f"Метрики не найдены для MR IID: {request.mr_iid}")
            metrics = [metric]
        
        elif request.author:
            metrics = await self.uow.metrics_repository.get_by_author(request.author)
            if not metrics:
                raise NotFoundError(f"Метрики не найдены для автора: {request.author}")
        
        elif request.days < ValidationLimits.MIN_DAYS or request.days > ValidationLimits.MAX_DAYS:
            raise BadRequestError(f"Days parameter must be between {ValidationLimits.MIN_DAYS} and {ValidationLimits.MAX_DAYS}, got: {request.days}")
        
        else:
            metrics = await self.uow.metrics_repository.get_by_date_range(start_date, end_date)
            if not metrics:
                raise NotFoundError(f"Метрики не найдены за последние {request.days} дней")
        
        return GetMetricsResponse(
            metrics=[m.__dict__ for m in metrics],
            total=len(metrics)
        )
