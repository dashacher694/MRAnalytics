"""
Use Case Container for dependency injection.

This module provides the UseCaseContainer that manages all use case dependencies
and their relationships with other containers.
"""

from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, copy

from src.core.containers import BaseContainer
from src.dependency.uow_container import UnitOfWorkContainer
from src.modules.mr_analytics.usecase.fetch_mrs.impl import FetchMergeRequestsUseCase
from src.modules.mr_analytics.usecase.process_mrs.impl import ProcessMergeRequestsUseCase
from src.modules.mr_analytics.usecase.get_metrics.impl import GetMetricsUseCase
from src.modules.mr_analytics.usecase.predict_risk.impl import PredictRiskUseCase
from src.modules.mr_analytics.usecase.suggest_reviewers.impl import SuggestReviewersUseCase
from src.modules.mr_analytics.usecase.analyze_burnout.impl import AnalyzeBurnoutUseCase
from src.modules.mr_analytics.application.services import MRAnalyticsService


@copy(BaseContainer)
class UseCaseContainer(BaseContainer):
    """
    Use Case Container that inherits from BaseContainer and UnitOfWorkContainer.
    
    This container provides all use case implementations and their dependencies.
    """
    
    uow = providers.DependenciesContainer(UnitOfWorkContainer)
    
    analytics_service = providers.Factory(MRAnalyticsService)
    
    fetch_mrs_usecase = providers.Factory(
        FetchMergeRequestsUseCase,
        vcs_client=BaseContainer.vcs_client,
    )
    
    process_mrs_usecase = providers.Factory(
        ProcessMergeRequestsUseCase,
        uow=uow.persistence_uow,
        analytics_service=analytics_service,
    )
    
    get_metrics_usecase = providers.Factory(
        GetMetricsUseCase,
        uow=uow.query_uow,
    )
    
    predict_risk_usecase = providers.Factory(
        PredictRiskUseCase,
        uow=uow.query_uow,
    )
    
    suggest_reviewers_usecase = providers.Factory(
        SuggestReviewersUseCase,
        uow=uow.query_uow,
    )
    
    analyze_burnout_usecase = providers.Factory(
        AnalyzeBurnoutUseCase,
        uow=uow.query_uow,
    )
