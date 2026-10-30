from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


def make_engine(url: str, **kwargs) -> AsyncEngine:
    engine = create_async_engine(url, **kwargs)
    if engine.dialect.name == "sqlite":
        # Лише для тестів: вбудований lower() у SQLite знає тільки ASCII, lower('Багряний') лишає 'Багряний'.
        # PostgreSQL кирилицю опускає сам; SQLite підміняємо Python-версією, щоб пошук поводився однаково.
        @event.listens_for(engine.sync_engine, "connect")
        def _unicode_lower(dbapi_connection, _record):
            dbapi_connection.create_function("lower", 1, lambda s: s.lower() if s is not None else None)

    return engine


# Створюємо асинхронний engine
engine = make_engine(settings.database_url, echo=settings.debug)

# Фабрика для створення асинхронних сесій
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# Базовий клас для всіх наших моделей
class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """Одна сесія на запит: відкривається перед ендпоінтом і закривається після відповіді."""
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
