from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
from starlette import status
from loguru import logger

from src.dependency.container import Container
router = APIRouter()
from src.modules.mr_analytics.usecase.fetch_mrs.impl import FetchMergeRequestsUseCase
from src.modules.mr_analytics.usecase.fetch_mrs.command import (
    FetchMergeRequestsCommand,
    FetchMergeRequestsResponse
)


@router.post(
    "/fetch-mrs",
    response_model=FetchMergeRequestsResponse,
    name="Fetch Merge Requests",
    summary="Загружает MR из VCS (GitLab/GitHub)",
    status_code=status.HTTP_200_OK,
)
@inject
async def fetch_merge_requests(
    days: int = 30,
    uc: FetchMergeRequestsUseCase = Depends(Provide[Container.fetch_mrs_usecase]),
) -> FetchMergeRequestsResponse:
    logger.info(f"API: Загрузка MR за последние {days} дней")
    
    command = FetchMergeRequestsCommand(days=days)
    result = await uc.invoke(command)
    
    return result
