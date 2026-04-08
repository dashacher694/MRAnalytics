"""
Unit of Work containers following complex-service pattern
"""
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, copy

from src.core.containers import BaseContainer
from src.modules.mr_analytics.infrastructure.persistence.uow import MRPersistenceUnitOfWork
from src.modules.mr_analytics.infrastructure.query.uow import QueryUnitOfWork


@copy(BaseContainer)
class UnitOfWorkContainer(BaseContainer):
    """Container for Unit of Work instances"""
    
    persistence_uow = providers.Factory(
        MRPersistenceUnitOfWork,
        engine=BaseContainer.db_engine,
    )
    
    query_uow = providers.Factory(
        QueryUnitOfWork,
        engine=BaseContainer.db_engine,
    )
