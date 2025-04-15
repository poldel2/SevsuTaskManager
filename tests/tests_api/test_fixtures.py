import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

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