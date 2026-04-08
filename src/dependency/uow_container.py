"""
Unit of Work containers following complex-service pattern
"""
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, copy

from src.core.containers import BaseContainer
from src.modules.mr_analytics.infrastructure.persistence.uow import MRPersistenceUnitOfWork


@copy(BaseContainer)
class UnitOfWorkContainer(BaseContainer):
    """Container for Unit of Work instances"""
    
    persistence_uow = providers.Factory(
        MRPersistenceUnitOfWork,
        engine=BaseContainer.db_engine,
    )
    
    query_uow = providers.Factory(
        MRPersistenceUnitOfWork,  # Use same UoW for now
        engine=BaseContainer.db_engine,
    )
