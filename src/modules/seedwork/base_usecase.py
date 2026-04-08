"""
Base use case classes to replace pymfdata dependencies
"""
from typing import TypeVar, Generic
from abc import ABC, abstractmethod

UoW = TypeVar('UoW')


class BaseUseCase(Generic[UoW], ABC):
    """Base use case class"""
    
    def __init__(self, uow: UoW):
        self._uow = uow
    
    @abstractmethod
    async def invoke(self, request):
        """Execute the use case"""
        pass


def async_transactional(read_only: bool = False):
    """Decorator for transactional operations - stub implementation"""
    def decorator(func):
        return func
    return decorator
