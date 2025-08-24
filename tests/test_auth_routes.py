# pylint:disable=redefined-outer-name
import asyncio
from fastapi import status
import pytest


@pytest.fixture
def test_user_data():
    """Фикстура с тестовыми данными пользователя"""
    return {"email": "test@gmail.com", "username": "test", "password": "test123"}


@pytest.mark.anyio
async def test_register(async_client, test_db, test_user_data):
    """Тест регистрации пользователя"""

    response = await async_client.post(
        "/auth/register",
        json=test_user_data,
    )

    assert response.status_code == 200

    # Проверяем ответ
    data = response.json()
    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_register_duplicate_email(async_client, test_db, test_user_data):
    """Тест регистрации с существующим email"""
    # Первая регистрация
    await async_client.post(
        "/auth/register",
        json=test_user_data,
    )

    # Вторая попытка с тем же email
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "test@gmail.com",
            "username": "test2",
            "password": "test123",
        },
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_duplicate_username(async_client, test_db, test_user_data):
    """Тест регистрации с существующим username"""
    # Первая регистрация
    await async_client.post(
        "/auth/register",
        json=test_user_data,
    )

    # Вторая попытка с тем же username
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "test1@gmail.com",
            "username": "test",
            "password": "test123",
        },
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.anyio
async def test_login(async_client, test_db, test_user_data):
    """Тест входа пользователя"""
    # Сначала регистрируем
    await async_client.post(
        "/auth/register",
        json=test_user_data,
    )

    # Затем логинимся
    response = await async_client.post(
        "/auth/login",
        json={
            "email": "test@gmail.com",
            "password": "test123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_wrong_password(async_client, test_db, test_user_data):
    """Тест входа с неправильным паролем"""
    # Сначала регистрируем
    await async_client.post(
        "/auth/register",
        json=test_user_data,
    )

    # Пытаемся войти с неправильным паролем
    response = await async_client.post(
        "/auth/login",
        json={
            "email": "test@gmail.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert "Incorrect email or password" == response.json()["detail"]


@pytest.mark.anyio
async def test_login_wrong_email(async_client, test_db, test_user_data):
    """Тест входа с несуществующим email"""
    # Сначала регистрируем
    await async_client.post(
        "/auth/register",
        json=test_user_data,
    )

    # Пытаемся войти
    response = await async_client.post(
        "/auth/login",
        json={
            "email": "unathorization_email@gmail.com",
            "password": "test123",
        },
    )

    assert response.status_code == 401
    assert "Incorrect email or password" == response.json()["detail"]


@pytest.mark.anyio
async def test_get_info_users_me(async_client, test_db, test_user_data):
    await async_client.post(
        "/auth/register",
        json=test_user_data,
    )

    response = await async_client.post(
        "/auth/login",
        json={
            "email": "test@gmail.com",
            "password": "test123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] is not None
    assert data["refresh_token"] is not None

    response_me = await async_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {data['refresh_token']}"}
    )

    user_data = response_me.json()

    assert response_me.status_code == 200
    assert user_data["email"] == "test@gmail.com"
    assert user_data["username"] == "test"
    assert user_data["is_active"] is True
    assert user_data["id"] == 1


@pytest.mark.anyio
async def test_me_without_token(async_client, test_db):
    """Тест получения информации без токена"""
    response = await async_client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_me_with_invalid_token(async_client, test_db):
    """Тест получения информации с невалидным токеном"""
    response = await async_client.get(
        "/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_refresh_token_success(async_client, test_db, test_user_data):
    register_response = await async_client.post("/auth/register", json=test_user_data)
    assert register_response.status_code == status.HTTP_200_OK
    original_refresh_token = register_response.json()["refresh_token"]

    await asyncio.sleep(2)
    refresh_response = await async_client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {original_refresh_token}"}
    )

    assert refresh_response.status_code == status.HTTP_200_OK
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert "refresh_token" in refresh_data
    assert "token_type" in refresh_data
    assert refresh_data["token_type"] == "bearer"

    assert refresh_data["refresh_token"] != original_refresh_token


@pytest.mark.anyio
async def test_refresh_token_invalid_token(async_client, test_db):
    response = await async_client.post(
        "/auth/refresh", headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid refresh token" in response.json()["detail"]


@pytest.mark.anyio
async def test_refresh_token_missing_header(async_client, test_db):
    response = await async_client.post("/auth/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Refresh token required" in response.json()["detail"]


@pytest.mark.anyio
async def test_refresh_token_expired_token(async_client, test_db, test_user_data):
    """Test refresh with expired token (simulated)"""
    # This test would require mocking time or creating an expired token
    # For now, we'll test with a malformed token
    response = await async_client.post(
        "/auth/refresh", headers={"Authorization": "Bearer expired.malformed.token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_logout_success(async_client, test_db, test_user_data):
    # pylint: disable=import-outside-toplevel
    """Test successful logout with valid access token"""
    # Register and login
    register_response = await async_client.post("/auth/register", json=test_user_data)
    access_token = register_response.json()["access_token"]

    # Logout
    logout_response = await async_client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert logout_response.status_code == status.HTTP_200_OK
    assert logout_response.json()["message"] == "Successfully logged out"

    # Verify user is deactivated and refresh token is cleared
    from app.database.models import User
    from sqlalchemy import select

    result = await test_db.execute(
        select(User).where(User.email == test_user_data["email"])
    )
    user = result.scalar_one()

    assert user.refresh_token is None
    assert user.is_active is False


@pytest.mark.anyio
async def test_logout_with_refresh_token(async_client, test_db, test_user_data):
    """Test logout using refresh token instead of access token"""
    # Register user
    register_response = await async_client.post("/auth/register", json=test_user_data)
    refresh_token = register_response.json()["refresh_token"]

    # Logout with refresh token
    logout_response = await async_client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert logout_response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_logout_unauthorized(async_client, test_db):
    """Test logout without authentication"""
    response = await async_client.post("/auth/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_logout_invalid_token(async_client, test_db):
    """Test logout with invalid token"""
    response = await async_client.post(
        "/auth/logout", headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_operations_after_logout(async_client, test_db, test_user_data):
    """Test that tokens are invalidated after logout"""
    # Register user
    register_response = await async_client.post("/auth/register", json=test_user_data)
    access_token = register_response.json()["access_token"]
    refresh_token = register_response.json()["refresh_token"]

    # Logout
    logout_response = await async_client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_response.status_code == status.HTTP_200_OK

    # Try to use access token after logout
    me_response = await async_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_response.status_code == status.HTTP_400_BAD_REQUEST

    # Try to refresh with old refresh token after logout
    refresh_response = await async_client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_refresh_token_rotation(async_client, test_db, test_user_data):
    """Test that refresh tokens are properly rotated"""
    # Register user
    register_response = await async_client.post("/auth/register", json=test_user_data)
    first_refresh_token = register_response.json()["refresh_token"]

    await asyncio.sleep(2)

    # First refresh
    refresh_1_response = await async_client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {first_refresh_token}"}
    )
    assert refresh_1_response.status_code == status.HTTP_200_OK
    second_refresh_token = refresh_1_response.json()["refresh_token"]

    await asyncio.sleep(2)

    # Second refresh with new token
    refresh_2_response = await async_client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {second_refresh_token}"}
    )
    assert refresh_2_response.status_code == status.HTTP_200_OK
    third_refresh_token = refresh_2_response.json()["refresh_token"]

    # Verify all tokens are different (proper rotation)
    assert first_refresh_token != second_refresh_token
    assert second_refresh_token != third_refresh_token
    assert first_refresh_token != third_refresh_token

    # Old tokens should no longer work
    old_token_response = await async_client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {first_refresh_token}"}
    )
    assert old_token_response.status_code == status.HTTP_401_UNAUTHORIZED
