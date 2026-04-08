"""
Use Case Container for dependency injection.

This module provides the UseCaseContainer that manages all use case dependencies
and their relationships with other containers.
"""

from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, copy

from src.core.containers import BaseContainer
from src.dependency.uow_container import UnitOfWorkContainer


@copy(BaseContainer)
class UseCaseContainer(BaseContainer):
    """
    Use Case Container that inherits from BaseContainer.
    
    This container provides all use case implementations and their dependencies.
    """
    
    # Create stub implementations to avoid import errors
    # These will be replaced with actual implementations later
    
    analytics_service = providers.Factory(lambda: None)  # Stub
    
    fetch_mrs_usecase = providers.Factory(
        lambda vcs_client: None,  # Stub
        vcs_client=BaseContainer.vcs_client,
    )
    
    process_mrs_usecase = providers.Factory(
        lambda uow, service: None,  # Stub
        uow=providers.Factory(lambda: None),
        service=analytics_service,
    )
    
    get_metrics_usecase = providers.Factory(
        lambda uow: None,  # Stub
        uow=providers.Factory(lambda: None),
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
