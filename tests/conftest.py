# pylint: disable=redefined-outer-name
import os
import pytest
import httpx
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database.db import Base, get_db
from app.main import app

load_dotenv(dotenv_path=".env.test")


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Автоматически загружает тестовое окружение"""
    load_dotenv(dotenv_path=".env.test")
    # Проверяем, что переменные загрузились
    assert os.getenv("TESTING") == "true", "TESTING must be true for tests"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def test_engine():
    """Тестовый движок базы данных"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
    )

    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Очищаем перед созданием
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очищаем после использования
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine):
    """Тестовая сессия базы данных с автоматическим rollback"""
    async with test_engine.connect() as conn:
        # Начинаем транзакцию
        transaction = await conn.begin()

        # Создаем сессию, привязанную к соединению
        async_session = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        session = async_session()

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()  # Все изменения откатываются


@pytest.fixture(scope="function")
async def async_client(test_db):
    """Асинхронный test client с подменой базы данных"""

    # Функция для подмены зависимости базы данных
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass  # Закрытие обрабатывается в test_db фикстуре

    # Подменяем зависимость
    app.dependency_overrides[get_db] = override_get_db

    # Создаем асинхронный клиент
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Восстанавливаем оригинальную зависимость
    app.dependency_overrides.clear()
