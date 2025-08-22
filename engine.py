import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError

from models import Base


engine = create_async_engine(os.getenv("DB_URL"), echo=True, pool_pre_ping=True)

session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = session_maker()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_engine():
    await engine.dispose()
