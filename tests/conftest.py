import pytest
import asyncio
import sys
from unittest.mock import MagicMock
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.db import Base, get_db

sys.modules['core.logging.config'] = MagicMock()

from main import app

TEST_DATABASE_URL = "postgresql+asyncpg://testuser:testpass@localhost:5434/testdb"


engine_test = create_async_engine(TEST_DATABASE_URL)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def init_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client