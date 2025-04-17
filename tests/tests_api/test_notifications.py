import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from models.domain.tasks import TaskStatus, TaskGrade
from models.domain.notifications import NotificationType
from .test_fixtures import auth_headers, project_id
from services.notification_service import NotificationService
from services.notification_manager import NotificationManager
from repositories.notification_repository import NotificationRepository
from dependencies import get_notification_manager

@pytest.fixture
async def notification_manager():
    manager = NotificationManager()
    yield manager
    await manager.disconnect() 

@pytest.fixture
async def assignee_data(client: AsyncClient):
    assignee = {
        "email": "assignee@test.com",
        "password": "test123",
        "first_name": "Assignee",
        "last_name": "User"
    }
    response = await client.post("/register", json=assignee)
    created_user = response.json()
    
    response = await client.post("/login/local", json={
        "email": assignee["email"],
        "password": assignee["password"]
    })
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    return {"headers": headers, "user_id": created_user["id"]}

@pytest.mark.asyncio
async def test_task_assignment_notification(client: AsyncClient, auth_headers, project_id, assignee_data, notification_manager):
    await client.post(
        f"/projects/{project_id}/users/{assignee_data['user_id']}",
        headers=auth_headers
    )
    
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "status": TaskStatus.TODO.value,
        "priority": "medium",
        "grade": TaskGrade.MEDIUM.value,
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "assignee_id": assignee_data["user_id"]
    }
    
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json=task_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    task = response.json()
    
    response = await client.get(
        "/notifications/",
        headers=assignee_data["headers"]
    )
    assert response.status_code == 200
    notifications = response.json()
    
    assert len(notifications) > 0
    notification = next(n for n in notifications if n["type"] == NotificationType.TASK_ASSIGNED)
    assert notification["read"] == False
    assert notification["notification_metadata"]["task_id"] == task["id"]
    assert notification["notification_metadata"]["task_title"] == task_data["title"]