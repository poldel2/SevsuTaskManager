import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from jose import jwt
from main import app
from fastapi import FastAPI
from models.domain.tasks import Task, TaskStatus, TaskGrade, TaskPriority
from models.domain.users import User
from models.domain.projects import Project
from models.domain.user_project import user_project_table, Role
from models.domain.tokens import Token
from tests.test_settings import test_settings
from models.schemas.users import UserResponse
from datetime import datetime, timedelta, timezone
from core.config.settings import settings
from sqlalchemy import text
from fastapi.testclient import TestClient

TEST_USER_DATA = {
    "id": 1,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "sub": "test-sub",
    "is_teacher": False,
    "project_roles": {1: "ADMIN"}
}

def create_test_token():
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {
        "sub": str(TEST_USER_DATA["id"]),
        "exp": expires_at
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

TEST_JWT_TOKEN = create_test_token()

@pytest_asyncio.fixture
async def mock_user():
    user = User(
        id=TEST_USER_DATA["id"],
        sub=TEST_USER_DATA["sub"],
        email=TEST_USER_DATA["email"],
        first_name=TEST_USER_DATA["first_name"],
        last_name=TEST_USER_DATA["last_name"]
    )
    type(user).is_teacher = property(lambda self: TEST_USER_DATA["is_teacher"])
    return user

@pytest_asyncio.fixture
async def mock_auth(mock_user):
    user_response = UserResponse(**TEST_USER_DATA)
    
    with patch("core.security.jwt.decode") as mock_jwt_decode, \
         patch("repositories.user_repository.UserRepository.get_token") as mock_get_token, \
         patch("repositories.user_repository.UserRepository.get_by_id") as mock_get_by_id:
        
        mock_jwt_decode.return_value = {"sub": str(TEST_USER_DATA["id"])}
        mock_get_token.return_value = True
        mock_get_by_id.return_value = mock_user
        yield user_response

@pytest_asyncio.fixture
async def async_client(setup_test_data):
    """Create an async HTTP client for testing."""
    app.dependency_overrides = {}
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.headers = {"Authorization": f"Bearer {TEST_JWT_TOKEN}"}
        yield client

@pytest_asyncio.fixture
async def setup_test_data(db_session):
    try:
        await db_session.execute(text("TRUNCATE TABLE users, projects, tasks, user_project RESTART IDENTITY CASCADE"))
        await db_session.commit()

        user = User(
            id=TEST_USER_DATA["id"],
            sub=TEST_USER_DATA["sub"],
            email=TEST_USER_DATA["email"],
            first_name=TEST_USER_DATA["first_name"],
            last_name=TEST_USER_DATA["last_name"]
        )
        db_session.add(user)
        await db_session.flush()
        
        project = Project(
            id=1,
            title="Test Project",
            description="Test Project Description",
            owner_id=user.id
        )
        db_session.add(project)
        await db_session.flush()
        
        await db_session.execute(
            user_project_table.insert().values(
                user_id=user.id,
                project_id=project.id,
                role=Role.ADMIN
            )
        )
        
        task = Task(
            id=1,
            title="Test Task",
            description="Test Description",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            project_id=project.id,
            assignee_id=user.id
        )
        db_session.add(task)
        
        task2 = Task(
            id=2,
            title="Task 2",
            description="Description 2",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            assignee_id=user.id
        )
        db_session.add(task2)
        
        token = Token(
            token=TEST_JWT_TOKEN,
            user_id=TEST_USER_DATA["id"],
            is_active=True,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1)
        )
        db_session.add(token)
        
        await db_session.commit()
        
        yield
    except Exception as e:
        print(f"Error in setup_test_data: {e}")
        await db_session.rollback()
        raise

@pytest_asyncio.fixture
async def mock_task_service():
    with patch("routers.task.get_task_service") as mock_get_service, \
         patch("dependencies.get_task_service") as mock_dep_service:
        
        mock_service = AsyncMock()
        mock_service.is_project_leader.return_value = True
        mock_service.get_user_project_role.return_value = Role.ADMIN
        
        mock_get_service.return_value = mock_service
        mock_dep_service.return_value = mock_service
        yield mock_service

@pytest.mark.asyncio
async def test_create_task(async_client):
    response = await async_client.post(
        "/projects/1/tasks/",
        json={"title": "New Test Task", "description": "New Test Description"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "New Test Task"

@pytest.mark.asyncio
async def test_get_task(async_client):
    response = await async_client.get("/projects/1/tasks/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

@pytest.mark.asyncio
async def test_update_task(async_client):
    response = await async_client.put(
        "/projects/1/tasks/1",
        json={"title": "Updated Task", "description": "Updated Description"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"

@pytest.mark.asyncio
async def test_delete_task(async_client):
    response = await async_client.delete("/projects/1/tasks/1")
    assert response.status_code == 204
    
    response = await async_client.get("/projects/1/tasks/1")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_tasks(async_client):
    response = await async_client.get("/projects/1/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert any(task["title"] == "Test Task" for task in tasks)
    assert any(task["title"] == "Task 2" for task in tasks)

@pytest.mark.asyncio
async def test_submit_for_review(async_client):
    response = await async_client.post("/projects/1/tasks/1/submit-for-review")
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.NEED_REVIEW

@pytest.mark.asyncio
async def test_approve_task(async_client):
    await async_client.post("/projects/1/tasks/1/submit-for-review")
    
    response = await async_client.post(
        "/projects/1/tasks/1/approve",
        json={"is_teacher_approval": False}
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.APPROVED_BY_LEADER

@pytest.mark.asyncio
async def test_reject_task(async_client):
    await async_client.post("/projects/1/tasks/1/submit-for-review")
    
    response = await async_client.post(
        "/projects/1/tasks/1/reject",
        json={"feedback": "Needs improvements"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.REJECTED
    assert response.json()["feedback"] == "Needs improvements"