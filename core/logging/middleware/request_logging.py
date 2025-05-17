import logging
import threading
from time import time
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..constants import SKIP_ROUTES, IMPORTANT_ROUTES, HTTP_METHODS_LOG_LEVELS

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._metrics = {}
        self._lock = threading.Lock()

    def _should_log(self, path: str, method: str) -> Optional[int]:
        if path in SKIP_ROUTES:
            return None
            
        if path in IMPORTANT_ROUTES:
            return logging.INFO
            
        if method == 'GET' and not any(p in path for p in ['/tasks/', '/columns/']):
            return None
            
        return HTTP_METHODS_LOG_LEVELS.get(method, logging.INFO)

    def _update_metrics(self, path: str, duration: float):
        with self._lock:
            if path not in self._metrics:
                self._metrics[path] = {"count": 0, "total_time": 0}
            self._metrics[path]["count"] += 1
            self._metrics[path]["total_time"] += duration

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        log_level = self._should_log(path, method)
        start_time = time()

        try:
            response = await call_next(request)
            
            if log_level is not None:
                duration = time() - start_time
                self._update_metrics(path, duration)
                
                if duration > 1.0:
                    log_level = logging.WARNING
                logger.info(
                    # log_level,
                    f"{method} {path}",
                    extra={
                        "request": {
                            "id": getattr(request.state, "request_id", None),
                            "method": method,
                            "path": path,
                            "duration": f"{duration:.3f}s",
                            "status": response.status_code
                        }
                    }
                )
            
            return response
            
        except Exception as e:
            duration = time() - start_time
            logger.error(
                f"Ошибка в {method} {path}: {str(e)}",
                extra={
                    "request": {
                        "id": getattr(request.state, "request_id", None),
                        "method": method,
                        "path": path,
                        "duration": f"{duration:.3f}s"
                    },
                    "error": str(e)
                },
                exc_info=True
            )
            raise