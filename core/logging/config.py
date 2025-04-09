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
    buffer_size: int = 100,  # Уменьшенный размер буфера
    flush_interval: float = 1.0  # Уменьшенный интервал
) -> None:
    """Настройка конфигурации логирования"""
    # Используем относительный путь
    log_dir = Path("logs")
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        print(f"Log directory created/verified at {log_dir.absolute()}")
    except Exception as e:
        print(f"Error creating log directory: {e}")
        return

    try:
        os.chmod(log_dir, 0o777)
        print(f"Permissions set for {log_dir}")
    except Exception as e:
        print(f"Error setting permissions: {e}")

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    log_file = log_file or DEFAULT_LOG_FILE
    file_path = log_dir / log_file
    
    try:
        file_handler = AsyncRotatingFileHandler(
            file_path,
            maxBytes=max_size,
            backupCount=backup_count,
            buffer_size=buffer_size,
            flush_interval=flush_interval,
            encoding='utf-8'
        )
        print(f"Log file handler created for {file_path.absolute()}")
        
        file_handler.setFormatter(JsonFormatter())
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        
        # Проверяем возможность записи
        test_msg = "Logging system initialized"
        root_logger.info(test_msg)
        file_handler.force_flush()  # Принудительная запись для проверки
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            print("Log file successfully created and written")
        else:
            print("Warning: Log file appears to be empty after write attempt")
            
    except Exception as e:
        print(f"Error setting up file handler: {e}")
        return

    for logger_name, level in EXTERNAL_LOGGERS_CONFIG.items():
        logging.getLogger(logger_name).setLevel(level)