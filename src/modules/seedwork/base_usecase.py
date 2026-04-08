"""
Base use case classes to replace pymfdata dependencies
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

UowType = TypeVar('UowType')


class BaseUseCase(Generic[UowType], ABC):
    """Base use case class"""
    
    def __init__(self, uow: UowType) -> None:
        self._uow = uow
    
    @property
    def uow(self) -> UowType:
        return self._uow
    
    @abstractmethod
    async def invoke(self, request):
        """Execute the use case"""
        pass


def async_transactional(read_only: bool = False):
    """Decorator for transactional operations - stub implementation"""
    def decorator(func):
        return func
    return decorator
