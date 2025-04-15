import pytest
from httpx import AsyncClient
from .test_fixtures import TEST_PROJECT, auth_headers, project_id

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
    assert response.status_code == 204
    
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