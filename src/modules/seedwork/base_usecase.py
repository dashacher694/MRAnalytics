from abc import ABC, abstractmethod
from typing import TypeVar, Generic

UowType = TypeVar('UowType')


class BaseUseCase(Generic[UowType], ABC):
    def __init__(self, uow: UowType) -> None:
        self._uow = uow
    
    @property
    def uow(self) -> UowType:
        return self._uow
    
    @abstractmethod
    async def invoke(self, request):
        pass


def async_transactional(read_only: bool = False):
    def decorator(func):
        return func
    return decorator
