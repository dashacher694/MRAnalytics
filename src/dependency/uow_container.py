"""
Unit of Work containers following complex-service pattern
"""
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from src.core.containers import BaseContainer
from src.modules.mr_analytics.infrastructure.persistence.uow import MRPersistenceUnitOfWork
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork


class UnitOfWorkContainer(DeclarativeContainer):
    """Container for Unit of Work instances"""
    
    base = providers.DependenciesContainer(BaseContainer)
    
    # Persistence Unit of Work
    persistence_uow = providers.Factory(
        MRPersistenceUnitOfWork,
        engine=base.db_engine,
    )
    
    # Query Unit of Work
    query_uow = providers.Factory(
        QueryUnitOfWork,
        engine=base.db_engine,
    )
