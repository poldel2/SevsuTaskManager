import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from models.domain.tasks import TaskStatus, TaskGrade

TEST_USER = {
    "email": "test@test.com",
    "password": "test123",
    "first_name": "Test",
    "last_name": "User"
}

TEST_PROJECT = {
    "title": "Test Project",
    "description": "Test Description"
}

TEST_TASK = {
    "title": "Test Task",
    "description": "Test Description",
    "status": TaskStatus.TODO.value,
    "priority": "medium",
    "grade": TaskGrade.MEDIUM.value,
    "due_date": (datetime.now() + timedelta(days=7)).isoformat()
}

@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post("/register", json=TEST_USER)
    response = await client.post("/login/local", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def project_id(client: AsyncClient, auth_headers):
    response = await client.post("/projects/", json=TEST_PROJECT, headers=auth_headers)
    return response.json()["id"]

@pytest.fixture
async def sprint_id(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/sprints/",
        json={
            "title": "Test Sprint",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=14)).isoformat()
        },
        headers=auth_headers
    )
    return response.json()["id"]

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json=TEST_TASK,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == TEST_TASK["title"]
    assert data["project_id"] == project_id

@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json=TEST_TASK,
        headers=auth_headers
    )
    task_id = response.json()["id"]
    
    response = await client.get(
        f"/projects/{project_id}/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == TEST_TASK["title"]

@pytest.mark.asyncio
async def test_get_project_tasks(client: AsyncClient, auth_headers, project_id):
    await client.post(f"/projects/{project_id}/tasks/", json=TEST_TASK, headers=auth_headers)
    await client.post(f"/projects/{project_id}/tasks/", json={**TEST_TASK, "title": "Task 2"}, headers=auth_headers)
    
    response = await client.get(f"/projects/{project_id}/tasks/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json=TEST_TASK,
        headers=auth_headers
    )
    task_id = response.json()["id"]
    
    update_data = {
        "title": "Updated Task",
        "description": "Updated Description"
    }
    
    response = await client.put(
        f"/projects/{project_id}/tasks/{task_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]

@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json=TEST_TASK,
        headers=auth_headers
    )
    task_id = response.json()["id"]
    
    response = await client.delete(
        f"/projects/{project_id}/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    response = await client.get(
        f"/projects/{project_id}/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_submit_for_review(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json=TEST_TASK,
        headers=auth_headers
    )
    task_id = response.json()["id"]
    
    response = await client.post(
        f"/projects/{project_id}/tasks/{task_id}/submit-for-review",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TaskStatus.NEED_REVIEW.value

@pytest.mark.asyncio
async def test_reject_task(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json=TEST_TASK,
        headers=auth_headers
    )
    task_id = response.json()["id"]
    
    await client.post(
        f"/projects/{project_id}/tasks/{task_id}/submit-for-review",
        headers=auth_headers
    )
    
    response = await client.post(
        f"/projects/{project_id}/tasks/{task_id}/reject",
        json={"feedback": "Needs improvement"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TaskStatus.REJECTED.value
    assert data["feedback"] == "Needs improvement"

@pytest.mark.asyncio
async def test_get_sprint_tasks(client: AsyncClient, auth_headers, project_id, sprint_id):
    task_with_sprint = {**TEST_TASK, "sprint_id": sprint_id}
    await client.post(f"/projects/{project_id}/tasks/", json=task_with_sprint, headers=auth_headers)
    await client.post(f"/projects/{project_id}/tasks/", json=TEST_TASK, headers=auth_headers)
    
    response = await client.get(
        f"/projects/{project_id}/tasks/sprint/{sprint_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sprint_id"] == sprint_id

@pytest.mark.asyncio
async def test_approve_task_as_leader(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json={**TEST_TASK, "grade": TaskGrade.MEDIUM.value},
        headers=auth_headers
    )
    task_id = response.json()["id"]
    
    await client.post(
        f"/projects/{project_id}/tasks/{task_id}/submit-for-review",
        headers=auth_headers
    )
    
    response = await client.post(
        f"/projects/{project_id}/tasks/{task_id}/approve",
        json={"is_teacher_approval": False},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TaskStatus.APPROVED_BY_LEADER.value

@pytest.mark.asyncio
async def test_approve_task_as_teacher(client: AsyncClient, auth_headers, project_id):
    teacher = {
        "email": "teacher@test.com",
        "password": "test123",
        "first_name": "Teacher",
        "last_name": "User"
    }
    await client.post("/register", json=teacher)
    
    response = await client.post("/login/local", json={
        "email": teacher["email"],
        "password": teacher["password"]
    })
    teacher_token = response.json()["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    await client.post(
        f"/projects/{project_id}/teachers",
        json={"email": teacher["email"]},
        headers=auth_headers
    )
    
    response = await client.post(
        f"/projects/{project_id}/tasks/",
        json={**TEST_TASK, "grade": TaskGrade.HARD.value},
        headers=auth_headers
    )
    task_id = response.json()["id"]
    
    await client.post(
        f"/projects/{project_id}/tasks/{task_id}/submit-for-review",
        headers=auth_headers
    )
    
    response = await client.post(
        f"/projects/{project_id}/tasks/{task_id}/approve",
        json={"is_teacher_approval": True},
        headers=teacher_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TaskStatus.APPROVED_BY_TEACHER.value