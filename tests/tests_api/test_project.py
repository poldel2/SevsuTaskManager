import pytest
from httpx import AsyncClient
from .test_fixtures import TEST_PROJECT, auth_headers, project_id

TEST_COLUMN = {
    "name": "Test Column",
    "position": 0,
    "color": "#808080"
}

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers):
    response = await client.post("/projects/", json=TEST_PROJECT, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == TEST_PROJECT["title"]
    assert data["description"] == TEST_PROJECT["description"]

@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, auth_headers, project_id):
    response = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["title"] == TEST_PROJECT["title"]

@pytest.mark.asyncio
async def test_get_all_projects(client: AsyncClient, auth_headers, project_id):
    await client.post("/projects/", json={**TEST_PROJECT, "title": "Second Project"}, headers=auth_headers)
    
    response = await client.get("/projects/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, auth_headers, project_id):
    update_data = {
        "title": "Updated Project",
        "description": "Updated Description"
    }
    
    response = await client.put(
        f"/projects/{project_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]

@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, auth_headers, project_id):
    response = await client.delete(
        f"/projects/{project_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    response = await client.get(
        f"/projects/{project_id}",
        headers=auth_headers
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_add_user_to_project(client: AsyncClient, auth_headers, project_id):
    other_user = {
        "email": "other@test.com",
        "password": "test123",
        "first_name": "Other",
        "last_name": "User"
    }
    response = await client.post("/register", json=other_user)
    created_user = response.json()
    
    response = await client.post(
        f"/projects/{project_id}/users/{created_user['id']}",
        headers=auth_headers
    )
    assert response.status_code == 201

    response = await client.get(
        f"/projects/{project_id}/users",
        headers=auth_headers
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    assert any(u["email"] == other_user["email"] for u in users)

@pytest.mark.asyncio
async def test_remove_user_from_project(client: AsyncClient, auth_headers, project_id):
    other_user = {
        "email": "other@test.com",
        "password": "test123",
        "first_name": "Other",
        "last_name": "User"
    }
    response = await client.post("/register", json=other_user)
    created_user = response.json()
    
    await client.post(
        f"/projects/{project_id}/users/{created_user['id']}",
        headers=auth_headers
    )
    
    response = await client.delete(
        f"/projects/{project_id}/users/{created_user['id']}",
        headers=auth_headers
    )
    assert response.status_code == 204

    response = await client.get(
        f"/projects/{project_id}/users",
        headers=auth_headers
    )
    users = response.json()
    assert len(users) == 1
    assert all(u["email"] != other_user["email"] for u in users)

@pytest.mark.asyncio
async def test_get_project_unauthorized(client: AsyncClient, project_id):
    response = await client.get(f"/projects/{project_id}")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_non_existent_project(client: AsyncClient, auth_headers):
    response = await client.get("/projects/999999", headers=auth_headers)
    assert response.status_code == 404

@pytest.fixture
async def column_id(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/columns",
        json=TEST_COLUMN,
        headers=auth_headers
    )
    return response.json()["id"]

@pytest.mark.asyncio
async def test_get_project_users(client: AsyncClient, auth_headers, project_id):
    response = await client.get(
        f"/projects/{project_id}/users",
        headers=auth_headers
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1 

@pytest.mark.asyncio
async def test_get_columns(client: AsyncClient, auth_headers, project_id):
    response = await client.get(
        f"/projects/{project_id}/columns",
        headers=auth_headers
    )
    assert response.status_code == 200
    columns = response.json()
    assert len(columns) > 0 

@pytest.mark.asyncio
async def test_create_column(client: AsyncClient, auth_headers, project_id):
    response = await client.post(
        f"/projects/{project_id}/columns",
        json=TEST_COLUMN,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == TEST_COLUMN["name"]
    assert data["position"] == TEST_COLUMN["position"]

@pytest.mark.asyncio
async def test_update_column(client: AsyncClient, auth_headers, project_id, column_id):
    update_data = {
        "name": "Updated Column",
        "position": 1,
        "color": "#000000"
    }
    response = await client.put(
        f"/projects/{project_id}/columns/{column_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["position"] == update_data["position"]
    assert data["color"] == update_data["color"]

@pytest.mark.asyncio
async def test_delete_column(client: AsyncClient, auth_headers, project_id, column_id):
    response = await client.delete(
        f"/projects/{project_id}/columns/{column_id}",
        headers=auth_headers
    )
    assert response.status_code == 200

    response = await client.get(
        f"/projects/{project_id}/columns",
        headers=auth_headers
    )
    columns = response.json()
    assert not any(col["id"] == column_id for col in columns)

@pytest.mark.asyncio
async def test_get_project_activities(client: AsyncClient, auth_headers, project_id):
    response = await client.get(
        f"/projects/{project_id}/activities",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)

@pytest.mark.asyncio
async def test_get_project_participants_report(client: AsyncClient, auth_headers, project_id):
    response = await client.get(
        f"/projects/{project_id}/reports/participants",
        headers=auth_headers
    )
    assert response.status_code == 200
    report = response.json()
    assert isinstance(report, list)