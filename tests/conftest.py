import os
os.environ["TESTING"] = "True"

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from tests.test_settings import test_settings
import asyncio
from core.config.settings import settings
from unittest.mock import patch
from core.db import AsyncSessionLocal, engine as main_engine
from core.db import Base
import platform

if platform.system() == 'Windows':
    from asyncio import WindowsSelectorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

@pytest.fixture(scope="session", autouse=True)
def set_testing_env():
    os.environ["TESTING"] = "True"
    test_settings.sync_with_main_settings(settings)
    print(f"Тестовая база данных: {settings.DATABASE_URL}")
    yield

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create engine for test database"""
    engine = create_async_engine(
        settings.DATABASE_URL,
        isolation_level="AUTOCOMMIT",
        echo=True,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def test_async_session_local(test_engine):
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    return async_session

@pytest_asyncio.fixture(autouse=True)
async def patch_db_components(test_engine, test_async_session_local):
    """Патчим компоненты базы данных для тестов"""
    with patch("core.db.engine", test_engine), \
         patch("core.db.AsyncSessionLocal", test_async_session_local):
         
        async def get_test_db():
            async with test_async_session_local() as session:
                try:
                    yield session
                finally:
                    await session.close()
        
        with patch("core.db.get_db", side_effect=get_test_db):
            yield

@pytest_asyncio.fixture
async def db_session(test_async_session_local):
    """Создаем сессию для каждого теста"""
    async with test_async_session_local() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture(autouse=True)
async def clean_tables(db_session):
    """Очищаем таблицы перед каждым тестом"""
    try:
        await db_session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        
        # Получаем список всех таблиц
        result = await db_session.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result]
        
        # Очищаем каждую таблицу
        for table in tables:
            if table != 'alembic_version':  # Пропускаем системные таблицы
                await db_session.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
        
        await db_session.commit()
    except Exception as e:
        print(f"Ошибка при очистке таблиц: {e}")
        await db_session.rollback()
        raise