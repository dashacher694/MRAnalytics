"""
Use Case Container for dependency injection.

This module provides the UseCaseContainer that manages all use case dependencies
and their relationships with other containers.
"""

from dependency_injector import providers
from dependency_injector.containers import copy

from src.dependency.uow_container import UnitOfWorkContainer
from src.modules.mr_analytics.usecase.fetch_mrs.impl import FetchMergeRequestsUseCase
from src.modules.mr_analytics.usecase.process_mrs.impl import ProcessMergeRequestsUseCase
from src.modules.mr_analytics.usecase.get_metrics.impl import GetMetricsUseCase
from src.modules.mr_analytics.usecase.get_revision_stats.impl import GetRevisionStatsUseCase
from src.modules.mr_analytics.usecase.run_analysis.impl import RunAnalysisUseCase


@copy(UnitOfWorkContainer)
class UseCaseContainer(UnitOfWorkContainer):
    """
    Use Case Container that inherits from BaseContainer.
    
    This container provides all use case implementations and their dependencies.
    """
    
    # Use case implementations
    
    fetch_mrs_usecase = providers.Factory(
        FetchMergeRequestsUseCase,
        vcs_client=UnitOfWorkContainer.vcs_client,
        uow=UnitOfWorkContainer.query_uow,
    )
    
    process_mrs_usecase = providers.Factory(
        ProcessMergeRequestsUseCase,
        uow=UnitOfWorkContainer.persistence_uow,
    )
    
    get_metrics_usecase = providers.Factory(
        GetMetricsUseCase,
        uow=UnitOfWorkContainer.query_uow,
    )
    
    get_revision_stats_usecase = providers.Factory(
        GetRevisionStatsUseCase,
        uow=UnitOfWorkContainer.query_uow,
    )
    
    run_analysis_usecase = providers.Factory(
        RunAnalysisUseCase,
        fetch_uc=fetch_mrs_usecase,
        process_uc=process_mrs_usecase,
    )
    
    predict_risk_usecase = providers.Factory(
        lambda uow: None,  # Stub
        uow=providers.Factory(lambda: None),
    )
    
    suggest_reviewers_usecase = providers.Factory(
        lambda uow: None,  # Stub
        uow=providers.Factory(lambda: None),
    )
    
    analyze_burnout_usecase = providers.Factory(
        lambda uow: None,  # Stub
        uow=providers.Factory(lambda: None),
    )
