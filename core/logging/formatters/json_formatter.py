import logging
import json
from datetime import datetime
from typing import Any, Dict
from ..constants import SKIP_ROUTES, HTTP_METHODS_LOG_LEVELS

class JsonFormatter(logging.Formatter):
    """
    Форматтер для структурированных JSON логов с дополнительным контекстом.
    Поддерживает фильтрацию технических маршрутов и динамические уровни логирования.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Пропускаем технические маршруты
        if hasattr(record, 'request_path') and record.request_path in SKIP_ROUTES:
            return ''

        # Определяем уровень логирования на основе HTTP метода
        if hasattr(record, 'request_method'):
            record.levelno = HTTP_METHODS_LOG_LEVELS.get(record.request_method, logging.INFO)
            record.levelname = logging.getLevelName(record.levelno)

        # Базовая информация
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line_number": record.lineno
        }
        
        # Добавляем метрики производительности
        if hasattr(record, 'duration_ms'):
            log_obj['performance'] = {
                'duration_ms': record.duration_ms
            }
            
        # Добавляем контекст запроса если есть
        if hasattr(record, 'request_id'):
            log_obj['request'] = {
                'id': record.request_id,
                'method': getattr(record, 'request_method', None),
                'path': getattr(record, 'request_path', None),
                'status_code': getattr(record, 'status_code', None),
                'client_ip': getattr(record, 'client_ip', None)
            }
            # Удаляем None значения
            log_obj['request'] = {k: v for k, v in log_obj['request'].items() if v is not None}
                
        # Добавляем информацию об ошибке если есть
        if record.exc_info:
            log_obj['error'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
            
        # Добавляем дополнительные поля из extra
        if hasattr(record, 'extra'):
            log_obj.update(record.extra)
            
        return json.dumps(log_obj, ensure_ascii=False)