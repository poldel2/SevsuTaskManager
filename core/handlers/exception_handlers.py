from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        f"Validation error on {request.url.path}:",
        extra={
            "method": request.method,
            "url": str(request.url),
            "errors": exc.errors(),
            "body": exc.body,
        }
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )