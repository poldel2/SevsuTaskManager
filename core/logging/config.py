import logging
import sys
import os
from pathlib import Path
from typing import Optional

from .constants import (
    DEFAULT_LOG_FILE,
    DEFAULT_MAX_BYTES,
    DEFAULT_BACKUP_COUNT,
    EXTERNAL_LOGGERS_CONFIG
)
from .formatters.json_formatter import JsonFormatter
from .handlers.async_handler import AsyncRotatingFileHandler

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_size: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    buffer_size: int = 100,
    flush_interval: float = 1.0
) -> None:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(log_dir, 0o777)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    file_handler = AsyncRotatingFileHandler(
        log_dir / (log_file or DEFAULT_LOG_FILE),
        maxBytes=max_size,
        backupCount=backup_count,
        buffer_size=buffer_size,
        flush_interval=flush_interval,
        encoding='utf-8'
    )
    file_handler.setFormatter(JsonFormatter())
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    for logger_name, level in EXTERNAL_LOGGERS_CONFIG.items():
        logging.getLogger(logger_name).setLevel(level)