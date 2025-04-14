import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/register", json={
        "email": "test@test.com",
        "password": "test123",
        "first_name": "Test",
        "last_name": "User"
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@test.com"

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # Регистрация пользователя
    await client.post("/register", json={
        "email": "test@test.com",
        "password": "test123",
        "first_name": "Test",
        "last_name": "User"
    })
    
    # Попытка входа
    response = await client.post("/login/local", json={
        "email": "test@test.com",
        "password": "test123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data