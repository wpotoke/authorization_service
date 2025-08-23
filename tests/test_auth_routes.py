# pylint:disable=redefined-outer-name
from datetime import datetime
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
    time_create = str(datetime.now()).split()[0]

    print(time_create)

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

    response_me = await async_client.get(
        "/auth/me", params={"token": data["access_token"]}
    )

    user_data = response_me.json()

    assert response_me.status_code == 200
    assert user_data["email"] == "test@gmail.com"
    assert user_data["username"] == "test"
    assert user_data["is_active"] is True
    assert user_data["created"].split(".")[0].split("T")[0] == time_create
    assert user_data["id"] == 1


@pytest.mark.anyio
async def test_me_without_token(async_client, test_db):
    """Тест получения информации без токена"""
    response = await async_client.get("/auth/me")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_me_with_invalid_token(async_client, test_db):
    """Тест получения информации с невалидным токеном"""
    response = await async_client.get(
        "/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 422
