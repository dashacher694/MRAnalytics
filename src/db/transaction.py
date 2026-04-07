"""
Transaction decorator for use cases
"""
import functools
from typing import Callable, Any
from loguru import logger

from src.core.errors import DatabaseError


def transactional(read_only: bool = False):
    """
    Decorator for transactional use case methods
    
    Automatically commits on success, rolls back on error
    
    Args:
        read_only: If True, no commit is performed (read-only transaction)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            uow = self.uow
            
            try:
                result = await func(self, *args, **kwargs)
                
                if not read_only:
                    await uow.commit()
                    logger.debug(f"Transaction committed: {func.__name__}")
                
                return result
            except Exception as e:
                await uow.rollback()
                logger.error(f"Transaction rolled back: {func.__name__} - {e}")
                raise DatabaseError(f"Transaction failed: {e}")
        
        return wrapper
    return decorator
