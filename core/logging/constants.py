from typing import Set, Dict
import logging

SKIP_ROUTES: Set[str] = {
    '/health',
    '/metrics',
    '/favicon.ico',
    '/me',  # Частые технические запросы
    '/projects/',  # Дублирующий маршрут
}

IMPORTANT_ROUTES: Set[str] = {
    '/login/local',
    '/register',
    '/logout',
}

HTTP_METHODS_LOG_LEVELS: Dict[str, int] = {
    'GET': logging.DEBUG,
    'POST': logging.INFO,
    'PUT': logging.INFO,
    'DELETE': logging.INFO,
    'PATCH': logging.INFO
}

DEFAULT_LOG_FILE = "app.log"
DEFAULT_MAX_BYTES = 50 * 1024 * 1024  # 50MB
DEFAULT_BACKUP_COUNT = 5  # Хранить 5 файлов

# 7 дней для INFO логов
RETENTION_DAYS = 7

EXTERNAL_LOGGERS_CONFIG = {
    "uvicorn.access": logging.WARNING,
    "sqlalchemy.engine": logging.WARNING,
    "apscheduler": logging.WARNING,
    "passlib": logging.WARNING
}