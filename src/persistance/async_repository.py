"""
AsyncRepository base class to replace pymfdata dependency
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

ModelType = TypeVar('ModelType')
IDType = TypeVar('IDType')


class AsyncRepository(Generic[ModelType, IDType], ABC):
    """Base async repository class"""
    
    @abstractmethod
    async def get(self, id: IDType) -> Optional[ModelType]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> list[ModelType]:
        """Get all entities"""
        pass
    
    @abstractmethod
    async def add(self, entity: ModelType) -> ModelType:
        """Add new entity"""
        pass
    
    @abstractmethod
    async def update(self, entity: ModelType) -> ModelType:
        """Update entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: IDType) -> bool:
        """Delete entity by ID"""
        pass
