import logging
import functools
import traceback
import asyncio
from typing import Callable, TypeVar, ParamSpec

T = TypeVar('T')
P = ParamSpec('P')

def log_error(logger: logging.Logger = None):
    """Декоратор для логирования ошибок в функциях/методах"""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                nonlocal logger
                if logger is None:
                    logger = logging.getLogger(func.__module__)
                
                error_details = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc(),
                    'function': func.__name__,
                    'args': repr(args),
                    'kwargs': repr(kwargs)
                }
                logger.error(
                    f"Ошибка в {func.__name__}",
                    extra=error_details
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                nonlocal logger
                if logger is None:
                    logger = logging.getLogger(func.__module__)
                
                error_details = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc(),
                    'function': func.__name__,
                    'args': repr(args),
                    'kwargs': repr(kwargs)
                }
                logger.error(
                    f"Ошибка в {func.__name__}",
                    extra=error_details
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator