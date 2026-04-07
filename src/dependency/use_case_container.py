from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from src.core.containers import BaseContainer
from src.dependency.uow_container import UnitOfWorkContainer
from src.modules.mr_analytics.usecase.process_mrs.impl import ProcessMergeRequestsUseCase
from src.modules.mr_analytics.usecase.get_metrics.impl import GetMetricsUseCase
from src.modules.mr_analytics.usecase.predict_risk.impl import PredictRiskUseCase
from src.modules.mr_analytics.usecase.suggest_reviewers.impl import SuggestReviewersUseCase
from src.modules.mr_analytics.usecase.analyze_burnout.impl import AnalyzeBurnoutUseCase
from src.modules.mr_analytics.application.services import MRAnalyticsService


class UseCaseContainer(DeclarativeContainer):
    
    base = providers.DependenciesContainer(BaseContainer)
    uow = providers.DependenciesContainer(UnitOfWorkContainer)
    
    analytics_service = providers.Factory(MRAnalyticsService)
    
    fetch_mrs_usecase = providers.Factory(
        FetchMergeRequestsUseCase,
        vcs_client=base.vcs_client,
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
