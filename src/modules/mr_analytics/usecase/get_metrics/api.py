from typing import List, Optional
import uuid
from fastapi import APIRouter, Query, Depends, Path
from dependency_injector.wiring import Provide, inject
from starlette import status
from loguru import logger

from src.dependency.container import Container
from src.modules.mr_analytics.usecase.get_metrics.impl import GetMetricsUseCase
from src.modules.mr_analytics.usecase.get_metrics.command import GetMetricsRequest
from src.modules.mr_analytics.infrastructure.query.dto import MRMetricsResponse, MRMetricsListResponse
from src.modules.mr_analytics.usecase import router


@router.get(
    "/metrics",
    response_model=MRMetricsListResponse,
    name="Get MR Metrics",
    summary="Получает метрики Merge Request",
    status_code=status.HTTP_200_OK,
)
@inject
async def get_metrics(
    mr_iid: Optional[int] = Query(default=None, description="Filter by MR IID"),
    author: Optional[str] = Query(default=None, description="Filter by author"),
    days: int = Query(default=30, ge=1, le=365, description="Filter by last N days"),
    uc: GetMetricsUseCase = Depends(Provide[Container.get_metrics_usecase]),
) -> MRMetricsListResponse:
    """
    # Получает метрики Merge Request.

    Метод для получения метрик Merge Request с возможностью фильтрации.

    ___

    #### Успешный ответ:
    Отдает 200 с списком метрик MR в формате MRMetricsListResponse

    #### Ошибки:
    - 400 Bad Request: Некорректный запрос или неверный формат данных.
    - 404 Not Found: MR с указанным IID не найден.
    - 404 Not Found: Отсутствуют метрики для указанного автора.
    - 404 Not Found: Отсутствуют метрики за указанный период.
    - 500 Internal Server Error: Внутренняя ошибка сервера.
    """
    
    logger.info(f"API: Getting metrics with filters: mr_iid={mr_iid}, author={author}, days={days}")
    
    request = GetMetricsRequest(mr_iid=mr_iid, author=author, days=days)
    result = await uc.invoke(request)
    
    return MRMetricsListResponse(
        data=[MRMetricsResponse.model_validate(m) for m in result.metrics],
        total=result.total
    )
