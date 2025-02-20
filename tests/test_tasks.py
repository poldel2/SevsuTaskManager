import pytest
import asyncio

from alembic import command
from alembic.config import Config
from httpx import AsyncClient, ASGITransport
from main import app
from core.db import AsyncSessionLocal, engine, Base
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas.tasks import TaskCreate, TaskUpdate
from fastapi import status
from core.config.settings import Settings

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """
    Фикстура, которая накатывает миграции Alembic перед запуском тестов.
    """
    # Указываем путь к alembic.ini (он должен быть корректным относительно корня проекта)
    alembic_cfg = Config("alembic.ini")
    # Подменяем URL подключения, чтобы он соответствовал тестовой БД из .env.test
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite+aiosqlite:///:memory:?cache=shared")

    # Применяем все миграции до head
    command.upgrade(alembic_cfg, "head")

    # Фикстура autouse, поэтому не обязательно возвращать значение
    yield

    # Если требуется, можно добавить откат миграций после тестов
    # command.downgrade(alembic_cfg, "base")


@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Создаёт новую сессию для каждого теста"""
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    """Асинхронный клиент для тестирования FastAPI"""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac



@pytest.fixture
def mocked_current_user():
    """Имитация текущего пользователя"""
    return {"id": 1}


@pytest.fixture
def task_create_data():
    """Данные для создания задачи"""
    return TaskCreate(
        title="Test Task",
        description="Test Description",
        priority="high",
        status="todo"
    )


@pytest.fixture
def task_update_data():
    """Данные для обновления задачи"""
    return TaskUpdate(
        title="Updated Test Task",
        description="Updated Test Description",
        priority="low",
        status="in_progress"
    )


class TestTasksRouter:
    @pytest.mark.asyncio
    async def test_create_task(self, client: AsyncClient, task_create_data):
        response = await client.post(
            "/projects/1/tasks/",
            json=task_create_data.model_dump(),
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["title"] == task_create_data.title
        assert response_data["description"] == task_create_data.description

    @pytest.mark.asyncio
    async def test_get_task(self, client: AsyncClient):
        response = await client.get(
            "/projects/1/tasks/1",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert "id" in response_data

    @pytest.mark.asyncio
    async def test_get_tasks_by_project(self, client: AsyncClient):
        response = await client.get(
            "/projects/1/tasks/",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)

    @pytest.mark.asyncio
    async def test_get_tasks_by_sprint(self, client: AsyncClient):
        response = await client.get(
            "/projects/1/tasks/sprint/1",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)

    @pytest.mark.asyncio
    async def test_update_task(self, client: AsyncClient, task_update_data):
        response = await client.put(
            "/projects/1/tasks/1",
            json=task_update_data.model_dump(),
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["title"] == task_update_data.title

    @pytest.mark.asyncio
    async def test_partial_update_task(self, client: AsyncClient, task_update_data):
        response = await client.patch(
            "/projects/1/tasks/1",
            json=task_update_data.model_dump(),
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["title"] == task_update_data.title

    @pytest.mark.asyncio
    async def test_delete_task(self, client: AsyncClient):
        response = await client.delete(
            "/projects/1/tasks/1",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
