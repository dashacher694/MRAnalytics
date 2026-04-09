import uuid
from fastapi import APIRouter, Depends, Path
from dependency_injector.wiring import Provide, inject
from starlette import status
from loguru import logger

from src.dependency.container import Container
from src.modules.mr_analytics.usecase.analyze_burnout.impl import AnalyzeBurnoutUseCase
from src.modules.mr_analytics.usecase.analyze_burnout.command import AnalyzeBurnoutRequest

router = APIRouter()


@router.post(
    "/burnout-analysis",
    name="Analyze Reviewer Burnout",
    summary="Анализирует выгорание ревьюеров",
    status_code=status.HTTP_200_OK,
)
@inject
async def analyze_burnout(
    request: AnalyzeBurnoutRequest,
    uc: AnalyzeBurnoutUseCase = Depends(Provide[Container.analyze_burnout_usecase]),
):
    logger.info("API: Начало анализа выгорания")
    
    result = await uc.invoke(request)
    return result
