"""
Комплексный API эндпоинт для автоматического сбора и анализа MR
"""
from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
from starlette import status

from src.dependency.container import Container
router = APIRouter()
from src.modules.mr_analytics.usecase.run_analysis.impl import RunAnalysisUseCase
from src.modules.mr_analytics.usecase.run_analysis.command import RunAnalysisCommand


@router.post(
    "/run-analysis",
    name="Run Full MR Analysis",
    summary="",
    status_code=status.HTTP_200_OK,
)
@inject
async def run_full_analysis(
    days: int = 30,
    uc: RunAnalysisUseCase = Depends(Provide[Container.run_analysis_usecase]),
):
    command = RunAnalysisCommand(days=days)
    result = await uc.invoke(command)
    return result
