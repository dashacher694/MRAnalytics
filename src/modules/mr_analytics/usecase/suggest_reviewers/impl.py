from typing import List, Dict, Any
from loguru import logger

from src.modules.seedwork.base_usecase import BaseUseCase, async_transactional

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics
from src.modules.utils.errors import NotFoundError, BadRequestError
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork
from src.modules.mr_analytics.application.analytics_services import ReviewerRecommendationService
from .command import SuggestReviewersRequest, SuggestReviewersResponse
from src.modules.mr_analytics.infrastructure.dto import ReviewerSuggestion, ReviewerProfile


class SuggestReviewersUseCase(BaseUseCase[QueryUnitOfWork]):
    
    def __init__(self, uow: QueryUnitOfWork) -> None:
        self._uow = uow
    
    @async_transactional(read_only=True)
    async def invoke(self, request: SuggestReviewersRequest) -> SuggestReviewersResponse:
        logger.info(f"Предложение ревьюеров для MR {request.mr_iid}")
        
        mr = await self.uow.metrics_repository.get_by_iid(request.mr_iid)
        if not mr:
            raise ValueError(f"MR {request.mr_iid} не найден")
        
        profiles = []
        for profile_data in request.team_profiles:
            profiles.append(ReviewerProfile(**profile_data))
        
        suggestions = ReviewerRecommendationService.suggest_reviewers(mr, profiles)
        
        reviewer_suggestions = [
            ReviewerSuggestion(
                reviewer=s.reviewer,
                score=s.score,
                reasoning=s.reasoning
            )
            for s in suggestions
        ]
        
        return SuggestReviewersResponse(
            mr_iid=request.mr_iid,
            suggestions=reviewer_suggestions
        )
