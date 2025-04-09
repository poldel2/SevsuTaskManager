import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core.scheduler import setup_scheduler
from core.logging.config import setup_logging
from core.logging.middleware.request_logging import RequestLoggingMiddleware
from routers import router

setup_logging()

app = FastAPI()

app.add_middleware(RequestLoggingMiddleware)

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

@app.on_event("startup")
async def start_scheduler():
    setup_scheduler()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

