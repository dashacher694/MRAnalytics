import uuid
from fastapi import APIRouter, Depends, Query, Path
from dependency_injector.wiring import Provide, inject
from starlette import status
from loguru import logger

from src.dependency.container import Container
from src.modules.mr_analytics.usecase.predict_risk.impl import PredictRiskUseCase

router = APIRouter()


@router.get(
    "/risk-prediction",
    name="Predict MR Risks",
    summary="Прогнозирует риски Merge Request",
    status_code=status.HTTP_200_OK,
)
@inject
async def predict_risk(
    days: int = Query(default=30, ge=1, le=365, description="Days to analyze"),
    uc: PredictRiskUseCase = Depends(Provide[Container.predict_risk_usecase]),
):
    logger.info(f"API: Запрос прогнозирования рисков на {days} дней")
    
    result = await uc.invoke(days)
    return result
