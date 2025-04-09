import logging
from contextlib import contextmanager
from typing import Optional

@contextmanager
def temp_log_level(logger: Optional[logging.Logger] = None, level: int = logging.DEBUG):
    """Временно меняет уровень логирования для указанного логгера"""
    if logger is None:
        logger = logging.getLogger()
        
    old_level = logger.level
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)