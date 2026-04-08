"""
Base use case classes to replace pymfdata dependencies
"""
from abc import ABC, abstractmethod


class BaseUseCase(ABC):
    """Base use case class"""
    
    @abstractmethod
    async def invoke(self, request):
        """Execute the use case"""
        pass


def async_transactional(read_only: bool = False):
    """Decorator for transactional operations - stub implementation"""
    def decorator(func):
        return func
    return decorator
