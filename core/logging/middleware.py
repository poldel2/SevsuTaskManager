import logging
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        extra = {
            "request_id": request_id,
            "request_method": request.method,
            "request_path": request.url.path,
            "client_ip": request.client.host if request.client else None,
        }
        
        start_time = time.time()
        status_code: Optional[int] = None
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
            
        except Exception as e:
            status_code = 500
            logger.error(
                f"Ошибка при обработке запроса: {str(e)}",
                extra={**extra, "status_code": status_code},
                exc_info=True
            )
            raise
            
        finally:
            duration_ms = (time.time() - start_time) * 1000
            extra["duration_ms"] = round(duration_ms, 2)
            if status_code:
                extra["status_code"] = status_code
            
            if request.url.path not in {'/health', '/metrics', '/favicon.ico'}:
                level = logging.DEBUG if request.method == "GET" else logging.INFO
                logger.log(
                    level,
                    f"{request.method} {request.url.path} - {status_code} - {round(duration_ms, 2)}ms",
                    extra=extra
                )