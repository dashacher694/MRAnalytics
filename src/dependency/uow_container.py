"""
Unit of Work containers following complex-service pattern
"""
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, copy

from src.core.containers import BaseContainer


@copy(BaseContainer)
class UnitOfWorkContainer(BaseContainer):
    """Container for Unit of Work instances"""
    
    # For now, create minimal stubs to avoid import errors
    # These will be implemented when the actual UoW classes are created
    persistence_uow = providers.Factory(
        lambda engine: None,  # Stub implementation
        engine=BaseContainer.db_engine,
    )
    
    query_uow = providers.Factory(
        lambda engine: None,  # Stub implementation  
        engine=BaseContainer.db_engine,
    )
