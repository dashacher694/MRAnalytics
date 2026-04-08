from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import Provide, inject

from src.dependency.container import Container
from src.modules.mr_analytics.usecase.get_revision_stats.command import GetRevisionStatsRequest
from src.modules.mr_analytics.usecase.get_revision_stats.impl import GetRevisionStatsUseCase


router = APIRouter(prefix="/revision-stats", tags=["Revision Statistics"])


@router.get(
    "/",
    name="Get Revision Statistics",
    summary="Get statistics about MRs sent back for changes",
    status_code=200,
)
@inject
async def get_revision_stats(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    author: str = Query(default=None, description="Filter by specific author"),
    uc: GetRevisionStatsUseCase = Depends(Provide[Container.get_revision_stats_usecase]),
):
    """Get revision statistics for MRs"""
    request = GetRevisionStatsRequest(days=days, author=author)
    result = await uc.invoke(request)
    return result
