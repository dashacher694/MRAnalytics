from typing import List, Dict, Any
from loguru import logger

from src.modules.seedwork.base_usecase import BaseUseCase, async_transactional

from src.modules.mr_analytics.domain.aggregate.model import MRMetrics
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork
from src.modules.mr_analytics.application.analytics_services import BurnoutAnalyticsService
from src.modules.mr_analytics.usecase.analyze_burnout.command import AnalyzeBurnoutRequest, BurnoutResponse
from src.modules.mr_analytics.infrastructure.dto import ReviewerProfile as DTOReviewerProfile


class AnalyzeBurnoutUseCase(BaseUseCase[QueryUnitOfWork]):
    
    def __init__(self, uow: QueryUnitOfWork) -> None:
        self._uow = uow
    
    @async_transactional(read_only=True)
    async def invoke(self, request: AnalyzeBurnoutRequest) -> BurnoutResponse:
        logger.info("Analyzing team reviewer burnout")
        
        profiles = []
        for profile_data in request.team_profiles:
            profiles.append(ReviewerProfile(**profile_data))
        
        burnout_scores = {}
        for profile in profiles:
            burnout_scores[profile.name] = BurnoutAnalyticsService.calculate_burnout_index(profile)
        
        high_risk = [name for name, score in burnout_scores.items() if score >= 0.8]
        
        team_avg = sum(burnout_scores.values()) / len(burnout_scores) if burnout_scores else 0.0
        
        logger.warning(f"Found {len(high_risk)} reviewers with high burnout index")
        
        return BurnoutResponse(
            team_burnout_avg=team_avg,
            high_risk_reviewers=high_risk,
            burnout_scores=burnout_scores
        )
