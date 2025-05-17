import random
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.handlers.exception_handlers import validation_exception_handler
from core.scheduler import setup_scheduler
from core.logging.config import setup_logging
from core.logging.middleware.request_logging import RequestLoggingMiddleware
from routers import router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_scheduler()
    setup_logging()
    yield


# setup_logging()

app = FastAPI(lifespan = lifespan)

app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://sevsutasktracker.ru"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def start_scheduler():
#     setup_scheduler()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

